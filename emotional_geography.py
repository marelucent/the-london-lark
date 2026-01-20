#!/usr/bin/env python3
# 🌙 emotional_geography.py

"""
The London Lark — Emotional Geography Configuration

This module contains the tarot adjacency map and shared need clusters
that enable smarter, more varied card drawing.

Philosophy: She doesn't give you what you searched for.
She gives you what you searched for, and one door you didn't know to ask about.
"""

# =============================================================================
# TAROT ADJACENCY MAP
# =============================================================================
# Each arcana maps to its 3 neighbouring arcana (based on emotional proximity)
# When drawing cards, the 3rd card comes from an adjacent arcana for variety

TAROT_ADJACENCY = {
    "Playful & Weird": ["Curious Encounters", "Cabaret & Glitter", "Big Night Out"],
    "Curious Encounters": ["Playful & Weird", "Word & Voice", "Rant & Rapture"],
    "Witchy & Wild": ["Nostalgic / Vintage / Retro", "Grief & Grace", "Spiritual / Sacred / Mystical"],
    "Folk & Intimate": ["Contemplative & Meditative", "Group Energy", "Word & Voice"],
    "The Thoughtful Stage": ["Rant & Rapture", "Curious Encounters", "Spiritual / Sacred / Mystical"],
    "Spiritual / Sacred / Mystical": ["Witchy & Wild", "The Thoughtful Stage", "Wonder & Awe"],
    "Cabaret & Glitter": ["Playful & Weird", "Comic Relief", "Folk & Intimate"],
    "Big Night Out": ["Playful & Weird", "Cabaret & Glitter", "Late-Night Lark"],
    "Punchy / Protest": ["Rant & Rapture", "Body-Based / Movement-Led", "Melancholic Beauty"],
    "Contemplative & Meditative": ["Grief & Grace", "Folk & Intimate", "Nostalgic / Vintage / Retro"],
    "Global Rhythms": ["Wonder & Awe", "Group Energy", "Word & Voice"],
    "Rant & Rapture": ["Punchy / Protest", "The Thoughtful Stage", "Curious Encounters"],
    "Body-Based / Movement-Led": ["Grief & Grace", "Punchy / Protest", "Melancholic Beauty"],
    "Grief & Grace": ["Contemplative & Meditative", "Body-Based / Movement-Led", "Nostalgic / Vintage / Retro"],
    "Word & Voice": ["Folk & Intimate", "Curious Encounters", "Global Rhythms"],
    "Late-Night Lark": ["Big Night Out", "Melancholic Beauty", "Cabaret & Glitter"],
    "Melancholic Beauty": ["Late-Night Lark", "Grief & Grace", "Body-Based / Movement-Led"],
    "Wonder & Awe": ["Nostalgic / Vintage / Retro", "Global Rhythms", "Spiritual / Sacred / Mystical"],
    "Nostalgic / Vintage / Retro": ["Wonder & Awe", "Grief & Grace", "Witchy & Wild"],
    "Comic Relief": ["Cabaret & Glitter", "Group Energy", "Playful & Weird"],
    "Group Energy": ["Folk & Intimate", "Comic Relief", "Global Rhythms"],
    "Queer Revelry": ["Comic Relief", "Group Energy", "Big Night Out"],
    "Romanticised London": ["Wonder & Awe", "Queer Revelry", "Playful & Weird"]
}


# =============================================================================
# SHARED NEED CLUSTERS
# =============================================================================
# Therapeutic groupings based on emotional needs (not mood matching)
# Used in care pathways (Tier 2/3) to offer diverse medicines

SHARED_NEEDS = {
    "to_be_held": ["Folk & Intimate", "Group Energy", "Word & Voice"],
    "to_move_through": ["Body-Based / Movement-Led", "Punchy / Protest", "Rant & Rapture"],
    "to_rest": ["Contemplative & Meditative", "Grief & Grace", "Nostalgic / Vintage / Retro"],
    "to_feel_joy": ["Comic Relief", "Cabaret & Glitter", "Playful & Weird"],
    "to_witness_beauty": ["Wonder & Awe", "Melancholic Beauty", "Romanticised London"],
    "to_touch_sacred": ["Spiritual / Sacred / Mystical", "Witchy & Wild", "Contemplative & Meditative"],
    "to_be_with_others": ["Group Energy", "Queer Revelry", "Big Night Out"],
    "to_rage_release": ["Punchy / Protest", "Rant & Rapture", "Body-Based / Movement-Led"],
    "to_feel_curious": ["Curious Encounters", "Playful & Weird", "Witchy & Wild"],
    "to_let_loose": ["Late-Night Lark", "Big Night Out", "Cabaret & Glitter"],
    "to_feel_connected": ["Global Rhythms", "Spiritual / Sacred / Mystical", "Wonder & Awe"],
    "to_think": ["The Thoughtful Stage", "Rant & Rapture", "Word & Voice"]
}


# =============================================================================
# CARE PATHWAY NEED SELECTIONS
# =============================================================================
# Maps emotional tiers to recommended need clusters for therapeutic spread

# For Tier 2 (Emotional) - softer needs
TIER2_NEED_SPREAD = ["to_be_held", "to_rest", "to_witness_beauty"]

# For Tier 3 (Distress) - deeper support needs
TIER3_NEED_SPREAD = ["to_rest", "to_be_held", "to_witness_beauty"]


# =============================================================================
# "I DON'T KNOW" / SURPRISE ME DETECTION
# =============================================================================
# Phrases that indicate the user wants fate to choose

SURPRISE_ME_PHRASES = {
    # Explicit uncertainty
    "i don't know",
    "i dont know",
    "don't know",
    "dont know",
    "not sure",
    "no idea",
    "no clue",
    "unsure",
    "uncertain",
    # Request for randomness
    "surprise me",
    "surprise",
    "random",
    "anything",
    "whatever",
    "you choose",
    "you decide",
    "dealer's choice",
    "dealers choice",
    "fate",
    "let fate decide",
    # Empty/vague
    "something",
    "somewhere",
    "idk",
    "dunno",
    "hmm",
    "um",
    "uh",
    # Draw metaphors
    "draw for me",
    "pick for me",
    "choose for me",
    "deal me",
    "shuffle"
}


def get_adjacent_arcana(arcana_name):
    """
    Get the list of adjacent arcana for a given arcana.
    Returns empty list if arcana not found.
    """
    return TAROT_ADJACENCY.get(arcana_name, [])


def get_random_adjacent(arcana_name):
    """
    Get a random adjacent arcana for a given arcana.
    Returns None if arcana not found or has no adjacents.
    """
    import random
    adjacents = get_adjacent_arcana(arcana_name)
    return random.choice(adjacents) if adjacents else None


def get_need_cluster(need_key):
    """
    Get the arcana list for a given need.
    Returns empty list if need not found.
    """
    return SHARED_NEEDS.get(need_key, [])


def get_all_need_keys():
    """Return all available need keys."""
    return list(SHARED_NEEDS.keys())


def is_surprise_me_query(query_text):
    """
    Check if a query indicates the user wants a surprise/random draw.

    Args:
        query_text: The user's search query

    Returns:
        True if query matches surprise-me patterns
    """
    if not query_text:
        return True  # Empty query = surprise me

    query_lower = query_text.lower().strip()

    # Very short queries (1-2 words) that match phrases
    if len(query_lower) < 20:
        for phrase in SURPRISE_ME_PHRASES:
            if phrase in query_lower or query_lower in phrase:
                return True

    # Check for exact matches
    if query_lower in SURPRISE_ME_PHRASES:
        return True

    return False


def get_therapeutic_spread_needs(tier='emotional'):
    """
    Get the need clusters to draw from for a therapeutic spread.

    Args:
        tier: 'emotional' (Tier 2) or 'distress' (Tier 3)

    Returns:
        List of 3 need keys for the spread
    """
    if tier == 'distress':
        return TIER3_NEED_SPREAD.copy()
    return TIER2_NEED_SPREAD.copy()


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  EMOTIONAL GEOGRAPHY — CONFIG TEST")
    print("=" * 60)

    # Test adjacency
    print("\n--- Tarot Adjacency ---")
    test_arcana = "Witchy & Wild"
    adjacents = get_adjacent_arcana(test_arcana)
    print(f"{test_arcana} is adjacent to: {adjacents}")

    random_adj = get_random_adjacent(test_arcana)
    print(f"Random adjacent: {random_adj}")

    # Test shared needs
    print("\n--- Shared Needs ---")
    test_need = "to_be_held"
    cluster = get_need_cluster(test_need)
    print(f"{test_need}: {cluster}")

    # Test surprise detection
    print("\n--- Surprise Me Detection ---")
    test_queries = [
        "i don't know",
        "surprise me",
        "jazz in soho",
        "anything",
        "",
        "witchy vibes"
    ]
    for query in test_queries:
        result = is_surprise_me_query(query)
        print(f"  '{query}' -> {'SURPRISE' if result else 'normal'}")

    print("\n" + "=" * 60)
