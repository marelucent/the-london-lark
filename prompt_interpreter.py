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

# Core interpreter function
def interpret_prompt(prompt):
    prompt_lower = prompt.lower()

    # Mood detection
    mood_matches = []
    for word in prompt_lower.split():
        if word in mood_lookup:
            mood_matches.append(mood_lookup[word])
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
        "genre": genre
    }

# Example usage
test_prompt = "Something cheap and poetic in East London tonight?"
print(interpret_prompt(test_prompt))
