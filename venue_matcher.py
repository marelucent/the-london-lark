# 🔍 venue_matcher.py

"""
The London Lark — Venue Matcher

Matches venue profiles to interpreted prompt filters.
Draws from `lark_venues_clean.json`, a curated dataset of venues.
Matches on:
- Venue name (high priority - direct text match)
- Venue blurb/whisper/moods/genres (medium priority - text match)
- Mood tag (using full synonym list from mood_index.json)
- Direct mood array search (finds moods even if not in mood_index.json)
- Location (if given)
- Group size compatibility

Now with adjacency-based card drawing:
- 2 primary arcana venues + 1 adjacent arcana venue
- "She gives you what you searched for, and one door you didn't know to ask about."
"""

import json
import random
import re
from pathlib import Path
from parse_venues import load_parsed_venues
from emotional_geography import get_random_adjacent, TAROT_ADJACENCY

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


def search_venue_text(search_text, venues, location=None):
    """
    Search venue names, blurbs, whispers, moods, and genres for matching text.

    Returns a tuple of (name_matches, text_matches) where:
    - name_matches: venues where search terms appear in the name (high priority)
    - text_matches: venues where search terms appear in blurb/whisper/moods/genres (medium priority)

    This ensures all mood tags are searchable, even those not in mood_index.json.
    Both lists are filtered by location if specified.
    """
    if not search_text:
        return [], []

    # Clean and extract meaningful search words (ignore common stopwords)
    stopwords = {
        'a', 'an', 'the', 'in', 'on', 'at', 'for', 'to', 'of', 'and', 'or',
        'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'i', 'me', 'my', 'we', 'our', 'you', 'your',
        'something', 'somewhere', 'anything', 'anywhere', 'want', 'looking',
        'find', 'show', 'tell', 'give', 'need', 'like', 'love',
        'tonight', 'today', 'tomorrow', 'weekend', 'evening', 'night', 'day',
        'london', 'near', 'around', 'nearby'
    }

    # Extract search terms
    search_lower = search_text.lower()
    # Remove punctuation and split
    words = re.sub(r'[^\w\s-]', ' ', search_lower).split()
    search_terms = [w for w in words if w not in stopwords and len(w) > 2]

    # Also check for multi-word phrases (like "death cafe", "tarot reading")
    multi_word_phrases = []
    for phrase_len in [3, 2]:  # Check 3-word and 2-word phrases
        for i in range(len(words) - phrase_len + 1):
            phrase = ' '.join(words[i:i+phrase_len])
            if phrase not in stopwords:
                multi_word_phrases.append(phrase)

    if not search_terms and not multi_word_phrases:
        return [], []

    print(f"   🔎 Text search terms: {search_terms[:5]}... phrases: {multi_word_phrases[:3]}...")

    name_matches = []
    text_matches = []

    for venue in venues:
        # Apply location filter if specified
        if location:
            area = venue.get("area", "") or venue.get("location", "")
            tags = venue.get("tags", [])
            tags_str = " ".join(tags) if isinstance(tags, list) else str(tags)
            if location.lower() not in area.lower() and location.lower() not in tags_str.lower():
                continue

        venue_name = venue.get("name", "").lower()
        venue_blurb = venue.get("blurb", "").lower()
        venue_whisper = venue.get("whisper", "").lower()

        # Also search the moods array - this makes all mood tags searchable
        # even if they're not in mood_index.json
        venue_moods = venue.get("moods", []) or venue.get("mood_tags", [])
        venue_moods_str = " ".join(m.lower() for m in venue_moods if m)

        # Also include genres in searchable text
        venue_genres = venue.get("genres", [])
        venue_genres_str = " ".join(g.lower() for g in venue_genres if g)

        # Check for multi-word phrase matches first (higher specificity)
        name_phrase_match = any(phrase in venue_name for phrase in multi_word_phrases)
        text_phrase_match = any(
            phrase in venue_blurb or
            phrase in venue_whisper or
            phrase in venue_moods_str or
            phrase in venue_genres_str
            for phrase in multi_word_phrases
        )

        # Check for single-word matches
        name_word_match = any(term in venue_name for term in search_terms)
        text_word_match = any(
            term in venue_blurb or
            term in venue_whisper or
            term in venue_moods_str or
            term in venue_genres_str
            for term in search_terms
        )

        # Also check for direct mood tag matches (e.g., "nerdy" matches ["nerdy", "geeky"])
        mood_direct_match = any(
            term == mood.lower() or mood.lower().startswith(term) or term in mood.lower()
            for term in search_terms
            for mood in venue_moods
        )

        if name_phrase_match or name_word_match:
            name_matches.append(venue)
        elif text_phrase_match or text_word_match or mood_direct_match:
            text_matches.append(venue)

    print(f"   📍 Text search found: {len(name_matches)} name matches, {len(text_matches)} text/mood matches")

    return name_matches, text_matches


def normalize_venue(venue):
    """Normalize venue data to expected format for responses."""
    mood_tags = venue.get("moods", []) or venue.get("mood_tags", [])
    return {
        "name": venue.get("name", "Unnamed venue"),
        "area": venue.get("area", venue.get("location", "London")),
        "vibe_note": venue.get("tone_notes", venue.get("blurb", "An experience beyond words")),
        "typical_start_time": venue.get("typical_start_time", ""),
        "price": venue.get("price", "TBC"),
        "website": venue.get("website", venue.get("url", "")),
        "whisper": venue.get("whisper", ""),
        "slug": venue.get("slug", ""),
        "mood_tags": mood_tags,
        "raw_data": venue
    }


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
            "whisper": venue.get("whisper", ""),  # Venue's unique whisper text
            "mood_tags": mood_tags,
            "raw_data": venue  # Keep original data for reference
        }
        matches.append(normalized_venue)

    # Shuffle matches to add variety
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

    # Return top 3 unique matches (basic matching, no adjacency)
    return deduplicated_matches[:3]


def match_venues_with_adjacency(filters, all_venues=None):
    """
    Smart card drawing with adjacency logic.

    Returns up to 3 venues:
    - Card 1: Primary arcana venue
    - Card 2: Primary arcana venue (different)
    - Card 3: Adjacent arcana venue (from a neighboring arcana)

    Now with text search priority:
    1. First check for name matches (high priority)
    2. Then check blurb/whisper matches (medium priority)
    3. Fall back to mood tag matching (standard behavior)

    "She gives you what you searched for, and one door you didn't know to ask about."
    """
    mood = filters.get("mood")
    location = filters.get("location")
    group = filters.get("group")
    budget = filters.get("budget")
    genre = filters.get("genre")
    search_text = filters.get("search_text", "")

    # Load all venues if not provided
    if all_venues is None:
        all_venues = load_parsed_venues()

    # UPGRADE 2: Try text search first (name, blurb, whisper)
    # Text search returns venues from ANY arcana that match keywords
    # The bridge will describe which arcana the results came from
    name_matches, text_matches = search_venue_text(search_text, all_venues, location)

    # If we have name matches, prioritize them
    if name_matches:
        print(f"   ✨ Using name matches for query")
        result = []
        seen_names = set()
        random.shuffle(name_matches)

        for venue in name_matches[:3]:
            venue_name = venue.get("name", "").lower().strip()
            if venue_name not in seen_names:
                result.append(normalize_venue(venue))
                seen_names.add(venue_name)

        # If we need more venues, add from text matches
        if len(result) < 3 and text_matches:
            random.shuffle(text_matches)
            for venue in text_matches:
                if len(result) >= 3:
                    break
                venue_name = venue.get("name", "").lower().strip()
                if venue_name not in seen_names:
                    result.append(normalize_venue(venue))
                    seen_names.add(venue_name)

        # If we still need more, try mood matching (from same arcana)
        if len(result) < 3 and mood:
            mood_matches = match_venues(filters)
            for venue in mood_matches:
                if len(result) >= 3:
                    break
                venue_name = venue.get("name", "").lower().strip()
                if venue_name not in seen_names:
                    result.append(venue)  # Already normalized by match_venues
                    seen_names.add(venue_name)

        if result:
            return result

    # If we have text matches but no name matches, use them
    if text_matches:
        print(f"   ✨ Using blurb/whisper matches for query")
        result = []
        seen_names = set()
        random.shuffle(text_matches)

        for venue in text_matches[:3]:
            venue_name = venue.get("name", "").lower().strip()
            if venue_name not in seen_names:
                result.append(normalize_venue(venue))
                seen_names.add(venue_name)

        # If we need more venues, try mood matching
        if len(result) < 3 and mood:
            mood_matches = match_venues(filters)
            for venue in mood_matches:
                if len(result) >= 3:
                    break
                venue_name = venue.get("name", "").lower().strip()
                if venue_name not in seen_names:
                    result.append(venue)  # Already normalized
                    seen_names.add(venue_name)

        if result:
            return result

    # Fall back to standard mood-based matching with adjacency
    print(f"   📜 Falling back to mood-based matching")

    # Determine the primary arcana
    # If mood is a valid arcana name, use it directly
    primary_arcana = None
    if mood and mood in TAROT_ADJACENCY:
        primary_arcana = mood
        print(f"   📍 Mood '{mood}' is a valid arcana, filtering by arcana field")

    # If mood is a valid arcana, filter venues directly by arcana field
    # This ensures we get venues FROM that arcana, not just venues with matching mood synonyms
    if primary_arcana:
        # Get all venues in the primary arcana
        primary_arcana_venues = []
        for venue in all_venues:
            if venue.get("arcana") == primary_arcana:
                # Apply location filter if specified
                if location:
                    area = venue.get("area", "") or venue.get("location", "")
                    tags = venue.get("tags", [])
                    tags_str = " ".join(tags) if isinstance(tags, list) else str(tags)
                    if location.lower() not in area.lower() and location.lower() not in tags_str.lower():
                        continue
                primary_arcana_venues.append(venue)

        # Shuffle for variety
        random.shuffle(primary_arcana_venues)
        print(f"   📊 Found {len(primary_arcana_venues)} venues in '{primary_arcana}' arcana")
    else:
        # Fallback: use mood synonym matching for non-arcana mood queries
        all_matches = match_venues(filters)

        if len(all_matches) < 2:
            return all_matches

        # Infer primary arcana from first match
        if all_matches:
            first_raw = all_matches[0].get("raw_data", {})
            primary_arcana = first_raw.get("arcana")
            print(f"   📍 Inferred primary arcana from first match: '{primary_arcana}'")

        # Separate matches into primary arcana and others
        primary_arcana_venues = []
        for venue in all_matches:
            raw_data = venue.get("raw_data", {})
            if raw_data.get("arcana") == primary_arcana:
                primary_arcana_venues.append(raw_data)  # Use raw_data for consistency

        print(f"   📊 Found {len(primary_arcana_venues)} primary venues from mood matching")

    # Build result: take up to 2 from primary arcana
    result = []
    seen_names = set()

    for venue in primary_arcana_venues[:2]:
        # Normalize venue data
        normalized = {
            "name": venue.get("name", "Unnamed venue"),
            "area": venue.get("area", venue.get("location", "London")),
            "vibe_note": venue.get("tone_notes", venue.get("blurb", "An experience beyond words")),
            "typical_start_time": venue.get("typical_start_time", ""),
            "price": venue.get("price", "TBC"),
            "website": venue.get("website", venue.get("url", "")),
            "whisper": venue.get("whisper", ""),
            "mood_tags": venue.get("moods", venue.get("mood_tags", [])),
            "raw_data": venue
        }
        result.append(normalized)
        seen_names.add(venue.get("name", "").lower().strip())

    # If we still need more primary venues (< 2), DON'T fill from random arcana
    # Instead, we'll get more from adjacent arcana in the next step
    if len(result) < 2:
        print(f"   ⚠️ Only {len(result)} primary venue(s) found, will draw extra from adjacent")

    # Calculate how many cards we still need (target: 3 total, with at least 1 from adjacent)
    cards_needed = 3 - len(result)

    # Get adjacent arcana list for drawing remaining cards
    adjacent_list = TAROT_ADJACENCY.get(primary_arcana, []) if primary_arcana else []

    if adjacent_list and cards_needed > 0:
        random.shuffle(adjacent_list)
        print(f"   🔗 Primary arcana '{primary_arcana}' → adjacents: {adjacent_list}")

        # Draw remaining cards from adjacent arcana
        for adj_arcana in adjacent_list:
            if cards_needed <= 0:
                break

            # Find venues in this adjacent arcana
            adjacent_candidates = []
            for venue in all_venues:
                if venue.get("arcana") == adj_arcana:
                    venue_name = venue.get("name", "").lower().strip()
                    if venue_name not in seen_names:
                        # Apply location filter if specified
                        if location:
                            area = venue.get("area", "") or venue.get("location", "")
                            tags = venue.get("tags", [])
                            tags_str = " ".join(tags) if isinstance(tags, list) else str(tags)
                            if location.lower() not in area.lower() and location.lower() not in tags_str.lower():
                                continue
                        adjacent_candidates.append(venue)

            if adjacent_candidates:
                random.shuffle(adjacent_candidates)
                adj_venue = adjacent_candidates[0]

                # Normalize to expected format
                normalized_adj = {
                    "name": adj_venue.get("name", "Unnamed venue"),
                    "area": adj_venue.get("area", adj_venue.get("location", "London")),
                    "vibe_note": adj_venue.get("tone_notes", adj_venue.get("blurb", "An experience beyond words")),
                    "typical_start_time": adj_venue.get("typical_start_time", ""),
                    "price": adj_venue.get("price", "TBC"),
                    "website": adj_venue.get("website", adj_venue.get("url", "")),
                    "whisper": adj_venue.get("whisper", ""),
                    "mood_tags": adj_venue.get("moods", adj_venue.get("mood_tags", [])),
                    "raw_data": adj_venue,
                    "is_adjacent": True,
                    "adjacent_from": primary_arcana
                }
                result.append(normalized_adj)
                seen_names.add(adj_venue.get("name", "").lower().strip())
                cards_needed -= 1
                print(f"   ✨ Adjacent card drawn: {normalized_adj['name']} from '{adj_arcana}'")

    # Fallback: if we still don't have 3 cards, try more from primary arcana
    if len(result) < 3 and len(primary_arcana_venues) > len(result):
        for venue in primary_arcana_venues[len(result):]:
            if len(result) >= 3:
                break
            venue_name = venue.get("name", "").lower().strip()
            if venue_name not in seen_names:
                normalized = {
                    "name": venue.get("name", "Unnamed venue"),
                    "area": venue.get("area", venue.get("location", "London")),
                    "vibe_note": venue.get("tone_notes", venue.get("blurb", "An experience beyond words")),
                    "typical_start_time": venue.get("typical_start_time", ""),
                    "price": venue.get("price", "TBC"),
                    "website": venue.get("website", venue.get("url", "")),
                    "whisper": venue.get("whisper", ""),
                    "mood_tags": venue.get("moods", venue.get("mood_tags", [])),
                    "raw_data": venue
                }
                result.append(normalized)
                seen_names.add(venue_name)
                print(f"   ⚠️ Fallback: extra primary venue '{venue.get('name')}'")

    if not adjacent_list and len(result) < 3:
        # No adjacency mapping found, fill remaining from primary arcana
        for venue in primary_arcana_venues[len(result):]:
            if len(result) >= 3:
                break
            venue_name = venue.get("name", "").lower().strip()
            if venue_name not in seen_names:
                normalized = {
                    "name": venue.get("name", "Unnamed venue"),
                    "area": venue.get("area", venue.get("location", "London")),
                    "vibe_note": venue.get("tone_notes", venue.get("blurb", "An experience beyond words")),
                    "typical_start_time": venue.get("typical_start_time", ""),
                    "price": venue.get("price", "TBC"),
                    "website": venue.get("website", venue.get("url", "")),
                    "whisper": venue.get("whisper", ""),
                    "mood_tags": venue.get("moods", venue.get("mood_tags", [])),
                    "raw_data": venue
                }
                result.append(normalized)
                seen_names.add(venue_name)
                print(f"   ⚠️ No adjacency map for '{primary_arcana}', using extra primary venue")

    return result


def match_surprise_with_adjacency(all_venues=None):
    """
    Draw for "I don't know" / "surprise me" queries.

    Returns up to 3 venues:
    - Card 1: Random arcana (fate chooses)
    - Card 2: Adjacent to Card 1 (first neighbor)
    - Card 3: Adjacent to Card 1 (different neighbor)

    Maximum variety across arcana — never 3 from the same arcana.
    """
    if all_venues is None:
        all_venues = load_parsed_venues()

    if not all_venues:
        return []

    # Pick a random starting venue (Card 1)
    random.shuffle(all_venues)
    card1_raw = all_venues[0]
    primary_arcana = card1_raw.get("arcana")

    seen_names = {card1_raw.get("name", "").lower().strip()}
    used_arcana = {primary_arcana}  # Track used arcana to ensure variety

    # Normalize Card 1
    card1 = {
        "name": card1_raw.get("name", "Unnamed venue"),
        "area": card1_raw.get("area", card1_raw.get("location", "London")),
        "vibe_note": card1_raw.get("tone_notes", card1_raw.get("blurb", "An experience beyond words")),
        "typical_start_time": card1_raw.get("typical_start_time", ""),
        "price": card1_raw.get("price", "TBC"),
        "website": card1_raw.get("website", card1_raw.get("url", "")),
        "whisper": card1_raw.get("whisper", ""),
        "mood_tags": card1_raw.get("moods", card1_raw.get("mood_tags", [])),
        "raw_data": card1_raw,
        "is_fate_draw": True
    }

    result = [card1]
    print(f"   🎲 Fate draw: '{card1['name']}' from '{primary_arcana}'")

    # Get adjacent arcana list
    adjacent_list = TAROT_ADJACENCY.get(primary_arcana, [])

    if len(adjacent_list) >= 2:
        # Pick 2 different adjacent arcana for Cards 2 and 3
        random.shuffle(adjacent_list)
        adj_arcana_1 = adjacent_list[0]
        adj_arcana_2 = adjacent_list[1]

        for i, adj_arcana in enumerate([adj_arcana_1, adj_arcana_2], start=2):
            # Find venues in this adjacent arcana
            adj_candidates = [
                v for v in all_venues
                if v.get("arcana") == adj_arcana
                and v.get("name", "").lower().strip() not in seen_names
            ]

            if adj_candidates:
                random.shuffle(adj_candidates)
                adj_raw = adj_candidates[0]
                seen_names.add(adj_raw.get("name", "").lower().strip())
                used_arcana.add(adj_arcana)

                adj_venue = {
                    "name": adj_raw.get("name", "Unnamed venue"),
                    "area": adj_raw.get("area", adj_raw.get("location", "London")),
                    "vibe_note": adj_raw.get("tone_notes", adj_raw.get("blurb", "An experience beyond words")),
                    "typical_start_time": adj_raw.get("typical_start_time", ""),
                    "price": adj_raw.get("price", "TBC"),
                    "website": adj_raw.get("website", adj_raw.get("url", "")),
                    "whisper": adj_raw.get("whisper", ""),
                    "mood_tags": adj_raw.get("moods", adj_raw.get("mood_tags", [])),
                    "raw_data": adj_raw,
                    "is_adjacent": True,
                    "adjacent_from": primary_arcana
                }
                result.append(adj_venue)
                print(f"   🔗 Adjacent card {i}: '{adj_venue['name']}' from '{adj_arcana}'")

    # If we don't have 3 cards yet, fill with venues from DIFFERENT arcana
    while len(result) < 3:
        # Prefer venues from arcana we haven't used yet
        remaining = [
            v for v in all_venues
            if v.get("name", "").lower().strip() not in seen_names
            and v.get("arcana") not in used_arcana
        ]

        # If no venues from different arcana, fall back to any unseen venue
        if not remaining:
            remaining = [
                v for v in all_venues
                if v.get("name", "").lower().strip() not in seen_names
            ]

        if remaining:
            random.shuffle(remaining)
            extra_raw = remaining[0]
            extra_arcana = extra_raw.get("arcana")
            seen_names.add(extra_raw.get("name", "").lower().strip())
            used_arcana.add(extra_arcana)
            print(f"   🎯 Fallback card from '{extra_arcana}': '{extra_raw.get('name')}'")

            extra = {
                "name": extra_raw.get("name", "Unnamed venue"),
                "area": extra_raw.get("area", extra_raw.get("location", "London")),
                "vibe_note": extra_raw.get("tone_notes", extra_raw.get("blurb", "An experience beyond words")),
                "typical_start_time": extra_raw.get("typical_start_time", ""),
                "price": extra_raw.get("price", "TBC"),
                "website": extra_raw.get("website", extra_raw.get("url", "")),
                "whisper": extra_raw.get("whisper", ""),
                "mood_tags": extra_raw.get("moods", extra_raw.get("mood_tags", [])),
                "raw_data": extra_raw
            }
            result.append(extra)
        else:
            break

    return result

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
