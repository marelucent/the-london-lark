# ✍️ response_generator.py

"""
The London Lark — Poetic Response Generator

Takes user filters + matched venue, and generates a poetic recommendation.
Pulls from `response_templates.md` logic formats and uses venue/mood slot values.
"""

import random

# Simple poetic format templates (in lieu of full markdown parser)
RESPONSE_TEMPLATES = {
    "Matchmaker": "{opening} Tonight, {venue} is hosting something that leans toward {mood}. {vibe_note} It starts at {time}, costs {price}, and the chairs are soft if you’re early.",
    "MoodMirror": "{opening} If you’re feeling {mood}, this might be for you: {venue} is holding something tender tonight. {vibe_note} It’s £{price} and gently lit.",
    "Wildcard": "Off-script we go, petal. Try this: {venue} has a {mood}-soaked oddity tonight. {vibe_note} You’ll either love it or write a poem about it.",
    "Shortlist": "Here are a few glowing lanterns to light your way, petal. Let’s start with {venue} — {vibe_note} Then we’ll wander from there...",
    "GentleRefusal": "The city’s quiet on that front tonight, petal. But give me a moment — the Lark always hears something stirring."
}

# Sample poetic opening lines (could be expanded)
OPENINGS = [
    "A hush in the streets, a rustle in the fringe...",
    "The city’s heart beats softer tonight...",
    "If your mood were a room, this might be it...",
    "Here’s something just off the usual path..."
]

# Basic generator function
def generate_response(venue, filters, response_type="Matchmaker"):
    """
    Generate a poetic response given a venue and filters.

    Args:
        venue: Dict with keys: name, vibe_note, price, typical_start_time, area
        filters: Dict with mood, time, etc.
        response_type: One of Matchmaker, MoodMirror, Wildcard, Shortlist, GentleRefusal
    """
    if not venue:
        return RESPONSE_TEMPLATES["GentleRefusal"]

    mood = filters.get("mood", "something interesting")
    price = venue.get("price", "TBC")
    time = venue.get("typical_start_time") or filters.get("time", "8pm")
    vibe_note = venue.get("vibe_note", "It hums with something special.")
    venue_name = venue.get("name", "a hidden gem")

    opening = random.choice(OPENINGS)

    template = RESPONSE_TEMPLATES.get(response_type, RESPONSE_TEMPLATES["Matchmaker"])

    try:
        return template.format(
            opening=opening,
            venue=venue_name,
            mood=mood,
            time=time,
            price=price,
            vibe_note=vibe_note
        )
    except KeyError as e:
        # Fallback if template has unexpected placeholders
        return f"{opening} {venue_name} awaits. {vibe_note}"

# Example usage
if __name__ == "__main__":
    test_venue = {
        "name": "Green Note",
        "vibe_note": "Folk harmonies spill from the stage.",
        "price": "14"
    }
    test_filters = {
        "mood": "Folk & Intimate",
        "time": "tonight"
    }
    print(generate_response(test_venue, test_filters))
