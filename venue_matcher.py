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
from parse_venues import load_parsed_venues

# Load parsed venue profiles
venue_data = load_parsed_venues()

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
    Given a dict of filters (mood, location, group), return matching venue dictionaries.
    Returns up to 3 venues that match the filters.
    """
    mood = filters.get("mood")
    location = filters.get("location")
    group = filters.get("group")

    matches = []

    for venue in venue_data:
        # Get mood tags (already a list from parsed data)
        mood_tags = venue.get("mood_tags", [])

        # Mood match (required if mood is specified)
        if mood and mood not in mood_tags:
            continue

        # Location match (optional)
        # Check both the specific area and the tags field (which has broader regions like "North London")
        area = venue.get("area", "") or venue.get("location", "")
        tags = venue.get("tags", "")
        if location:
            location_lower = location.lower()
            if location_lower not in area.lower() and location_lower not in tags.lower():
                continue

        # Group compatibility (basic solo logic — can refine later)
        vibe_notes = venue.get("tone_notes", "")
        if group == "solo" and any(word in vibe_notes.lower() for word in ["rowdy", "raucous", "heaving"]):
            continue

        # Normalize venue data to expected format
        normalized_venue = {
            "name": venue.get("name", "Unnamed venue"),
            "area": venue.get("area", venue.get("location", "London")),
            "vibe_note": venue.get("tone_notes", "An experience beyond words"),
            "typical_start_time": venue.get("typical_start_time", ""),
            "price": venue.get("price", "TBC"),
            "mood_tags": mood_tags,
            "raw_data": venue  # Keep original data for reference
        }
        matches.append(normalized_venue)

    # Return top 3 matches
    return matches[:3]

if __name__ == "__main__":
    test_filters = {
        "mood": None,
        "location": None,
        "group": None
    }

    result = match_venues(test_filters)
    print("🕊️ The Lark offers these resonances:\n")
    if result:
        for venue in result:
            print(f"• {venue['name']} in {venue['area']}")
            print(f"  {venue['vibe_note']}")
            if venue['typical_start_time']:
                print(f"  Doors around {venue['typical_start_time']}")
            print()
    else:
        print("No venues sang in harmony with your mood — try another mood or area?")
