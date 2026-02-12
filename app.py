"""
Streamlit GUI for Dining Hall Meal Optimizer
"""

import streamlit as st
from dining_optimizer import DiningHallOptimizer
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Dining Hall Meal Optimizer",
    page_icon="🍽️",
    layout="wide"
)

# Title and description
st.title("🍽️ Dining Hall Meal Optimizer")
st.markdown("""
Find the perfect meal combinations to meet your protein goals while staying within your calorie limits!
""")

# Initialize optimizer (with caching)
@st.cache_resource
def get_optimizer():
    return DiningHallOptimizer()

optimizer = get_optimizer()

# Sidebar for inputs
st.sidebar.header("Meal Preferences")

# Dining hall selection
dining_hall_option = st.sidebar.selectbox(
    "Select Dining Hall",
    ["West Village", "North Ave Dining Hall", "Both"]
)

# Map selection to internal values
if dining_hall_option == "West Village":
    selected_halls = ["west-village"]
    dining_hall_filter = "West Village"
elif dining_hall_option == "North Ave Dining Hall":
    selected_halls = ["north-ave-dining-hall"]
    dining_hall_filter = "North Ave Dining Hall"
else:
    selected_halls = ["west-village", "north-ave-dining-hall"]
    dining_hall_filter = None

# Meal type selection
meal_type = st.sidebar.selectbox(
    "Meal Type",
    ["lunch", "dinner"]
).lower()

# Protein and calorie inputs
protein_goal = st.sidebar.number_input(
    "Protein Goal (grams)",
    min_value=10,
    max_value=150,
    value=40,
    step=5
)

calorie_limit = st.sidebar.number_input(
    "Calorie Limit",
    min_value=200,
    max_value=2000,
    value=600,
    step=50
)

# Find meals button
find_button = st.sidebar.button("🔍 Find Meals", type="primary", use_container_width=True)

# Main content area
if find_button:
    with st.spinner("Fetching menus and finding optimal combinations..."):
        # Fetch menu data
        all_items = []
        for hall_id in selected_halls:
            items = optimizer.fetch_menu(hall_id, meal_type)
            all_items.extend(items)

        if not all_items:
            st.error("❌ Could not fetch menu data. Please try again later.")
        else:
            # Find combinations
            combinations = optimizer.find_combinations(
                all_items,
                protein_goal,
                calorie_limit,
                dining_hall_filter
            )

            if not combinations:
                st.warning("❌ No combinations found that meet your criteria. Try adjusting your protein goal or calorie limit.")
            else:
                st.success(f"✅ Found {len(combinations)} meal combination(s)!")

                # Display results
                for idx, (items, total_protein, total_calories) in enumerate(combinations, 1):
                    # Calculate protein efficiency
                    protein_efficiency = total_protein / max(total_calories, 1)

                    # Calculate macros
                    total_fat = sum(item['fat'] for item in items)
                    total_carbs = sum(item['carbs'] for item in items)
                    total_cals_from_macros = (total_protein * 4) + (total_carbs * 4) + (total_fat * 9)

                    # Create expander for each option
                    with st.expander(
                        f"**Option {idx}**: {total_protein:.1f}g protein, {total_calories:.0f} cal - Efficiency: {protein_efficiency:.3f}g/cal",
                        expanded=(idx <= 3)  # First 3 expanded by default
                    ):
                        # Items table
                        st.markdown("#### Meal Items")
                        for item in items:
                            category_emoji = {
                                'protein': '🍗',
                                'carb': '🍚',
                                'vegetable': '🥦',
                                'fruit': '🍎',
                                'other': '🍴'
                            }
                            emoji = category_emoji.get(item.get('category', 'other'), '🍴')

                            col1, col2, col3 = st.columns([2, 1, 2])
                            with col1:
                                st.markdown(f"**{emoji} {item['name']}**")
                                st.caption(f"_{item.get('category', 'other').title()}_")
                            with col2:
                                st.caption(f"📍 {item['dining_hall']}")
                                st.caption(f"📏 {item['serving']}")
                            with col3:
                                st.caption(f"Protein: {item['protein']:.1f}g")
                                st.caption(f"Calories: {item['calories']:.0f}")
                                st.caption(f"Fat: {item['fat']:.1f}g | Carbs: {item['carbs']:.1f}g")

                        # Nutritional summary
                        st.markdown("---")
                        st.markdown("#### 📊 Nutritional Summary")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric("Protein Efficiency", f"{protein_efficiency:.3f}g/cal")
                            st.metric("Total Protein", f"{total_protein:.1f}g")
                            st.metric("Total Calories", f"{total_calories:.0f}")

                        with col2:
                            if total_cals_from_macros > 0:
                                protein_pct = (total_protein * 4) / total_cals_from_macros
                                carb_pct = (total_carbs * 4) / total_cals_from_macros
                                fat_pct = (total_fat * 9) / total_cals_from_macros

                                st.markdown(f"""
                                **Macros:**
                                - Protein: {protein_pct*100:.0f}%
                                - Carbs: {carb_pct*100:.0f}%
                                - Fat: {fat_pct*100:.0f}%
                                """)

else:
    # Welcome screen
    st.info("👈 Use the sidebar to set your preferences and click 'Find Meals' to get started!")

    # Show some stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Dining Halls", "2")
    with col2:
        st.metric("Meal Types", "2")
    with col3:
        st.metric("Search Time", "~5s")

    st.markdown("---")
    st.markdown("""
    ### How It Works

    1. **Select your dining hall** - Choose West Village, North Ave, or search both
    2. **Choose meal type** - Lunch or Dinner
    3. **Set your goals** - Protein target and calorie limit
    4. **Get results** - View meal combinations sorted by protein efficiency

    ### Optimization Strategy

    Finds the **BEST** items by protein efficiency:
    - 🔥 **Best protein/calorie ratio** - Lean, high-protein foods
    - 🥦 **Quality vegetables** - Low-calorie, nutrient-dense
    - ⚡ **Strategic carbs** - Energy sources with protein

    Results are sorted by **protein efficiency** (grams of protein per calorie).

    ### Features

    - 🚀 **Fast caching** - Menu data cached for the week
    - 🎯 **Efficiency-optimized** - Only the best items are used
    - 📊 **Complete nutrition** - Full macros for every item
    - 📈 **Smart ranking** - Best protein/calorie ratios ranked first
    """)

# Footer
st.markdown("---")
st.caption("Data sourced from Nutrislice • Built for Georgia Tech students")
