# 🧠 prompt_interpreter.py

"""
The London Lark — Prompt Interpreter

This module takes natural language input and extracts key filters:
- mood (from mood_index.json)
- time (e.g. tonight, Friday, this weekend)
- location (neighbourhoods, boroughs)
- genre / style clues
- budget cues (cheap, splurge, etc.)
- solo/group context

Intended as the first step in the matching pipeline.
"""

import re
import json
from datetime import datetime, timedelta

# Load mood index (with synonyms)
with open("mood_index.json", "r") as f:
    mood_index = json.load(f)

# Flatten mood synonyms into lookup
mood_lookup = {}
for mood, values in mood_index.items():
    for synonym in values.get("synonyms", []):
        mood_lookup[synonym.lower()] = mood

# Simple time phrase mapping
TIME_KEYWORDS = {
    "tonight": "tonight",
    "this evening": "tonight",
    "tomorrow": "tomorrow",
    "this weekend": "weekend",
    "friday": "Friday",
    "saturday": "Saturday",
    "sunday": "Sunday",
}

# Genre keywords to detect - maps user terms to normalized genre categories
GENRE_KEYWORDS = {
    # Music genres (generic)
    "music": "music",
    "live music": "music",
    "gig": "music",
    "gigs": "music",
    "concert": "music",
    "concerts": "music",
    "band": "music",
    "bands": "music",
    "singer": "music",
    "singing": "music",

    # Specific music genres
    "jazz": "jazz",
    "folk": "folk",
    "electronic": "electronic",
    "rock": "rock",
    "indie": "indie",
    "reggae": "reggae",
    "reggaeton": "reggaeton",
    "blues": "blues",
    "soul": "soul",
    "hip-hop": "hip-hop",
    "hip hop": "hip-hop",
    "classical": "classical",
    "punk": "punk",
    "metal": "metal",
    "techno": "techno",
    "house": "house",
    "industrial": "industrial",
    "ebm": "industrial",
    "goth": "goth",
    "gothic": "goth",
    "darkwave": "goth",
    "dark techno": "industrial",
    "latin": "latin",
    "afrobeat": "afrobeat",
    "amapiano": "afrobeat",

    # Theatre
    "theatre": "theatre",
    "theater": "theatre",
    "play": "theatre",
    "plays": "theatre",
    "drama": "theatre",
    "stage": "theatre",
    "fringe": "theatre",
    "musical": "theatre",
    "musicals": "theatre",

    # Comedy
    "comedy": "comedy",
    "standup": "comedy",
    "stand-up": "comedy",
    "stand up": "comedy",
    "comic": "comedy",
    "comics": "comedy",
    "comedian": "comedy",
    "comedians": "comedy",
    "funny": "comedy",
    "laughs": "comedy",

    # Film/Cinema
    "film": "film",
    "films": "film",
    "cinema": "film",
    "movie": "film",
    "movies": "film",
    "screening": "film",
    "screenings": "film",

    # Dance
    "dance": "dance",
    "dancing": "dance",
    "ballet": "dance",

    # Art/Exhibition
    "art": "art",
    "gallery": "art",
    "exhibition": "art",
    "exhibitions": "art",

    # Poetry/Spoken Word
    "poetry": "poetry",
    "poems": "poetry",
    "spoken word": "poetry",
    "open mic": "poetry",

    # Cabaret/Drag
    "cabaret": "cabaret",
    "burlesque": "cabaret",
    "drag": "drag",
    "drag show": "drag",
    "drag queen": "drag",

    # Books/Literary
    "bookshop": "bookshop",
    "bookstore": "bookshop",
    "book shop": "bookshop",
    "book store": "bookshop",
    "books": "bookshop",
    "bookshops": "bookshop",
    "literary": "bookshop",
    "reading": "bookshop",
}

# Helper function to clean and tokenize
def clean_text(text):
    """Remove punctuation and extra whitespace for better matching"""
    # Remove common punctuation but keep spaces
    text = re.sub(r'[^\w\s-]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Core interpreter function
def interpret_prompt(prompt):
    prompt_lower = prompt.lower()
    prompt_clean = clean_text(prompt_lower)

    # Mood detection - try multi-word phrases first, then single words
    mood_matches = []

    # First, check for multi-word mood synonyms (e.g., "spoken word", "live music")
    for synonym, mood_name in mood_lookup.items():
        if ' ' in synonym:  # Multi-word synonym
            if synonym in prompt_clean:
                mood_matches.append(mood_name)

    # Then check single words (with punctuation stripped)
    if not mood_matches:
        words = prompt_clean.split()
        for word in words:
            # Strip any remaining punctuation/hyphens and check
            clean_word = word.strip('-')
            if clean_word in mood_lookup:
                mood_matches.append(mood_lookup[clean_word])
            # Also check the original word in case it's hyphenated (folk-y -> folk)
            word_root = word.split('-')[0] if '-' in word else word
            if word_root in mood_lookup and mood_lookup[word_root] not in mood_matches:
                mood_matches.append(mood_lookup[word_root])

    mood = mood_matches[0] if mood_matches else None

    # Time detection
    time = None
    for key in TIME_KEYWORDS:
        if key in prompt_lower:
            time = TIME_KEYWORDS[key]
            break

    # Budget detection
    if any(phrase in prompt_lower for phrase in ["not too expensive", "not expensive", "cheap", "free", "affordable", "budget-friendly", "inexpensive"]):
        budget = "low"
    elif any(word in prompt_lower for word in ["expensive", "splurge", "fancy", "pricey", "upscale"]):
        budget = "high"
    else:
        budget = None

    # Solo/group
    if any(phrase in prompt_lower for phrase in ["just me", "just for me", "alone", "solo", "on my own", "by myself"]):
        group = "solo"
    elif any(word in prompt_lower for word in ["friends", "partner", "group", "mates", "crowd"]):
        group = "group"
    else:
        group = None

    # Location detection - check regions first, then specific areas
    location = None
    if "north london" in prompt_lower:
        location = "North London"
    elif "south london" in prompt_lower:
        location = "South London"
    elif "east london" in prompt_lower:
        location = "East London"
    elif "west london" in prompt_lower:
        location = "West London"
    elif "central london" in prompt_lower:
        location = "Central London"
    # Specific neighborhoods - West London
    elif "ealing" in prompt_lower:
        location = "Ealing"
    elif "chiswick" in prompt_lower:
        location = "Chiswick"
    elif "richmond" in prompt_lower:
        location = "Richmond"
    elif "kew" in prompt_lower:
        location = "Kew"
    elif "acton" in prompt_lower:
        location = "Acton"
    elif "twickenham" in prompt_lower:
        location = "Twickenham"
    elif "kilburn" in prompt_lower:
        location = "Kilburn"
    elif "east sheen" in prompt_lower or "sheen" in prompt_lower:
        location = "East Sheen"
    elif "wood green" in prompt_lower:
        location = "Wood Green"
    elif "park royal" in prompt_lower:
        location = "Park Royal"
    # Other specific neighborhoods
    elif "camden" in prompt_lower:
        location = "Camden"
    elif "islington" in prompt_lower:
        location = "Islington"
    elif "brixton" in prompt_lower:
        location = "Brixton"
    elif "peckham" in prompt_lower:
        location = "Peckham"
    elif "dalston" in prompt_lower:
        location = "Dalston"
    elif "shoreditch" in prompt_lower or "hackney" in prompt_lower:
        location = "East London"
    elif "notting hill" in prompt_lower or "portobello" in prompt_lower:
        location = "West London"
    elif "deptford" in prompt_lower:
        location = "Deptford"
    elif "canning town" in prompt_lower:
        location = "Canning Town"
    elif "barking" in prompt_lower:
        location = "Barking"
    elif "stepney" in prompt_lower:
        location = "Stepney"

    # Genre detection - try multi-word phrases first, then single words
    genre = None

    # First check multi-word genre keywords (e.g., "live music", "stand up", "spoken word")
    for keyword, genre_value in GENRE_KEYWORDS.items():
        if ' ' in keyword:  # Multi-word keyword
            if keyword in prompt_clean:
                genre = genre_value
                break

    # If no multi-word match, check single-word keywords
    if not genre:
        words = prompt_clean.split()
        for word in words:
            clean_word = word.strip('-')
            if clean_word in GENRE_KEYWORDS:
                genre = GENRE_KEYWORDS[clean_word]
                break

    return {
        "mood": mood,
        "time": time,
        "budget": budget,
        "group": group,
        "genre": genre,
        "location": location
    }

# Example usage
if __name__ == "__main__":
    test_prompt = "Something cheap and poetic in East London tonight?"
    print(interpret_prompt(test_prompt))
