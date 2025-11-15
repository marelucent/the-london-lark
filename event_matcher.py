#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Event Matcher

"""
The London Lark - Event Matcher
Matches live events to user filters (mood, location, time, budget).
Parallel to venue_matcher.py but for time-specific events.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

def load_events() -> List[Dict]:
    """Load events from cache"""
    try:
        with open('events_cache.json', 'r') as f:
            events = json.load(f)
        return events
    except FileNotFoundError:
        print("⚠️  No events cache found. Run event_fetcher.py first.")
        return []

def match_events(filters: Dict) -> List[Dict]:
    """
    Match events to user filters.
    Similar to venue_matcher.py but for time-specific events.

    Args:
        filters: Dict with keys:
            - mood: Mood category (e.g., "Folk & Intimate")
            - location: Area/neighborhood (e.g., "Camden", "North London")
            - time: Time filter (e.g., "tonight", "this weekend", "Friday")
            - budget: Budget level ("low", "high")
            - group: Group size ("solo", "group")

    Returns:
        List of matching events (up to 3)
    """
    mood = filters.get("mood")
    location = filters.get("location")
    time = filters.get("time")
    budget = filters.get("budget")
    group = filters.get("group")

    events = load_events()
    matches = []

    # Filter out past events
    today = datetime.now().date()
    events = [e for e in events if datetime.strptime(e['date'], '%Y-%m-%d').date() >= today]

    for event in events:
        # Time filtering
        if time:
            event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()

            if time.lower() == "tonight":
                if event_date != today:
                    continue
            elif time.lower() == "tomorrow":
                tomorrow = today + timedelta(days=1)
                if event_date != tomorrow:
                    continue
            elif time.lower() in ["weekend", "this weekend"]:
                # Next weekend (Saturday/Sunday)
                days_until_saturday = (5 - today.weekday()) % 7
                if days_until_saturday == 0:
                    days_until_saturday = 7
                next_saturday = today + timedelta(days=days_until_saturday)
                next_sunday = next_saturday + timedelta(days=1)
                if event_date not in [next_saturday, next_sunday]:
                    continue
            elif time.lower() in ["friday", "saturday", "sunday"]:
                # Next occurrence of that day
                target_day = {"friday": 4, "saturday": 5, "sunday": 6}[time.lower()]
                days_ahead = (target_day - today.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                target_date = today + timedelta(days=days_ahead)
                if event_date != target_date:
                    continue

        # Mood filtering
        if mood:
            event_mood_tags = event.get('mood_tags', [])
            if mood not in event_mood_tags:
                # Check genre tags as fallback
                genre_tags = event.get('genre_tags', [])
                genre_str = ' '.join(genre_tags).lower()

                # Basic mood-to-genre mapping
                mood_genre_map = {
                    'Folk & Intimate': ['folk', 'acoustic', 'singer-songwriter'],
                    'Queer Revelry': ['queer', 'drag', 'lgbtq', 'cabaret'],
                    'Cabaret & Glitter': ['cabaret', 'drag', 'burlesque'],
                    'Comic Relief': ['comedy', 'standup', 'improv'],
                    'The Thoughtful Stage': ['theatre', 'drama', 'new writing'],
                    'Melancholic Beauty': ['jazz', 'classical', 'ambient'],
                    'Playful & Weird': ['experimental', 'weird', 'alternative'],
                }

                expected_genres = mood_genre_map.get(mood, [])
                if not any(g in genre_str for g in expected_genres):
                    continue

        # Location filtering
        if location:
            event_area = event.get('area', '').lower()
            location_lower = location.lower()

            # Check direct match or broader region
            if location_lower not in event_area:
                # Check if location is a broader region
                region_map = {
                    'north london': ['camden', 'islington', 'kentish town', 'archway', 'highgate'],
                    'south london': ['brixton', 'peckham', 'tooting', 'streatham', 'camberwell'],
                    'east london': ['shoreditch', 'hackney', 'dalston', 'bethnal green', 'whitechapel'],
                    'west london': ['notting hill', 'shepherds bush', 'chiswick', 'hammersmith'],
                }

                if location_lower in region_map:
                    if not any(area in event_area for area in region_map[location_lower]):
                        continue
                else:
                    continue

        # Budget filtering
        if budget:
            price_range = event.get('price_range', '').lower()
            price_min = event.get('price_min', 0)

            if budget == "low":
                # Free or cheap (under £10)
                if price_range not in ['free', '£'] and price_min > 10:
                    continue
            elif budget == "high":
                # User wants to splurge, no filtering needed
                pass

        # Group compatibility
        if group:
            genre_tags = event.get('genre_tags', [])
            event_name = event.get('event_name', '').lower()

            if group == "solo":
                # Filter out explicitly group-focused events
                if any(word in event_name for word in ['party', 'festival', 'rave', 'massive']):
                    continue
            elif group == "group":
                # Prefer events that work for groups
                # No specific filtering needed
                pass

        # Event passed all filters
        matches.append(event)

    # Return top 3 matches
    return matches[:3]


if __name__ == '__main__':
    print("="*70)
    print("  LONDON LARK - EVENT MATCHER TEST")
    print("="*70)
    print()

    # Test 1: Tonight
    print("Test 1: Events tonight")
    filters = {'mood': None, 'location': None, 'time': 'tonight', 'budget': None, 'group': None}
    matches = match_events(filters)
    print(f"Found {len(matches)} events:")
    for m in matches:
        print(f"  - {m['event_name']} at {m['venue_name']} ({m['time']})")
    print()

    # Test 2: Folk in Camden
    print("Test 2: Folk events in Camden")
    filters = {'mood': 'Folk & Intimate', 'location': 'Camden', 'time': None, 'budget': None, 'group': None}
    matches = match_events(filters)
    print(f"Found {len(matches)} events:")
    for m in matches:
        print(f"  - {m['event_name']} on {m['date']} at {m['time']}")
    print()

    # Test 3: Free events
    print("Test 3: Free/cheap events")
    filters = {'mood': None, 'location': None, 'time': None, 'budget': 'low', 'group': None}
    matches = match_events(filters)
    print(f"Found {len(matches)} events:")
    for m in matches:
        print(f"  - {m['event_name']} ({m['price_range']})")
