#!/usr/bin/env python3
"""
Poetic Templates for The London Lark

The Lark's voice is poetic, warm, and emotionally intelligent.
This module provides modular templates for responses based on:
- Mood tags
- Venue types
- Time of day
- Context (empty state, single match, multiple matches)
"""

import random
from typing import Optional, Dict, List

# ═══════════════════════════════════════════════════════════════════
# OPENING PHRASES - Sets the scene
# ═══════════════════════════════════════════════════════════════════

OPENINGS = {
    "general": [
        "A hush in the streets, a rustle in the fringe...",
        "The night stretches its wings...",
        "Close your eyes and imagine...",
        "Tonight, the city offers this...",
        "The city's heart beats softer tonight...",
        "Here's something just off the usual path...",
        "The Lark whispers this...",
    ],
    "Folk & Intimate": [
        "Not all wildness needs a crowd...",
        "In candlelight, voices carry further...",
        "The quietest rooms hold the deepest songs...",
        "Where strings hum low and stories breathe...",
    ],
    "Queer Revelry": [
        "The rainbow unfurls after dark...",
        "Where chosen family gathers...",
        "Pride wears many faces tonight...",
        "A space where you can be wholly yourself...",
    ],
    "Melancholic Beauty": [
        "Some nights call for tenderness...",
        "Let the sadness sing, petal...",
        "In sorrow, there is strange comfort...",
        "The ache in your chest knows where to go...",
    ],
    "Late-Night Lark": [
        "When the clock strikes twelve, the real city wakes...",
        "For those who bloom after midnight...",
        "The witching hour approaches...",
        "Night owls, this one's for you...",
    ],
    "Curious Encounters": [
        "Prepare to have your expectations gently upended...",
        "The strange and wonderful await...",
        "For minds that wander down unusual paths...",
        "Something delightfully unexpected...",
    ],
    "The Thoughtful Stage": [
        "Theatre is where we rehearse being human...",
        "Stories that linger long after curtain fall...",
        "Words that ask questions of your soul...",
        "The stage holds up a mirror tonight...",
    ],
    "Global Rhythms": [
        "The world dances in London tonight...",
        "Borders dissolve on the dance floor...",
        "Music that carries passports from everywhere...",
        "Let your body remember older rhythms...",
    ],
    "Cabaret & Glitter": [
        "Sequins catch the light just so...",
        "Tonight we celebrate the spectacular...",
        "Glamour is its own kind of rebellion...",
        "Where performance becomes poetry...",
    ],
    "Poetic": [
        "Words fall like rain on dry earth...",
        "The poets gather to speak truth...",
        "Language as spell, as salve, as sword...",
        "Verses wait to find their way to you...",
    ],
    "Punchy / Protest": [
        "The revolution needs a soundtrack...",
        "Angry? Good. Channel it here...",
        "Where dissent becomes art...",
        "Songs that refuse to be quiet...",
    ],
    "Wonder & Awe": [
        "Prepare to have your breath taken...",
        "The extraordinary hides in plain sight...",
        "Some moments rewrite what's possible...",
        "Magic still exists, petal...",
    ],
    "Comic Relief": [
        "Laughter is the best rebellion...",
        "Sometimes you just need to laugh...",
        "Joy as medicine for these times...",
        "The absurd makes the world bearable...",
    ],
    "Spiritual / Sacred / Mystical": [
        "The veil between worlds thins here...",
        "Sacred spaces hold what words cannot...",
        "Listen with more than your ears tonight...",
        "Something ancient stirs...",
    ],
    "Big Night Out": [
        "The night is young and so are we...",
        "Energy crackles in the air...",
        "Tonight we dance until our feet forget themselves...",
        "The city pulses with possibility...",
    ],
    "Dreamlike & Hypnagogic": [
        "Between waking and sleeping, there is this...",
        "Let reality blur at the edges...",
        "Dreams leak into the evening...",
        "The subconscious wants to play...",
    ],
}

# ═══════════════════════════════════════════════════════════════════
# VENUE INTRODUCTIONS - Presents the space
# ═══════════════════════════════════════════════════════════════════

VENUE_INTROS = {
    "warm": [
        "Something warm:",
        "Something tender:",
        "Try this:",
        "Consider this:",
        "Here's a place:",
    ],
    "energetic": [
        "Something alive:",
        "Feel this energy:",
        "Try this on for size:",
        "Here's where it happens:",
    ],
    "mysterious": [
        "Something hidden:",
        "Down this path:",
        "Behind the ordinary door:",
        "Seek this:",
    ],
    "poetic": [
        "A verse made physical:",
        "Where atmosphere is everything:",
        "A place that understands:",
        "This corner of the city:",
    ],
}

# ═══════════════════════════════════════════════════════════════════
# TIME PHRASES - When things happen
# ═══════════════════════════════════════════════════════════════════

TIME_PHRASES = {
    "tonight": [
        "Happening tonight.",
        "This very evening.",
        "Tonight, if you're ready.",
        "Before the moon sets.",
    ],
    "weekend": [
        "This weekend awaits.",
        "Come the weekend.",
        "When Saturday stretches her arms.",
        "For your weekend wandering.",
    ],
    "tomorrow": [
        "Tomorrow beckons.",
        "Just one sleep away.",
        "Tomorrow's promise.",
    ],
    "soon": [
        "Soon, if the stars align.",
        "In the coming days.",
        "Mark your calendar.",
    ],
}

# ═══════════════════════════════════════════════════════════════════
# CLOSING PHRASES - Sends them off
# ═══════════════════════════════════════════════════════════════════

CLOSINGS = {
    "general": [
        "",
        "Trust your feet.",
        "The Lark has spoken.",
        "Go gently.",
    ],
    "encouraging": [
        "You won't regret it.",
        "This one's special.",
        "The night rewards the curious.",
    ],
    "mysterious": [
        "But don't take my word for it...",
        "See for yourself.",
        "The rest is up to you.",
    ],
}

# ═══════════════════════════════════════════════════════════════════
# EMPTY STATE MESSAGES - When no matches found
# ═══════════════════════════════════════════════════════════════════

EMPTY_STATE_MESSAGES = [
    "The wind found no doors tonight, petal. Try another path.",
    "Even the Lark must sometimes rest her wings. No matches found.",
    "The city hums, but not in that key tonight. Seek elsewhere.",
    "No feathers stirred for this request. Perhaps rephrase your longing?",
    "The map is vast, but this corner lies silent. Ask again differently.",
    "Sometimes the right place is still being dreamed. Try another mood?",
    "The Lark circled, but found no perch. Cast your net wider.",
    "Not every path has a destination tonight. Change your course?",
]

# ═══════════════════════════════════════════════════════════════════
# ERROR MESSAGES - Gentle failures
# ═══════════════════════════════════════════════════════════════════

ERROR_MESSAGES = [
    "The Lark stumbled on an unseen stone. Please try again.",
    "Something went awry in the telling. Give me another chance.",
    "A mist descended — try once more, petal.",
    "The words got tangled. Shall we try again?",
]

# ═══════════════════════════════════════════════════════════════════
# TEMPLATE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════


def get_opening(mood: Optional[str] = None) -> str:
    """Get an appropriate opening phrase for the given mood."""
    if mood and mood in OPENINGS:
        # 70% chance to use mood-specific opening
        if random.random() < 0.7:
            return random.choice(OPENINGS[mood])
    return random.choice(OPENINGS["general"])


def get_venue_intro(energy: str = "warm") -> str:
    """Get a venue introduction phrase."""
    if energy in VENUE_INTROS:
        return random.choice(VENUE_INTROS[energy])
    return random.choice(VENUE_INTROS["warm"])


def get_time_phrase(time_filter: Optional[str] = None) -> str:
    """Get a time phrase based on the filter."""
    if time_filter in TIME_PHRASES:
        return random.choice(TIME_PHRASES[time_filter])
    return ""


def get_closing() -> str:
    """Get a closing phrase."""
    # 60% chance of no closing (keep it clean)
    if random.random() < 0.6:
        return ""
    return random.choice(CLOSINGS["general"] + CLOSINGS["encouraging"])


def get_empty_state_message() -> str:
    """Get a poetic message for when no matches are found."""
    return random.choice(EMPTY_STATE_MESSAGES)


def get_error_message() -> str:
    """Get a gentle error message."""
    return random.choice(ERROR_MESSAGES)


def determine_energy(venue: Dict, mood: Optional[str] = None) -> str:
    """Determine the energy level for venue intro."""
    if mood in ["Big Night Out", "Global Rhythms", "Queer Revelry", "Cabaret & Glitter"]:
        return "energetic"
    elif mood in ["Curious Encounters", "Dreamlike & Hypnagogic", "Spiritual / Sacred / Mystical"]:
        return "mysterious"
    elif mood in ["Poetic", "Folk & Intimate", "Melancholic Beauty"]:
        return "poetic"
    else:
        return "warm"


def compose_response(
    venue: Dict,
    filters: Dict,
    include_opening: bool = True,
    include_closing: bool = True
) -> str:
    """
    Compose a complete poetic response for a venue recommendation.

    Args:
        venue: Venue dictionary with name, tone_notes, etc.
        filters: User's filters including mood, time, location
        include_opening: Whether to include an opening phrase
        include_closing: Whether to include a closing phrase

    Returns:
        str: Complete poetic response
    """
    parts = []

    # Opening phrase
    if include_opening:
        mood = filters.get("mood")
        opening = get_opening(mood)
        parts.append(opening)

    # Venue introduction
    energy = determine_energy(venue, filters.get("mood"))
    intro = get_venue_intro(energy)

    # Venue name and description
    venue_name = venue.get("name", "this place")
    tone_notes = venue.get("vibe_note", venue.get("tone_notes", ""))

    parts.append(f"{intro} {venue_name}. {tone_notes}")

    # Time phrase
    if filters.get("time"):
        time_phrase = get_time_phrase(filters["time"])
        if time_phrase:
            parts.append(time_phrase)

    # Closing
    if include_closing:
        closing = get_closing()
        if closing:
            parts.append(closing)

    return " ".join(parts)


def compose_multiple_responses(
    venues: List[Dict],
    filters: Dict
) -> List[str]:
    """
    Compose responses for multiple venue recommendations.
    Only the first gets an opening, variety in intros.

    Args:
        venues: List of venue dictionaries
        filters: User's filters

    Returns:
        List[str]: List of responses
    """
    responses = []

    for i, venue in enumerate(venues):
        # Only first response gets opening
        include_opening = (i == 0)

        response = compose_response(
            venue,
            filters,
            include_opening=include_opening,
            include_closing=False  # Keep individual responses clean
        )
        responses.append(response)

    return responses


# ═══════════════════════════════════════════════════════════════════
# TESTING / DEMO
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("  POETIC TEMPLATES - DEMO")
    print("=" * 70)

    # Test with sample venue
    sample_venue = {
        "name": "🎷 Jazzlive at the Crypt",
        "tone_notes": "Intimate, candle-lit jazz beneath gothic arches. Deep reverb, low light, and serious musicianship.",
        "area": "South London"
    }

    sample_filters = {
        "mood": "Melancholic Beauty",
        "time": "tonight",
        "location": "South London"
    }

    print("\nSample Venue Response:")
    print("-" * 70)
    response = compose_response(sample_venue, sample_filters)
    print(response)

    print("\n\nMood-Specific Openings:")
    print("-" * 70)
    for mood in ["Folk & Intimate", "Queer Revelry", "Late-Night Lark", "Curious Encounters"]:
        print(f"{mood}:")
        print(f"  {get_opening(mood)}")
        print()

    print("\nEmpty State Messages:")
    print("-" * 70)
    for _ in range(3):
        print(f"  • {get_empty_state_message()}")

    print("\n" + "=" * 70)
