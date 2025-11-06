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
    if any(word in prompt_lower for word in ["cheap", "free", "affordable"]):
        budget = "low"
    elif any(word in prompt_lower for word in ["expensive", "splurge", "fancy"]):
        budget = "high"
    else:
        budget = None

    # Solo/group
    if "just me" in prompt_lower or "alone" in prompt_lower or "solo" in prompt_lower:
        group = "solo"
    elif "friends" in prompt_lower or "partner" in prompt_lower:
        group = "group"
    else:
        group = None

    # Location detection
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
    # Also check for specific neighborhoods
    elif "camden" in prompt_lower:
        location = "Camden"
    elif "islington" in prompt_lower:
        location = "Islington"
    elif "brixton" in prompt_lower:
        location = "Brixton"
    elif "peckham" in prompt_lower:
        location = "Peckham"
    elif "shoreditch" in prompt_lower or "hackney" in prompt_lower:
        location = "East London"
    elif "notting hill" in prompt_lower or "portobello" in prompt_lower:
        location = "West London"

    # Genre/style stub (can be expanded)
    genre = None
    if "theatre" in prompt_lower:
        genre = "theatre"
    elif "gig" in prompt_lower or "live music" in prompt_lower:
        genre = "music"
    elif "drag" in prompt_lower:
        genre = "drag"

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
