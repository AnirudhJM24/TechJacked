#!/usr/bin/env python3
"""
Dining Hall Meal Optimizer
Helps you find meals that meet protein goals while staying under calorie limits.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import json
import sys
import io
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class DiningHallOptimizer:
    def __init__(self, cache_dir: str = ".cache"):
        self.base_url = "https://techdining.api.nutrislice.com/menu/api/weeks/school"
        self.dining_halls = {
            "west-village": "West Village",
            "north-ave-dining-hall": "North Ave Dining Hall"
        }
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def clear_cache(self):
        """Clear all cached menu data."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        print("Cache cleared!")

    def get_cache_info(self):
        """Get information about cached data."""
        cache_files = list(self.cache_dir.glob("*.json"))
        if not cache_files:
            return "No cached data"

        info = []
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    age_days = (datetime.now() - timestamp).days
                    info.append(f"{cache_file.stem}: {age_days} days old")
            except:
                pass
        return "\n".join(info) if info else "No valid cache"

    def _get_cache_key(self, dining_hall: str, meal_type: str, date: datetime) -> str:
        """Generate a cache key for a specific menu request."""
        # Use Monday of the week as the key since API returns weekly data
        monday = date - timedelta(days=date.weekday())
        return f"{dining_hall}_{meal_type}_{monday.strftime('%Y-%m-%d')}.json"

    def _load_from_cache(self, cache_key: str) -> Optional[List[Dict]]:
        """Load menu data from cache if it exists and is fresh."""
        cache_file = self.cache_dir / cache_key
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    # Check if cache is still valid (within 7 days)
                    cache_time = datetime.fromisoformat(cached_data['timestamp'])
                    if datetime.now() - cache_time < timedelta(days=7):
                        return cached_data['menu_items']
            except (json.JSONDecodeError, KeyError, ValueError):
                pass
        return None

    def _save_to_cache(self, cache_key: str, menu_items: List[Dict]):
        """Save menu data to cache."""
        cache_file = self.cache_dir / cache_key
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'menu_items': menu_items
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)

    def fetch_menu(self, dining_hall: str, meal_type: str, date: datetime = None, verbose: bool = True) -> List[Dict]:
        """Fetch menu items from a dining hall for a specific meal (with caching)."""
        if date is None:
            date = datetime.now()

        # Check cache first
        cache_key = self._get_cache_key(dining_hall, meal_type, date)
        cached_items = self._load_from_cache(cache_key)
        if cached_items is not None:
            if verbose:
                print(f"    ✓ Loaded from cache (week of {(date - timedelta(days=date.weekday())).strftime('%Y-%m-%d')})")
            return cached_items

        # Cache miss - fetch from API
        if verbose:
            print(f"    ↓ Fetching from API...")
        year = date.year
        month = f"{date.month:02d}"
        day = f"{date.day:02d}"

        url = f"{self.base_url}/{dining_hall}/menu-type/{meal_type}/{year}/{month}/{day}/"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Extract menu items from the response
            menu_items = []
            for day in data.get('days', []):
                for item in day.get('menu_items', []):
                    food = item.get('food', {})

                    # Parse nutritional info
                    if food is not None:
                        # rounded_nutrition_info is a dictionary, not a string
                        serving_size_info = food.get('serving_size_info', {})
                        nutrition = food.get('rounded_nutrition_info', {})

                        # Fix serving size for pounds (1 lb serving = 0.25 lbs actual)
                        amount = serving_size_info.get('serving_size_amount', '')
                        unit = serving_size_info.get('serving_size_unit', '')

                        # If unit is pounds/lbs, divide by 4 since one serving is 0.25 lbs
                        if unit and 'lb' in unit.lower() and amount:
                            try:
                                amount_float = float(amount)
                                amount = str(amount_float * 0.25)
                            except (ValueError, TypeError):
                                pass

                        serving_str = f"{amount} {unit}".strip()

                        menu_items.append({
                            'name': food.get('name', 'Unknown'),
                            'calories': nutrition.get('calories', 0) or 0,
                            'protein': nutrition.get('g_protein', 0) or 0,
                            'fat': nutrition.get('g_fat', 0) or 0,
                            'carbs': nutrition.get('g_carbs', 0) or 0,
                            'sodium': nutrition.get('mg_sodium', 0) or 0,
                            'serving': serving_str,
                            'dining_hall': self.dining_halls.get(dining_hall, dining_hall)
                        })

            # Save to cache
            self._save_to_cache(cache_key, menu_items)
            return menu_items

        except Exception as e:
            print(f"Error fetching menu from {dining_hall}: {e}")
            return []

    def _parse_nutrition(self, nutrition_str: str) -> Dict[str, float]:
        """Parse the nutrition string into a dictionary."""
        nutrition = {}
        if not nutrition_str:
            return nutrition

        # Format: "calories: 118.0, g_protein: 23.0, g_fat: 2.4, ..."
        pairs = nutrition_str.split(', ')
        for pair in pairs:
            if ':' in pair:
                key, value = pair.split(': ')
                try:
                    nutrition[key] = float(value)
                except ValueError:
                    nutrition[key] = 0.0

        return nutrition

    def categorize_food(self, item: Dict) -> str:
        """Categorize a food item based on its name and nutrition."""
        name = item['name'].lower()

        # Define keywords for each category
        protein_keywords = [
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'turkey', 'duck',
            'tofu', 'tempeh', 'seitan', 'egg', 'shrimp', 'steak', 'patty', 'sausage',
            'bacon', 'ham', 'lamb', 'tilapia', 'cod', 'halibut', 'edamame', 'beans'
        ]

        carb_keywords = [
            'rice', 'pasta', 'bread', 'potato', 'fries', 'noodle', 'quinoa', 'couscous',
            'tortilla', 'bun', 'roll', 'bagel', 'cereal', 'oat', 'waffle', 'pancake',
            'muffin', 'biscuit', 'mac', 'macaroni', 'spaghetti', 'penne', 'linguine'
        ]

        vegetable_keywords = [
            'broccoli', 'salad', 'lettuce', 'spinach', 'kale', 'carrot', 'broccolini',
            'tomato', 'cucumber', 'pepper', 'green beans', 'corn', 'peas', 'mushroom',
            'vegetable', 'greens', 'cabbage', 'cauliflower', 'asparagus', 'zucchini',
            'squash', 'brussels', 'bok choy', 'celery', 'onion', 'eggplant'
        ]

        fruit_keywords = [
            'apple', 'banana', 'orange', 'berry', 'strawberry', 'blueberry', 'melon',
            'grape', 'pineapple', 'mango', 'peach', 'pear', 'fruit', 'watermelon'
        ]

        # Check keywords (protein first as it's most important)
        for keyword in protein_keywords:
            if keyword in name:
                return 'protein'

        for keyword in vegetable_keywords:
            if keyword in name:
                return 'vegetable'

        for keyword in fruit_keywords:
            if keyword in name:
                return 'fruit'

        for keyword in carb_keywords:
            if keyword in name:
                return 'carb'

        # Use nutrition to help classify ambiguous items
        if item['protein'] >= 15:  # High protein content
            return 'protein'
        elif item['carbs'] >= 25 and item['protein'] < 8:  # High carb, low protein
            return 'carb'
        elif item['calories'] < 50 and item['carbs'] < 15:  # Low calorie, likely veggie
            return 'vegetable'

        return 'other'

    def calculate_meal_score(self, items: List[Dict], protein_goal: float,
                            calorie_limit: float) -> Tuple[float, Dict]:
        """Calculate a comprehensive score for a meal combination."""
        total_protein = sum(item['protein'] for item in items)
        total_calories = sum(item['calories'] for item in items)
        total_fat = sum(item['fat'] for item in items)
        total_carbs = sum(item['carbs'] for item in items)

        score = 0
        reasons = {}

        # Must meet basic requirements
        if total_protein < protein_goal or total_calories > calorie_limit:
            return 0, {}

        # 1. Protein efficiency (0-40 points) - PRIMARY metric
        protein_per_cal = total_protein / max(total_calories, 1)
        efficiency_score = min(protein_per_cal * 80, 40)
        score += efficiency_score
        reasons['protein_efficiency'] = protein_per_cal

        # 2. Precision bonus (0-20 points) - closer to targets is better
        protein_waste = total_protein - protein_goal
        protein_precision = max(0, 10 - protein_waste * 0.3)
        calorie_usage = total_calories / max(calorie_limit, 1)
        calorie_precision = 10 * calorie_usage if calorie_usage <= 1 else 0
        precision_score = protein_precision + calorie_precision
        score += precision_score
        reasons['precision'] = precision_score

        # 3. Balanced macros (0-25 points)
        total_cals_from_macros = (total_protein * 4) + (total_carbs * 4) + (total_fat * 9)
        if total_cals_from_macros > 0:
            protein_pct = (total_protein * 4) / total_cals_from_macros
            carb_pct = (total_carbs * 4) / total_cals_from_macros
            fat_pct = (total_fat * 9) / total_cals_from_macros

            # Ideal ranges: protein 25-35%, carbs 40-55%, fat 20-30%
            balance_score = 0
            if 0.25 <= protein_pct <= 0.35:
                balance_score += 10
            elif 0.20 <= protein_pct <= 0.40:
                balance_score += 5

            if 0.40 <= carb_pct <= 0.55:
                balance_score += 10
            elif 0.30 <= carb_pct <= 0.65:
                balance_score += 5

            if 0.20 <= fat_pct <= 0.30:
                balance_score += 5
            elif 0.15 <= fat_pct <= 0.40:
                balance_score += 2

            score += balance_score
            reasons['macro_balance'] = balance_score
            reasons['macros'] = {
                'protein_pct': protein_pct,
                'carb_pct': carb_pct,
                'fat_pct': fat_pct
            }

        # 4. Meal composition (0-15 points)
        categories = [self.categorize_food(item) for item in items]
        composition_score = 0

        has_protein = 'protein' in categories
        has_vegetable = 'vegetable' in categories or 'fruit' in categories
        has_carb = 'carb' in categories

        if has_protein:
            composition_score += 7
        if has_vegetable:
            composition_score += 5
        if has_carb:
            composition_score += 2

        # Diversity bonus - encourage variety
        unique_categories = len(set(categories))
        composition_score += min(unique_categories, 3)

        score += min(composition_score, 15)
        reasons['composition'] = min(composition_score, 15)
        reasons['categories'] = categories
        reasons['has_protein'] = has_protein
        reasons['has_vegetable'] = has_vegetable
        reasons['has_carb'] = has_carb

        return score, reasons

    def find_combinations(self, menu_items: List[Dict], protein_goal: float,
                         calorie_limit: float, dining_hall_filter: Optional[str] = None) -> List[Tuple[List[Dict], float, float]]:
        """
        Find meal combinations that meet protein goal under calorie limit.

        Strategy:
        1. Select items with best protein/calorie ratio
        2. Add quality carbs for energy
        3. Include vegetables for nutrition
        4. Sort by protein efficiency

        Args:
            menu_items: List of all menu items
            protein_goal: Minimum protein target in grams
            calorie_limit: Maximum calories allowed
            dining_hall_filter: Optional - filter to only one dining hall

        Returns list of (items, total_protein, total_calories) tuples.
        """
        valid_combos = []

        # Filter out items with no nutritional info or unreasonably high calories
        valid_items = [item for item in menu_items
                      if item['calories'] > 0
                      and item['calories'] < calorie_limit]

        # Filter by dining hall if specified
        if dining_hall_filter:
            valid_items = [item for item in valid_items if item['dining_hall'] == dining_hall_filter]
            print(f"  Filtering to {dining_hall_filter} only ({len(valid_items)} items)...")

        # Calculate efficiency metrics for all items
        for item in valid_items:
            item['category'] = self.categorize_food(item)
            item['protein_efficiency'] = item['protein'] / max(item['calories'], 1)

        # Strategy: Get the BEST items by protein efficiency

        # Top protein sources (best protein/calorie ratio, min 10g protein)
        high_protein_items = [item for item in valid_items if item['protein'] >= 10]
        high_protein_items.sort(key=lambda x: (-x['protein_efficiency'], -x['protein']))
        top_proteins = high_protein_items[:30]  # Top 30 protein-efficient items

        # Quality vegetables (nutrient-dense, low calorie)
        veggie_items = [item for item in valid_items
                       if item['category'] in ['vegetable', 'fruit']
                       and item['calories'] < 100]  # Low calorie veggies
        veggie_items.sort(key=lambda x: (-x['protein_efficiency'], x['calories']))
        top_veggies = veggie_items[:25]  # Top 25 veggies

        # Quality carbs (good energy sources with decent protein)
        carb_items = [item for item in valid_items
                     if item['category'] == 'carb'
                     and item['carbs'] >= 15  # Substantial carbs
                     and item['calories'] < 300]  # Not too calorie-dense
        carb_items.sort(key=lambda x: (-x['protein_efficiency'], x['calories']))
        top_carbs = carb_items[:20]  # Top 20 quality carbs

        print(f"  Found {len(top_proteins)} high-protein items, {len(top_veggies)} vegetables, {len(top_carbs)} quality carbs")

        # Build combinations using efficiency-optimized items

        # Strategy 1: Best Protein + Vegetable (lean & clean)
        for protein in top_proteins[:15]:  # Top 15 proteins
            for veggie in top_veggies[:15]:  # Top 15 vegetables
                if protein['name'] == veggie['name']:
                    continue  # Skip duplicates

                combo = [protein, veggie]
                total_protein = sum(i['protein'] for i in combo)
                total_calories = sum(i['calories'] for i in combo)

                if total_protein >= protein_goal and total_calories <= calorie_limit:
                    valid_combos.append((combo, total_protein, total_calories))

        # Strategy 2: Best Protein + Vegetable + Quality Carb (balanced performance)
        for protein in top_proteins[:12]:  # Top 12 proteins
            for veggie in top_veggies[:12]:  # Top 12 vegetables
                if protein['name'] == veggie['name']:
                    continue

                for carb in top_carbs[:10]:  # Top 10 carbs
                    if carb['name'] in [protein['name'], veggie['name']]:
                        continue

                    combo = [protein, veggie, carb]
                    total_protein = sum(i['protein'] for i in combo)
                    total_calories = sum(i['calories'] for i in combo)

                    if total_protein >= protein_goal and total_calories <= calorie_limit:
                        valid_combos.append((combo, total_protein, total_calories))

        # Strategy 3: Best Protein + Quality Carb (simple & effective)
        for protein in top_proteins[:15]:
            for carb in top_carbs[:12]:
                if protein['name'] == carb['name']:
                    continue

                combo = [protein, carb]
                total_protein = sum(i['protein'] for i in combo)
                total_calories = sum(i['calories'] for i in combo)

                if total_protein >= protein_goal and total_calories <= calorie_limit:
                    valid_combos.append((combo, total_protein, total_calories))

        # Strategy 4: Double Best Protein + Vegetable (high protein focus)
        for i, protein1 in enumerate(top_proteins[:10]):
            for protein2 in top_proteins[i+1:15]:
                for veggie in top_veggies[:10]:
                    if veggie['name'] in [protein1['name'], protein2['name']]:
                        continue

                    combo = [protein1, protein2, veggie]
                    total_protein = sum(i['protein'] for i in combo)
                    total_calories = sum(i['calories'] for i in combo)

                    if total_protein >= protein_goal and total_calories <= calorie_limit:
                        valid_combos.append((combo, total_protein, total_calories))

        # Strategy 5: Single item if it's exceptionally efficient
        for item in top_proteins[:20]:
            if item['protein'] >= protein_goal and item['calories'] <= calorie_limit:
                combo = [item]
                valid_combos.append((combo, item['protein'], item['calories']))

        # Remove duplicates
        unique_combos = []
        seen = set()
        for combo in valid_combos:
            items_key = tuple(sorted(item['name'] for item in combo[0]))
            if items_key not in seen:
                seen.add(items_key)
                unique_combos.append(combo)

        # Sort by protein efficiency (protein/calorie ratio), then by total protein
        unique_combos.sort(key=lambda x: (-x[1]/max(x[2], 1), -x[1]))

        return unique_combos[:15]  # Return top 15 combinations

    def display_results(self, combinations: List[Tuple[List[Dict], float, float]]):
        """Display the meal combinations in a simple list format."""
        if not combinations:
            print("\n❌ No combinations found that meet your criteria.")
            print("Try adjusting your protein goal or calorie limit.\n")
            return

        print(f"\n✅ Found {len(combinations)} meal combination(s):\n")
        print("=" * 90)

        for idx, (items, total_protein, total_calories) in enumerate(combinations, 1):
            # Calculate protein efficiency
            protein_efficiency = total_protein / max(total_calories, 1)

            # Calculate total macros
            total_fat = sum(item['fat'] for item in items)
            total_carbs = sum(item['carbs'] for item in items)

            # Header
            print(f"\n🍽️  Option {idx}: {total_protein:.1f}g protein, {total_calories:.0f} cal")
            print(f"   Protein efficiency: {protein_efficiency:.3f}g/cal")
            print("-" * 90)

            # List items with categories
            for item in items:
                category_emoji = {
                    'protein': '🍗',
                    'carb': '🍚',
                    'vegetable': '🥦',
                    'fruit': '🍎',
                    'other': '🍴'
                }
                emoji = category_emoji.get(item.get('category', 'other'), '🍴')

                print(f"  {emoji} {item['name']} ({item.get('category', 'other').title()})")
                print(f"     [{item['dining_hall']}] {item['serving']}")
                print(f"     {item['protein']:.1f}g protein, {item['calories']:.0f} cal, "
                      f"{item['fat']:.1f}g fat, {item['carbs']:.1f}g carbs")

            # Simple macro summary
            total_cals_from_macros = (total_protein * 4) + (total_carbs * 4) + (total_fat * 9)
            if total_cals_from_macros > 0:
                protein_pct = (total_protein * 4) / total_cals_from_macros
                carb_pct = (total_carbs * 4) / total_cals_from_macros
                fat_pct = (total_fat * 9) / total_cals_from_macros

                print(f"\n  📊 Macros: {protein_pct*100:.0f}% protein, "
                      f"{carb_pct*100:.0f}% carbs, {fat_pct*100:.0f}% fat")

            print()

        print("=" * 90)


    def show_top_items(self, menu_items: List[Dict], top_n: int = 10):
        """Show top N items with best protein-to-calorie ratio."""
        # Filter items with meaningful protein (min 12g) and valid calories
        valid_items = [item for item in menu_items
                      if item['calories'] > 0 and item['protein'] >= 12]

        # Remove duplicates by name + dining hall
        seen = set()
        unique_items = []
        for item in valid_items:
            key = (item['name'], item['dining_hall'])
            if key not in seen:
                seen.add(key)
                unique_items.append(item)

        # Create a list with efficiency scores
        items_with_efficiency = []
        for item in unique_items:
            protein_efficiency = item['protein'] / item['calories']
            items_with_efficiency.append({
                **item,
                'protein_efficiency': protein_efficiency
            })

        # Sort by protein efficiency (highest first)
        items_with_efficiency.sort(key=lambda x: -x['protein_efficiency'])

        # Display top N
        print(f"\n✅ Top {top_n} items by protein efficiency:\n")
        print("=" * 90)

        for idx, item in enumerate(items_with_efficiency[:top_n], 1):
            print(f"\n{idx}. {item['name']}")
            print(f"   [{item['dining_hall']}] {item['serving']}")
            print(f"   Protein: {item['protein']:.1f}g | Calories: {item['calories']:.0f}")
            print(f"   Efficiency: {item['protein_efficiency']:.3f}g/cal")
            print(f"   Fat: {item['fat']:.1f}g | Carbs: {item['carbs']:.1f}g")

        print("\n" + "=" * 90)


def main():
    print("🍽️  Dining Hall Meal Optimizer")
    print("=" * 80)

    optimizer = DiningHallOptimizer()

    # Get user inputs
    print("\nDining Hall:")
    print("1. West Village")
    print("2. North Ave Dining Hall")
    print("3. Both (search across both halls)")
    hall_choice = input("Select (1, 2, or 3): ").strip()

    if hall_choice == "1":
        selected_halls = ["west-village"]
    elif hall_choice == "2":
        selected_halls = ["north-ave-dining-hall"]
    else:
        selected_halls = list(optimizer.dining_halls.keys())

    print("\nMeal Type:")
    print("1. Lunch")
    print("2. Dinner")
    meal_choice = input("Select (1 or 2): ").strip()
    meal_type = "lunch" if meal_choice == "1" else "dinner"

    print(f"\n🔍 Loading {meal_type} menus...")

    # Fetch menus from selected dining halls
    all_items = []
    for hall_id in selected_halls:
        print(f"  • {optimizer.dining_halls[hall_id]}:")
        items = optimizer.fetch_menu(hall_id, meal_type, verbose=True)
        all_items.extend(items)
        print(f"    → {len(items)} items available")

    if not all_items:
        print("\n❌ Could not fetch menu data. Please try again later.")
        return

    # Show top 10 items by protein efficiency
    optimizer.show_top_items(all_items, top_n=10)


if __name__ == "__main__":
    main()
