#!/usr/bin/env python3
"""
Poetic Templates for The London Lark

The Lark's voice is poetic, warm, and emotionally intelligent.
This module provides modular templates for responses based on:
- Mood tags
- Venue types
- Time of day
- Context (empty state, single match, multiple matches)

The Lark's voice SHIFTS based on the mood being queried, with five distinct profiles:
1. MYTHIC NIGHTS - Archaic, ritualistic (sacred/haunted moods)
2. NOSTALGIC NEON - Warm, vintage, cinematic (nostalgic/tender moods)
3. WILD BECOMING - Urgent, transformative (rebellious/ecstatic moods)
4. TENDER BELONGING - Soft, inclusive, home-like (folk/intimate moods)
5. CURIOUS WONDER - Light, inquisitive (curious/playful moods)
"""

import random
from typing import Optional, Dict, List

# ═══════════════════════════════════════════════════════════════════
# VOICE PROFILES - Complete personality systems
# ═══════════════════════════════════════════════════════════════════

VOICE_PROFILES = {
    "MYTHIC_NIGHTS": {
        "description": "Archaic language, ritualistic cadence. Ceremonial and timeless.",
        "moods": [
            "Spiritual / Sacred / Mystical",
            "Witchy & Wild",
            "Dreamlike & Hypnagogic",
            "Grief & Grace",
        ],
        "openings": [
            "In the crypt where candles breathe and shadows remember...",
            "The ancient stones hum with frequencies beyond hearing...",
            "Where the veil grows thin and the old gods listen...",
            "A ritual unfolds for those who dare witness...",
            "The moon pulls at something deep within you tonight...",
            "In sacred spaces where time bends and meaning multiplies...",
            "The ancestors gather in corners unseen...",
            "Where ceremony meets the edge of mystery...",
            "Something primordial stirs beneath the city's skin...",
            "The eternal returns, dressed in new garments...",
        ],
        "venue_intros": [
            "A temple waits:",
            "The altar is prepared at",
            "Seek sanctuary within",
            "A consecrated space:",
            "The ritual ground is",
            "Where incense and intention meet:",
            "The portal opens at",
            "A threshold between worlds:",
            "The sacred waits at",
            "An offering place:",
        ],
        "rejections": [
            "The oracle is silent tonight. The spirits offer no path forward.",
            "Even the ancient ones rest. The ritual cannot be completed.",
            "The veil remains closed, petal. Seek again when the moon shifts.",
            "No sacred ground revealed itself. The journey continues elsewhere.",
            "The ceremony requires different elements. Transform your seeking.",
        ],
    },

    "NOSTALGIC_NEON": {
        "description": "Warm, vintage, cinematic language. Gentle and memory-soaked.",
        "moods": [
            "Nostalgic / Vintage / Retro",
            "Melancholic Beauty",
            "Jazz & Contemplation",
            "Cabaret & Glitter",
        ],
        "openings": [
            "Where chandeliers remember 1904 and every drink tells a story...",
            "The past isn't dead here—it wears velvet and pours bourbon...",
            "Somewhere between sepia and color, tonight lives...",
            "Old songs know your heartbreak by name...",
            "The city has corners that time forgot to update...",
            "Dust motes dance in amber light, and so might you...",
            "What the future discarded, the night cherishes...",
            "Memory has a texture here—worn wood, soft jazz, familiar ache...",
            "Some places hold time like a love letter holds perfume...",
            "The ghosts of better evenings await your company...",
        ],
        "venue_intros": [
            "A relic, lovingly preserved:",
            "Step back in time at",
            "Where history exhales:",
            "A fragment of yesterday:",
            "The past lives on at",
            "Time-worn and beautiful:",
            "Echoes of elegance at",
            "A vintage gem:",
            "Where memories crystallize:",
            "The old world beckons at",
        ],
        "rejections": [
            "The gramophone skips tonight, petal. No record matches your longing.",
            "Even nostalgia needs rest. The past offers no venue this evening.",
            "The photograph album lies empty for this request. Try another frame.",
            "No vintage door opened to your knock. Seek different memories.",
            "The neon flickers but doesn't spell your destination. Adjust the dial.",
        ],
    },

    "WILD_BECOMING": {
        "description": "Urgent, transformative, edge-walking. Alive, dangerous, free.",
        "moods": [
            "Big Night Out",
            "Late-Night Lark",
            "Punchy / Protest",
            "Queer Revelry",
        ],
        "openings": [
            "Where the night tears open and possibility bleeds through...",
            "The edge is where you find yourself, petal...",
            "Something in you wants to howl—let it...",
            "Tonight you are not who you were yesterday...",
            "The rules were made by people afraid of becoming...",
            "Your skin is electric. Trust that current...",
            "What if tonight you became the person you're afraid to be?",
            "The city's underbelly knows your true name...",
            "Revolution happens in moments of absolute presence...",
            "The cage door is open. Your wings remember...",
        ],
        "venue_intros": [
            "Where transformation happens:",
            "The edge awaits at",
            "Become something at",
            "The uprising gathers at",
            "Raw and alive:",
            "Where you shed your skin:",
            "Danger and beauty collide at",
            "The fire burns at",
            "Unchain yourself at",
            "Where the wild things are:",
        ],
        "rejections": [
            "The wildness sleeps tonight. The revolution takes a breath.",
            "No door opens to that particular chaos. Redirect your lightning.",
            "The edge retreated. Even danger needs variety.",
            "The night offers no arena for that becoming. Seek another transformation.",
            "Your wings find no updraft here. The storm gathers elsewhere.",
        ],
    },

    "TENDER_BELONGING": {
        "description": "Soft, inclusive, home-like. Safe, warm, welcoming.",
        "moods": [
            "Folk & Intimate",
            "Comic Relief",
            "Wonder & Awe",
            "Body-Based / Movement-Led",
        ],
        "openings": [
            "Where voices rise gently over worn wood floors...",
            "Some rooms feel like coming home to a family you chose...",
            "The kindest spaces ask nothing of you but presence...",
            "Warmth has an address tonight...",
            "Community isn't built—it's grown, like these walls know...",
            "Where strangers become friends between verses...",
            "The softest rebellions happen in gentle company...",
            "Your loneliness has an antidote, and it lives here...",
            "Some doors open wider for the weary...",
            "Home is a feeling, and tonight it has a postcode...",
        ],
        "venue_intros": [
            "A hearth awaits:",
            "Gather with kindred spirits at",
            "Find your people at",
            "Belonging lives at",
            "A gentle refuge:",
            "Where you're welcome:",
            "Community blooms at",
            "The circle forms at",
            "Warmth radiates from",
            "Your place at the table:",
        ],
        "rejections": [
            "The hearth lies cold for this request, petal. Seek different warmth.",
            "No circle forms around those words tonight. Rephrase your belonging.",
            "The community gathers elsewhere. Your people await different coordinates.",
            "Home doesn't answer to that call. Try a softer key.",
            "The welcome mat isn't out for this particular seeking. Adjust your heart.",
        ],
    },

    "CURIOUS_WONDER": {
        "description": "Light, inquisitive, possibility-filled. Open, experimental, fun.",
        "moods": [
            "Curious Encounters",
            "Playful & Weird",
            "The Thoughtful Stage",
            "Global Rhythms",
            "Poetic",
        ],
        "openings": [
            "What hides behind this door? Only one way to find out...",
            "Your sense of wonder isn't broken—it just needs exercise...",
            "The universe winks at those who stay curious...",
            "Questions are better than answers tonight...",
            "Every strange evening starts with 'what if'...",
            "The experimental path is paved with delightful mistakes...",
            "Boring is a choice you don't have to make...",
            "The peculiar and the profound share a postcode...",
            "Adventure is just inconvenience with a better attitude...",
            "The interesting people are already there, waiting for you...",
        ],
        "venue_intros": [
            "Discover this:",
            "Wonder awaits at",
            "The unexpected lives at",
            "Curiosity finds home at",
            "An experiment in joy:",
            "Question everything at",
            "The delightfully strange:",
            "Where 'why not?' leads:",
            "Possibility incarnate:",
            "The adventure begins at",
        ],
        "rejections": [
            "The question has no answer tonight. Ask again with different words.",
            "Even wonder needs rest, petal. The curious path winds elsewhere.",
            "No experiment matches those parameters. Adjust your variables.",
            "The strange and wonderful hide from this request. Seek with fresher eyes.",
            "Adventure sleeps for now. Wake it with different intentions.",
        ],
    },
}

# Mood to voice profile mapping
MOOD_TO_PROFILE = {
    # MYTHIC_NIGHTS
    "Spiritual / Sacred / Mystical": "MYTHIC_NIGHTS",
    "Witchy & Wild": "MYTHIC_NIGHTS",
    "Dreamlike & Hypnagogic": "MYTHIC_NIGHTS",
    "Grief & Grace": "MYTHIC_NIGHTS",

    # NOSTALGIC_NEON
    "Nostalgic / Vintage / Retro": "NOSTALGIC_NEON",
    "Melancholic Beauty": "NOSTALGIC_NEON",
    "Jazz & Contemplation": "NOSTALGIC_NEON",
    "Cabaret & Glitter": "NOSTALGIC_NEON",

    # WILD_BECOMING
    "Big Night Out": "WILD_BECOMING",
    "Late-Night Lark": "WILD_BECOMING",
    "Punchy / Protest": "WILD_BECOMING",
    "Queer Revelry": "WILD_BECOMING",

    # TENDER_BELONGING
    "Folk & Intimate": "TENDER_BELONGING",
    "Comic Relief": "TENDER_BELONGING",
    "Wonder & Awe": "TENDER_BELONGING",
    "Body-Based / Movement-Led": "TENDER_BELONGING",

    # CURIOUS_WONDER
    "Curious Encounters": "CURIOUS_WONDER",
    "Playful & Weird": "CURIOUS_WONDER",
    "The Thoughtful Stage": "CURIOUS_WONDER",
    "Global Rhythms": "CURIOUS_WONDER",
    "Poetic": "CURIOUS_WONDER",
}

# ═══════════════════════════════════════════════════════════════════
# LEGACY OPENINGS - For backwards compatibility
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
}

# Populate OPENINGS from voice profiles for backwards compatibility
for profile_name, profile_data in VOICE_PROFILES.items():
    for mood in profile_data["moods"]:
        if mood not in OPENINGS:
            OPENINGS[mood] = profile_data["openings"]

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


def get_voice_profile(mood: Optional[str] = None) -> Optional[Dict]:
    """
    Get the voice profile for a given mood.

    Args:
        mood: The mood tag

    Returns:
        Voice profile dictionary or None if no match
    """
    if mood and mood in MOOD_TO_PROFILE:
        profile_name = MOOD_TO_PROFILE[mood]
        return VOICE_PROFILES.get(profile_name)
    return None


def get_profile_name(mood: Optional[str] = None) -> str:
    """Get the name of the voice profile for a mood."""
    if mood and mood in MOOD_TO_PROFILE:
        return MOOD_TO_PROFILE[mood]
    return "GENERAL"


def get_opening(mood: Optional[str] = None) -> str:
    """Get an appropriate opening phrase for the given mood."""
    # Try voice profile first
    profile = get_voice_profile(mood)
    if profile and random.random() < 0.85:  # 85% chance to use profile
        return random.choice(profile["openings"])

    # Fallback to legacy openings
    if mood and mood in OPENINGS:
        if random.random() < 0.7:
            return random.choice(OPENINGS[mood])
    return random.choice(OPENINGS["general"])


def get_venue_intro(energy: str = "warm", mood: Optional[str] = None) -> str:
    """
    Get a venue introduction phrase.

    Args:
        energy: Energy level (warm, energetic, mysterious, poetic)
        mood: Optional mood to select profile-specific intro
    """
    # Try voice profile first if mood is provided
    profile = get_voice_profile(mood)
    if profile and random.random() < 0.8:  # 80% chance to use profile
        return random.choice(profile["venue_intros"])

    # Fallback to energy-based intros
    if energy in VENUE_INTROS:
        return random.choice(VENUE_INTROS[energy])
    return random.choice(VENUE_INTROS["warm"])


def get_rejection_message(mood: Optional[str] = None) -> str:
    """
    Get a mood-appropriate rejection message when no venues match.

    Args:
        mood: The mood that was searched for

    Returns:
        A poetic rejection message in the appropriate voice
    """
    profile = get_voice_profile(mood)
    if profile and "rejections" in profile:
        return random.choice(profile["rejections"])

    # Fallback to general empty state
    return random.choice(EMPTY_STATE_MESSAGES)


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


def get_empty_state_message(mood: Optional[str] = None) -> str:
    """
    Get a poetic message for when no matches are found.

    Args:
        mood: Optional mood to get profile-specific rejection
    """
    return get_rejection_message(mood)


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

    The Lark's voice shifts based on the detected mood, using voice profiles
    (MYTHIC_NIGHTS, NOSTALGIC_NEON, WILD_BECOMING, TENDER_BELONGING, CURIOUS_WONDER).

    Args:
        venue: Venue dictionary with name, tone_notes, etc.
        filters: User's filters including mood, time, location
        include_opening: Whether to include an opening phrase
        include_closing: Whether to include a closing phrase

    Returns:
        str: Complete poetic response in the appropriate voice
    """
    parts = []
    mood = filters.get("mood")

    # Opening phrase (voice-profile aware)
    if include_opening:
        opening = get_opening(mood)
        parts.append(opening)

    # Venue introduction (voice-profile aware)
    energy = determine_energy(venue, mood)
    intro = get_venue_intro(energy, mood)  # Now passes mood for profile selection

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
    print("  THE LARK'S VOICE PROFILES - DEMO")
    print("=" * 70)

    # Test voice profile selection
    print("\n🎭 VOICE PROFILE MAPPING:")
    print("-" * 70)
    test_moods = [
        "Spiritual / Sacred / Mystical",  # MYTHIC_NIGHTS
        "Melancholic Beauty",              # NOSTALGIC_NEON
        "Queer Revelry",                   # WILD_BECOMING
        "Folk & Intimate",                 # TENDER_BELONGING
        "Curious Encounters",              # CURIOUS_WONDER
    ]

    for mood in test_moods:
        profile_name = get_profile_name(mood)
        print(f"  {mood} → {profile_name}")

    # Demonstrate each voice profile
    print("\n\n🌟 VOICE PROFILE SAMPLES:")
    print("=" * 70)

    sample_venue = {
        "name": "🎷 Jazzlive at the Crypt",
        "tone_notes": "Intimate, candle-lit jazz beneath gothic arches.",
        "area": "South London"
    }

    # MYTHIC NIGHTS
    print("\n1. MYTHIC NIGHTS (Sacred/Mystical)")
    print("-" * 70)
    filters = {"mood": "Spiritual / Sacred / Mystical", "time": "tonight"}
    print(f"Opening: {get_opening('Spiritual / Sacred / Mystical')}")
    print(f"Venue Intro: {get_venue_intro('mysterious', 'Spiritual / Sacred / Mystical')}")
    print(f"Rejection: {get_rejection_message('Spiritual / Sacred / Mystical')}")

    # NOSTALGIC NEON
    print("\n2. NOSTALGIC NEON (Melancholic/Vintage)")
    print("-" * 70)
    print(f"Opening: {get_opening('Melancholic Beauty')}")
    print(f"Venue Intro: {get_venue_intro('poetic', 'Melancholic Beauty')}")
    print(f"Rejection: {get_rejection_message('Melancholic Beauty')}")

    # WILD BECOMING
    print("\n3. WILD BECOMING (Rebellious/Ecstatic)")
    print("-" * 70)
    print(f"Opening: {get_opening('Queer Revelry')}")
    print(f"Venue Intro: {get_venue_intro('energetic', 'Queer Revelry')}")
    print(f"Rejection: {get_rejection_message('Queer Revelry')}")

    # TENDER BELONGING
    print("\n4. TENDER BELONGING (Folk/Intimate)")
    print("-" * 70)
    print(f"Opening: {get_opening('Folk & Intimate')}")
    print(f"Venue Intro: {get_venue_intro('warm', 'Folk & Intimate')}")
    print(f"Rejection: {get_rejection_message('Folk & Intimate')}")

    # CURIOUS WONDER
    print("\n5. CURIOUS WONDER (Playful/Experimental)")
    print("-" * 70)
    print(f"Opening: {get_opening('Curious Encounters')}")
    print(f"Venue Intro: {get_venue_intro('mysterious', 'Curious Encounters')}")
    print(f"Rejection: {get_rejection_message('Curious Encounters')}")

    # Full composed responses
    print("\n\n📝 FULL COMPOSED RESPONSES:")
    print("=" * 70)

    profiles_to_test = [
        ("TENDER BELONGING", {"mood": "Folk & Intimate", "time": "tonight"}),
        ("WILD BECOMING", {"mood": "Late-Night Lark", "time": "weekend"}),
        ("NOSTALGIC NEON", {"mood": "Melancholic Beauty", "time": "tonight"}),
    ]

    for profile_name, filters in profiles_to_test:
        print(f"\n{profile_name} Response:")
        print("-" * 70)
        response = compose_response(sample_venue, filters)
        print(response)
        print()

    print("=" * 70)
    print("  Voice profiles enable the Lark to shift her tone based on mood!")
    print("=" * 70)
