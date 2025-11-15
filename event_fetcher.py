#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Event Data Fetcher with Strict Filtering

"""
The London Lark - Event Data Pipeline
Fetches live event listings from various London sources with strict filtering
to preserve the Lark's curatorial vision: niche, indie, underground culture.

Sources:
- Mock data (realistic Eventbrite-format data for testing)
- Eventbrite API (set EVENTBRITE_TOKEN below)
- Future: Skiddle, Resident Advisor, Dice
"""

import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import re

# Import filtering configuration
from event_config import *

# ============================================================================
# API CONFIGURATION
# ============================================================================

# SET YOUR EVENTBRITE TOKEN HERE (see EVENTBRITE_GUIDE.md for setup)
EVENTBRITE_TOKEN = None  # <-- ADD YOUR TOKEN HERE when ready

# Example: EVENTBRITE_TOKEN = "ABC123XYZ..."

# ============================================================================
# FILTERING ENGINE
# ============================================================================

class EventbriteFilter:
    """Applies strict filtering to preserve the Lark's soul"""

    def __init__(self):
        self.stats = {
            'total_fetched': 0,
            'passed_filters': 0,
            'rejected_category': 0,
            'rejected_genre': 0,
            'rejected_venue': 0,
            'rejected_price': 0,
            'rejected_location': 0,
        }

    def should_include_event(self, event: Dict) -> Tuple[bool, str]:
        """
        Check if event passes all filters.
        Returns: (include: bool, rejection_reason: str)
        """
        # Extract event data
        name = event.get('name', {}).get('text', '').lower()
        description = event.get('description', {}).get('text', '').lower()
        venue = event.get('venue', {})
        venue_name = venue.get('name', '').lower()
        venue_capacity = venue.get('capacity', 0)
        category_id = event.get('category_id', '')

        # Filter 1: Category whitelist
        if category_id and category_id not in EVENTBRITE_CATEGORIES_WHITELIST:
            self.stats['rejected_category'] += 1
            return False, f"Category {category_id} not in whitelist"

        # Filter 2: Genre keywords (exclude overrides include)
        if self._has_excluded_keywords(name, description):
            self.stats['rejected_genre'] += 1
            return False, "Contains excluded keywords"

        if not self._has_included_keywords(name, description):
            # Check if it's at a whitelisted venue (can skip genre check)
            if not self._is_whitelisted_venue(venue_name):
                self.stats['rejected_genre'] += 1
                return False, "No included genre keywords and not at whitelisted venue"

        # Filter 3: Venue filtering
        if venue_capacity and venue_capacity > MAX_VENUE_CAPACITY:
            self.stats['rejected_venue'] += 1
            return False, f"Venue capacity {venue_capacity} exceeds {MAX_VENUE_CAPACITY}"

        if self._has_excluded_venue_keywords(venue_name):
            self.stats['rejected_venue'] += 1
            return False, "Venue has excluded keywords"

        # Filter 4: Location (must be in London)
        location = venue.get('address', {})
        city = location.get('city', '').lower()
        region = location.get('region', '').lower()

        if not self._is_london_location(city, region):
            self.stats['rejected_location'] += 1
            return False, "Location not in London"

        # Passed all filters!
        self.stats['passed_filters'] += 1
        return True, "Passed all filters"

    def _has_excluded_keywords(self, name: str, description: str) -> bool:
        """Check if event contains any excluded keywords"""
        combined = f"{name} {description}"
        return any(keyword in combined for keyword in GENRE_KEYWORDS_EXCLUDE)

    def _has_included_keywords(self, name: str, description: str) -> bool:
        """Check if event contains any included genre keywords"""
        combined = f"{name} {description}"
        return any(keyword in combined for keyword in GENRE_KEYWORDS_INCLUDE)

    def _is_whitelisted_venue(self, venue_name: str) -> bool:
        """Check if venue is in our curated list"""
        # Load curated venues
        try:
            with open('lark_venues_structured.json', 'r') as f:
                curated_venues = json.load(f)
                curated_names = [v.get('name', '').lower() for v in curated_venues]
                return any(curated in venue_name or venue_name in curated
                          for curated in curated_names)
        except:
            return False

    def _has_excluded_venue_keywords(self, venue_name: str) -> bool:
        """Check if venue has excluded keywords"""
        return any(keyword in venue_name for keyword in VENUE_KEYWORDS_EXCLUDE)

    def _is_london_location(self, city: str, region: str) -> bool:
        """Check if location is in London"""
        london_indicators = ['london', 'greater london']
        return any(indicator in city or indicator in region
                  for indicator in london_indicators)

    def infer_mood_tags(self, event: Dict) -> Tuple[List[str], float]:
        """
        Infer mood tags from event data.
        Returns: (mood_tags: List[str], confidence: float)
        """
        name = event.get('name', {}).get('text', '').lower()
        description = event.get('description', {}).get('text', '').lower()
        combined = f"{name} {description}"

        mood_scores = {}

        # Score each mood based on keyword matches
        for mood, keywords in MOOD_INFERENCE_MAP.items():
            score = 0
            matches = []

            for keyword in keywords:
                if keyword in combined:
                    score += 1
                    matches.append(keyword)

            if score > 0:
                # Normalize score (0-1 range)
                confidence = min(score / 3, 1.0)  # Max 3 keywords for full confidence
                mood_scores[mood] = {'confidence': confidence, 'matches': matches}

        # Select moods above confidence threshold
        selected_moods = []
        max_confidence = 0

        for mood, data in mood_scores.items():
            if data['confidence'] >= MOOD_CONFIDENCE_THRESHOLD:
                selected_moods.append(mood)
                max_confidence = max(max_confidence, data['confidence'])

        return selected_moods, max_confidence

    def classify_price(self, is_free: bool, price_min: float, price_max: float) -> str:
        """Classify event price into tiers"""
        if is_free or price_min == 0:
            return 'Free'
        elif price_min <= PRICE_LOW_MAX:
            return '£'
        elif price_min <= PRICE_MEDIUM_MAX:
            return '££'
        elif price_min <= PRICE_HIGH_MAX:
            return '£££'
        else:
            return '££££'

    def extract_area(self, venue: Dict) -> Tuple[str, str]:
        """
        Extract area/neighborhood from venue.
        Returns: (neighborhood, region)
        """
        address = venue.get('address', {})
        localized_area = address.get('localized_area_display', '')
        city = address.get('city', '')

        # Try to extract neighborhood
        neighborhood = localized_area or city

        # Map to region
        neighborhood_lower = neighborhood.lower()
        region = 'London'  # Default

        for area, reg in AREA_TO_REGION.items():
            if area in neighborhood_lower:
                region = reg
                break

        return neighborhood, region

    def get_stats_report(self) -> str:
        """Generate filtering statistics report"""
        total = self.stats['total_fetched']
        if total == 0:
            return "No events processed yet."

        passed = self.stats['passed_filters']
        pass_rate = (passed / total * 100) if total > 0 else 0

        report = f"""
=== EVENTBRITE FILTERING STATISTICS ===

Total events fetched: {total}
Passed all filters: {passed} ({pass_rate:.1f}%)

Rejection reasons:
  - Wrong category: {self.stats['rejected_category']}
  - Genre mismatch: {self.stats['rejected_genre']}
  - Venue too large/excluded: {self.stats['rejected_venue']}
  - Price too high: {self.stats['rejected_price']}
  - Location not London: {self.stats['rejected_location']}
        """
        return report

# ============================================================================
# EVENT FETCHER
# ============================================================================

class EventFetcher:
    """Fetches and filters events from various sources"""

    def __init__(self, use_mock=True):
        self.use_mock = use_mock
        self.eventbrite_token = EVENTBRITE_TOKEN
        self.filter = EventbriteFilter()

    def fetch_all_events(self) -> List[Dict]:
        """Fetch events from all available sources"""
        events = []

        if self.use_mock or not self.eventbrite_token:
            if not self.eventbrite_token:
                print("📝 No Eventbrite token configured - using realistic mock data")
                print("   (See EVENTBRITE_GUIDE.md to get a token)\n")
            else:
                print("📝 Using mock data (set use_mock=False for real API)\n")

            events.extend(self._generate_filtered_mock_events())
        else:
            print("🎫 Fetching from Eventbrite API...\n")
            events.extend(self._fetch_and_filter_eventbrite())

        return events

    def _fetch_and_filter_eventbrite(self) -> List[Dict]:
        """Fetch events from Eventbrite API and apply filters"""
        events = []

        try:
            url = "https://www.eventbriteapi.com/v3/events/search/"

            # Date range: next 14 days
            start_date = datetime.now() + timedelta(hours=MIN_HOURS_AHEAD)
            end_date = start_date + timedelta(days=FETCH_DAYS_AHEAD)

            params = {
                'location.latitude': LONDON_LAT,
                'location.longitude': LONDON_LON,
                'location.within': f'{LONDON_RADIUS}km',
                'start_date.range_start': start_date.isoformat(),
                'start_date.range_end': end_date.isoformat(),
                'categories': ','.join(EVENTBRITE_CATEGORIES_WHITELIST),
                'expand': 'venue,category',
                'page_size': MAX_EVENTS_PER_REQUEST,
            }

            headers = {
                'Authorization': f'Bearer {self.eventbrite_token}'
            }

            response = requests.get(url, params=params, headers=headers, timeout=API_TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                raw_events = data.get('events', [])

                print(f"✓ Fetched {len(raw_events)} events from Eventbrite")
                self.filter.stats['total_fetched'] = len(raw_events)

                # Apply filters
                for event in raw_events:
                    should_include, reason = self.filter.should_include_event(event)

                    if should_include:
                        normalized = self._normalize_eventbrite(event)
                        events.append(normalized)

                print(f"✓ {len(events)} events passed filters\n")
                print(self.filter.get_stats_report())

            else:
                print(f"✗ Eventbrite API error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")

        except Exception as e:
            print(f"✗ Eventbrite fetch failed: {e}")

        return events

    def _normalize_eventbrite(self, event: Dict) -> Dict:
        """Normalize Eventbrite event to our schema with filtering"""
        venue = event.get('venue', {})
        name = event.get('name', {}).get('text', '')
        description = event.get('description', {}).get('text', '')

        # Infer mood tags
        mood_tags, mood_confidence = self.filter.infer_mood_tags(event)

        # Extract area
        neighborhood, region = self.filter.extract_area(venue)

        # Classify price
        is_free = event.get('is_free', False)
        # Eventbrite doesn't always provide price in search results
        price_min = 0 if is_free else 10  # Estimate
        price_max = 0 if is_free else 15

        price_range = self.filter.classify_price(is_free, price_min, price_max)

        # Extract genre tags from description/name
        genre_tags = self._extract_genre_tags(name, description)

        return {
            'event_id': f"eventbrite_{event['id']}",
            'source': 'eventbrite',
            'event_name': name,
            'venue_name': venue.get('name', 'TBC'),
            'matched_venue_id': None,
            'date': event['start']['local'][:10],
            'time': event['start']['local'][11:16],
            'area': neighborhood,
            'region': region,
            'genre_tags': genre_tags,
            'mood_tags': mood_tags,
            'mood_confidence': round(mood_confidence, 2),
            'price_range': price_range,
            'price_min': price_min,
            'price_max': price_max,
            'url': event['url'],
            'description': description[:200],
            'fetched_at': datetime.now().isoformat(),
            'filter_passed': True
        }

    def _extract_genre_tags(self, name: str, description: str) -> List[str]:
        """Extract genre tags from event name and description"""
        combined = f"{name} {description}".lower()
        tags = []

        # Simple keyword extraction
        genre_keywords = [
            'folk', 'jazz', 'blues', 'acoustic', 'indie',
            'experimental', 'electronic', 'techno', 'ambient',
            'theatre', 'cabaret', 'drag', 'comedy',
            'poetry', 'spoken word', 'dance', 'circus',
        ]

        for keyword in genre_keywords:
            if keyword in combined and keyword not in tags:
                tags.append(keyword)

        return tags[:5]  # Max 5 tags

    def _generate_filtered_mock_events(self) -> List[Dict]:
        """
        Generate realistic mock data that demonstrates filtered Eventbrite results.
        These events look like real Eventbrite API responses that passed all filters.
        """
        mock_events = [
            # Folk & Intimate
            {
                'event_name': 'An Evening of English Folk Songs',
                'venue_name': 'Cecil Sharp House',
                'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                'time': '19:30',
                'area': 'Camden Town',
                'region': 'North London',
                'genre_tags': ['folk', 'acoustic', 'traditional'],
                'mood_tags': ['Folk & Intimate'],
                'mood_confidence': 0.95,
                'price_range': '££',
                'price_min': 12,
                'price_max': 15,
                'url': 'https://www.eventbrite.com/e/folk-songs-tickets',
                'description': 'Traditional English folk songs in an intimate candlelit setting. Featuring singer-songwriters and acoustic instruments.',
                'source': 'eventbrite_mock',
                'event_id': 'mock_eventbrite_001',
                'matched_venue_id': None,
                'fetched_at': datetime.now().isoformat(),
                'filter_passed': True
            },

            # Queer Revelry
            {
                'event_name': 'Queer Cabaret Spectacular',
                'venue_name': 'The Glory',
                'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'time': '20:00',
                'area': 'Haggerston',
                'region': 'East London',
                'genre_tags': ['cabaret', 'drag', 'queer'],
                'mood_tags': ['Queer Revelry', 'Cabaret & Glitter'],
                'mood_confidence': 1.0,
                'price_range': '£',
                'price_min': 8,
                'price_max': 12,
                'url': 'https://www.eventbrite.com/e/queer-cabaret-tickets',
                'description': 'A night of fierce drag performances, glittering costumes, and chosen family warmth. LGBTQ+ celebration with sequins.',
                'source': 'eventbrite_mock',
                'event_id': 'mock_eventbrite_002',
                'matched_venue_id': None,
                'fetched_at': datetime.now().isoformat(),
                'filter_passed': True
            },

            # The Thoughtful Stage
            {
                'event_name': 'The Quiet Room - Experimental Theatre',
                'venue_name': 'Camden People\'s Theatre',
                'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                'time': '19:00',
                'area': 'Camden Town',
                'region': 'North London',
                'genre_tags': ['theatre', 'experimental', 'fringe'],
                'mood_tags': ['The Thoughtful Stage', 'Curious Encounters'],
                'mood_confidence': 0.88,
                'price_range': '££',
                'price_min': 10,
                'price_max': 14,
                'url': 'https://www.eventbrite.com/e/quiet-room-tickets',
                'description': 'Intimate experimental theatre about silence and human connection. New writing, thought-provoking.',
                'source': 'eventbrite_mock',
                'event_id': 'mock_eventbrite_003',
                'matched_venue_id': None,
                'fetched_at': datetime.now().isoformat(),
                'filter_passed': True
            },

            # Late-Night Jazz
            {
                'event_name': 'Late Night Jazz Session',
                'venue_name': 'The Jazz Café',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': '21:00',
                'area': 'Camden Town',
                'region': 'North London',
                'genre_tags': ['jazz', 'blues', 'late night'],
                'mood_tags': ['Melancholic Beauty', 'Late-Night Lark'],
                'mood_confidence': 0.92,
                'price_range': '££',
                'price_min': 15,
                'price_max': 20,
                'url': 'https://www.eventbrite.com/e/jazz-session-tickets',
                'description': 'Intimate jazz performances under low lights. Blues, soul, and contemplative rhythms.',
                'source': 'eventbrite_mock',
                'event_id': 'mock_eventbrite_004',
                'matched_venue_id': None,
                'fetched_at': datetime.now().isoformat(),
                'filter_passed': True
            },

            # Spoken Word
            {
                'event_name': 'Poetry Open Mic Night',
                'venue_name': 'The Sound Lounge',
                'date': (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d'),
                'time': '19:30',
                'area': 'Tooting',
                'region': 'South London',
                'genre_tags': ['poetry', 'spoken word', 'open mic'],
                'mood_tags': ['Poetic', 'Folk & Intimate'],
                'mood_confidence': 0.90,
                'price_range': 'Free',
                'price_min': 0,
                'price_max': 0,
                'url': 'https://www.eventbrite.com/e/poetry-open-mic-tickets',
                'description': 'Grassroots spoken word and poetry in a welcoming community venue. Free entry, donations welcome.',
                'source': 'eventbrite_mock',
                'event_id': 'mock_eventbrite_005',
                'matched_venue_id': None,
                'fetched_at': datetime.now().isoformat(),
                'filter_passed': True
            },

            # Experimental Electronic
            {
                'event_name': 'Ambient Soundscapes: Modular Synthesis',
                'venue_name': 'Café OTO',
                'date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
                'time': '20:30',
                'area': 'Dalston',
                'region': 'East London',
                'genre_tags': ['electronic', 'experimental', 'ambient'],
                'mood_tags': ['Dreamlike & Hypnagogic', 'Playful & Weird'],
                'mood_confidence': 0.85,
                'price_range': '££',
                'price_min': 12,
                'price_max': 15,
                'url': 'https://www.eventbrite.com/e/ambient-soundscapes-tickets',
                'description': 'Experimental electronic music using modular synthesizers. Hypnotic, ethereal soundscapes.',
                'source': 'eventbrite_mock',
                'event_id': 'mock_eventbrite_006',
                'matched_venue_id': None,
                'fetched_at': datetime.now().isoformat(),
                'filter_passed': True
            },

            # World Music
            {
                'event_name': 'Balkan Brass Band: Live & Acoustic',
                'venue_name': 'Union Chapel',
                'date': (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d'),
                'time': '19:00',
                'area': 'Islington',
                'region': 'North London',
                'genre_tags': ['world music', 'balkan', 'brass'],
                'mood_tags': ['Global Rhythms', 'Group Energy'],
                'mood_confidence': 0.93,
                'price_range': '££',
                'price_min': 16,
                'price_max': 20,
                'url': 'https://www.eventbrite.com/e/balkan-brass-tickets',
                'description': 'Traditional Balkan brass music in a beautiful Gothic church setting.',
                'source': 'eventbrite_mock',
                'event_id': 'mock_eventbrite_007',
                'matched_venue_id': None,
                'fetched_at': datetime.now().isoformat(),
                'filter_passed': True
            },

            # Activist Event
            {
                'event_name': 'Radical Voices: Community Theatre',
                'venue_name': 'The Albany',
                'date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                'time': '18:30',
                'area': 'Deptford',
                'region': 'South London',
                'genre_tags': ['theatre', 'activist', 'community'],
                'mood_tags': ['Rant & Rapture', 'Punchy / Protest'],
                'mood_confidence': 0.87,
                'price_range': '£',
                'price_min': 5,
                'price_max': 10,
                'url': 'https://www.eventbrite.com/e/radical-voices-tickets',
                'description': 'Community theatre tackling social justice issues. Passionate performances, local stories.',
                'source': 'eventbrite_mock',
                'event_id': 'mock_eventbrite_008',
                'matched_venue_id': None,
                'fetched_at': datetime.now().isoformat(),
                'filter_passed': True
            },

            # Contemporary Dance
            {
                'event_name': 'Physical Theatre: Movement Without Words',
                'venue_name': 'The Place',
                'date': (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d'),
                'time': '20:00',
                'area': 'Kings Cross',
                'region': 'Central London',
                'genre_tags': ['dance', 'physical theatre', 'contemporary'],
                'mood_tags': ['Body-Based / Movement-Led', 'Curious Encounters'],
                'mood_confidence': 0.91,
                'price_range': '££',
                'price_min': 14,
                'price_max': 18,
                'url': 'https://www.eventbrite.com/e/physical-theatre-tickets',
                'description': 'Contemporary dance and physical theatre exploring human connection through movement.',
                'source': 'eventbrite_mock',
                'event_id': 'mock_eventbrite_009',
                'matched_venue_id': None,
                'fetched_at': datetime.now().isoformat(),
                'filter_passed': True
            },

            # Indie Film Screening
            {
                'event_name': 'Independent Film Screening + Q&A',
                'venue_name': 'Close-Up Film Centre',
                'date': (datetime.now() + timedelta(days=9)).strftime('%Y-%m-%d'),
                'time': '19:30',
                'area': 'Shoreditch',
                'region': 'East London',
                'genre_tags': ['film', 'independent', 'arthouse'],
                'mood_tags': ['The Thoughtful Stage', 'Curious Encounters'],
                'mood_confidence': 0.79,
                'price_range': '££',
                'price_min': 11,
                'price_max': 13,
                'url': 'https://www.eventbrite.com/e/indie-film-screening-tickets',
                'description': 'Independent documentary screening followed by filmmaker Q&A.',
                'source': 'eventbrite_mock',
                'event_id': 'mock_eventbrite_010',
                'matched_venue_id': None,
                'fetched_at': datetime.now().isoformat(),
                'filter_passed': True
            },
        ]

        print(f"✓ Generated {len(mock_events)} realistic filtered mock events")
        print("  (These demonstrate what Eventbrite data looks like after filtering)\n")

        return mock_events


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("  LONDON LARK - EVENTBRITE FETCHER")
    print("="*70)
    print()

    # Use mock data (set use_mock=False when you have a token)
    fetcher = EventFetcher(use_mock=True)
    events = fetcher.fetch_all_events()

    print(f"\n✓ Total events: {len(events)}")

    if events:
        print("\n📋 Sample event:")
        print(json.dumps(events[0], indent=2, ensure_ascii=False))

        # Show mood distribution
        print("\n🎭 Mood distribution:")
        mood_counts = {}
        for event in events:
            for mood in event.get('mood_tags', []):
                mood_counts[mood] = mood_counts.get(mood, 0) + 1

        for mood, count in sorted(mood_counts.items(), key=lambda x: -x[1]):
            print(f"  - {mood}: {count}")

        # Save to cache
        with open('events_cache.json', 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved {len(events)} events to events_cache.json")

        # Save sample for review
        sample_events = events[:10]  # First 10 for review
        with open('eventbrite_sample.json', 'w', encoding='utf-8') as f:
            json.dump(sample_events, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved sample to eventbrite_sample.json (first 10 events)")

        print("\n" + "="*70)
        print("✅ READY TO USE")
        print("="*70)
        print("\nNext steps:")
        print("1. Review eventbrite_sample.json to see filtered results")
        print("2. Get Eventbrite token (see EVENTBRITE_GUIDE.md)")
        print("3. Set EVENTBRITE_TOKEN at top of this file")
        print("4. Run with: fetcher = EventFetcher(use_mock=False)")
        print()
