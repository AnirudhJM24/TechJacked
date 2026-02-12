# Optimization Strategy Overhaul

## Latest Update (Feb 2026)

**Major Simplification:**
- ❌ Removed fiber tracking (always null in data)
- ❌ Removed complex 100-point scoring system
- ✅ Simple ranking by protein efficiency (g protein / calorie)
- ✅ Fixed serving sizes (1lb servings now correctly show as 0.25lbs)

Results now show clean meal lists sorted by protein-to-calorie ratio.

---

## Previous Changes

Completely redesigned the meal combination algorithm to focus on **efficiency ratios** instead of templates.

## New Strategy: Efficiency-First

### 1. **Best Protein/Calorie Ratio**
- Identifies items with highest protein per calorie
- Filters for minimum 10g protein
- Takes top 25 most efficient protein sources
- Examples: Grilled chicken breast, fish, lean turkey, tofu

### 2. **Best Fiber/Calorie Ratio**
- Identifies items with highest fiber per calorie
- Filters for minimum 3g fiber
- Takes top 20 most efficient fiber sources
- Examples: Broccoli, spinach, beans, berries, whole grains

### 3. **Strategic Carbs**
- Selects quality carbs with decent protein or fiber
- Minimum 15g carbs, maximum 300 calories
- Ranked by combined protein + fiber efficiency
- Examples: Quinoa, oats, sweet potato, whole grain bread

## Combination Strategies

Instead of rigid templates, uses **5 flexible strategies**:

1. **Best Protein + Best Fiber** (lean & clean)
   - Top 15 proteins × Top 15 fiber sources
   - 2-item combinations
   - Maximizes both efficiency metrics

2. **Best Protein + Best Fiber + Quality Carb** (balanced performance)
   - Top 12 proteins × Top 12 fiber × Top 10 carbs
   - 3-item combinations
   - Complete balanced meal

3. **Best Protein + Quality Carb** (simple & effective)
   - Top 15 proteins × Top 12 carbs
   - 2-item combinations
   - Quick energy with high protein

4. **Double Best Protein + Fiber** (high protein focus)
   - Top 10 proteins × Top 15 proteins × Top 10 fiber
   - 3-item combinations
   - For maximum protein intake

5. **Single Item** (exceptionally efficient)
   - Top 20 proteins only
   - 1-item meal if it meets all criteria
   - For ultra-lean goals

## Simplified Ranking System

**No more complex scoring** - meals are now simply sorted by **protein efficiency** (grams of protein per calorie).

### Why This Change?

- Simpler to understand
- Directly optimizes for the main goal: max protein, min calories
- Removes arbitrary point allocations
- Cleaner output without score breakdowns

### Ranking Criteria

Meals are sorted by:
1. **Primary**: Protein efficiency (protein/calories ratio) - highest first
2. **Secondary**: Total protein - higher is better

### Efficiency Reference

**Protein Efficiency:**
- 🔥 Excellent: > 0.25g per calorie
- ✅ Good: > 0.15g per calorie
- Fair: < 0.15g per calorie

## Benefits

✅ **Higher Quality Meals** - Only uses the most efficient items
✅ **Better Protein Density** - Prioritizes lean, high-protein foods
✅ **Improved Satiety** - High fiber keeps you full longer
✅ **Better Nutrition** - Fiber is now a first-class metric
✅ **Faster Search** - Smaller pool of top items = quicker results
✅ **More Realistic** - Combinations are actually buildable meals

## Example: Old vs New

### Old Template Approach
```
Strategy: Pick any protein + any carb + any vegetable
Result: BBQ Chicken (18g protein, 164 cal) +
        Mac & Cheese (2g protein, 34 cal) +
        Corn (2g protein, 72 cal)
Total: 22g protein, 270 cal, 1g fiber
Protein efficiency: 0.081g/cal
Fiber efficiency: 0.004g/cal
```

### New Efficiency Approach
```
Strategy: Best protein + Best fiber
Result: Grilled Chicken Breast (31g protein, 152 cal) +
        Steamed Broccoli (3g protein, 35 cal, 3g fiber)
Total: 34g protein, 187 cal, 3g fiber
Protein efficiency: 0.182g/cal 🔥
Fiber efficiency: 0.016g/cal ✅
```

## Code Changes

### Files Modified
1. `dining_optimizer.py`
   - Added fiber to nutrition data
   - Complete rewrite of `find_combinations()`
   - Updated `calculate_meal_score()` with fiber scoring
   - Updated display to show fiber

2. `app.py`
   - Added fiber display in meal cards
   - Updated score breakdown with fiber
   - Updated documentation

### Key Functions

**`find_combinations()`** - New efficiency-based algorithm:
```python
# Calculate efficiency metrics
item['protein_efficiency'] = protein / calories
item['fiber_efficiency'] = fiber / calories

# Get TOP items by efficiency
top_proteins = sorted_by_protein_efficiency[:25]
top_fiber = sorted_by_fiber_efficiency[:20]
top_carbs = sorted_by_quality[:15]

# Build combinations from best items
# 5 different strategies...
```

**`calculate_meal_score()`** - New scoring:
```python
# Protein efficiency: 35 points (was 30)
# Fiber efficiency: 15 points (NEW)
# Precision: 15 points (was 20)
# Macro balance: 20 points (was 25)
# Composition: 15 points (was 25)
```

## Migration Guide

### For Users
- No breaking changes - same input/output interface
- Results will be **higher quality** automatically
- Fiber information now displayed
- Expect to see more lean proteins and vegetables
- Fewer "junk food" combinations

### For Developers
- `find_combinations()` signature unchanged
- Items now have `fiber` field
- Score details include `fiber_efficiency` and `total_fiber`
- Templates removed - now uses strategy-based approach

## Performance

- **Same speed** - Still ~5 seconds
- **Better results** - Higher average scores
- **More consistent** - Less variance in quality

## Future Enhancements

Potential additions:
- [ ] Micronutrient tracking (vitamins, minerals)
- [ ] Sodium/sugar limits
- [ ] User preference learning
- [ ] Meal prep / batch cooking optimization
- [ ] Cost optimization
- [ ] Seasonal ingredient boosting
