import streamlit as st
import pymongo
from datetime import datetime, timedelta
import random
from typing import List, Tuple, Optional

# MongoDB setup using Streamlit secrets
client = pymongo.MongoClient(st.secrets["mongo"]["uri"])
db = client[st.secrets["mongo"]["database"]]
selections_collection = db[st.secrets["mongo"]["collection"]]

# Team members list - you can modify this
TEAM_MEMBERS = [
    "Guy",
    "Daniel",
    "Elzareez",
    "Aharon",
    "Yinon",
    "Camilla",
    "Yarin",
    "Freddy",
]


def get_current_week_number() -> int:
    """Get the current ISO week number."""
    return datetime.now().isocalendar()[1]


def get_current_selection() -> Optional[Tuple[str, str]]:
    """Retrieve the current week's selection from MongoDB."""
    current_week = get_current_week_number()
    current_year = datetime.now().year

    selection = selections_collection.find_one(
        {"week": current_week, "year": current_year}
    )

    if selection:
        return selection["team_members"]
    return None


def save_selection(team_members: Tuple[str, str]) -> None:
    """Save the selection to MongoDB."""
    current_week = get_current_week_number()
    current_year = datetime.now().year

    selections_collection.update_one(
        {"week": current_week, "year": current_year},
        {"$set": {"team_members": team_members, "timestamp": datetime.now()}},
        upsert=True,
    )


def select_team_members() -> Tuple[str, str]:
    """Randomly select two team members."""
    selected = random.sample(TEAM_MEMBERS, 2)
    return tuple(selected)


# Streamlit UI
st.title("🎉 The-Guy Happy Hour Takeout Team Selector")

st.markdown(
    """
### Why does this exist? 🤔

Ever noticed how choosing who gets to handle the takeout order
feels like picking tribute for the Hunger Games?
*"May the odds of getting everyone's order right be ever in your favor!"*

This app randomly selects two brave souls each week to tackle:
- 🗒️ Collecting everyone's picky orders
- 💰 Managing the complicated money situation
- 🚗 Braving (elevator) traffic for pickup
- 📦 Distribution of food without mixing up orders

Don't worry, heroes - you only have to do this once every... *checks notes*...
few weeks!
"""
)

# Get current selection
current_selection = get_current_selection()

if current_selection:
    st.success(
        f"This week's Happy Hour team: **{current_selection[0]}** and **{current_selection[1]}**"
    )

    # Show when the next selection will be available
    current_date = datetime.now()
    next_selection = current_date + timedelta(days=7)
    st.info(
        f"Next selection will be available on {next_selection.strftime('%A, %B %d')}"
    )
else:
    st.write("No selection has been made for this week yet!")

    if st.button("Pick This Week's Team! 🎲"):
        new_selection = select_team_members()
        save_selection(new_selection)
        st.success(
            f"Selected team for this week: **{new_selection[0]}** and **{new_selection[1]}**"
        )
        st.balloons()

# Show history of selections
st.subheader("Previous Selections")
history = selections_collection.find().sort("timestamp", -1).limit(5)

history_data = []
for entry in history:
    # Format the timestamp nicely
    selection_date = entry["timestamp"].strftime("%B %d, %Y")
    history_data.append(
        {
            "Date": selection_date,
            "Team Members": f"{entry['team_members'][0]} and {entry['team_members'][1]}",
        }
    )

if history_data:
    st.table(history_data)
else:
    st.write("No previous selections found.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ for streamlined Happy Hour organization")
