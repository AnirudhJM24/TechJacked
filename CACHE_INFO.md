# Caching Information

## How It Works

The app intelligently caches menu data to minimize API requests:

### Single Request Per Week
- **One API call** fetches an entire week's worth of menu data
- Data is cached using the Monday of that week as the key
- Format: `{dining_hall}_{meal_type}_{YYYY-MM-DD}.json`

### Cache Reuse
When you run the app multiple times:
- ✅ **1st run**: Fetches from API (downloads week's data)
- ✅ **2nd run**: Loads from cache (instant!)
- ✅ **3rd run**: Still from cache (no API call needed)

### Cache Validity
- Cached data is valid for **7 days**
- Automatically refreshes after expiration
- Weekly data means menus update on Mondays

## Example Cache Usage

```
Monday (Feb 10):
  - Run app → API call → Downloads week Feb 10-16
  - Cache: west-village_lunch_2026-02-10.json

Tuesday (Feb 11):
  - Run app → Cache hit! → No API call
  - Same cache file used

Wednesday (Feb 12):
  - Run app → Cache hit! → No API call
  - Still using same week's data

Next Monday (Feb 17):
  - Run app → New week → API call
  - Cache: west-village_lunch_2026-02-17.json
```

## Cache Location

```
DiningDiet/
  .cache/
    west-village_lunch_2026-02-10.json
    west-village_dinner_2026-02-10.json
    north-ave-dining-hall_lunch_2026-02-10.json
    north-ave-dining-hall_dinner_2026-02-10.json
```

## When You'll See API Calls

API calls only happen when:
1. **First time** fetching a specific dining hall + meal type + week
2. **New week** starts (Monday)
3. **Cache expires** (after 7 days)
4. **Cache cleared** manually

## Visual Indicators

The app now shows what's happening:

### Cache Hit (Data Reused)
```
🔍 Loading lunch menus...
  • West Village:
    ✓ Loaded from cache (week of 2026-02-10)
    → 404 items available
```

### Cache Miss (Fresh Fetch)
```
🔍 Loading lunch menus...
  • West Village:
    ↓ Fetching from API...
    → 404 items available
```

## Clear Cache

If you want to force fresh data:

### Option 1: Delete Cache Folder
```bash
rm -rf .cache
# or on Windows:
rmdir /s .cache
```

### Option 2: Python Script (TODO)
```python
from dining_optimizer import DiningHallOptimizer

optimizer = DiningHallOptimizer()
optimizer.clear_cache()
```

## Benefits

✅ **Speed**: Cache hits are ~10x faster than API calls
✅ **Reliability**: Works offline if cache exists
✅ **API-Friendly**: Reduces load on Nutrislice servers
✅ **Weekly Updates**: Menus refresh automatically each week

## Troubleshooting

### "Old menu showing up"
- Wait until Monday for new week's menu
- Or clear cache to force refresh

### "Items missing fiber data"
- Old cached items didn't have fiber field
- Clear cache to get fresh data with fiber
- Or wait for automatic refresh next Monday

### "Too much disk space"
- Each cache file is ~200KB
- 4 files (2 halls × 2 meals) = ~800KB per week
- Auto-deletes after 7 days

## Technical Details

### Cache Key Generation
```python
monday = date - timedelta(days=date.weekday())
cache_key = f"{dining_hall}_{meal_type}_{monday:%Y-%m-%d}.json"
```

### Cache Structure
```json
{
  "timestamp": "2026-02-11T10:30:00",
  "menu_items": [
    {
      "name": "Grilled Chicken Breast",
      "calories": 152,
      "protein": 31,
      "fiber": 0,
      ...
    }
  ]
}
```

### Expiration Check
```python
cache_age = datetime.now() - cached_timestamp
is_valid = cache_age < timedelta(days=7)
```
