# 🔍 venue_matcher.py

"""
The London Lark — Venue Matcher

Matches venue profiles to interpreted prompt filters.
Draws from `lark_venues_clean.json`, a curated dataset of venues.
Matches on:
- Mood tag (using full synonym list from mood_index.json)
- Location (if given)
- Group size compatibility
"""

import json
from pathlib import Path
from parse_venues import load_parsed_venues

# Load parsed venue profiles
venue_data = load_parsed_venues()

# Load mood index for synonym expansion
PROJECT_ROOT = Path(__file__).parent
MOOD_INDEX_PATH = PROJECT_ROOT / "mood_index.json"

mood_index = {}
mood_synonyms = {}  # Maps mood name -> list of all synonyms

if MOOD_INDEX_PATH.exists():
    with open(MOOD_INDEX_PATH, "r", encoding="utf-8") as f:
        mood_index = json.load(f)
    
    # Build synonym lookup: mood_name -> [all synonyms]
    for mood_name, values in mood_index.items():
        synonyms = [s.lower() for s in values.get("synonyms", [])]
        mood_synonyms[mood_name.lower()] = synonyms
        # Also map the mood name itself
        mood_synonyms[mood_name.lower()].append(mood_name.lower())


def get_synonyms_for_mood(mood_name):
    """
    Get all synonyms for a mood from mood_index.json.
    Returns the full list of words that should match this mood.
    """
    if not mood_name:
        return []
    
    mood_lower = mood_name.lower()
    
    # Direct lookup
    if mood_lower in mood_synonyms:
        return mood_synonyms[mood_lower]
    
    # Try to find a partial match (e.g., "cabaret & glitter" -> "Cabaret & Glitter")
    for key in mood_synonyms:
        if mood_lower in key or key in mood_lower:
            return mood_synonyms[key]
    
    # Fallback: split the mood name into words
    return [w.strip().lower() for w in mood_name.replace('&', ' ').replace('/', ' ').split() if len(w.strip()) > 2]


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
    Given a dict of filters (mood, location, group, budget, genre), return matching venue dictionaries.
    Returns up to 3 venues that match the filters.
    """
    mood = filters.get("mood")
    location = filters.get("location")
    group = filters.get("group")
    budget = filters.get("budget")
    genre = filters.get("genre")

    matches = []
    filtered_out_reasons = []  # Track why venues were filtered out

    # Get the full synonym list for the requested mood
    mood_search_terms = get_synonyms_for_mood(mood) if mood else []
    
    # Debug logging
    if mood:
        print(f"   🔍 Mood '{mood}' expanded to {len(mood_search_terms)} search terms: {mood_search_terms[:10]}...")

    for venue in venue_data:
        # Get mood tags (already a list from parsed data)
        mood_tags = venue.get("moods", []) or venue.get("mood_tags", [])

        # Mood match (required if mood is specified)
        if mood:
            # Lowercase all venue mood tags
            venue_moods_lower = [m.lower() for m in mood_tags]
            
            # Check if ANY synonym matches ANY venue mood tag
            mood_match = any(
                any(
                    # Exact match
                    search_term == venue_mood or
                    # Substring match (for compound words)
                    search_term in venue_mood or venue_mood in search_term or
                    # Stem match (first 8 characters for words like melancholic/melancholy)
                    (len(search_term) >= 8 and len(venue_mood) >= 8 and search_term[:8] == venue_mood[:8])
                    for venue_mood in venue_moods_lower
                )
                for search_term in mood_search_terms
            )
            
            if not mood_match:
                continue

        # Location match (optional)
        # Check both the specific area and the tags field (which has broader regions like "North London")
        area = venue.get("area", "") or venue.get("location", "")
        tags = venue.get("tags", [])  # Now an array
        tags_str = " ".join(tags) if isinstance(tags, list) else str(tags)  # Convert to string for searching
        if location:
            location_lower = location.lower()
            if location_lower not in area.lower() and location_lower not in tags_str.lower():
                filtered_out_reasons.append(f"{venue.get('name', 'Venue')} filtered by location")
                continue

        # Genre match (optional) - check venue type and tags
        if genre:
            venue_type = venue.get("type", "").lower()
            tags_lower = tags_str.lower()

            if genre == "theatre" and not any(word in venue_type or word in tags_lower for word in ["theatre", "theater", "stage", "fringe"]):
                filtered_out_reasons.append(f"{venue.get('name', 'Venue')} filtered by genre (not theatre)")
                continue
            elif genre == "music" and not any(word in venue_type or word in tags_lower for word in ["music", "gig", "concert", "jazz", "folk"]):
                filtered_out_reasons.append(f"{venue.get('name', 'Venue')} filtered by genre (not music)")
                continue
            elif genre == "drag" and not any(word in venue_type or word in tags_lower for word in ["drag", "cabaret", "queer", "LGBTQ"]):
                filtered_out_reasons.append(f"{venue.get('name', 'Venue')} filtered by genre (not drag)")
                continue

        # Budget match (optional) - based on typical venue characteristics
        if budget:
            # Venues with "pub", "free", "community" tend to be cheaper
            # Venues with "theatre", "concert hall", "club" might be pricier
            venue_type_lower = venue.get("type", "").lower()
            if budget == "low":
                # Filter out expensive-sounding venues
                if any(word in venue_type_lower for word in ["concert hall", "opera", "philharmonic"]):
                    filtered_out_reasons.append(f"{venue.get('name', 'Venue')} might be too expensive")
                    continue
            elif budget == "high":
                # User wants to splurge - no filtering needed, keep all venues
                pass

        # Group compatibility - improved logic
        vibe_notes = venue.get("tone_notes", "")
        venue_type_lower = venue.get("type", "").lower()

        if group == "solo":
            # Filter out venues that are explicitly too rowdy/crowded for solo visits
            if any(word in vibe_notes.lower() for word in ["rowdy", "raucous", "heaving", "packed", "sweaty crowd"]):
                filtered_out_reasons.append(f"{venue.get('name', 'Venue')} might be too crowded for solo visit")
                continue
            # Nightclubs are generally not great solo
            if "nightclub" in venue_type_lower or "club night" in venue_type_lower:
                filtered_out_reasons.append(f"{venue.get('name', 'Venue')} not ideal for solo visit")
                continue
        elif group == "group":
            # Filter out venues that are too intimate for groups
            if any(word in vibe_notes.lower() for word in ["tiny", "intimate", "20-seat", "small space"]):
                filtered_out_reasons.append(f"{venue.get('name', 'Venue')} might be too small for group")
                continue

        # Normalize venue data to expected format
        normalized_venue = {
            "name": venue.get("name", "Unnamed venue"),
            "area": venue.get("area", venue.get("location", "London")),
            "vibe_note": venue.get("tone_notes", venue.get("blurb", "An experience beyond words")),
            "typical_start_time": venue.get("typical_start_time", ""),
            "price": venue.get("price", "TBC"),
            "website": venue.get("website", venue.get("url", "")),  # Added website field
            "mood_tags": mood_tags,
            "raw_data": venue  # Keep original data for reference
        }
        matches.append(normalized_venue)

    # Shuffle matches to add variety
    import random
    random.shuffle(matches)

    # Deduplicate matches by venue name (prevents same venue appearing multiple times)
    seen_names = set()
    deduplicated_matches = []
    for venue in matches:
        venue_name = venue.get("name", "").lower().strip()
        if venue_name not in seen_names:
            seen_names.add(venue_name)
            deduplicated_matches.append(venue)

    # Debug: log match count
    if mood:
        print(f"   ✓ Found {len(deduplicated_matches)} venues matching '{mood}'")

    # Return top 3 unique matches
    return deduplicated_matches[:3]

if __name__ == "__main__":
    test_filters = {
        "mood": "Cabaret & Glitter",
        "location": None,
        "group": None
    }

    result = match_venues(test_filters)
    print("🕊️ The Lark offers these resonances:\n")
    if result:
        for venue in result:
            print(f"• {venue['name']} in {venue['area']}")
            print(f"  {venue['vibe_note'][:100]}...")
            print()
    else:
        print("No venues sang in harmony with your mood — try another mood or area?")
