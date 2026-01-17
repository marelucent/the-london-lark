#!/usr/bin/env python3
# 🕊️ safety_detector.py

"""
The London Lark — Safety & Emotional Triage

Detects emotional state in user queries and returns appropriate tier:
- AESTHETIC: Melancholic moods that are artistic/intentional (normal venues)
- EMOTIONAL: Genuine sadness/loneliness (warm venues + soft footer)
- DISTRESS: Struggling/breaking (gentle venues + visible support)
- CRISIS: Immediate danger signals (resources first, venue optional)

Philosophy: "I'm lonely" should get cosy venues and maybe a soft footer — 
not a suicide hotline. Tiered, gentle, human.
"""

import re
from typing import Tuple, List, Optional

# =============================================================================
# KEYWORD DICTIONARIES
# =============================================================================

# TIER 1: AESTHETIC MELANCHOLY
# These are artistic/intentional mood requests — NOT distress signals
# Response: Normal venue matching, no safety intervention
AESTHETIC_KEYWORDS = {
    # Mood descriptors (artistic intent)
    "melancholic", "melancholy", "bittersweet", "wistful", "nostalgic",
    "atmospheric", "moody", "contemplative", "pensive", "reflective",
    "sombre", "somber", "haunting", "ethereal", "dreamy",
    # Venue-seeking language
    "somewhere sad", "beautiful sadness", "aching", "longing",
    "tender", "gentle", "quiet", "peaceful", "still",
    # Grief & Grace arcana (intentional grief spaces)
    "grief cafe", "death cafe", "grief circle", "grief tending",
    "mortality", "bereavement space", "grief support group"
}

# TIER 2: EMOTIONAL WEIGHT
# Genuine emotional difficulty, but not crisis
# Response: Warm/cosy venues + soft footer linking to resources
EMOTIONAL_KEYWORDS = {
    # Sadness
    "i'm sad", "i am sad", "feeling sad", "feeling down", "feeling low",
    "feeling blue", "heavy heart", "heavy-hearted", "heartache",
    "a bit sad", "a bit low", "a bit down", "bit sad", "bit low", "bit down",
    # Loneliness  
    "lonely", "i'm lonely", "so lonely", "feeling lonely", "alone tonight",
    "feeling alone", "no one to talk to", "isolated", "disconnected",
    "need company", "need connection", "need people",
    # Tiredness/exhaustion (emotional, not physical)
    "exhausted", "drained", "worn out", "burnt out", "burned out",
    "running on empty", "nothing left", "so tired", "emotionally tired",
    # General low mood
    "bad day", "rough day", "hard day", "difficult day", "tough time",
    "going through a lot", "not myself", "off today", "struggling a bit",
    "need comfort", "need some comfort", "need somewhere gentle", "need somewhere quiet",
    "feeling fragile", "fragile today", "tender today",
    "want to be around people", "need to be around people", "don't want to be alone"
}

# TIER 3: DISTRESS
# Clear emotional difficulty requiring gentle support
# Response: Gentle refuge venues + visible (but warm) support box
DISTRESS_KEYWORDS = {
    # Struggling language
    "i'm struggling", "i am struggling", "really struggling", 
    "can't cope", "cannot cope", "barely coping", "not coping",
    "falling apart", "breaking", "i'm breaking", "feel broken",
    "at my limit", "can't do this", "can't take it",
    # Hopelessness (but not crisis-level)
    "hopeless", "feeling hopeless", "no hope", "what's the point",
    "pointless", "meaningless", "empty inside", "numb",
    # Help-seeking
    "i need help", "need support", "don't know what to do",
    "don't know where to turn", "nowhere to turn",
    # Overwhelm
    "overwhelmed", "too much", "can't breathe", "drowning",
    "spiralling", "spiraling", "losing it", "losing my mind"
}

# TIER 4: CRISIS
# Immediate danger signals — requires crisis resources FIRST
# Response: Crisis resources prominently, then optional gentle venue
CRISIS_KEYWORDS = {
    # Self-harm ideation
    "suicide", "suicidal", "kill myself", "end it", "end it all",
    "don't want to be here", "don't want to exist", "want to die",
    "better off dead", "better off without me", "no reason to live",
    # Self-harm
    "hurt myself", "harm myself", "self harm", "self-harm", "cutting",
    "want to hurt", "want to cut",
    # Immediate crisis
    "going to do something", "can't go on", "can't continue",
    "this is it", "goodbye", "final", "last night", "ending things",
    # Danger
    "in danger", "not safe", "unsafe", "emergency"
}

# =============================================================================
# DETECTION FUNCTIONS
# =============================================================================

def _normalise_text(text: str) -> str:
    """Lowercase, strip extra whitespace, normalise apostrophes"""
    text = text.lower().strip()
    text = text.replace("'", "'").replace("'", "'")  # Normalise apostrophes
    text = re.sub(r'\s+', ' ', text)  # Collapse whitespace
    return text


def _check_keywords(text: str, keywords: set) -> List[str]:
    """Check if any keywords appear in text. Returns list of matches."""
    text_normalised = _normalise_text(text)
    matches = []
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Check for exact phrase match (handles multi-word keywords)
        if keyword_lower in text_normalised:
            matches.append(keyword)
    
    return matches


def detect_emotional_state(query_text: str) -> Tuple[Optional[str], List[str]]:
    """
    Analyse user query for emotional state.
    
    Args:
        query_text: The user's search query
        
    Returns:
        Tuple of (tier, matched_keywords):
        - tier: 'crisis' | 'distress' | 'emotional' | 'aesthetic' | None
        - matched_keywords: List of keywords that triggered the detection
        
    Priority order: crisis > distress > emotional > aesthetic
    (We check most serious first)
    """
    if not query_text or not query_text.strip():
        return (None, [])
    
    # Check tiers in order of severity (most serious first)
    
    # TIER 4: CRISIS — check first, highest priority
    crisis_matches = _check_keywords(query_text, CRISIS_KEYWORDS)
    if crisis_matches:
        return ('crisis', crisis_matches)
    
    # TIER 3: DISTRESS
    distress_matches = _check_keywords(query_text, DISTRESS_KEYWORDS)
    if distress_matches:
        return ('distress', distress_matches)
    
    # TIER 2: EMOTIONAL
    emotional_matches = _check_keywords(query_text, EMOTIONAL_KEYWORDS)
    if emotional_matches:
        return ('emotional', emotional_matches)
    
    # TIER 1: AESTHETIC (only flag if detected, otherwise None)
    aesthetic_matches = _check_keywords(query_text, AESTHETIC_KEYWORDS)
    if aesthetic_matches:
        return ('aesthetic', aesthetic_matches)
    
    # No emotional signals detected
    return (None, [])


def get_tier_response_config(tier: Optional[str]) -> dict:
    """
    Get response configuration for a given tier.
    
    Returns dict with:
    - show_venues: bool (whether to show venue results)
    - venue_filter: str | None (e.g., 'refuge' for gentle venues)
    - show_soft_footer: bool (subtle resources link)
    - show_support_box: bool (visible but warm support)
    - show_crisis_resources: bool (prominent crisis info)
    - lark_preamble: str | None (what the Lark says before venues)
    """
    
    if tier == 'crisis':
        return {
            'show_venues': True,  # Optional gentle venue after resources
            'venue_filter': 'refuge',
            'show_soft_footer': False,
            'show_support_box': False,
            'show_crisis_resources': True,
            'lark_preamble': (
                "I hear you, petal. Before anything else — there are people "
                "who want to help hold what you're carrying right now."
            )
        }
    
    elif tier == 'distress':
        return {
            'show_venues': True,
            'venue_filter': 'refuge',
            'show_soft_footer': False,
            'show_support_box': True,
            'show_crisis_resources': False,
            'lark_preamble': (
                "That sounds really hard. I'm here — and so are others, "
                "if you need them."
            )
        }
    
    elif tier == 'emotional':
        return {
            'show_venues': True,
            'venue_filter': 'cosy',  # Warm, gentle venues (not necessarily refuge)
            'show_soft_footer': True,
            'show_support_box': False,
            'show_crisis_resources': False,
            'lark_preamble': None  # No special preamble, just warm venues
        }
    
    elif tier == 'aesthetic':
        return {
            'show_venues': True,
            'venue_filter': None,  # Normal venue matching
            'show_soft_footer': False,
            'show_support_box': False,
            'show_crisis_resources': False,
            'lark_preamble': None
        }
    
    else:  # None — no emotional signal detected
        return {
            'show_venues': True,
            'venue_filter': None,
            'show_soft_footer': False,
            'show_support_box': False,
            'show_crisis_resources': False,
            'lark_preamble': None
        }


# =============================================================================
# REFUGE VENUE HELPERS
# =============================================================================

# Keywords to identify potential refuge venues in existing database
REFUGE_VENUE_INDICATORS = {
    # Venue types
    "library", "reading room", "bookshop", "cafe", "café", "garden",
    "church", "chapel", "meeting house", "quaker", "meditation",
    "community centre", "community center", "drop-in",
    # Mood indicators
    "quiet", "peaceful", "gentle", "contemplative", "sanctuary",
    "refuge", "haven", "rest", "breathe", "calm", "still",
    # Activity types  
    "meditation", "mindfulness", "sitting", "reflection",
    "grief", "support", "holding space"
}

COSY_VENUE_INDICATORS = {
    # Warm, friendly venues (broader than refuge)
    "cosy", "cozy", "intimate", "warm", "friendly", "welcoming",
    "folk", "acoustic", "candlelit", "fireplace", "snug",
    "community", "inclusive", "low-key", "relaxed", "gentle"
}


def is_potential_refuge_venue(venue: dict) -> bool:
    """
    Check if a venue might work as a gentle refuge.
    Looks at blurb, whisper, moods, genres, and name.
    """
    # Combine all text fields for searching
    searchable_text = " ".join([
        venue.get('name', ''),
        venue.get('blurb', ''),
        venue.get('whisper', ''),
        venue.get('tone_notes', ''),
        " ".join(venue.get('moods', [])),
        " ".join(venue.get('genres', []))
    ]).lower()
    
    # Check for refuge indicators
    for indicator in REFUGE_VENUE_INDICATORS:
        if indicator in searchable_text:
            return True
    
    # Check arcana — some are naturally gentle
    gentle_arcana = {
        'Contemplative & Meditative',
        'Grief & Grace', 
        'Folk & Intimate',
        'Spiritual / Sacred / Mystical'
    }
    if venue.get('arcana') in gentle_arcana:
        return True
    
    return False


def is_cosy_venue(venue: dict) -> bool:
    """
    Check if a venue has warm, cosy energy.
    Broader than refuge — for emotional tier responses.
    """
    # First check if it's a refuge (refuge is a subset of cosy)
    if is_potential_refuge_venue(venue):
        return True
    
    # Combine text fields
    searchable_text = " ".join([
        venue.get('name', ''),
        venue.get('blurb', ''),
        venue.get('whisper', ''),
        " ".join(venue.get('moods', []))
    ]).lower()
    
    # Check for cosy indicators
    for indicator in COSY_VENUE_INDICATORS:
        if indicator in searchable_text:
            return True
    
    return False


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🕊️  SAFETY DETECTOR — TEST SUITE")
    print("=" * 60)
    
    test_queries = [
        # Aesthetic (Tier 1) — normal venue flow
        ("somewhere melancholic and beautiful", "aesthetic"),
        ("I want a bittersweet evening", "aesthetic"),
        ("nostalgic jazz vibes", "aesthetic"),
        ("grief cafe in London", "aesthetic"),
        
        # Emotional (Tier 2) — warm venues + soft footer
        ("I'm feeling sad tonight", "emotional"),
        ("lonely and need somewhere to go", "emotional"),
        ("had a rough day", "emotional"),
        ("feeling a bit low", "emotional"),
        
        # Distress (Tier 3) — refuge venues + support box
        ("I'm really struggling", "distress"),
        ("can't cope anymore", "distress"),
        ("feeling hopeless", "distress"),
        ("I'm falling apart", "distress"),
        
        # Crisis (Tier 4) — resources first
        ("I want to end it", "crisis"),
        ("don't want to be here anymore", "crisis"),
        ("thinking about suicide", "crisis"),
        
        # No signal — normal venue flow
        ("jazz clubs in Soho", None),
        ("drag shows this weekend", None),
        ("somewhere with good vibes", None),
    ]
    
    print("\n" + "-" * 60)
    passed = 0
    failed = 0
    
    for query, expected_tier in test_queries:
        detected_tier, keywords = detect_emotional_state(query)
        status = "✓" if detected_tier == expected_tier else "✗"
        
        if detected_tier == expected_tier:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status} Query: \"{query}\"")
        print(f"  Expected: {expected_tier}")
        print(f"  Detected: {detected_tier}")
        if keywords:
            print(f"  Keywords: {keywords}")
    
    print("\n" + "-" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
