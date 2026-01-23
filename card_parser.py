#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Card Parser - Extracts venue cards and draws from Lark Mind responses

Parses [[CARD:venue_name]] and [[DRAW:type]] markup and enriches
responses with venue data for frontend rendering.
"""

import re
import json
import os
import random
from typing import Optional

# =============================================================================
# VENUE DATABASE
# =============================================================================

_venue_cache = None

def load_venues():
    """Load and cache venue database"""
    global _venue_cache
    if _venue_cache is not None:
        return _venue_cache

    possible_paths = [
        'lark_venues_clean.json',
        os.path.join(os.path.dirname(__file__), 'lark_venues_clean.json'),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                venues = json.load(f)
                # Index by name (case-insensitive)
                _venue_cache = {v['name'].lower(): v for v in venues}
                return _venue_cache

    _venue_cache = {}
    return _venue_cache


def get_venue(name: str) -> Optional[dict]:
    """
    Look up a venue by name (case-insensitive).
    Supports partial matching - if exact match fails, tries starts-with match.
    """
    venues = load_venues()
    name_lower = name.lower().strip()

    # Try exact match first
    if name_lower in venues:
        return venues[name_lower]

    # Try starts-with match (handles "Treadwell's Bookshop" → "Treadwell's Bookshop - Witchcraft Classes")
    for venue_name, venue in venues.items():
        if venue_name.startswith(name_lower):
            return venue

    # Try contains match as last resort
    for venue_name, venue in venues.items():
        if name_lower in venue_name:
            return venue

    return None


def get_random_venues(count: int = 1, arcana: str = None) -> list:
    """Get random venues, optionally filtered by arcana"""
    venues = load_venues()
    venue_list = list(venues.values())

    if arcana:
        venue_list = [v for v in venue_list if v.get('arcana') == arcana]

    if not venue_list:
        return []

    return random.sample(venue_list, min(count, len(venue_list)))


def get_adjacent_venues(primary_arcana: str, count: int = 2) -> list:
    """Get venues from adjacent arcana for triad draws"""
    from emotional_geography import TAROT_ADJACENCY

    adjacent_arcana = TAROT_ADJACENCY.get(primary_arcana, [])
    if not adjacent_arcana:
        return get_random_venues(count)

    venues = load_venues()
    result = []

    # Pick from different adjacent arcana
    for i, arcana in enumerate(adjacent_arcana[:count]):
        arcana_venues = [v for v in venues.values() if v.get('arcana') == arcana]
        if arcana_venues:
            result.append(random.choice(arcana_venues))

    return result


# =============================================================================
# PARSING
# =============================================================================

# Pattern for [[CARD:venue_name]]
CARD_PATTERN = re.compile(r'\[\[CARD:([^\]]+)\]\]')

# Pattern for [[DRAW:type]]
DRAW_PATTERN = re.compile(r'\[\[DRAW:(\w+)\]\]')


def parse_response(text: str) -> dict:
    """
    Parse a Lark Mind response for card and draw markers.

    Returns:
        {
            "segments": [
                {"type": "text", "content": "..."},
                {"type": "card", "venue": {...}, "display": "revealed"},
                {"type": "draw", "draw_type": "single", "venues": [...], "display": "facedown"},
                {"type": "text", "content": "..."}
            ],
            "raw_text": "original text without markers",
            "has_cards": True/False,
            "has_draws": True/False
        }
    """
    segments = []
    has_cards = False
    has_draws = False

    # Find all markers with positions
    markers = []

    for match in CARD_PATTERN.finditer(text):
        markers.append({
            'type': 'card',
            'start': match.start(),
            'end': match.end(),
            'venue_name': match.group(1).strip()
        })

    for match in DRAW_PATTERN.finditer(text):
        markers.append({
            'type': 'draw',
            'start': match.start(),
            'end': match.end(),
            'draw_type': match.group(1).strip().lower()
        })

    # Sort markers by position
    markers.sort(key=lambda m: m['start'])

    # Build segments
    current_pos = 0

    for marker in markers:
        # Add text before marker
        if marker['start'] > current_pos:
            text_segment = text[current_pos:marker['start']].strip()
            if text_segment:
                segments.append({
                    'type': 'text',
                    'content': text_segment
                })

        # Process marker
        if marker['type'] == 'card':
            venue = get_venue(marker['venue_name'])
            if venue:
                has_cards = True
                segments.append({
                    'type': 'card',
                    'venue': _format_venue(venue),
                    'display': 'revealed'
                })
            else:
                # Venue not found - include as text with note
                segments.append({
                    'type': 'text',
                    'content': f"*{marker['venue_name']}*"
                })

        elif marker['type'] == 'draw':
            has_draws = True
            draw_venues = _get_draw_venues(marker['draw_type'])
            segments.append({
                'type': 'draw',
                'draw_type': marker['draw_type'],
                'venues': [_format_venue(v) for v in draw_venues],
                'display': 'facedown'
            })

        current_pos = marker['end']

    # Add remaining text
    if current_pos < len(text):
        text_segment = text[current_pos:].strip()
        if text_segment:
            segments.append({
                'type': 'text',
                'content': text_segment
            })

    # If no markers found, treat entire text as single segment
    if not segments:
        segments.append({
            'type': 'text',
            'content': text
        })

    # Build raw text (without markers)
    raw_text = CARD_PATTERN.sub('', text)
    raw_text = DRAW_PATTERN.sub('', raw_text)
    raw_text = re.sub(r'\n{3,}', '\n\n', raw_text).strip()

    return {
        'segments': segments,
        'raw_text': raw_text,
        'has_cards': has_cards,
        'has_draws': has_draws
    }


def _format_venue(venue: dict) -> dict:
    """Format venue data for frontend consumption"""
    return {
        'name': venue.get('name', 'Unknown'),
        'arcana': venue.get('arcana', 'Romanticised London'),
        'location': venue.get('location', 'London'),
        'whisper': venue.get('whisper', ''),
        'blurb': venue.get('blurb', ''),
        'website': venue.get('url', ''),
        'moods': venue.get('moods', [])
    }


def _get_draw_venues(draw_type: str) -> list:
    """Get venues for a draw based on type"""
    if draw_type == 'single':
        return get_random_venues(1)

    elif draw_type == 'triad':
        # Card 1: Random (fate)
        primary = get_random_venues(1)
        if not primary:
            return []

        # Cards 2-3: Adjacent arcana
        primary_arcana = primary[0].get('arcana', 'Romanticised London')
        adjacent = get_adjacent_venues(primary_arcana, 2)

        return primary + adjacent

    elif draw_type == 'shuffle':
        return get_random_venues(6)

    elif draw_type == 'spread':
        return get_random_venues(5)

    else:
        # Default to single
        return get_random_venues(1)


# =============================================================================
# CLI TEST
# =============================================================================

if __name__ == '__main__':
    # Test parsing
    test_response = """*The veil is thin tonight.*

[[CARD:Treadwell's Bookshop]]

Does that land? Or are you after something more... feral?"""

    print("Test 1: Single card")
    print("-" * 40)
    result = parse_response(test_response)
    print(json.dumps(result, indent=2))

    print("\nTest 2: Draw")
    print("-" * 40)
    test_draw = """*Then let's see what finds you...*

[[DRAW:triad]]"""

    result = parse_response(test_draw)
    print(json.dumps(result, indent=2))

    print("\nTest 3: Text only")
    print("-" * 40)
    test_text = "*That's a tender thing to want.* Tell me more — what would make tonight feel right?"
    result = parse_response(test_text)
    print(json.dumps(result, indent=2))
