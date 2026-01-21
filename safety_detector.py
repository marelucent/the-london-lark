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

# Import care voice functions from poetic_templates_v2 (HOLDING family)
try:
    from poetic_templates_v2 import (
        get_opening as get_care_opening,
        get_choices as get_care_choices,
        get_choice_preamble,
        get_resources_footer,
        get_care_voice
    )
    HAS_CARE_VOICES = True
except ImportError:
    HAS_CARE_VOICES = False
    get_care_voice = None

# Import shared need clusters for therapeutic spread drawing
try:
    from emotional_geography import (
        SHARED_NEEDS,
        get_therapeutic_spread_needs
    )
    HAS_SHARED_NEEDS = True
except ImportError:
    HAS_SHARED_NEEDS = False
    SHARED_NEEDS = {}

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
    # Sadness / LOW_HEAVY
    "i'm sad", "i am sad", "feeling sad", "feeling down", "feeling low",
    "feeling blue", "heavy heart", "heavy-hearted", "heartache",
    "a bit sad", "a bit low", "a bit down", "bit sad", "bit low", "bit down",
    "sad today", "sad tonight", "heavy today", "heavy tonight",
    "so sad", "really sad", "very sad", "feel sad",
    "struggling", "i'm struggling", "really struggling",
    # Loneliness / LONELY
    "lonely", "i'm lonely", "so lonely", "feeling lonely", "alone tonight",
    "feeling alone", "no one to talk to", "isolated", "disconnected",
    "need company", "need connection", "need people",
    "alone", "feel alone", "i feel alone", "so alone", "all alone",
    "on my own", "no one", "no friends", "by myself",
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
    "get out of my head", "clear my head",
    # ANGRY state triggers
    "angry", "i'm angry", "so angry", "feeling angry", "really angry",
    "furious", "so mad", "i'm mad", "rage", "raging", "fuming", "livid",
    "seething", "pissed off", "pissed", "frustrated", "enraged",
    # OVERWHELMED state triggers (additional)
    "i'm overwhelmed", "so overwhelmed", "feeling overwhelmed",
    "too much", "everything's too much", "everything is too much",
    "too loud", "everything's too loud", "sensory overload", "overstimulated",
    "panic", "panicking", "suffocating",
    # GRIEF state triggers
    "grieving", "i'm grieving", "mourning", "in mourning",
    "loss", "dealing with loss", "processing loss",
    "someone died", "lost someone", "lost my", "they're gone", "miss them",
    "bereavement", "after the funeral", "since the funeral",
    "grief", "full of grief", "heavy with grief"
}

# TIER 3: DISTRESS
# Clear emotional difficulty requiring gentle support
# Response: Warm preamble → Choice buttons → Arcana venues → Visible resources
DISTRESS_KEYWORDS = {
    # Struggling language
    "i'm struggling", "i am struggling", "really struggling",
    "can't cope", "cannot cope", "barely coping", "not coping",
    "struggling to cope", "don't know how to cope", "dont know how to cope",
    "falling apart", "breaking", "i'm breaking", "feel broken",
    "at my limit", "can't do this", "can't take it",
    # Intensified low mood (escalated from emotional tier)
    "feeling really low", "i'm feeling really low", "really low",
    "feeling so low", "so low today", "really down", "feeling really down",
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
# EMOTIONAL STATE DETECTION (Context-Aware Care Pathways)
# =============================================================================
# Detects which emotional state the user is in for context-aware offerings
# Instead of one fixed menu, detect state and show appropriate textures

# Trigger phrases for each emotional state
EMOTIONAL_STATE_TRIGGERS = {
    "LOW_HEAVY": {
        "feeling low", "feeling down", "struggling", "heavy", "sad", "down today",
        "rough day", "hard time", "hard day", "bad day", "difficult day",
        "a bit low", "bit low", "a bit sad", "bit sad", "a bit down", "bit down",
        "i'm sad", "i am sad", "feeling sad", "heavy heart", "heavy-hearted"
    },
    "ANGRY": {
        "angry", "furious", "so mad", "rage", "fuming", "livid", "seething",
        "pissed off", "pissed", "frustrated", "enraged", "raging"
    },
    "LONELY": {
        "lonely", "alone", "isolated", "no one", "on my own", "no friends",
        "feeling alone", "feel alone", "so lonely", "i'm lonely", "all alone",
        "disconnected", "by myself", "need company", "need connection"
    },
    "OVERWHELMED": {
        "overwhelmed", "too much", "can't cope", "cannot cope", "cant cope", "anxious",
        "everything's too loud", "drowning", "can't breathe", "cannot breathe", "cant breathe",
        "spiralling", "spiraling", "losing it", "too loud", "suffocating",
        "sensory overload", "overstimulated", "panic", "panicking"
    },
    "GRIEF": {
        "grieving", "mourning", "loss", "someone died", "lost someone",
        "they're gone", "miss them", "death of", "died", "passed away",
        "bereavement", "funeral", "lost my", "missing them", "grief"
    }
}

# =============================================================================
# STATE-SPECIFIC PREAMBLES
# =============================================================================

STATE_PREAMBLES = {
    "LOW_HEAVY": "That sounds like a lot to carry.",
    "ANGRY": "That fire deserves somewhere to go.",
    "LONELY": "I hear you. You don't have to be alone tonight.",
    "OVERWHELMED": "It's too loud, isn't it. Let's find somewhere softer.",
    "GRIEF": "I'm here. This is a tender place to be."
}

# =============================================================================
# TEXTURE → ARCANA POOL MAPPINGS
# =============================================================================
# Each texture maps to a need cluster and an arcana pool for drawing venues

TEXTURE_ARCANA_MAPPING = {
    "somewhere_still": {
        "texture": "Somewhere still",
        "icon": "⟡",
        "need_cluster": "to_rest",
        "arcana_pool": ["Contemplative & Meditative", "Grief & Grace", "Nostalgic / Vintage / Retro"]
    },
    "somewhere_soft_to_land": {
        "texture": "Somewhere soft to land",
        "icon": "⟡",
        "need_cluster": "to_rest",
        "arcana_pool": ["Contemplative & Meditative", "Grief & Grace", "Nostalgic / Vintage / Retro"]
    },
    "somewhere_your_body_can_move": {
        "texture": "Somewhere your body can move",
        "icon": "∴",
        "need_cluster": "to_move_through",
        "arcana_pool": ["Body-Based / Movement-Led", "Punchy / Protest", "Rant & Rapture"]
    },
    "somewhere_brave": {
        "texture": "Somewhere brave",
        "icon": "∞",
        "need_cluster": "to_rage_release",
        "arcana_pool": ["Punchy / Protest", "Rant & Rapture", "Body-Based / Movement-Led"]
    },
    "somewhere_loud_and_alive": {
        "texture": "Somewhere loud and alive",
        "icon": "⛧",
        "need_cluster": "to_let_loose",
        "arcana_pool": ["Late-Night Lark", "Big Night Out", "Cabaret & Glitter"]
    },
    "somewhere_others_have_felt_this_too": {
        "texture": "Somewhere others have felt this too",
        "icon": "△",
        "need_cluster": "to_be_with_others",
        "arcana_pool": ["Group Energy", "Queer Revelry", "Big Night Out"]
    },
    "somewhere_to_be_among_others": {
        "texture": "Somewhere to be among others",
        "icon": "⚘",
        "need_cluster": "to_be_held",
        "arcana_pool": ["Folk & Intimate", "Group Energy", "Word & Voice"]
    },
    "somewhere_that_feels_like_belonging": {
        "texture": "Somewhere that feels like belonging",
        "icon": "◎",
        "need_cluster": "to_feel_connected",
        "arcana_pool": ["Global Rhythms", "Spiritual / Sacred / Mystical", "Wonder & Awe"]
    },
    "somewhere_with_beauty_in_it": {
        "texture": "Somewhere with beauty in it",
        "icon": "✦",
        "need_cluster": "to_witness_beauty",
        "arcana_pool": ["Wonder & Awe", "Melancholic Beauty", "Romanticised London"]
    },
    "let_me_draw_for_you": {
        "texture": "Let me draw for you",
        "icon": "❦",
        "need_cluster": "therapeutic_spread",
        "arcana_pool": "therapeutic_spread"  # Special handling - draws from all care clusters
    }
}

# =============================================================================
# STATE-SPECIFIC TEXTURE OPTIONS
# =============================================================================
# Each state has 4 texture options tailored to that emotional need

STATE_TEXTURES = {
    "LOW_HEAVY": [
        "somewhere_still",
        "somewhere_your_body_can_move",
        "somewhere_to_be_among_others",
        "let_me_draw_for_you"
    ],
    "ANGRY": [
        "somewhere_brave",
        "somewhere_loud_and_alive",
        "somewhere_others_have_felt_this_too",
        "let_me_draw_for_you"
    ],
    "LONELY": [
        "somewhere_to_be_among_others",
        "somewhere_that_feels_like_belonging",
        "somewhere_with_beauty_in_it",
        "let_me_draw_for_you"
    ],
    "OVERWHELMED": [
        "somewhere_still",
        "somewhere_soft_to_land",
        "somewhere_with_beauty_in_it",
        "let_me_draw_for_you"
    ],
    "GRIEF": [
        "somewhere_still",
        "somewhere_with_beauty_in_it",
        "somewhere_to_be_among_others",
        "let_me_draw_for_you"
    ]
}

# =============================================================================
# ARCANA ICONS (for texture cards)
# =============================================================================

ARCANA_ICONS = {
    "Contemplative & Meditative": "⟡",   # Hermit (IX)
    "Grief & Grace": "✿",                 # Death (XIII)
    "Nostalgic / Vintage / Retro": "☾",  # Moon (XVIII)
    "Body-Based / Movement-Led": "∴",    # Hanged Man (XII)
    "Punchy / Protest": "∞",              # Strength (VIII)
    "Rant & Rapture": "⚖",                # Justice (XI)
    "Late-Night Lark": "⛧",               # Devil (XV)
    "Big Night Out": "↑",                 # Chariot (VII)
    "Cabaret & Glitter": "⚯",             # Lovers (VI)
    "Group Energy": "△",                  # Judgement (XX)
    "Queer Revelry": "◉",                 # World (XXI)
    "Folk & Intimate": "⚘",               # Empress (III)
    "Word & Voice": "≋",                  # Temperance (XIV)
    "Global Rhythms": "◎",                # Wheel (X)
    "Spiritual / Sacred / Mystical": "⚷", # Hierophant (V)
    "Wonder & Awe": "✦",                  # Star (XVII)
    "Melancholic Beauty": "↯",            # Tower (XVI)
    "Romanticised London": "❦",           # The Lark (✦)
    # Additional for completeness
    "Playful & Weird": "✵",               # Fool (0)
    "Curious Encounters": "✧",            # Magician (I)
    "Witchy & Wild": "☽",                 # High Priestess (II)
    "The Thoughtful Stage": "♛",          # Emperor (IV)
    "Comic Relief": "☀"                   # Sun (XIX)
}

# =============================================================================
# CARE PATHWAY CONFIGURATIONS (Legacy - kept for backward compatibility)
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
        "arcana": "therapeutic_spread"  # Draws from 3 different need clusters
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
        "arcana": "therapeutic_spread"  # Draws from 3 different need clusters
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


def detect_care_state(query_text: str) -> Tuple[str, List[str]]:
    """
    Detect which of the 5 emotional states the user is in.

    Args:
        query_text: The user's search query

    Returns:
        Tuple of (state, matched_keywords):
        - state: 'ANGRY' | 'LONELY' | 'OVERWHELMED' | 'GRIEF' | 'LOW_HEAVY'
        - matched_keywords: List of keywords that triggered the detection

    Priority order: GRIEF > OVERWHELMED > ANGRY > LONELY > LOW_HEAVY (default)
    (We check most specific emotional states first)
    """
    if not query_text or not query_text.strip():
        return ('LOW_HEAVY', [])

    text_normalised = _normalise_text(query_text)

    # Check states in priority order (most specific first)

    # GRIEF - check first as it's often very specific
    grief_matches = []
    for keyword in EMOTIONAL_STATE_TRIGGERS.get("GRIEF", set()):
        if keyword.lower() in text_normalised:
            grief_matches.append(keyword)
    if grief_matches:
        return ('GRIEF', grief_matches)

    # OVERWHELMED - specific anxiety/sensory language
    overwhelmed_matches = []
    for keyword in EMOTIONAL_STATE_TRIGGERS.get("OVERWHELMED", set()):
        if keyword.lower() in text_normalised:
            overwhelmed_matches.append(keyword)
    if overwhelmed_matches:
        return ('OVERWHELMED', overwhelmed_matches)

    # ANGRY - check before lonely as it's more actionable
    angry_matches = []
    for keyword in EMOTIONAL_STATE_TRIGGERS.get("ANGRY", set()):
        if keyword.lower() in text_normalised:
            angry_matches.append(keyword)
    if angry_matches:
        return ('ANGRY', angry_matches)

    # LONELY - specific isolation language
    lonely_matches = []
    for keyword in EMOTIONAL_STATE_TRIGGERS.get("LONELY", set()):
        if keyword.lower() in text_normalised:
            lonely_matches.append(keyword)
    if lonely_matches:
        return ('LONELY', lonely_matches)

    # LOW_HEAVY - check last (it's the default/catch-all)
    low_heavy_matches = []
    for keyword in EMOTIONAL_STATE_TRIGGERS.get("LOW_HEAVY", set()):
        if keyword.lower() in text_normalised:
            low_heavy_matches.append(keyword)
    if low_heavy_matches:
        return ('LOW_HEAVY', low_heavy_matches)

    # Default to LOW_HEAVY if no specific match (for Tier 2/3 queries)
    return ('LOW_HEAVY', [])


def get_state_preamble(state: str) -> str:
    """Get the state-specific preamble for the care pathway."""
    return STATE_PREAMBLES.get(state, STATE_PREAMBLES['LOW_HEAVY'])


def get_state_textures(state: str) -> List[dict]:
    """
    Get the 4 texture card configurations for a given emotional state.

    Returns list of dicts with:
    - texture_key: The key for this texture
    - texture: Display text (e.g., "Somewhere still")
    - icon: The arcana icon
    - arcana_pool: List of arcana to draw from
    """
    texture_keys = STATE_TEXTURES.get(state, STATE_TEXTURES['LOW_HEAVY'])
    textures = []

    for key in texture_keys:
        mapping = TEXTURE_ARCANA_MAPPING.get(key, {})
        textures.append({
            'texture_key': key,
            'texture': mapping.get('texture', key),
            'icon': mapping.get('icon', '✦'),
            'arcana_pool': mapping.get('arcana_pool', 'therapeutic_spread'),
            'need_cluster': mapping.get('need_cluster', '')
        })

    return textures


def get_texture_arcana_pool(texture_key: str) -> List[str]:
    """Get the arcana pool for a given texture key."""
    mapping = TEXTURE_ARCANA_MAPPING.get(texture_key, {})
    pool = mapping.get('arcana_pool', 'therapeutic_spread')
    if pool == 'therapeutic_spread':
        return 'therapeutic_spread'
    return pool


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
        # Use v2 care voice system (HOLDING family) if available
        if HAS_CARE_VOICES:
            preamble = get_care_opening(tier='distress')
            footer = get_resources_footer('distress')
        else:
            preamble = random.choice(TIER3_PREAMBLES)
            footer = "And if you need more than a place tonight, there are people who can hold that too."

        return {
            'show_venues': False,  # Don't auto-show venues, wait for choice
            'venue_filter': 'refuge',
            'show_soft_footer': False,
            'show_support_box': False,  # Now using care pathway instead
            'show_crisis_resources': False,
            'show_care_pathway': True,
            'care_choices': TIER3_CARE_CHOICES,
            'resources_footer': footer,
            'lark_preamble': preamble
        }

    elif tier == 'emotional':
        # Use v2 care voice system (HOLDING family) if available
        if HAS_CARE_VOICES:
            preamble = get_care_opening(tier='emotional')
        else:
            preamble = random.choice(TIER2_PREAMBLES)

        return {
            'show_venues': False,  # Don't auto-show venues, wait for choice
            'venue_filter': 'cosy',
            'show_soft_footer': True,  # Still show soft footer after venues
            'show_support_box': False,
            'show_crisis_resources': False,
            'show_care_pathway': True,
            'care_choices': TIER2_CARE_CHOICES,
            'resources_footer': None,
            'lark_preamble': preamble
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

    Uses v2 HOLDING family voice for warm presence.

    Returns dict with:
    - preamble: str (warm presence message)
    - choices: list (action buttons for user)
    """
    # Use v2 care voice system (HOLDING family - Null State) if available
    if HAS_CARE_VOICES:
        preamble = get_care_opening(tier='null')
    else:
        preamble = random.choice(NULL_STATE_PREAMBLES)

    return {
        'preamble': preamble,
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
# THERAPEUTIC SPREAD DRAWING (Shared Need Clusters)
# =============================================================================

def get_therapeutic_spread_arcana(tier: str = 'emotional') -> List[str]:
    """
    Get arcana for a therapeutic spread based on shared need clusters.

    Instead of drawing 3 venues from the same sad arcana, draw one from each
    of 3 different need clusters — three different medicines.

    Args:
        tier: 'emotional' (Tier 2) or 'distress' (Tier 3)

    Returns:
        List of 3 arcana names (one from each need cluster)
    """
    if not HAS_SHARED_NEEDS:
        # Fallback to existing therapeutic arcana
        return random.sample(THERAPEUTIC_ARCANA, min(3, len(THERAPEUTIC_ARCANA)))

    # Get the need keys for this tier
    if tier == 'distress':
        # Tier 3: to_rest, to_be_held, to_witness_beauty
        needs = ['to_rest', 'to_be_held', 'to_witness_beauty']
    else:
        # Tier 2: to_be_held, to_rest, to_feel_joy (softer mix)
        needs = ['to_be_held', 'to_rest', 'to_feel_joy']

    # Pick one random arcana from each need cluster
    arcana_spread = []
    used_arcana = set()

    for need in needs:
        cluster = SHARED_NEEDS.get(need, [])
        if cluster:
            # Filter out already used arcana for variety
            available = [a for a in cluster if a not in used_arcana]
            if available:
                chosen = random.choice(available)
                arcana_spread.append(chosen)
                used_arcana.add(chosen)
            elif cluster:
                # All used, but still pick one
                arcana_spread.append(random.choice(cluster))

    return arcana_spread


def get_care_pathway_arcana_spread(tier: str = 'emotional') -> dict:
    """
    Get the full therapeutic spread configuration for care pathways.

    Returns dict with:
    - arcana_spread: List of 3 arcana (one from each need cluster)
    - needs_used: List of need names used for the spread
    - description: Human-readable description of the spread
    """
    if tier == 'distress':
        needs = ['to_rest', 'to_be_held', 'to_witness_beauty']
        description = "Rest, connection, and beauty — three different medicines."
    else:
        needs = ['to_be_held', 'to_rest', 'to_feel_joy']
        description = "Connection, rest, and a spark of joy."

    arcana_spread = get_therapeutic_spread_arcana(tier)

    return {
        'arcana_spread': arcana_spread,
        'needs_used': needs,
        'description': description
    }


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
