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
import random
from typing import Tuple, List, Optional, Dict

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
# Response: Warm preamble → Choice buttons → Arcana venues → Soft footer
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
    "want to be around people", "need to be around people", "don't want to be alone",
    # Expanded keywords (from brief)
    "rough week", "hard time", "overwhelmed",
    "anxious", "stressed", "burned out", "burnout",
    "bit lost", "lost lately", "feeling lost",
    "need to get out of my head", "stuck", "feeling stuck", "restless",
    "get out of my head", "clear my head"
}

# TIER 3: DISTRESS
# Clear emotional difficulty requiring gentle support
# Response: Warm preamble → Choice buttons → Arcana venues → Visible resources
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
    "too much", "can't breathe", "drowning",
    "spiralling", "spiraling", "losing it", "losing my mind",
    # Expanded keywords (from brief)
    "breaking down", "at my limit",
    "nothing helps", "so tired of this", "exhausted by everything",
    "don't know what to do anymore"
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
# CARE PATHWAY CONFIGURATIONS
# =============================================================================

# Tier 2 (Emotional) preambles - rotated randomly
TIER2_PREAMBLES = [
    "That sounds like a lot to carry.",
    "I hear you. Let's find the right place for tonight.",
    "I'm glad you told me."
]

# Tier 3 (Distress) preambles - rotated randomly
TIER3_PREAMBLES = [
    "I hear you. I'm with you.",
    "That sounds heavy. Let me be your compass tonight.",
    "You don't need to know what you need — I can hold the map."
]

# Null state preambles - rotated randomly
NULL_STATE_PREAMBLES = [
    "I'm not quite sure what you're after — but I'd love to find it with you.",
    "That's not ringing a bell, but let's wander and see what calls.",
    "Tell me more? Or I could draw a card and see what finds you.",
    "Hmm, I'm not certain — but I have a few guesses."
]

# Tier 2 care pathway choices - maps button labels to arcana
TIER2_CARE_CHOICES = [
    {
        "label": "Somewhere quiet",
        "arcana": ["Contemplative & Meditative"]  # Hermit
    },
    {
        "label": "Somewhere to move",
        "arcana": ["Body-Based / Movement-Led"]  # Hanged Man
    },
    {
        "label": "Something to make me laugh",
        "arcana": ["Comic Relief", "Playful & Weird"]  # Sun, Fool
    },
    {
        "label": "Let's wander",
        "arcana": "therapeutic_random"  # Random draw from therapeutic arcana
    }
]

# Tier 3 care pathway choices - maps button labels to arcana
TIER3_CARE_CHOICES = [
    {
        "label": "Somewhere quiet to sit with it",
        "arcana": ["Contemplative & Meditative", "Grief & Grace", "Melancholic Beauty"]  # Hermit, Death, Tower
    },
    {
        "label": "Somewhere to let it out",
        "arcana": ["Body-Based / Movement-Led", "Rant & Rapture"]  # Hanged Man, Justice
    },
    {
        "label": "Somewhere to be held by others",
        "arcana": ["Group Energy", "Folk & Intimate"]  # Judgement, Empress
    },
    {
        "label": "Draw for me",
        "arcana": "therapeutic_random"  # Random draw from therapeutic arcana
    }
]

# Therapeutic arcana for random draws (excludes energetic/chaotic arcana)
THERAPEUTIC_ARCANA = [
    "Contemplative & Meditative",  # Hermit
    "Grief & Grace",               # Death
    "Body-Based / Movement-Led",   # Hanged Man
    "Word & Voice",                # Temperance
    "Spiritual / Sacred / Mystical",  # Hierophant
    "Group Energy",                # Judgement
    "Melancholic Beauty",          # Tower
    "Wonder & Awe",                # Star
    "Folk & Intimate"              # Empress
]

# Excluded from therapeutic random: Devil, Chariot, Magician, Fool, Lovers, World, Lark


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
    - show_care_pathway: bool (whether to show choice buttons)
    - care_choices: list | None (choice button configurations)
    - resources_footer: str | None (warm resources message for Tier 3)
    """

    if tier == 'crisis':
        return {
            'show_venues': True,  # Optional gentle venue after resources
            'venue_filter': 'refuge',
            'show_soft_footer': False,
            'show_support_box': False,
            'show_crisis_resources': True,
            'show_care_pathway': False,  # Crisis gets immediate resources, not choices
            'care_choices': None,
            'resources_footer': None,
            'lark_preamble': (
                "I hear you, petal. Before anything else — there are people "
                "who want to help hold what you're carrying right now."
            )
        }

    elif tier == 'distress':
        return {
            'show_venues': False,  # Don't auto-show venues, wait for choice
            'venue_filter': 'refuge',
            'show_soft_footer': False,
            'show_support_box': False,  # Now using care pathway instead
            'show_crisis_resources': False,
            'show_care_pathway': True,
            'care_choices': TIER3_CARE_CHOICES,
            'resources_footer': (
                "And if you need more than a place tonight, there are people who can hold that too."
            ),
            'lark_preamble': random.choice(TIER3_PREAMBLES)
        }

    elif tier == 'emotional':
        return {
            'show_venues': False,  # Don't auto-show venues, wait for choice
            'venue_filter': 'cosy',
            'show_soft_footer': True,  # Still show soft footer after venues
            'show_support_box': False,
            'show_crisis_resources': False,
            'show_care_pathway': True,
            'care_choices': TIER2_CARE_CHOICES,
            'resources_footer': None,
            'lark_preamble': random.choice(TIER2_PREAMBLES)
        }

    elif tier == 'aesthetic':
        return {
            'show_venues': True,
            'venue_filter': None,  # Normal venue matching
            'show_soft_footer': False,
            'show_support_box': False,
            'show_crisis_resources': False,
            'show_care_pathway': False,
            'care_choices': None,
            'resources_footer': None,
            'lark_preamble': None
        }

    else:  # None — no emotional signal detected
        return {
            'show_venues': True,
            'venue_filter': None,
            'show_soft_footer': False,
            'show_support_box': False,
            'show_crisis_resources': False,
            'show_care_pathway': False,
            'care_choices': None,
            'resources_footer': None,
            'lark_preamble': None
        }


def get_null_state_config() -> dict:
    """
    Get configuration for null state (no match found).

    Returns dict with:
    - preamble: str (warm presence message)
    - choices: list (action buttons for user)
    """
    return {
        'preamble': random.choice(NULL_STATE_PREAMBLES),
        'choices': [
            {"label": "Draw a card for me", "action": "draw_random"},
            {"label": "Show me the deck", "action": "browse"},
            {"label": "Let me try again", "action": "clear_input"}
        ]
    }


def get_therapeutic_arcana() -> List[str]:
    """Return the list of therapeutic arcana for random draws."""
    return THERAPEUTIC_ARCANA.copy()


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
