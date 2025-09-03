# 🌈 mood_resolver.py

"""
The London Lark — Mood Resolver

Given a user phrase or extracted keyword list, resolves to the best-matching mood tag.
Uses `mood_index.json` for synonym mapping and vibe alignment.
"""

import json

# Load mood index
with open("mood_index.json", "r") as f:
    mood_index = json.load(f)

# Invert synonym map for lookup
synonym_to_mood = {}
for mood, values in mood_index.items():
    for synonym in values.get("synonyms", []):
        synonym_to_mood[synonym.lower()] = mood

# Optional: Add fuzzy matching or similarity scoring in future

def resolve_mood_from_phrase(phrase):
    """
    Given a user phrase or word, return best-matching mood tag.
    """
    phrase = phrase.lower().strip()
    if phrase in synonym_to_mood:
        return synonym_to_mood[phrase]
    else:
        return None

# Bulk resolver for list of keywords
def resolve_from_keywords(keywords):
    """
    Given a list of keywords, return top matching mood tag (first match).
    """
    for word in keywords:
        mood = resolve_mood_from_phrase(word)
        if mood:
            return mood
    return None

# Example usage
if __name__ == "__main__":
    test_keywords = ["sad", "quiet", "intimate"]
    print("Resolved mood:", resolve_from_keywords(test_keywords))
