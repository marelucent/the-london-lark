"""
Distress Detection System for The London Lark

Detects crisis language in user queries and determines appropriate response level.
This is a critical safety feature that errs on the side of care.

IMPORTANT: This system should catch more than it misses. Better to offer
resources to someone who doesn't need them than to miss someone who does.
"""

# Tier 1: Immediate Crisis (Highest Priority)
# Keywords indicating active suicidal ideation or immediate danger
# Note: Include variants without apostrophes since users may type quickly
CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end it all", "ending it all",
    "end my life", "want to die", "better off dead", "can't go on", "cant go on",
    "cannot go on", "no point living", "going to hurt myself", "self harm",
    "self-harm", "cutting myself", "overdose", "jump off", "take pills",
    "slit my", "hang myself", "not worth living", "don't want to exist",
    "dont want to exist", "don't want to be here", "dont want to be here",
    "no reason to live", "end the pain", "make it stop", "can't do this anymore",
    "cant do this anymore", "goodbye cruel", "final goodbye", "last night on earth",
    "one last", "hurt myself", "harm myself", "take my life", "life is over",
    "see no way out", "only way out", "no point anymore", "whats the point"
]

# Tier 2: Severe Distress (High Priority)
# Keywords indicating serious struggle but not immediate crisis
# Note: Single words like "broken" will also match "heartbroken" - that's intentional
DISTRESS_KEYWORDS = [
    "breaking", "broken", "can't cope", "cannot cope", "falling apart", "give up",
    "giving up", "no hope", "hopeless", "worthless", "hate myself", "so alone",
    "completely alone", "nobody cares", "want to disappear", "want to vanish",
    "can't take it", "cannot take it", "too much to bear", "drowning",
    "at the end of my rope", "rock bottom", "lost everything", "nothing matters",
    "nobody would notice", "nobody would miss", "burden to everyone",
    "everyone hates me", "i'm nothing", "i'm a failure", "can't feel anything",
    "numb inside", "empty inside", "dead inside", "going through the motions",
    "barely surviving", "barely holding on", "losing my mind", "losing myself",
    "spiraling", "in a dark place", "darkness consuming", "no way out",
    "trapped", "suffocating", "can't breathe", "breaking down", "i feel broken",
    "completely broken", "totally broken", "feel like giving up", "ready to give up"
]

# Tier 3: Heavy Melancholy (Monitor)
# Keywords indicating deep sadness but within normal emotional range
# Note: These should NOT overlap with DISTRESS_KEYWORDS
HEAVY_MELANCHOLY_KEYWORDS = [
    "depressed", "depression", "really sad", "so sad", "deep sadness", "sad",
    "grief", "grieving", "mourning", "devastated",
    "lonely", "isolated", "lost", "adrift", "struggling",
    "anxious", "anxiety", "panic", "scared", "afraid", "worried",
    "tired of everything", "exhausted", "burnt out", "burnout",
    "stressed", "can't sleep", "sleepless", "insomnia",
    "crying", "can't stop crying", "tears", "hurt", "hurting",
    "miss them", "miss someone", "lost someone", "breakup", "divorce",
    "rejected", "abandoned", "betrayed", "aching", "melancholy", "low",
    "sorrow", "pain", "sadness", "heartbroken", "heartbreak", "blue", "down"
]


def detect_distress_level(query_text):
    """
    Analyze query text for distress indicators.

    This function checks user queries against tiered keyword lists
    to identify potential crisis situations. It errs on the side
    of care - better to flag a false positive than miss someone in need.

    Args:
        query_text: User's search query (string)

    Returns:
        tuple: (level, matched_keywords)
            level: "crisis" | "distress" | "melancholy" | "none"
            matched_keywords: list of matched keywords (for logging level only)
    """
    if not query_text:
        return ("none", [])

    query_lower = query_text.lower()

    # Check each tier in order of severity (most severe first)

    # Tier 1: Crisis - check for immediate danger keywords
    crisis_matches = [kw for kw in CRISIS_KEYWORDS if kw in query_lower]
    if crisis_matches:
        return ("crisis", crisis_matches)

    # Tier 2: Distress - check for severe struggle keywords
    distress_matches = [kw for kw in DISTRESS_KEYWORDS if kw in query_lower]
    if distress_matches:
        return ("distress", distress_matches)

    # Tier 3: Melancholy - check for heavy sadness keywords
    melancholy_matches = [kw for kw in HEAVY_MELANCHOLY_KEYWORDS if kw in query_lower]
    if melancholy_matches:
        return ("melancholy", melancholy_matches)

    return ("none", [])


def should_show_resources(distress_level):
    """
    Determine if crisis resources should be prominently displayed.

    Args:
        distress_level: "crisis" | "distress" | "melancholy" | "none"

    Returns:
        bool: True if resources should be prominently displayed
    """
    return distress_level in ["crisis", "distress"]


def should_show_venues(distress_level):
    """
    Determine if venues should be shown in the response.

    For crisis level, we show resources only - no venues.
    For all other levels, venues are appropriate.

    Args:
        distress_level: "crisis" | "distress" | "melancholy" | "none"

    Returns:
        bool: True if venues should be included in response
    """
    return distress_level != "crisis"


def get_venue_filter_mode(distress_level):
    """
    Determine how venues should be filtered based on distress level.

    Args:
        distress_level: "crisis" | "distress" | "melancholy" | "none"

    Returns:
        str: "gentle" for soft/refuge venues, "normal" for standard filtering
    """
    if distress_level == "distress":
        return "gentle"
    return "normal"
