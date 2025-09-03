# 📍 venue_matcher.py

"""
The London Lark — Venue Matcher

Matches venue profiles to interpreted prompt filters.
Draws from `venue_profiles.md` or a parsed JSON equivalent.
Matches on:
- Mood tag
- Location (if given)
- Group size compatibility
- Optional: vibe notes, capacity, genre fit
"""

import json

# Load parsed venue profiles (converted from venue_profiles.md)
with open("venue_profiles.json", "r") as f:
    venue_data = json.load(f)

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

    return matches

# Example usage
if __name__ == "__main__":
    test_filters = {
        "mood": "Grief & Grace",
        "location": "Camden",
        "group": "solo"
    }
    result = match_venues(test_filters)
    for r in result:
        print(f"- {r['name']} ({r['area']})")
