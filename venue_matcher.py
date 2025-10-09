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
    Given a dict of filters (mood, location, group), return matching venues with poetic phrasing.
    """
    mood = filters.get("mood")
    location = filters.get("location")
    group = filters.get("group")

    matches = []

    for venue in venue_data:
        # Get and parse mood tags from the new dataset format
        mood_tags_raw = venue.get("Mapped Mood Tags", "")
        mood_tags = [tag.strip() for tag in mood_tags_raw.split(",")]

        # Mood match (required)
        if mood and mood not in mood_tags:
            continue

        # Location match (optional)
        area = venue.get("Area", "") or venue.get("name", "")
        if location and location.lower() not in area.lower():
            continue

        # Group compatibility (basic solo logic — can refine later)
        vibe_notes = venue.get("Tone Notes", "")
        if group == "solo" and any(word in vibe_notes.lower() for word in ["rowdy", "raucous", "heaving"]):
            continue

        matches.append(venue)

    # Generate poetic lines
    poetic_lines = []
    for venue in matches[:3]:
        name = venue.get("name", "Unnamed venue")
        area = venue.get("Area", "London")
        note = venue.get("Tone Notes", "An experience beyond words")
        time = venue.get("Typical Start Time", "")
        mood_hint = f"for {mood.lower()} hearts" if mood else "for curious souls"
        timing = f"— doors around {time}" if time else ""

        line = f"• {name} in {area}: {note} {mood_hint}{timing}."
        poetic_lines.append(line)

    return poetic_lines

if __name__ == "__main__":
    test_filters = {
        "mood": None,
        "location": None,
        "group": None
    }


    result = match_venues(test_filters)
    print("🕊️ The Lark offers these resonances:\n")
    if result:
        for line in result:
            print(line)
    else:
        print("No venues sang in harmony with your mood — try another mood or area?")
