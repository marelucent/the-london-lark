#!/usr/bin/env python3
# 🌈 mood_resolver.py

"""
The London Lark — Enhanced Mood Resolver

Intelligently resolves user queries to mood tags using:
- Multi-keyword matching with scoring
- Synonym specificity weighting
- Fuzzy matching for close matches
- Context-aware phrase detection

Returns the best-matching mood with confidence score.
"""

import json
import difflib
import re

# Load mood index
with open("mood_index.json", "r") as f:
    mood_index = json.load(f)

# Build synonym lookup with specificity scores
# Longer/more specific synonyms get higher weights
synonym_to_mood = {}
synonym_specificity = {}

for mood, values in mood_index.items():
    for synonym in values.get("synonyms", []):
        synonym_lower = synonym.lower()
        synonym_to_mood[synonym_lower] = mood
        # Specificity score: longer phrases = more specific
        # Also boost certain highly specific terms
        base_score = len(synonym.split())  # Multi-word phrases score higher
        
        # Boost scores for very specific emotional/experiential terms
        if synonym_lower in ["sweaty", "ecstatic", "hopeless", "struggling", "contemplative", 
                             "witchy", "ritual", "activist", "drag", "burlesque"]:
            base_score += 2
        
        synonym_specificity[synonym_lower] = base_score


def clean_text(text):
    """Remove punctuation and normalize whitespace"""
    text = re.sub(r'[^\w\s-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _calculate_similarity(word1, word2):
    """Calculate similarity between two words (0.0 to 1.0)"""
    return difflib.SequenceMatcher(None, word1.lower(), word2.lower()).ratio()


def _find_exact_matches(query_text):
    """
    Find all exact synonym matches in the query.
    Returns list of (synonym, mood, specificity_score) tuples.
    """
    query_lower = query_text.lower()
    query_clean = clean_text(query_lower)
    matches = []
    
    # Check for multi-word phrases first (they're more specific)
    for synonym, mood in synonym_to_mood.items():
        if ' ' in synonym:  # Multi-word
            if synonym in query_clean:
                specificity = synonym_specificity.get(synonym, 1)
                matches.append((synonym, mood, specificity, 1.0))  # 1.0 = exact match
    
    # Then check single words
    words = query_clean.split()
    for word in words:
        clean_word = word.strip('-')
        if clean_word in synonym_to_mood:
            mood = synonym_to_mood[clean_word]
            specificity = synonym_specificity.get(clean_word, 1)
            # Don't add duplicate moods
            if not any(m[1] == mood for m in matches):
                matches.append((clean_word, mood, specificity, 1.0))
    
    return matches


def _find_fuzzy_matches(query_text, threshold=0.75):
    """
    Find close fuzzy matches for the query.
    Returns list of (synonym, mood, specificity_score, similarity) tuples.
    """
    query_lower = query_text.lower().strip()
    tokens = clean_text(query_lower).split()
    matches = []

    for synonym, mood in synonym_to_mood.items():
        # Compare both the whole query and individual tokens to catch typos (e.g., "dragg" → "drag")
        similarities = [_calculate_similarity(query_lower, synonym)]
        if tokens:
            similarities.append(max(_calculate_similarity(token, synonym) for token in tokens))

        similarity = max(similarities)
        if similarity >= threshold:
            specificity = synonym_specificity.get(synonym, 1)
            matches.append((synonym, mood, specificity, similarity))

    return matches


def _score_mood_matches(matches):
    """
    Score and rank mood matches.
    
    Scoring formula:
    - Base: specificity_score (higher for specific terms)
    - Multiplier: match_quality (1.0 for exact, <1.0 for fuzzy)
    - Bonus: multiple synonym matches for same mood
    
    Returns list of (mood, confidence_score) tuples, sorted by score.
    """
    mood_scores = {}
    best_match_quality = {}
    
    for synonym, mood, specificity, match_quality in matches:
        # Calculate base score
        score = specificity * match_quality

        # Add to existing score (rewards multiple matches for same mood)
        if mood in mood_scores:
            mood_scores[mood] += score * 0.5  # Diminishing returns for additional matches
        else:
            mood_scores[mood] = score

        # Track the highest quality match per mood (exact > fuzzy)
        best_match_quality[mood] = max(best_match_quality.get(mood, 0), match_quality)
    
    # Normalize to 0-1 confidence range
    if not mood_scores:
        return []
    
    max_score = max(mood_scores.values())
    normalized = []
    for mood, score in mood_scores.items():
        base_confidence = score / max_score if max_score else 0
        confidence = min(1.0, base_confidence * best_match_quality.get(mood, 1))
        normalized.append((mood, confidence))
    
    # Sort by confidence (highest first)
    normalized.sort(key=lambda x: x[1], reverse=True)
    return normalized


def resolve_mood_from_query(query_text, fuzzy=True, return_all=False):
    """
    Resolve a user query to the best-matching mood tag(s).
    
    Args:
        query_text: The full user query
        fuzzy: If True, use fuzzy matching for close matches (default: True)
        return_all: If True, return all scored moods; if False, return only top match
    
    Returns:
        If return_all=False: tuple of (mood_name, confidence)
        If return_all=True: list of (mood_name, confidence) tuples
        Returns (None, 0.0) or [] if no matches found
    """
    if not query_text:
        return (None, 0.0) if not return_all else []
    
    # Find all exact matches
    exact_matches = _find_exact_matches(query_text)
    
    # Find fuzzy matches if enabled and no exact matches
    fuzzy_matches = []
    if fuzzy and not exact_matches:
        fuzzy_matches = _find_fuzzy_matches(query_text, threshold=0.75)
    
    # Combine and score all matches
    all_matches = exact_matches + fuzzy_matches
    scored_moods = _score_mood_matches(all_matches)
    
    if return_all:
        return scored_moods
    
    # Return top match
    if scored_moods:
        return scored_moods[0]
    
    return (None, 0.0)


# Legacy function for backwards compatibility
def resolve_mood_from_phrase(phrase, fuzzy=True):
    """
    Legacy function - resolves a single phrase/word to a mood.
    Kept for backwards compatibility.
    """
    return resolve_mood_from_query(phrase, fuzzy=fuzzy, return_all=False)


# Legacy function for backwards compatibility  
def resolve_from_keywords(keywords, fuzzy=True):
    """
    Legacy function - resolves from list of keywords.
    Now joins keywords and uses main resolver.
    """
    if not keywords:
        return (None, 0.0)
    
    # Join keywords into a query and resolve
    query = " ".join(keywords)
    return resolve_mood_from_query(query, fuzzy=fuzzy, return_all=False)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCED MOOD RESOLVER - TEST SUITE")
    print("=" * 60)
    
    test_queries = [
        "I want to dance until I'm sweaty",
        "I'm feeling really low tonight",
        "I need somewhere gentle, I'm struggling",
        "somewhere contemplative and slow-paced",
        "playful but adult",
        "ecstatic and communal",
        "I need to move my body and feel alive",
        "somewhere with big group energy",
        "I want to feel connected to other people",
        "witchy and wild experiences",
        "drag and cabaret",
        "folk music and intimate vibes"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        
        # Get top match
        mood, confidence = resolve_mood_from_query(query)
        print(f"  → Top match: {mood} ({confidence:.0%} confidence)")
        
        # Show all scored matches
        all_matches = resolve_mood_from_query(query, return_all=True)
        if len(all_matches) > 1:
            print(f"  → Other matches:")
            for m, c in all_matches[1:4]:  # Show top 3 alternatives
                print(f"     - {m} ({c:.0%})")
