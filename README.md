# Dining Hall Meal Optimizer 🍽️

An intelligent app to help you meet your protein goals while staying within your calorie limits using Georgia Tech's campus dining halls.

## Dining Halls Supported
- West Village
- North Ave Dining Hall

## Features

✨ **Smart Meal Combinations** - Uses efficiency-optimized combinations (Protein + Vegetables + Carbs)
🎯 **Protein Efficiency Ranking** - Meals sorted by protein-to-calorie ratio
⚡ **Fast Caching** - Stores menu data for the week to speed up searches
🖥️ **Two Interfaces** - Command-line or beautiful Streamlit web app
📊 **Detailed Nutrition** - See complete macros and serving sizes for every item

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Streamlit Web App (Recommended)

Launch the interactive web interface:
```bash
streamlit run app.py
```

Then open your browser to the URL shown (usually `http://localhost:8501`)

**Features:**
- Beautiful, interactive UI
- Visual meal cards with emojis
- Expandable results with detailed breakdowns
- Easy-to-use dropdowns and sliders

### Option 2: Command-Line Interface

Run the CLI optimizer:
```bash
python dining_optimizer.py
```

You'll be prompted to:
1. Choose dining hall (West Village, North Ave, or Both)
2. Choose meal type (lunch or dinner)
3. Enter your protein goal (in grams)
4. Enter your calorie limit

## How It Works

### Smart Search Algorithm

The app uses **efficiency-based optimization** to find the best combinations:

1. Selects top items by protein/calorie ratio (highest efficiency)
2. Includes quality vegetables for nutrition
3. Adds strategic carbs for energy
4. Creates multiple combination strategies:
   - Best Protein + Vegetable (lean & clean)
   - Best Protein + Vegetable + Carb (balanced)
   - Best Protein + Carb (simple & effective)
   - Double Protein + Vegetable (high protein focus)
   - Single item (exceptionally efficient)

### Ranking System

Meals are sorted by **protein efficiency** (grams of protein per calorie):
- Higher efficiency = more protein for fewer calories
- Results show efficiency ratio for easy comparison
- Best combinations appear first

### Caching

Menu data is automatically cached for up to 7 days to:
- Speed up searches (5s instead of 15s)
- Reduce API load
- Work offline with recent data

Cached data is stored in `.cache/` directory.

## Example Output

```
Option 1: 45.0g protein, 466 cal
Protein efficiency: 0.097g/cal
──────────────────────────────────────
  🍗 Cajun Chicken Breast (Protein)
     [West Village] 1 breast
     31.0g protein, 152 cal, 3.3g fat, 0.0g carbs

  🍚 Cheese Breadstick (Carb)
     [West Village] 2 stick
     10.0g protein, 272 cal, 8.0g fat, 38.0g carbs

  🥦 Chickpeas, Zucchini, Tomatoes (Vegetable)
     [West Village] 0.5 cups
     4.0g protein, 42 cal, 0.5g fat, 7.0g carbs

📊 Macros: 35% protein, 40% carbs, 25% fat
```

## Architecture

```
dining_optimizer.py  # Core optimizer logic
app.py              # Streamlit GUI
requirements.txt    # Python dependencies
.cache/            # Cached menu data (auto-created)
```

## Data Source

Menu data is fetched from [Nutrislice](https://nutrislice.com/), Georgia Tech's dining services platform.

**Sources:**
- [REST - Nutrislice JSON Values - Home Assistant Community](https://community.home-assistant.io/t/rest-nutrislice-json-values/609250)
- [MMM-Nutrislice GitHub](https://github.com/vees/MMM-Nutrislice)
- [Nutrislice Project GitHub](https://github.com/sp1603/nutrislice-project)

## Tips for Best Results

- **High protein goals** (40g+): Look for chicken, fish, or tofu-based meals
- **Low calorie limits** (400-600): Choose lean proteins with vegetables
- **Balanced nutrition**: Select "Both" dining halls for more variety
- **Bulk mode**: Increase calorie limit to maximize protein intake
- **Cut mode**: Decrease calories while maintaining protein goal
