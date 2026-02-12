#!/usr/bin/env python3
"""Debug script to check menu data"""

from dining_optimizer import DiningHallOptimizer
from datetime import datetime

optimizer = DiningHallOptimizer()

# Fetch lunch menu
print("Fetching menus...")
all_items = []
for hall_id in optimizer.dining_halls.keys():
    items = optimizer.fetch_menu(hall_id, "lunch")
    all_items.extend(items)

print(f"Total items: {len(all_items)}\n")

# Categorize items
for item in all_items:
    item['category'] = optimizer.categorize_food(item)

# Show distribution
from collections import Counter
categories = Counter(item['category'] for item in all_items)
print("Category distribution:")
for cat, count in categories.items():
    print(f"  {cat}: {count}")

# Show high protein items
print("\n\nTop 10 high protein items:")
protein_items = sorted(all_items, key=lambda x: x['protein'], reverse=True)[:10]
for item in protein_items:
    print(f"  {item['name']}: {item['protein']:.1f}g protein, {item['calories']:.0f} cal, category: {item['category']}")

# Show items that could meet 40g protein under 600 cal alone
print("\n\nSingle items with ≥40g protein and ≤600 cal:")
single_solutions = [item for item in all_items if item['protein'] >= 40 and item['calories'] <= 600]
for item in single_solutions[:5]:
    print(f"  {item['name']}: {item['protein']:.1f}g protein, {item['calories']:.0f} cal")

# Check a simple combo manually
proteins = [item for item in all_items if item['category'] == 'protein']
veggies = [item for item in all_items if item['category'] == 'vegetable']
carbs = [item for item in all_items if item['category'] == 'carb']

print(f"\n\nProteins: {len(proteins)}")
print(f"Vegetables: {len(veggies)}")
print(f"Carbs: {len(carbs)}")

if proteins:
    print("\n\nSample protein items:")
    for p in proteins[:5]:
        print(f"  {p['name']}: {p['protein']:.1f}g protein, {p['calories']:.0f} cal")

# Check raw API data for first item
print("\n\nChecking raw API data...")
import requests
url = "https://techdining.api.nutrislice.com/menu/api/weeks/school/west-village/menu-type/lunch/2026/02/11/"
response = requests.get(url)
data = response.json()

if data.get('days'):
    first_day = data['days'][0]
    if first_day.get('menu_items'):
        print(f"\nFirst 3 menu items (raw):")
        for item in first_day['menu_items'][:3]:
            food = item.get('food', {})
            if food:
                print(f"\nName: {food.get('name')}")
                print(f"Has nutrition info: {food.get('has_nutrition_info')}")
                print(f"Rounded nutrition info: {food.get('rounded_nutrition_info')}")
                print(f"Serving size info: {food.get('serving_size_info')}")
                print(f"Aggregated data: {food.get('aggregated_data')}")
                print(f"Food sizes: {food.get('food_sizes')}")
