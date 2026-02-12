"""
Streamlit GUI for Dining Hall Meal Optimizer
"""

import streamlit as st
from dining_optimizer import DiningHallOptimizer
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Dining Hall Protein Finder",
    page_icon="🍽️",
    layout="wide"
)

# Title and description
st.title("🍽️ Dining Hall Protein Finder")
st.markdown("""
Find the best high-protein items at Georgia Tech dining halls ranked by protein efficiency!
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
elif dining_hall_option == "North Ave Dining Hall":
    selected_halls = ["north-ave-dining-hall"]
else:
    selected_halls = ["west-village", "north-ave-dining-hall"]

# Meal type selection
meal_type = st.sidebar.selectbox(
    "Meal Type",
    ["lunch", "dinner"]
).lower()

# Find meals button
find_button = st.sidebar.button("🔍 Show Top Items", type="primary", use_container_width=True)

# Main content area
if find_button:
    with st.spinner("Fetching menus..."):
        # Fetch menu data
        all_items = []
        for hall_id in selected_halls:
            items = optimizer.fetch_menu(hall_id, meal_type, verbose=False)
            all_items.extend(items)

        if not all_items:
            st.error("❌ Could not fetch menu data. Please try again later.")
        else:
            # Filter items with meaningful protein (min 12g) and valid calories
            valid_items = [item for item in all_items
                          if item['calories'] > 0 and item['protein'] >= 12]

            # Remove duplicates by name + dining hall
            seen = set()
            unique_items = []
            for item in valid_items:
                key = (item['name'], item['dining_hall'])
                if key not in seen:
                    seen.add(key)
                    unique_items.append(item)

            # Create list with efficiency scores
            items_with_efficiency = []
            for item in unique_items:
                protein_efficiency = item['protein'] / item['calories']
                items_with_efficiency.append({
                    **item,
                    'protein_efficiency': protein_efficiency
                })

            # Sort by efficiency (highest first)
            items_with_efficiency.sort(key=lambda x: -x['protein_efficiency'])

            # Display top 10
            st.success(f"✅ Top 10 items by protein efficiency!")

            for idx, item in enumerate(items_with_efficiency[:10], 1):
                with st.expander(
                    f"**#{idx}**: {item['name']} - {item['protein_efficiency']:.3f}g/cal",
                    expanded=(idx <= 5)
                ):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"### {item['name']}")
                        st.caption(f"📍 {item['dining_hall']}")
                        st.caption(f"📏 Serving: {item['serving']}")

                    with col2:
                        st.metric("Efficiency", f"{item['protein_efficiency']:.3f}g/cal")

                    st.markdown("---")
                    st.markdown("#### Nutrition Facts")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Protein", f"{item['protein']:.1f}g")
                    with col2:
                        st.metric("Calories", f"{item['calories']:.0f}")
                    with col3:
                        st.metric("Fat", f"{item['fat']:.1f}g")
                    with col4:
                        st.metric("Carbs", f"{item['carbs']:.1f}g")

else:
    # Welcome screen
    st.info("👈 Select your dining hall and meal type, then click 'Show Top Items' to see the best protein sources!")

    # Show some stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Dining Halls", "2")
    with col2:
        st.metric("Meal Types", "2")
    with col3:
        st.metric("Load Time", "~2s")

    st.markdown("---")
    st.markdown("""
    ### How It Works

    1. **Select your dining hall** - Choose West Village, North Ave, or search both
    2. **Choose meal type** - Lunch or Dinner
    3. **Click "Show Top Items"** - See the top 10 items by protein efficiency

    ### What is Protein Efficiency?

    **Protein efficiency = grams of protein ÷ calories**

    Higher efficiency means you get more protein for fewer calories. Perfect for:
    - 💪 Building muscle
    - 🔥 Cutting weight
    - 🎯 Hitting protein goals

    ### Features

    - 🚀 **Fast caching** - Menu data cached for the week
    - 📊 **Complete nutrition** - Full macros for every item
    - 📈 **Smart ranking** - Best protein/calorie ratios first
    - 🔄 **Always current** - Fresh menu data
    """)

# Footer
st.markdown("---")
st.caption("Data sourced from Nutrislice • AnirudhJM24")
