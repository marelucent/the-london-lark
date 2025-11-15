#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Event Data Fetcher

"""
The London Lark - Event Data Pipeline
Fetches live event listings from various London sources.

Current sources:
- Mock data generator (for testing/demo)
- Eventbrite API (requires token - see EVENT_PIPELINE_SETUP.md)
- Skiddle API (requires token - see EVENT_PIPELINE_SETUP.md)

Future sources:
- Resident Advisor scraper
- Dice scraper
- Venue-specific scrapers
"""

import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

# API Configuration (set these to enable real data fetching)
EVENTBRITE_TOKEN = None  # Set to your Eventbrite OAuth token
SKIDDLE_API_KEY = None   # Set to your Skiddle API key

# London coordinates for geo-filtering
LONDON_LAT = 51.5074
LONDON_LON = -0.1278
LONDON_RADIUS = 20  # km

class EventFetcher:
    """Fetches events from various sources"""

    def __init__(self, use_mock=True):
        self.use_mock = use_mock
        self.eventbrite_token = EVENTBRITE_TOKEN
        self.skiddle_key = SKIDDLE_API_KEY

    def fetch_all_events(self) -> List[Dict]:
        """Fetch events from all available sources"""
        events = []

        if self.use_mock:
            print("📝 Using mock event data (no API keys configured)")
            events.extend(self._generate_mock_events())
        else:
            if self.eventbrite_token:
                print("🎫 Fetching from Eventbrite...")
                events.extend(self._fetch_eventbrite())

            if self.skiddle_key:
                print("🎸 Fetching from Skiddle...")
                events.extend(self._fetch_skiddle())

            if not events:
                print("⚠️  No API keys configured, falling back to mock data")
                events.extend(self._generate_mock_events())

        return events

    def _fetch_eventbrite(self) -> List[Dict]:
        """Fetch events from Eventbrite API"""
        events = []

        try:
            # Eventbrite search endpoint
            url = "https://www.eventbriteapi.com/v3/events/search/"

            params = {
                'location.latitude': LONDON_LAT,
                'location.longitude': LONDON_LON,
                'location.within': f'{LONDON_RADIUS}km',
                'start_date.range_start': datetime.now().isoformat(),
                'start_date.range_end': (datetime.now() + timedelta(days=14)).isoformat(),
                'categories': '103,105,110,113',  # Music, performing arts, film & media, cultural
                'expand': 'venue',
            }

            headers = {
                'Authorization': f'Bearer {self.eventbrite_token}'
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for event in data.get('events', []):
                    events.append(self._normalize_eventbrite(event))
                print(f"✓ Fetched {len(events)} events from Eventbrite")
            else:
                print(f"✗ Eventbrite API error: {response.status_code}")

        except Exception as e:
            print(f"✗ Eventbrite fetch failed: {e}")

        return events

    def _fetch_skiddle(self) -> List[Dict]:
        """Fetch events from Skiddle API"""
        events = []

        try:
            url = "https://www.skiddle.com/api/v1/events/"

            params = {
                'api_key': self.skiddle_key,
                'latitude': LONDON_LAT,
                'longitude': LONDON_LON,
                'radius': LONDON_RADIUS,
                'minDate': datetime.now().strftime('%Y-%m-%d'),
                'maxDate': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
                'eventcode': 'LIVE',  # Live music events
                'limit': 100
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for event in data.get('results', []):
                    events.append(self._normalize_skiddle(event))
                print(f"✓ Fetched {len(events)} events from Skiddle")
            else:
                print(f"✗ Skiddle API error: {response.status_code}")

        except Exception as e:
            print(f"✗ Skiddle fetch failed: {e}")

        return events

    def _normalize_eventbrite(self, event: Dict) -> Dict:
        """Normalize Eventbrite event to our schema"""
        venue = event.get('venue', {})

        return {
            'event_id': f"eventbrite_{event['id']}",
            'source': 'eventbrite',
            'event_name': event['name']['text'],
            'venue_name': venue.get('name', 'TBC'),
            'matched_venue_id': None,  # Will be matched later
            'date': event['start']['local'][:10],
            'time': event['start']['local'][11:16],
            'area': venue.get('address', {}).get('localized_area_display', 'London'),
            'genre_tags': [],  # Extract from category
            'mood_tags': [],  # To be inferred
            'price_range': self._infer_price_range(event.get('is_free', False)),
            'price_min': 0 if event.get('is_free') else None,
            'price_max': None,
            'url': event['url'],
            'description': event.get('description', {}).get('text', '')[:200],
            'fetched_at': datetime.now().isoformat()
        }

    def _normalize_skiddle(self, event: Dict) -> Dict:
        """Normalize Skiddle event to our schema"""
        return {
            'event_id': f"skiddle_{event['id']}",
            'source': 'skiddle',
            'event_name': event['eventname'],
            'venue_name': event.get('venue', {}).get('name', 'TBC'),
            'matched_venue_id': None,
            'date': event['date'][:10],
            'time': event.get('openingtimes', {}).get('doorsopen', '20:00'),
            'area': event.get('venue', {}).get('town', 'London'),
            'genre_tags': [event.get('EventCode', '').lower()],
            'mood_tags': [],
            'price_range': self._infer_price_range(float(event.get('MinPrice', 0)) == 0),
            'price_min': float(event.get('MinPrice', 0)),
            'price_max': float(event.get('MaxPrice', 0)),
            'url': event['link'],
            'description': event.get('description', '')[:200],
            'fetched_at': datetime.now().isoformat()
        }

    def _infer_price_range(self, is_free: bool) -> str:
        """Infer price range symbol"""
        if is_free:
            return 'Free'
        return '££'  # Default assumption

    def _generate_mock_events(self) -> List[Dict]:
        """Generate realistic mock event data for testing"""
        mock_events = [
            {
                'event_id': 'mock_001',
                'source': 'mock',
                'event_name': 'An Evening of English Folk Songs',
                'venue_name': 'Cecil Sharp House',
                'matched_venue_id': None,
                'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                'time': '19:30',
                'area': 'Camden',
                'genre_tags': ['folk', 'acoustic', 'traditional'],
                'mood_tags': ['Folk & Intimate'],
                'price_range': '££',
                'price_min': 12,
                'price_max': 15,
                'url': 'https://cecilsharphouse.org',
                'description': 'Traditional English folk songs in an intimate setting',
                'fetched_at': datetime.now().isoformat()
            },
            {
                'event_id': 'mock_002',
                'source': 'mock',
                'event_name': 'Late Night Jazz Session',
                'venue_name': 'The Jazz Café',
                'matched_venue_id': None,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': '21:00',
                'area': 'Camden',
                'genre_tags': ['jazz', 'live music', 'late night'],
                'mood_tags': ['Melancholic Beauty', 'Late-Night Lark'],
                'price_range': '££',
                'price_min': 15,
                'price_max': 20,
                'url': 'https://thejazzcafelondon.com',
                'description': 'Intimate jazz performances under low lights',
                'fetched_at': datetime.now().isoformat()
            },
            {
                'event_id': 'mock_003',
                'source': 'mock',
                'event_name': 'Queer Cabaret Night',
                'venue_name': 'The Glory',
                'matched_venue_id': None,
                'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'time': '20:00',
                'area': 'Haggerston',
                'genre_tags': ['cabaret', 'drag', 'queer'],
                'mood_tags': ['Queer Revelry', 'Cabaret & Glitter'],
                'price_range': '£',
                'price_min': 8,
                'price_max': 12,
                'url': 'https://www.theglory.co',
                'description': 'A night of glitter, performance art, and chosen family warmth',
                'fetched_at': datetime.now().isoformat()
            },
            {
                'event_id': 'mock_004',
                'source': 'mock',
                'event_name': 'Experimental Theatre: The Quiet Room',
                'venue_name': 'Camden People\'s Theatre',
                'matched_venue_id': None,
                'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                'time': '19:00',
                'area': 'Camden',
                'genre_tags': ['theatre', 'experimental', 'fringe'],
                'mood_tags': ['Curious Encounters', 'The Thoughtful Stage'],
                'price_range': '££',
                'price_min': 10,
                'price_max': 14,
                'url': 'https://cptheatre.co.uk',
                'description': 'Intimate experimental performance about silence and connection',
                'fetched_at': datetime.now().isoformat()
            },
            {
                'event_id': 'mock_005',
                'source': 'mock',
                'event_name': 'Community Open Mic Night',
                'venue_name': 'The Sound Lounge',
                'matched_venue_id': None,
                'date': (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d'),
                'time': '19:30',
                'area': 'Tooting',
                'genre_tags': ['open mic', 'acoustic', 'community'],
                'mood_tags': ['Folk & Intimate', 'Salon & Spark'],
                'price_range': 'Free',
                'price_min': 0,
                'price_max': 0,
                'url': 'https://thesoundlounge.org.uk',
                'description': 'Grassroots music and spoken word in a welcoming vegan café',
                'fetched_at': datetime.now().isoformat()
            }
        ]

        print(f"✓ Generated {len(mock_events)} mock events for testing")
        return mock_events


if __name__ == '__main__':
    print("="*70)
    print("  LONDON LARK - EVENT FETCHER TEST")
    print("="*70)
    print()

    fetcher = EventFetcher(use_mock=True)
    events = fetcher.fetch_all_events()

    print(f"\n✓ Total events fetched: {len(events)}")

    if events:
        print("\nSample event:")
        print(json.dumps(events[0], indent=2))

        # Save to file
        with open('events_cache.json', 'w') as f:
            json.dump(events, f, indent=2)
        print(f"\n✓ Saved events to events_cache.json")
