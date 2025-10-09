# 📍 venue_matcher.py

"""
The London Lark — Venue Matcher

Matches venue profiles to interpreted prompt filters.
Draws from `lark_venues_clean.json`, a curated dataset of venues.
Matches on:
- Mood tag
- Location (if given)
- Group size compatibility
"""

import json
from pathlib import Path

# Load parsed venue profiles from the cleaned JSON dataset
DATA_PATH = Path(__file__).with_name("lark_venues_clean.json")
with DATA_PATH.open("r", encoding="utf-8") as f:
    venue_data = json.load(f)

def _poetic_line(venue, mood):
    """Shape a lyrical sentence for the recommended venue."""
    mood_hint = f"for {mood.lower()} hearts" if mood else "for wandering hearts"
    start = venue.get("typical_start_time")
    timing_phrase = f"— doors around {start}" if start else ""
    return (
        f"• {venue['name']} in {venue['area']}: {venue['vibe_note']} "
        f"{mood_hint}{timing_phrase}."
    )

def match_venues(filters):
    """
    Given a dict of filters (mood, location, group, etc), return matching venues.
    """
    mood = filters.get("mood")
    location = filters.get("location")  # Optional
    group = filters.get("group")

    matches = []
    for venue in venue_data:
        # Mood match (required)
        if mood and mood not in venue.get("mood_tags", []):
            continue

        # Location match (if filter provided)
        if location:
            if location.lower() not in venue.get("area", "").lower():
                continue

        # Group compatibility (optional logic — could expand later)
        if group == "solo" and "rowdy" in venue.get("vibe_notes", ""):
            continue  # skip overly loud venues for solo seekers

        matches.append(venue)

    # Return up to three matches with poetic phrasing
    poetic_matches = []
    for venue in matches[:3]:
        poetic_matches.append(_poetic_line(venue, mood))

    return poetic_matches

# Example usage
if __name__ == "__main__":
    test_filters = {
        "mood": "Tender & Strange",
        # "location": "Hackney",  # Optional
        # "group": "solo"         # Optional
    }
    result = match_venues(test_filters)
    print("🕊️ The Lark offers these resonances:\n")
    for line in result:
        print(line)
