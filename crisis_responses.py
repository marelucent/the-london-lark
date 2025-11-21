"""
Crisis Response Templates for The London Lark

These templates provide caring, non-patronizing responses for users
who may be in distress. The Lark's voice remains warm and poetic,
while acknowledging her limits and pointing to human support.

IMPORTANT: These responses must never be dismissive. They should
always offer both acknowledgment and concrete resources.
"""

import random

# Crisis resources for UK users
CRISIS_RESOURCES = {
    "emergency": {
        "name": "Emergency Services",
        "number": "999",
        "description": "For immediate danger to life",
        "icon": "emergency"
    },
    "samaritans": {
        "name": "Samaritans",
        "number": "116 123",
        "description": "24/7, free to call, here to listen",
        "icon": "phone"
    },
    "crisis_text": {
        "name": "Crisis Text Line",
        "number": "SHOUT to 85258",
        "description": "Free, 24/7 text support",
        "icon": "text"
    },
    "calm": {
        "name": "CALM",
        "number": "0800 58 58 58",
        "description": "5pm-midnight, for men in crisis",
        "icon": "phone"
    },
    "papyrus": {
        "name": "PAPYRUS",
        "number": "0800 068 4141",
        "description": "For under 35s, prevention of young suicide",
        "icon": "phone"
    }
}

# Response templates organized by distress level
CRISIS_RESPONSE_TEMPLATES = {
    "crisis": {
        "intros": [
            "I hear something in your words that makes me want to reach beyond venues tonight, petal.",
            "Your words carry a weight that venues alone cannot hold, love.",
            "I hear you, and I need you to hear me: you matter, and there are humans trained to help carry this.",
            "Oh, love. I'm just a bird with a map of London's tender places, but what you're carrying needs human hands tonight.",
            "I hear the heaviness in what you're asking, petal. Before I show you anywhere, I need to show you something else first.",
            "Something in your words has made me stop, love. What you're feeling deserves more than venues right now."
        ],
        "resources_header": "Please, reach out right now:",
        "closings": [
            "I'm here, but I'm not enough for all pain. Let these humans help hold what you're carrying.",
            "I'll still be here when you're ready to explore, but right now, let someone hold this with you.",
            "The city will wait for you, petal. But these humans are ready to listen right now.",
            "I'm a guide to places, but you need a guide to this moment. These people are trained to help.",
            "London's gentle corners will still be here. For now, please let someone hear you."
        ]
    },

    "distress": {
        "intros": [
            "I sense you're carrying something heavy tonight, petal.",
            "There's a tenderness in your words that makes me want to offer more than just venues.",
            "I hear struggle in what you're seeking. Let me offer both places and people who can help.",
            "Your words tell me you're going through something difficult, love. Let me be gentle with you tonight.",
            "I hear you, petal. Sometimes we need both a place to rest and someone to talk to.",
            "There's an ache in what you're asking. I want to tend to that as well as find you somewhere soft to land."
        ],
        "resources_header": "If you're struggling, these humans are here for you:",
        "closings": [
            "And if you still want a place to sit with this feeling, I have some gentle suggestions below.",
            "Below, I've found you some tender places. But the humans above are always there if you need them.",
            "I've chosen some soft landing spots for you below. And the resources above are there whenever you need.",
            "Let me show you some gentle refuges, love. And remember, the people above are just a call away.",
            "Here are some quiet corners of London that might hold you tonight. The humans above can hold you too."
        ],
        "venue_intro": "Here are some gentle places that might embrace you tonight:"
    },

    "melancholy": {
        "footer_note": "If you're struggling more than usual tonight, <a href='/resources'>support resources</a> are available, petal.",
        "footer_note_plain": "If you're struggling more than usual tonight, support resources are available at /resources, petal."
    }
}


def get_crisis_intro(distress_level):
    """
    Get a random intro message for the given distress level.

    Args:
        distress_level: "crisis" | "distress" | "melancholy" | "none"

    Returns:
        str: An intro message, or None if no special intro needed
    """
    if distress_level in ["crisis", "distress"]:
        intros = CRISIS_RESPONSE_TEMPLATES[distress_level]["intros"]
        return random.choice(intros)
    return None


def get_crisis_closing(distress_level):
    """
    Get a random closing message for the given distress level.

    Args:
        distress_level: "crisis" | "distress" | "melancholy" | "none"

    Returns:
        str: A closing message, or None if no special closing needed
    """
    if distress_level in ["crisis", "distress"]:
        closings = CRISIS_RESPONSE_TEMPLATES[distress_level]["closings"]
        return random.choice(closings)
    return None


def get_resources_header(distress_level):
    """
    Get the resources header text for the given distress level.

    Args:
        distress_level: "crisis" | "distress"

    Returns:
        str: The resources header text
    """
    if distress_level in CRISIS_RESPONSE_TEMPLATES:
        return CRISIS_RESPONSE_TEMPLATES[distress_level].get("resources_header", "Support resources:")
    return "Support resources:"


def get_melancholy_footer():
    """
    Get the footer note for melancholy-level responses.

    Returns:
        dict: Contains both HTML and plain text versions of the footer
    """
    return {
        "html": CRISIS_RESPONSE_TEMPLATES["melancholy"]["footer_note"],
        "plain": CRISIS_RESPONSE_TEMPLATES["melancholy"]["footer_note_plain"]
    }


def get_crisis_resources(distress_level):
    """
    Get the list of crisis resources to display.

    For crisis level, return all resources with emergency first.
    For distress level, return support lines (not emergency).

    Args:
        distress_level: "crisis" | "distress"

    Returns:
        list: List of resource dictionaries
    """
    if distress_level == "crisis":
        # All resources, emergency first
        return [
            CRISIS_RESOURCES["emergency"],
            CRISIS_RESOURCES["samaritans"],
            CRISIS_RESOURCES["crisis_text"],
            CRISIS_RESOURCES["calm"],
            CRISIS_RESOURCES["papyrus"]
        ]
    elif distress_level == "distress":
        # Support lines, no emergency
        return [
            CRISIS_RESOURCES["samaritans"],
            CRISIS_RESOURCES["crisis_text"],
            CRISIS_RESOURCES["calm"]
        ]
    return []


def build_crisis_response(distress_level, venues=None):
    """
    Build a complete crisis response structure.

    Args:
        distress_level: "crisis" | "distress" | "melancholy" | "none"
        venues: Optional list of venue recommendations

    Returns:
        dict: Complete response structure with all needed components
    """
    if distress_level == "crisis":
        return {
            "type": "crisis",
            "intro": get_crisis_intro("crisis"),
            "show_resources": True,
            "resources_header": get_resources_header("crisis"),
            "resources": get_crisis_resources("crisis"),
            "resources_priority": "urgent",
            "show_venues": False,
            "closing": get_crisis_closing("crisis"),
            "resources_link": "/resources"
        }

    elif distress_level == "distress":
        return {
            "type": "distress",
            "intro": get_crisis_intro("distress"),
            "show_resources": True,
            "resources_header": get_resources_header("distress"),
            "resources": get_crisis_resources("distress"),
            "resources_priority": "important",
            "show_venues": True,
            "venue_filter": "refuge",  # Filter for gentle refuge venues only
            "venue_intro": CRISIS_RESPONSE_TEMPLATES["distress"]["venue_intro"],
            "closing": get_crisis_closing("distress"),
            "resources_link": "/resources"
        }

    elif distress_level == "melancholy":
        return {
            "type": "melancholy",
            "intro": None,
            "show_resources": False,
            "show_venues": True,
            "footer_note": get_melancholy_footer()
        }

    else:  # "none"
        return {
            "type": "none",
            "intro": None,
            "show_resources": False,
            "show_venues": True
        }
