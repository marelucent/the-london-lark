# 🔍 venue_matcher.py

"""
The London Lark – Venue Matcher

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

# =============================================================================
# SYNONYM DICTIONARIES
# These expand user search terms to match our venue tags more flexibly
# =============================================================================

# Mood synonyms - map user terms to our official mood tags
MOOD_SYNONYMS = {
    # Comedy cluster
    "comic": ["comic", "playful", "fun", "irreverent", "hilarious"],
    "comedy": ["comic", "playful", "fun", "irreverent", "hilarious"],
    "relief": ["comic", "playful", "fun"],
    "funny": ["comic", "playful", "fun", "irreverent"],

    # Melancholic cluster
    "melancholy": ["melancholy", "melancholic"],
    "melancholic": ["melancholy", "melancholic"],
    "sad": ["melancholy", "tender"],
    "blue": ["melancholy", "nostalgic"],

    # Queer cluster
    "gay": ["queer"],
    "lgbt": ["queer"],
    "lgbtq": ["queer"],
    "lgbtq+": ["queer"],

    # Spooky cluster
    "spooky": ["haunted", "witchy"],
    "creepy": ["haunted"],
    "gothic": ["haunted", "sacred"],

    # Playful cluster
    "fun": ["playful", "curious", "fun", "comic"],
    "weird": ["playful", "experimental"],
    "strange": ["curious", "witchy"],
    "playful": ["playful", "fun", "curious", "irreverent"],

    # Intimate cluster
    "cozy": ["intimate", "tender"],
    "small": ["intimate"],
    "quiet": ["intimate", "thoughtful"],

    # Energy cluster
    "party": ["ecstatic", "rebellious"],
    "dancing": ["ecstatic", "wild"],
    "rave": ["ecstatic", "rebellious"],
    "clubbing": ["big night out", "ecstatic"],

    # Calm cluster
    "peaceful": ["tender", "thoughtful"],
    "chill": ["tender", "folk"],
    "relaxed": ["tender", "intimate"],

    # Cabaret & glitter cluster
    "cabaret": ["cabaret", "queer", "drag", "burlesque", "glitter"],
    "drag": ["cabaret", "queer", "drag", "burlesque", "glitter"],
    "glitter": ["cabaret", "queer", "drag", "burlesque", "glitter"],
    "burlesque": ["cabaret", "queer", "drag", "burlesque", "glitter"],

    # Cultural cluster
    "ethnic": ["global"],
    "international": ["global"],
    "world music": ["global"],
}

# Location synonyms - map broad terms to specific neighborhoods
LOCATION_SYNONYMS = {
    "south london": ["peckham", "brixton", "camberwell", "dulwich", "clapham", "streatham", "lewisham", "deptford", "nunhead"],
    "south": ["peckham", "brixton", "camberwell", "dulwich", "clapham", "streatham", "lewisham", "deptford", "nunhead"],

    "north london": ["camden", "islington", "highgate", "finsbury park", "tottenham", "wood green", "barnet"],
    "north": ["camden", "islington", "highgate", "finsbury park", "tottenham", "wood green", "barnet"],

    "east london": ["hackney", "shoreditch", "dalston", "bethnal green", "whitechapel", "stratford", "walthamstow"],
    "east": ["hackney", "shoreditch", "dalston", "bethnal green", "whitechapel", "stratford", "walthamstow"],

    "west london": ["hammersmith", "shepherd's bush", "chiswick", "ealing", "brentford", "acton"],
    "west": ["hammersmith", "shepherd's bush", "chiswick", "ealing", "brentford", "acton"],

    "central london": ["soho", "covent garden", "holborn", "king's cross", "fitzrovia"],
    "central": ["soho", "covent garden", "holborn", "king's cross", "fitzrovia"],

    # Specific neighborhood aliases
    "shoreditch": ["shoreditch", "hoxton"],
    "kings cross": ["king's cross"],
    "shepherds bush": ["shepherd's bush"],
}

# =============================================================================
# EXPANSION FUNCTIONS
# =============================================================================

def expand_mood(mood_term):
    """
    Expand a mood term to include synonyms.

    Args:
        mood_term: User's mood search term (lowercase)

    Returns:
        List of mood tags to search for
    """
    if not mood_term:
        return []

    mood_lower = mood_term.lower().strip()

    # Check if it's in our synonym dictionary
    if mood_lower in MOOD_SYNONYMS:
        return MOOD_SYNONYMS[mood_lower]

    # Otherwise just return the original term
    return [mood_lower]


def expand_location(location_term):
    """
    Expand a location term to include neighborhoods.

    Args:
        location_term: User's location search term (lowercase)

    Returns:
        List of location names to search for
    """
    if not location_term:
        return []

    location_lower = location_term.lower().strip()

    # Check if it's in our synonym dictionary
    if location_lower in LOCATION_SYNONYMS:
        return LOCATION_SYNONYMS[location_lower]

    # Otherwise just return the original term
    return [location_lower]


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

    for venue in venue_data:
        # Get mood tags (already a list from parsed data)
        mood_tags = venue.get("moods", []) or venue.get("mood_tags", [])

        # Mood match (required if mood is specified)
        # Normalize and match moods flexibly using synonym expansion
        if mood:
            # Split mood filter into words and lowercase (handles "Folk & Intimate" -> ["folk", "intimate"])
            mood_words = [w.strip().lower() for w in mood.replace('&', ' ').replace('/', ' ').split() if len(w.strip()) > 2]

            # Expand each mood word to include synonyms
            mood_variants = []
            for word in mood_words:
                mood_variants.extend(expand_mood(word))

            # If no words were expanded (short words filtered out), try the whole phrase
            if not mood_variants:
                mood_variants = expand_mood(mood.lower().strip())

            # Lowercase all venue mood tags
            venue_moods_lower = [m.lower() for m in mood_tags]

            # Check if ANY mood variant matches ANY venue mood tag
            # Uses exact match, substring match, OR stem match (first 8 chars)
            mood_match = any(
                any(
                    # Exact match
                    variant == venue_mood or
                    # Substring match
                    variant in venue_mood or venue_mood in variant or
                    # Stem match (first 8 characters for words like melancholic/melancholy)
                    (len(variant) >= 8 and len(venue_mood) >= 8 and variant[:8] == venue_mood[:8])
                    for venue_mood in venue_moods_lower
                )
                for variant in mood_variants
            )

            if not mood_match:
                continue

        # Location match (optional)
        # Check both the specific area and the tags field (which has broader regions like "North London")
        # Uses location expansion for broader area searches (e.g., "south london" -> all south neighborhoods)
        area = venue.get("area", "") or venue.get("location", "")
        tags = venue.get("tags", [])  # Now an array
        genres = venue.get("genres", [])
        combined_tags = []
        if isinstance(tags, list):
            combined_tags.extend(tags)
        else:
            combined_tags.append(str(tags))

        if isinstance(genres, list):
            combined_tags.extend(genres)
        elif genres:
            combined_tags.append(str(genres))

        tags_str = " ".join(combined_tags)  # Convert to string for searching
        if location:
            # Expand location to include neighborhoods
            location_variants = expand_location(location)

            # Check if ANY variant matches venue area or tags
            location_match = any(
                variant in area.lower() or variant in tags_str.lower()
                for variant in location_variants
            )

            if not location_match:
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

    # Deduplicate matches by venue name (prevents same venue appearing multiple times)
    seen_names = set()
    deduplicated_matches = []
    for venue in matches:
        venue_name = venue.get("name", "").lower().strip()
        if venue_name not in seen_names:
            seen_names.add(venue_name)
            deduplicated_matches.append(venue)

    # Return top 3 unique matches
    return deduplicated_matches

if __name__ == "__main__":
    print("=" * 60)
    print("VENUE MATCHER TESTS - Synonym & Location Expansion")
    print("=" * 60)

    # Test mood expansion
    print("\n1. Testing mood expansion:")
    print(f"   'gay' expands to: {expand_mood('gay')}")
    print(f"   'spooky' expands to: {expand_mood('spooky')}")
    print(f"   'melancholy' expands to: {expand_mood('melancholy')}")
    print(f"   'cozy' expands to: {expand_mood('cozy')}")
    print(f"   'party' expands to: {expand_mood('party')}")
    print(f"   'folk' (no synonym) expands to: {expand_mood('folk')}")

    # Test location expansion
    print("\n2. Testing location expansion:")
    print(f"   'south london' expands to: {expand_location('south london')}")
    print(f"   'east' expands to: {expand_location('east')}")
    print(f"   'central' expands to: {expand_location('central')}")
    print(f"   'peckham' (no synonym) expands to: {expand_location('peckham')}")

    # Test actual venue matching with synonyms
    print("\n3. Testing venue matching with mood synonyms:")

    # Test queer synonym
    test_queer = {"mood": "gay"}
    queer_results = match_venues(test_queer)
    print(f"   Query 'gay' found {len(queer_results)} venues:")
    for v in queer_results:
        print(f"      - {v['name']} (moods: {v['mood_tags']})")

    # Test spooky synonym
    test_spooky = {"mood": "spooky"}
    spooky_results = match_venues(test_spooky)
    print(f"\n   Query 'spooky' found {len(spooky_results)} venues:")
    for v in spooky_results:
        print(f"      - {v['name']} (moods: {v['mood_tags']})")

    # Test cozy synonym
    test_cozy = {"mood": "cozy"}
    cozy_results = match_venues(test_cozy)
    print(f"\n   Query 'cozy' found {len(cozy_results)} venues:")
    for v in cozy_results:
        print(f"      - {v['name']} (moods: {v['mood_tags']})")

    print("\n4. Testing venue matching with location expansion:")

    # Test south london
    test_south = {"location": "south london"}
    south_results = match_venues(test_south)
    print(f"   Query 'south london' found {len(south_results)} venues:")
    for v in south_results:
        print(f"      - {v['name']} in {v['area']}")

    # Test combined mood + location
    print("\n5. Testing combined mood + location:")
    test_combined = {"mood": "gay", "location": "south"}
    combined_results = match_venues(test_combined)
    print(f"   Query 'gay' + 'south' found {len(combined_results)} venues:")
    for v in combined_results:
        print(f"      - {v['name']} in {v['area']} (moods: {v['mood_tags']})")

    # Basic test without filters
    print("\n6. Testing without filters (baseline):")
    result = match_venues({})
    print(f"   No filters found {len(result)} venues")
    if result:
        for venue in result:
            print(f"      - {venue['name']} in {venue['area']}")

    print("\n" + "=" * 60)
    print("Tests complete!")
    print("=" * 60)