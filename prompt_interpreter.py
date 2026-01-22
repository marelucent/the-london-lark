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
with open("mood_index.json", "r", encoding="utf-8") as f:
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

    # Grief/Death/End of Life
    "death cafe": "death cafe",
    "death café": "death cafe",
    "grief": "grief",
    "grieving": "grief",
    "bereavement": "grief",
    "mourning": "grief",
    "loss": "grief",
    "grief circle": "grief",
    "grief group": "grief",
    "grief support": "grief",
    "grief tending": "grief",
    "death positive": "death cafe",
    "mortality": "death cafe",

    # Choirs/Singing
    "choir": "choir",
    "choirs": "choir",
    "singing": "choir",
    "vocal": "choir",
    "chorus": "choir",
    "community singing": "choir",
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

    # Location detection - comprehensive London neighbourhoods
    # Check regions first, then specific areas
    location = None

    # Regions (broad areas)
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
    elif "southeast london" in prompt_lower or "south east london" in prompt_lower:
        location = "South East London"
    elif "southwest london" in prompt_lower or "south west london" in prompt_lower:
        location = "South West London"
    elif "northeast london" in prompt_lower or "north east london" in prompt_lower:
        location = "North East London"
    elif "northwest london" in prompt_lower or "north west london" in prompt_lower:
        location = "North West London"

    # East London neighbourhoods
    elif "shoreditch" in prompt_lower:
        location = "Shoreditch"
    elif "hackney" in prompt_lower:
        location = "Hackney"
    elif "dalston" in prompt_lower:
        location = "Dalston"
    elif "bethnal green" in prompt_lower:
        location = "Bethnal Green"
    elif "whitechapel" in prompt_lower:
        location = "Whitechapel"
    elif "mile end" in prompt_lower:
        location = "Mile End"
    elif "bow" in prompt_lower:
        location = "Bow"
    elif "limehouse" in prompt_lower:
        location = "Limehouse"
    elif "canary wharf" in prompt_lower:
        location = "Canary Wharf"
    elif "stratford" in prompt_lower:
        location = "Stratford"
    elif "walthamstow" in prompt_lower:
        location = "Walthamstow"
    elif "leyton" in prompt_lower:
        location = "Leyton"
    elif "leytonstone" in prompt_lower:
        location = "Leytonstone"
    elif "canning town" in prompt_lower:
        location = "Canning Town"
    elif "barking" in prompt_lower:
        location = "Barking"
    elif "stepney" in prompt_lower:
        location = "Stepney"

    # South London neighbourhoods
    elif "brixton" in prompt_lower:
        location = "Brixton"
    elif "peckham" in prompt_lower:
        location = "Peckham"
    elif "deptford" in prompt_lower:
        location = "Deptford"
    elif "greenwich" in prompt_lower:
        location = "Greenwich"
    elif "lewisham" in prompt_lower:
        location = "Lewisham"
    elif "catford" in prompt_lower:
        location = "Catford"
    elif "bermondsey" in prompt_lower:
        location = "Bermondsey"
    elif "borough" in prompt_lower:
        location = "Borough"
    elif "southwark" in prompt_lower:
        location = "Southwark"
    elif "waterloo" in prompt_lower:
        location = "Waterloo"
    elif "elephant" in prompt_lower or "elephant and castle" in prompt_lower:
        location = "Elephant and Castle"
    elif "clapham" in prompt_lower:
        location = "Clapham"
    elif "balham" in prompt_lower:
        location = "Balham"
    elif "tooting" in prompt_lower:
        location = "Tooting"
    elif "streatham" in prompt_lower:
        location = "Streatham"
    elif "crystal palace" in prompt_lower:
        location = "Crystal Palace"
    elif "camberwell" in prompt_lower:
        location = "Camberwell"
    elif "dulwich" in prompt_lower:
        location = "Dulwich"
    elif "herne hill" in prompt_lower:
        location = "Herne Hill"
    elif "vauxhall" in prompt_lower:
        location = "Vauxhall"
    elif "kennington" in prompt_lower:
        location = "Kennington"
    elif "stockwell" in prompt_lower:
        location = "Stockwell"
    elif "new cross" in prompt_lower:
        location = "New Cross"
    elif "brockley" in prompt_lower:
        location = "Brockley"
    elif "forest hill" in prompt_lower:
        location = "Forest Hill"
    elif "sydenham" in prompt_lower:
        location = "Sydenham"
    elif "nunhead" in prompt_lower:
        location = "Nunhead"
    elif "honor oak" in prompt_lower:
        location = "Honor Oak"

    # North London neighbourhoods
    elif "camden" in prompt_lower:
        location = "Camden"
    elif "islington" in prompt_lower:
        location = "Islington"
    elif "king's cross" in prompt_lower or "kings cross" in prompt_lower:
        location = "King's Cross"
    elif "finsbury park" in prompt_lower:
        location = "Finsbury Park"
    elif "stoke newington" in prompt_lower or "stokey" in prompt_lower:
        location = "Stoke Newington"
    elif "tottenham" in prompt_lower:
        location = "Tottenham"
    elif "hampstead" in prompt_lower:
        location = "Hampstead"
    elif "highgate" in prompt_lower:
        location = "Highgate"
    elif "muswell hill" in prompt_lower:
        location = "Muswell Hill"
    elif "crouch end" in prompt_lower:
        location = "Crouch End"
    elif "hornsey" in prompt_lower:
        location = "Hornsey"
    elif "archway" in prompt_lower:
        location = "Archway"
    elif "holloway" in prompt_lower:
        location = "Holloway"
    elif "kentish town" in prompt_lower:
        location = "Kentish Town"
    elif "tufnell park" in prompt_lower:
        location = "Tufnell Park"
    elif "wood green" in prompt_lower:
        location = "Wood Green"
    elif "turnpike lane" in prompt_lower:
        location = "Turnpike Lane"
    elif "angel" in prompt_lower and "islington" not in prompt_lower:
        location = "Angel"
    elif "highbury" in prompt_lower:
        location = "Highbury"
    elif "canonbury" in prompt_lower:
        location = "Canonbury"
    elif "kilburn" in prompt_lower:
        location = "Kilburn"

    # West London neighbourhoods
    elif "notting hill" in prompt_lower:
        location = "Notting Hill"
    elif "portobello" in prompt_lower:
        location = "Notting Hill"
    elif "shepherd's bush" in prompt_lower or "shepherds bush" in prompt_lower:
        location = "Shepherd's Bush"
    elif "hammersmith" in prompt_lower:
        location = "Hammersmith"
    elif "fulham" in prompt_lower:
        location = "Fulham"
    elif "chelsea" in prompt_lower:
        location = "Chelsea"
    elif "kensington" in prompt_lower:
        location = "Kensington"
    elif "earl's court" in prompt_lower or "earls court" in prompt_lower:
        location = "Earl's Court"
    elif "ealing" in prompt_lower:
        location = "Ealing"
    elif "chiswick" in prompt_lower:
        location = "Chiswick"
    elif "richmond" in prompt_lower:
        location = "Richmond"
    elif "kew" in prompt_lower:
        location = "Kew"
    elif "wimbledon" in prompt_lower:
        location = "Wimbledon"
    elif "kingston" in prompt_lower:
        location = "Kingston"
    elif "acton" in prompt_lower:
        location = "Acton"
    elif "twickenham" in prompt_lower:
        location = "Twickenham"
    elif "brentford" in prompt_lower:
        location = "Brentford"
    elif "putney" in prompt_lower:
        location = "Putney"
    elif "barnes" in prompt_lower:
        location = "Barnes"
    elif "east sheen" in prompt_lower or "sheen" in prompt_lower:
        location = "East Sheen"
    elif "park royal" in prompt_lower:
        location = "Park Royal"
    elif "white city" in prompt_lower:
        location = "White City"
    elif "ladbroke grove" in prompt_lower:
        location = "Ladbroke Grove"
    elif "queens park" in prompt_lower or "queen's park" in prompt_lower:
        location = "Queen's Park"
    elif "kensal" in prompt_lower:
        location = "Kensal"

    # Central London neighbourhoods
    elif "soho" in prompt_lower:
        location = "Soho"
    elif "covent garden" in prompt_lower:
        location = "Covent Garden"
    elif "leicester square" in prompt_lower:
        location = "Leicester Square"
    elif "piccadilly" in prompt_lower:
        location = "Piccadilly"
    elif "mayfair" in prompt_lower:
        location = "Mayfair"
    elif "westminster" in prompt_lower:
        location = "Westminster"
    elif "victoria" in prompt_lower:
        location = "Victoria"
    elif "pimlico" in prompt_lower:
        location = "Pimlico"
    elif "marylebone" in prompt_lower:
        location = "Marylebone"
    elif "fitzrovia" in prompt_lower:
        location = "Fitzrovia"
    elif "bloomsbury" in prompt_lower:
        location = "Bloomsbury"
    elif "holborn" in prompt_lower:
        location = "Holborn"
    elif "clerkenwell" in prompt_lower:
        location = "Clerkenwell"
    elif "farringdon" in prompt_lower:
        location = "Farringdon"
    elif "barbican" in prompt_lower:
        location = "Barbican"
    elif "the city" in prompt_lower or "city of london" in prompt_lower:
        location = "City of London"
    elif "bank" in prompt_lower:
        location = "Bank"
    elif "strand" in prompt_lower:
        location = "Strand"
    elif "temple" in prompt_lower:
        location = "Temple"
    elif "embankment" in prompt_lower:
        location = "Embankment"
    elif "st paul" in prompt_lower or "st. paul" in prompt_lower:
        location = "St Paul's"

    # Outer London areas
    elif "wembley" in prompt_lower:
        location = "Wembley"
    elif "harrow" in prompt_lower:
        location = "Harrow"
    elif "croydon" in prompt_lower:
        location = "Croydon"
    elif "bromley" in prompt_lower:
        location = "Bromley"
    elif "woolwich" in prompt_lower:
        location = "Woolwich"
    elif "eltham" in prompt_lower:
        location = "Eltham"
    elif "enfield" in prompt_lower:
        location = "Enfield"
    elif "barnet" in prompt_lower:
        location = "Barnet"
    elif "ilford" in prompt_lower:
        location = "Ilford"
    elif "romford" in prompt_lower:
        location = "Romford"
    elif "sutton" in prompt_lower:
        location = "Sutton"
    elif "morden" in prompt_lower:
        location = "Morden"
    elif "bexley" in prompt_lower:
        location = "Bexley"
    elif "hounslow" in prompt_lower:
        location = "Hounslow"
    elif "uxbridge" in prompt_lower:
        location = "Uxbridge"

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

    # Determine query type for conversational fallbacks
    location_only = location is not None and mood is None and genre is None

    # Detect vague/unclear queries
    vague_words = ["something", "somewhere", "anything", "whatever", "nice", "good", "different", "interesting"]
    prompt_words = prompt_lower.split()
    is_vague = any(word in prompt_words for word in vague_words) and mood is None

    return {
        "mood": mood,
        "time": time,
        "budget": budget,
        "group": group,
        "genre": genre,
        "location": location,
        "search_text": prompt,  # Keep original prompt for name search fallback
        "location_only": location_only,  # Flag for conversational fallback
        "is_vague": is_vague  # Flag for vague queries needing clarification
    }

# Example usage
if __name__ == "__main__":
    test_prompt = "Something cheap and poetic in East London tonight?"
    print(interpret_prompt(test_prompt))
