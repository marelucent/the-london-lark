# ✍️ response_generator.py

"""
The London Lark — Poetic Response Generator

Takes user filters + matched venue, and generates a poetic recommendation.
Dynamically builds responses with real logistics (time, price, location).

Now uses voice profiles from poetic_templates.py for mood-aware responses:
- MYTHIC_NIGHTS: Sacred, ritualistic moods
- NOSTALGIC_NEON: Vintage, melancholic moods
- WILD_BECOMING: Rebellious, ecstatic moods
- TENDER_BELONGING: Folk, intimate moods
- CURIOUS_WONDER: Playful, experimental moods
"""

import random
from datetime import datetime

# Import voice profile system
try:
    from poetic_templates import (
        get_opening,
        get_venue_intro,
        get_rejection_message,
        get_profile_name,
        VOICE_PROFILES,
        MOOD_TO_PROFILE
    )
    HAS_VOICE_PROFILES = True
except ImportError:
    HAS_VOICE_PROFILES = False

# Fallback opening lines (used if poetic_templates not available)
FALLBACK_OPENINGS = [
    "A hush in the streets, a rustle in the fringe...",
    "The city's heart beats softer tonight...",
    "If your mood were a room, this might be it...",
    "Here's something just off the usual path...",
    "I whisper this to you...",
    "Let me paint you an evening...",
    "Close your eyes and imagine...",
    "Tonight, the city offers this...",
]

# Fallback mood-specific transition phrases
FALLBACK_MOOD_PHRASES = {
    "Folk & Intimate": ["Something warm", "Something tender", "Something close"],
    "Queer Revelry": ["Something glittering", "Something jubilant", "Something fierce"],
    "Playful & Weird": ["Something peculiar", "Something delightfully odd", "Something off-kilter"],
    "Comic Relief": ["Something to make you laugh", "Something light", "Something silly in the best way"],
    "Poetic": ["Something lyrical", "Something that shimmers with words", "Something to carry home"],
    "The Thoughtful Stage": ["Something that makes you lean in", "Something quietly brilliant", "Something to ponder"],
}

# Genre-aware opening phrases for genre-only searches
GENRE_OPENINGS = {
    "music": [
        "I hear music in your words, petal...",
        "When you seek sound, I offer this...",
        "The city hums with melody tonight...",
        "For those who chase the note and rhythm...",
    ],
    "jazz": [
        "Ah, jazz... where improvisation is prayer...",
        "Smoke and brass, petal. I know a place...",
        "For the jazz-hearted wanderer...",
    ],
    "folk": [
        "Something acoustic and honest calls to you...",
        "Where strings tell stories...",
        "Folk finds its way to those who listen...",
    ],
    "theatre": [
        "The stage whispers your name tonight...",
        "When drama calls, the Lark knows where...",
        "For those who crave the curtain's rise...",
        "Theatre, petal — where truth wears a mask...",
    ],
    "comedy": [
        "Laughter is medicine, petal...",
        "Something to tickle your ribs tonight...",
        "When you need to laugh, I offer this...",
        "Comedy finds those who need it most...",
    ],
    "film": [
        "The silver screen beckons...",
        "For the cinema-hearted souls...",
        "Somewhere, a projector hums just for you...",
    ],
    "cabaret": [
        "Glitter and gasps, petal...",
        "Where spectacle meets soul...",
        "For the cabaret curious...",
    ],
    "drag": [
        "Fierce, fabulous, and waiting for you...",
        "Where queens reign supreme...",
        "Drag, darling — art in sequins...",
    ],
    "poetry": [
        "Words hang in the air tonight...",
        "For those who speak in verse...",
        "Poetry breathes here...",
    ],
    "dance": [
        "Where bodies tell stories...",
        "Movement calls to you, petal...",
        "Dance, like secrets shared in motion...",
    ],
    "art": [
        "Canvas and vision await...",
        "For the gallery wanderer...",
        "Art speaks when words fail...",
    ],
}

def get_genre_opening(genre):
    """Get a random opening phrase for a genre-only search"""
    if genre and genre.lower() in GENRE_OPENINGS:
        return random.choice(GENRE_OPENINGS[genre.lower()])
    # Default for unknown genres
    return f"When you seek {genre}, petal, I offer this..."

def _format_time(time_str, user_time_filter):
    """Format time information naturally"""
    if not time_str or time_str == "TBC":
        if user_time_filter:
            if user_time_filter.lower() == "tonight":
                return "tonight"
            elif user_time_filter.lower() == "tomorrow":
                return "tomorrow"
            elif user_time_filter.lower() in ["friday", "saturday", "sunday"]:
                return f"on {user_time_filter}"
            else:
                return user_time_filter
        return "soon"
    return f"at {time_str}"

def _format_price(price_str):
    """Format price information naturally"""
    if not price_str or price_str == "TBC":
        return None  # Don't mention price if unknown

    # Clean up price string
    price_clean = price_str.replace("£", "").strip()

    try:
        price_num = float(price_clean)
        if price_num == 0:
            return "It's free"
        elif price_num < 10:
            return f"It's just £{price_clean}"
        elif price_num < 20:
            return f"It's £{price_clean}"
        else:
            return f"It's £{price_clean} (but worth every penny)"
    except:
        return f"It costs {price_str}"

def _format_location(venue):
    """Format location information poetically"""
    name = venue.get("name", "this place")
    area = venue.get("area", "")

    if area:
        return f"{name} in {area}"
    return name

def generate_response(venue, filters, response_type="Matchmaker"):
    """
    Generate a poetic response with real logistics.

    The Lark's voice shifts based on the detected mood using voice profiles.

    Args:
        venue: Dict with keys: name, vibe_note, price, typical_start_time, area
        filters: Dict with mood, time, location, budget, genre, group
        response_type: Type of response to generate
    """
    if not venue:
        return _generate_gentle_refusal(filters)

    # Extract data
    mood = filters.get("mood")
    genre = filters.get("genre")
    venue_name = venue.get("name", "a hidden gem")
    vibe_note = venue.get("vibe_note", "It hums with something special.")
    area = venue.get("area", "London")

    # Format logistics
    time_phrase = _format_time(venue.get("typical_start_time"), filters.get("time"))
    price_phrase = _format_price(venue.get("price"))
    location_phrase = _format_location(venue)

    # Choose opening (voice-profile aware, with genre fallback)
    # If genre-only search (no strong mood), use genre-aware language
    if not mood and genre:
        opening = get_genre_opening(genre)
    elif HAS_VOICE_PROFILES:
        opening = get_opening(mood)
    else:
        opening = random.choice(FALLBACK_OPENINGS)

    # Build response dynamically
    response_parts = []

    # Opening
    response_parts.append(opening)

    # Mood-specific venue introduction (voice-profile aware)
    if HAS_VOICE_PROFILES:
        intro = get_venue_intro("warm", mood)
        response_parts.append(f"{intro} {venue_name}.")
    elif mood and mood in FALLBACK_MOOD_PHRASES:
        intro = random.choice(FALLBACK_MOOD_PHRASES[mood])
        response_parts.append(f"{intro}: {venue_name}.")
    else:
        response_parts.append(f"Try {venue_name}.")

    # Vibe note (ensure it ends with punctuation)
    if vibe_note and not vibe_note.endswith(('.', '!', '?')):
        vibe_note = vibe_note + "."
    response_parts.append(vibe_note)

    # Logistics (if available)
    logistics = []
    if time_phrase and time_phrase != "soon":
        logistics.append(f"happening {time_phrase}")
    if price_phrase:
        logistics.append(price_phrase.lower())

    if logistics:
        response_parts.append(" — ".join([l.capitalize() for l in logistics]) + ".")

    # Join with proper spacing
    return " ".join(response_parts)

def _generate_gentle_refusal(filters):
    """
    Generate a gentle refusal when no venues match.

    Uses voice-profile-aware rejection messages.
    """
    mood = filters.get("mood")
    genre = filters.get("genre")
    location = filters.get("location")

    # Use voice profile rejection if available
    if HAS_VOICE_PROFILES and mood:
        response = get_rejection_message(mood)
    elif genre:
        # Genre-specific gentle refusal
        genre_refusals = {
            "music": "The city's stages are quiet on that front tonight, petal.",
            "theatre": "No curtains rising for that request just now.",
            "comedy": "The laughter's hiding tonight, but try me again.",
            "film": "No projectors humming for that, I'm afraid.",
            "jazz": "The jazz clubs are keeping their secrets tonight.",
            "poetry": "No verses floating by just now, but keep asking.",
        }
        response = genre_refusals.get(genre.lower(),
            f"Nothing's singing in the {genre} key tonight, petal.")
    else:
        refusals = [
            "The city's quiet on that front tonight, petal.",
            "I've found nothing quite right just yet.",
            "Hmm, the city's being shy about this one.",
            "Nothing's singing in quite that key tonight.",
        ]
        response = random.choice(refusals)

    # Add specific guidance (only if not using voice profiles)
    if not (HAS_VOICE_PROFILES and mood):
        if mood and location:
            response += f" (Looking for {mood} in {location} proved tricky.)"
        elif genre and location:
            response += f" (No {genre} venues in {location} turned up.)"
        elif mood:
            response += f" (No {mood} vibes turning up just now.)"
        elif genre:
            response += f" (No {genre} spots matched your ask.)"
        elif location:
            response += f" (Nothing in {location} matched your ask.)"

        response += " Try broadening your search, or ask me something else?"

    return response


def generate_surprise_response(venue):
    """
    Generate a first-person surprise response for a random venue.

    Uses intimate, present-tense voice with "I/me/my" instead of "The Lark".
    More personal and companion-like.

    Args:
        venue: Dict with keys: name, vibe_note, price, typical_start_time, area

    Returns:
        String with poetic first-person response
    """
    if not venue:
        return "I couldn't find the right place for you right now, petal. Ask again?"

    # Intimate opening lines in first person
    surprise_openings = [
        "I've chosen something for you...",
        "Trust my wings tonight...",
        "Here's a secret I've been keeping...",
        "Something you didn't know you needed...",
        "Let me take you somewhere...",
        "I've found a place that sings...",
        "Close your eyes — I'll guide you...",
        "Here's where I'd go tonight...",
        "I whisper this to you...",
        "Come with me, petal...",
    ]

    # Extract venue data
    venue_name = venue.get("name", "a hidden gem")
    vibe_note = venue.get("vibe_note", "It holds something special.")
    area = venue.get("area", "London")
    time_phrase = venue.get("typical_start_time", "")
    price = venue.get("price", "")

    # Ensure vibe note ends with punctuation
    if vibe_note and not vibe_note.endswith(('.', '!', '?')):
        vibe_note = vibe_note + "."

    # Build response in first person
    response_parts = []

    # Opening
    response_parts.append(random.choice(surprise_openings))

    # Venue introduction (first person)
    response_parts.append(f"I'm sending you to {venue_name}.")

    # Vibe note
    response_parts.append(vibe_note)

    # Logistics (if available) - converted to first person
    logistics = []
    if time_phrase and time_phrase != "TBC":
        logistics.append(f"doors around {time_phrase}")
    if price and price != "TBC":
        try:
            price_num = float(price.replace("£", "").strip())
            if price_num == 0:
                logistics.append("it's free")
            elif price_num < 10:
                logistics.append(f"just £{price}")
            else:
                logistics.append(f"£{price}")
        except:
            logistics.append(f"{price}")

    if logistics:
        response_parts.append(" — ".join([l.capitalize() for l in logistics]) + ".")

    # Closing note - encouragement to try again
    closing_notes = [
        "Want another? Ask again.",
        "Trust me on this one.",
        "Something tells me you'll like this.",
        "Not quite right? Ask me again.",
        "I chose this one especially for you.",
    ]
    response_parts.append(closing_notes[random.randint(0, len(closing_notes) - 1)])

    return " ".join(response_parts)


def get_current_voice_profile(mood):
    """
    Get information about the current voice profile being used.

    Args:
        mood: The mood tag

    Returns:
        Dict with profile name and description, or None
    """
    if not HAS_VOICE_PROFILES:
        return None

    profile_name = get_profile_name(mood)
    if profile_name in VOICE_PROFILES:
        return {
            "name": profile_name,
            "description": VOICE_PROFILES[profile_name]["description"]
        }
    return {"name": "GENERAL", "description": "Default Lark voice"}

# Example usage
if __name__ == "__main__":
    test_venue = {
        "name": "🎻 Green Note",
        "vibe_note": "Folk harmonies spill from the stage in this Camden basement",
        "price": "14",
        "area": "Camden Town",
        "typical_start_time": "8pm"
    }
    test_filters = {
        "mood": "Folk & Intimate",
        "time": "tonight",
        "location": "Camden"
    }
    print(generate_response(test_venue, test_filters))
    print("\n---\n")
    print(generate_response(None, test_filters))

