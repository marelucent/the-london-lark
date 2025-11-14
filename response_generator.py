# ✍️ response_generator.py

"""
The London Lark — Poetic Response Generator

Takes user filters + matched venue, and generates a poetic recommendation.
Dynamically builds responses with real logistics (time, price, location).
"""

import random
from datetime import datetime

# Expanded poetic opening lines
OPENINGS = [
    "A hush in the streets, a rustle in the fringe...",
    "The city's heart beats softer tonight...",
    "If your mood were a room, this might be it...",
    "Here's something just off the usual path...",
    "The Lark whispers this...",
    "Let me paint you an evening...",
    "Close your eyes and imagine...",
    "Tonight, the city offers this...",
]

# Mood-specific transition phrases
MOOD_PHRASES = {
    "Folk & Intimate": ["Something warm", "Something tender", "Something close"],
    "Queer Revelry": ["Something glittering", "Something jubilant", "Something fierce"],
    "Playful & Weird": ["Something peculiar", "Something delightfully odd", "Something off-kilter"],
    "Comic Relief": ["Something to make you laugh", "Something light", "Something silly in the best way"],
    "Poetic": ["Something lyrical", "Something that shimmers with words", "Something to carry home"],
    "The Thoughtful Stage": ["Something that makes you lean in", "Something quietly brilliant", "Something to ponder"],
}

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

    Args:
        venue: Dict with keys: name, vibe_note, price, typical_start_time, area
        filters: Dict with mood, time, location, budget, genre, group
        response_type: Type of response to generate
    """
    if not venue:
        return _generate_gentle_refusal(filters)

    # Extract data
    mood = filters.get("mood")
    venue_name = venue.get("name", "a hidden gem")
    vibe_note = venue.get("vibe_note", "It hums with something special.")
    area = venue.get("area", "London")

    # Format logistics
    time_phrase = _format_time(venue.get("typical_start_time"), filters.get("time"))
    price_phrase = _format_price(venue.get("price"))
    location_phrase = _format_location(venue)

    # Choose opening
    opening = random.choice(OPENINGS)

    # Build response dynamically
    response_parts = []

    # Opening
    response_parts.append(opening)

    # Mood-specific phrase if we have one
    if mood and mood in MOOD_PHRASES:
        intro = random.choice(MOOD_PHRASES[mood])
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
    """Generate a gentle refusal when no venues match"""
    mood = filters.get("mood")
    location = filters.get("location")

    refusals = [
        "The city's quiet on that front tonight, petal.",
        "The Lark's found nothing quite right just yet.",
        "Hmm, the city's being shy about this one.",
        "Nothing's singing in quite that key tonight.",
    ]

    response = random.choice(refusals)

    # Add specific guidance
    if mood and location:
        response += f" (Looking for {mood} in {location} proved tricky.)"
    elif mood:
        response += f" (No {mood} vibes turning up just now.)"
    elif location:
        response += f" (Nothing in {location} matched your ask.)"

    response += " Try broadening your search, or ask me something else?"

    return response

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

