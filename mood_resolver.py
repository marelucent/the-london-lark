# 🌈 mood_resolver.py

"""
The London Lark — Mood Resolver

Given a user phrase or extracted keyword list, resolves to the best-matching mood tag.
Uses `mood_index.json` for synonym mapping and fuzzy matching for close matches.
"""

import json
import difflib

# Load mood index
with open("mood_index.json", "r") as f:
    mood_index = json.load(f)

# Invert synonym map for lookup
synonym_to_mood = {}
for mood, values in mood_index.items():
    for synonym in values.get("synonyms", []):
        synonym_to_mood[synonym.lower()] = mood

def _calculate_similarity(word1, word2):
    """
    Calculate similarity between two words (0.0 to 1.0)
    Uses sequence matching for fuzzy comparison
    """
    return difflib.SequenceMatcher(None, word1.lower(), word2.lower()).ratio()

def _find_close_matches(phrase, threshold=0.75):
    """
    Find synonyms that are close matches to the phrase
    Returns list of (synonym, mood, similarity_score) tuples
    """
    matches = []
    phrase_lower = phrase.lower().strip()

    for synonym, mood in synonym_to_mood.items():
        similarity = _calculate_similarity(phrase_lower, synonym)
        if similarity >= threshold:
            matches.append((synonym, mood, similarity))

    # Sort by similarity score (highest first)
    matches.sort(key=lambda x: x[2], reverse=True)
    return matches

def resolve_mood_from_phrase(phrase, fuzzy=True):
    """
    Given a user phrase or word, return best-matching mood tag.

    Args:
        phrase: The word or phrase to match
        fuzzy: If True, use fuzzy matching for close matches (default: True)

    Returns:
        tuple: (mood_name, confidence) where confidence is 1.0 for exact, <1.0 for fuzzy
    """
    phrase = phrase.lower().strip()

    # Try exact match first
    if phrase in synonym_to_mood:
        return (synonym_to_mood[phrase], 1.0)

    # Try fuzzy matching if enabled
    if fuzzy:
        close_matches = _find_close_matches(phrase, threshold=0.75)
        if close_matches:
            synonym, mood, similarity = close_matches[0]
            return (mood, similarity)

    return (None, 0.0)

# Bulk resolver for list of keywords
def resolve_from_keywords(keywords, fuzzy=True):
    """
    Given a list of keywords, return top matching mood tag.

    Args:
        keywords: List of words to check
        fuzzy: If True, use fuzzy matching (default: True)

    Returns:
        tuple: (mood_name, confidence) or (None, 0.0) if no match
    """
    best_match = (None, 0.0)

    for word in keywords:
        mood, confidence = resolve_mood_from_phrase(word, fuzzy=fuzzy)
        if mood and confidence > best_match[1]:
            best_match = (mood, confidence)

    return best_match

# Example usage
if __name__ == "__main__":
    # Test exact matches
    print("Exact matches:")
    print("  'sad':", resolve_mood_from_phrase("sad"))
    print("  'folk':", resolve_mood_from_phrase("folk"))
    print("  'drag':", resolve_mood_from_phrase("drag"))

    # Test fuzzy matches
    print("\nFuzzy matches:")
    print("  'folky':", resolve_mood_from_phrase("folky"))
    print("  'comdy':", resolve_mood_from_phrase("comdy"))  # typo for comedy
    print("  'dragg':", resolve_mood_from_phrase("dragg"))  # typo for drag
    print("  'queeer':", resolve_mood_from_phrase("queeer"))  # typo for queer

    # Test keyword list
    print("\nKeyword list:")
    test_keywords = ["sad", "quiet", "intimate"]
    print(f"  {test_keywords}:", resolve_from_keywords(test_keywords))
