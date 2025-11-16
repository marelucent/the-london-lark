#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The London Lark - Local Event Scraper
======================================

A standalone web scraping system to fetch real London events from:
- Resident Advisor (RA)
- Dice.fm
- Time Out London

Run this on your local machine to collect events, then import into the Lark.

Usage:
    python local_scraper.py                    # Scrape all sources
    python local_scraper.py --source ra        # Scrape only RA
    python local_scraper.py --source dice      # Scrape only Dice
    python local_scraper.py --source timeout   # Scrape only Time Out
    python local_scraper.py --days 14          # Scrape next 14 days
    python local_scraper.py --output events.json  # Custom output file
"""

import argparse
import json
import logging
import random
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Missing dependencies! Please run:")
    print("   pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Rate limiting configuration
MIN_DELAY = 1.0  # Minimum seconds between requests
MAX_DELAY = 2.0  # Maximum seconds between requests (adds randomness)

# User agent to appear as a regular browser
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Common headers for requests
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
}


def rate_limit():
    """Sleep for a random duration to avoid overwhelming servers"""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    logger.debug(f"Rate limiting: sleeping {delay:.2f}s")
    time.sleep(delay)


def safe_request(url: str, headers: Optional[Dict] = None, timeout: int = 30) -> Optional[requests.Response]:
    """
    Make a safe HTTP request with error handling and retries.

    Args:
        url: The URL to fetch
        headers: Optional custom headers
        timeout: Request timeout in seconds

    Returns:
        Response object or None if request failed
    """
    if headers is None:
        headers = DEFAULT_HEADERS.copy()

    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.debug(f"Fetching {url} (attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, headers=headers, timeout=timeout)

            if response.status_code == 200:
                return response
            elif response.status_code == 403:
                logger.warning(f"⚠️ Access denied (403) for {url}")
                return None
            elif response.status_code == 429:
                # Rate limited - wait longer
                wait_time = (attempt + 1) * 30
                logger.warning(f"⚠️ Rate limited (429). Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.warning(f"⚠️ HTTP {response.status_code} for {url}")
                if attempt < max_retries - 1:
                    time.sleep(5)

        except requests.exceptions.Timeout:
            logger.warning(f"⚠️ Timeout for {url}")
            if attempt < max_retries - 1:
                time.sleep(5)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Connection error for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error for {url}: {e}")
            return None

    return None


def parse_date(date_str: str) -> Optional[str]:
    """
    Parse various date formats into ISO format (YYYY-MM-DD).

    Args:
        date_str: Date string in various formats

    Returns:
        ISO formatted date string or None
    """
    # Common date patterns
    patterns = [
        ("%Y-%m-%d", date_str),  # ISO format
        ("%d %B %Y", date_str),   # "15 January 2025"
        ("%d %b %Y", date_str),   # "15 Jan 2025"
        ("%B %d, %Y", date_str),  # "January 15, 2025"
        ("%b %d, %Y", date_str),  # "Jan 15, 2025"
        ("%d/%m/%Y", date_str),   # "15/01/2025"
        ("%m/%d/%Y", date_str),   # "01/15/2025"
    ]

    for fmt, s in patterns:
        try:
            dt = datetime.strptime(s.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Try to extract date from longer strings
    # Pattern: "Sat 15 Jan" or "Saturday 15 January"
    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }

    match = re.search(r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', date_str.lower())
    if match:
        day = int(match.group(1))
        month = month_map[match.group(2)]
        year = datetime.now().year
        # If the date is in the past, assume next year
        test_date = datetime(year, month, day)
        if test_date < datetime.now() - timedelta(days=1):
            year += 1
        return f"{year}-{month:02d}-{day:02d}"

    logger.debug(f"Could not parse date: {date_str}")
    return None


def infer_mood_tags(event_name: str, venue_name: str, description: str = "") -> List[str]:
    """
    Infer mood tags from event details using keyword matching.

    Args:
        event_name: Name of the event
        venue_name: Name of the venue
        description: Optional event description

    Returns:
        List of mood tag strings
    """
    text = f"{event_name} {venue_name} {description}".lower()

    mood_keywords = {
        "Folk & Intimate": ["folk", "acoustic", "singer-songwriter", "intimate", "unplugged"],
        "Queer Revelry": ["queer", "lgbtq", "pride", "drag", "gay", "lesbian", "trans"],
        "Melancholic Beauty": ["melancholic", "sad", "blues", "minor key", "haunting", "ethereal"],
        "Late-Night Lark": ["late night", "after hours", "midnight", "2am", "all night", "club"],
        "Curious Encounters": ["experimental", "avant-garde", "weird", "strange", "unusual"],
        "The Thoughtful Stage": ["poetry", "spoken word", "theatre", "play", "performance"],
        "Global Rhythms": ["world music", "african", "latin", "caribbean", "reggae", "afrobeat"],
        "Cabaret & Glitter": ["cabaret", "burlesque", "variety", "showgirl", "glitter"],
        "Big Night Out": ["party", "rave", "dance", "dj set", "club night"],
        "Comic Relief": ["comedy", "stand-up", "improv", "funny", "laugh"],
        "Dreamlike & Hypnagogic": ["ambient", "drone", "meditation", "soundscape", "dreamy"],
        "Wonder & Awe": ["orchestra", "symphony", "classical", "choir", "choral"],
        "Spiritual / Sacred / Mystical": ["spiritual", "sacred", "ritual", "ceremony", "mystical"],
        "Playful & Weird": ["playful", "interactive", "immersive", "game", "weird"],
        "Nostalgic / Vintage / Retro": ["vintage", "retro", "80s", "90s", "throwback", "classic"],
        "Body-Based / Movement-Led": ["dance", "movement", "yoga", "somatic", "body"],
        "Punchy / Protest": ["punk", "protest", "political", "activist", "riot"],
        "Witchy & Wild": ["witch", "pagan", "moon", "ritual", "wild"],
    }

    tags = []
    for mood, keywords in mood_keywords.items():
        if any(kw in text for kw in keywords):
            tags.append(mood)
            if len(tags) >= 2:  # Max 2 tags
                break

    # Default if nothing matched
    if not tags:
        tags = ["Curious Encounters"]

    return tags


class ResidentAdvisorScraper:
    """Scraper for Resident Advisor London events"""

    BASE_URL = "https://ra.co"
    EVENTS_URL = "https://ra.co/events/uk/london"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def scrape(self, days_ahead: int = 7) -> List[Dict]:
        """
        Scrape RA events for the next N days.

        Note: RA uses heavy JavaScript rendering, so we may get limited results
        from static HTML. Consider this a best-effort scraper.
        """
        logger.info(f"🎧 Scraping Resident Advisor (next {days_ahead} days)...")
        events = []

        # RA organizes events by date, try each date
        for day_offset in range(days_ahead):
            target_date = datetime.now() + timedelta(days=day_offset)
            date_str = target_date.strftime("%Y-%m-%d")

            # RA date-specific URL pattern
            url = f"{self.EVENTS_URL}?week={date_str}"

            rate_limit()
            response = safe_request(url)

            if not response:
                logger.warning(f"Failed to fetch RA events for {date_str}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try to find event listings (RA's structure may vary)
            # Look for event cards or list items
            event_elements = soup.find_all('article') or soup.find_all('div', class_=re.compile(r'event', re.I))

            if not event_elements:
                # Try alternative selectors
                event_elements = soup.find_all('a', href=re.compile(r'/events/\d+'))

            for element in event_elements[:10]:  # Limit per day
                try:
                    event = self._parse_event_element(element, date_str)
                    if event:
                        events.append(event)
                except Exception as e:
                    logger.debug(f"Error parsing RA event: {e}")
                    continue

        # If static scraping failed, try the listing page
        if not events:
            events = self._scrape_listing_page()

        logger.info(f"✅ Found {len(events)} events from Resident Advisor")
        return events

    def _parse_event_element(self, element, date_str: str) -> Optional[Dict]:
        """Parse a single event element from RA HTML"""
        # Try to extract event details
        event_name = None
        venue_name = None
        event_url = None

        # Find event link/title
        link = element.find('a', href=re.compile(r'/events/\d+'))
        if link:
            event_url = urljoin(self.BASE_URL, link.get('href', ''))
            event_name = link.get_text(strip=True)

        # Find venue
        venue_link = element.find('a', href=re.compile(r'/clubs/'))
        if venue_link:
            venue_name = venue_link.get_text(strip=True)

        # If we couldn't find structured data, try text extraction
        if not event_name:
            text = element.get_text(strip=True)
            if len(text) > 10 and len(text) < 200:
                event_name = text[:100]

        if not event_name or not venue_name:
            return None

        return {
            "event_name": event_name,
            "venue_name": venue_name,
            "date": date_str,
            "time": "23:00",  # RA events typically start late
            "source": "Resident Advisor",
            "url": event_url or "",
            "description": "",
            "mood_tags": infer_mood_tags(event_name, venue_name)
        }

    def _scrape_listing_page(self) -> List[Dict]:
        """Fallback: scrape the main listing page"""
        logger.info("Trying RA main listing page...")
        rate_limit()

        response = safe_request(self.EVENTS_URL)
        if not response:
            return []

        events = []
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for any event-like content
        # RA uses React, so actual event data might be in script tags
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'Event':
                            events.append(self._parse_jsonld_event(item))
                elif data.get('@type') == 'Event':
                    events.append(self._parse_jsonld_event(data))
            except (json.JSONDecodeError, AttributeError):
                continue

        return [e for e in events if e]

    def _parse_jsonld_event(self, data: Dict) -> Optional[Dict]:
        """Parse JSON-LD structured event data"""
        try:
            event_name = data.get('name', '')
            venue_data = data.get('location', {})
            venue_name = venue_data.get('name', '') if isinstance(venue_data, dict) else str(venue_data)

            start_date = data.get('startDate', '')
            date_str = start_date[:10] if start_date else datetime.now().strftime('%Y-%m-%d')
            time_str = start_date[11:16] if len(start_date) > 16 else "21:00"

            return {
                "event_name": event_name,
                "venue_name": venue_name,
                "date": date_str,
                "time": time_str,
                "source": "Resident Advisor",
                "url": data.get('url', ''),
                "description": data.get('description', '')[:500],
                "mood_tags": infer_mood_tags(event_name, venue_name, data.get('description', ''))
            }
        except Exception as e:
            logger.debug(f"Error parsing JSON-LD: {e}")
            return None


class DiceFMScraper:
    """Scraper for Dice.fm London events"""

    BASE_URL = "https://dice.fm"
    EVENTS_URL = "https://dice.fm/browse/london"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def scrape(self, days_ahead: int = 7) -> List[Dict]:
        """Scrape Dice.fm events for London"""
        logger.info(f"🎲 Scraping Dice.fm (next {days_ahead} days)...")
        events = []

        rate_limit()
        response = safe_request(self.EVENTS_URL)

        if not response:
            logger.warning("Failed to fetch Dice.fm events")
            return events

        soup = BeautifulSoup(response.text, 'html.parser')

        # Dice.fm uses specific class patterns for event cards
        event_cards = soup.find_all('a', href=re.compile(r'/event/'))

        if not event_cards:
            # Try finding structured data
            events = self._scrape_structured_data(soup)
        else:
            cutoff_date = datetime.now() + timedelta(days=days_ahead)

            for card in event_cards[:30]:  # Limit to avoid too many
                try:
                    event = self._parse_event_card(card)
                    if event:
                        # Check if within date range
                        event_date = datetime.strptime(event['date'], '%Y-%m-%d')
                        if event_date <= cutoff_date:
                            events.append(event)
                except Exception as e:
                    logger.debug(f"Error parsing Dice event: {e}")
                    continue

        logger.info(f"✅ Found {len(events)} events from Dice.fm")
        return events

    def _parse_event_card(self, card) -> Optional[Dict]:
        """Parse a single Dice.fm event card"""
        event_url = urljoin(self.BASE_URL, card.get('href', ''))

        # Extract text content
        text_content = card.get_text(separator=' | ', strip=True)
        parts = text_content.split(' | ')

        if len(parts) < 2:
            return None

        event_name = parts[0] if parts else "Unknown Event"
        venue_name = "London Venue"  # Default, try to extract
        date_str = datetime.now().strftime('%Y-%m-%d')
        time_str = "20:00"

        # Try to find venue in the card
        for part in parts:
            if any(word in part.lower() for word in ['hall', 'club', 'theatre', 'pub', 'bar', 'venue']):
                venue_name = part
                break

        # Try to parse date from text
        for part in parts:
            parsed = parse_date(part)
            if parsed:
                date_str = parsed
                break

        # Look for time pattern (HH:MM)
        time_match = re.search(r'\b(\d{1,2}:\d{2})\b', text_content)
        if time_match:
            time_str = time_match.group(1)

        return {
            "event_name": event_name[:100],
            "venue_name": venue_name,
            "date": date_str,
            "time": time_str,
            "source": "Dice.fm",
            "url": event_url,
            "description": "",
            "mood_tags": infer_mood_tags(event_name, venue_name)
        }

    def _scrape_structured_data(self, soup) -> List[Dict]:
        """Extract events from JSON-LD or script data"""
        events = []

        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') in ['Event', 'MusicEvent']:
                            event = self._parse_jsonld_event(item)
                            if event:
                                events.append(event)
            except (json.JSONDecodeError, AttributeError):
                continue

        return events

    def _parse_jsonld_event(self, data: Dict) -> Optional[Dict]:
        """Parse JSON-LD structured event data"""
        try:
            event_name = data.get('name', '')
            venue_data = data.get('location', {})
            venue_name = venue_data.get('name', 'London Venue') if isinstance(venue_data, dict) else str(venue_data)

            start_date = data.get('startDate', '')
            date_str = start_date[:10] if start_date else datetime.now().strftime('%Y-%m-%d')
            time_str = start_date[11:16] if len(start_date) > 16 else "20:00"

            return {
                "event_name": event_name,
                "venue_name": venue_name,
                "date": date_str,
                "time": time_str,
                "source": "Dice.fm",
                "url": data.get('url', ''),
                "description": data.get('description', '')[:500],
                "mood_tags": infer_mood_tags(event_name, venue_name, data.get('description', ''))
            }
        except Exception as e:
            logger.debug(f"Error parsing Dice JSON-LD: {e}")
            return None


class TimeOutScraper:
    """Scraper for Time Out London events"""

    BASE_URL = "https://www.timeout.com"
    MUSIC_URL = "https://www.timeout.com/london/music"
    THEATRE_URL = "https://www.timeout.com/london/theatre"
    NIGHTLIFE_URL = "https://www.timeout.com/london/nightlife"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def scrape(self, days_ahead: int = 7) -> List[Dict]:
        """Scrape Time Out London events from multiple categories"""
        logger.info(f"⏰ Scraping Time Out London (next {days_ahead} days)...")
        events = []

        # Scrape different categories
        categories = [
            (self.MUSIC_URL, "music"),
            (self.THEATRE_URL, "theatre"),
            (self.NIGHTLIFE_URL, "nightlife")
        ]

        for url, category in categories:
            logger.info(f"  Fetching {category} events...")
            rate_limit()

            response = safe_request(url)
            if not response:
                logger.warning(f"Failed to fetch Time Out {category}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            category_events = self._extract_events(soup, category)
            events.extend(category_events)

        # Filter to date range
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        filtered_events = []

        for event in events:
            try:
                event_date = datetime.strptime(event['date'], '%Y-%m-%d')
                if event_date <= cutoff_date:
                    filtered_events.append(event)
            except:
                # If date parsing fails, include anyway
                filtered_events.append(event)

        logger.info(f"✅ Found {len(filtered_events)} events from Time Out London")
        return filtered_events

    def _extract_events(self, soup, category: str) -> List[Dict]:
        """Extract events from Time Out page"""
        events = []

        # Time Out uses article cards
        articles = soup.find_all('article') or soup.find_all('div', class_=re.compile(r'card', re.I))

        for article in articles[:20]:  # Limit per category
            try:
                event = self._parse_article(article, category)
                if event:
                    events.append(event)
            except Exception as e:
                logger.debug(f"Error parsing Time Out article: {e}")
                continue

        # Also check for JSON-LD
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') in ['Event', 'MusicEvent', 'TheaterEvent']:
                            event = self._parse_jsonld_event(item)
                            if event:
                                events.append(event)
            except (json.JSONDecodeError, AttributeError):
                continue

        return events

    def _parse_article(self, article, category: str) -> Optional[Dict]:
        """Parse a Time Out article/card element"""
        # Find title
        title_elem = article.find(['h2', 'h3', 'h4']) or article.find('a')
        if not title_elem:
            return None

        event_name = title_elem.get_text(strip=True)
        if len(event_name) < 3 or len(event_name) > 200:
            return None

        # Find link
        link = article.find('a', href=True)
        event_url = urljoin(self.BASE_URL, link.get('href', '')) if link else ""

        # Try to extract venue from text
        venue_name = "London Venue"
        text = article.get_text()

        # Look for "at [Venue]" pattern
        at_match = re.search(r'\bat\s+([A-Z][^,\n]{3,40})', text)
        if at_match:
            venue_name = at_match.group(1).strip()

        # Try to extract date
        date_str = datetime.now().strftime('%Y-%m-%d')
        date_elem = article.find(class_=re.compile(r'date', re.I))
        if date_elem:
            parsed = parse_date(date_elem.get_text())
            if parsed:
                date_str = parsed

        # Default time based on category
        time_str = "20:00"
        if category == "nightlife":
            time_str = "22:00"
        elif category == "theatre":
            time_str = "19:30"

        # Extract description snippet
        desc_elem = article.find('p') or article.find(class_=re.compile(r'desc|summary', re.I))
        description = desc_elem.get_text(strip=True)[:300] if desc_elem else ""

        return {
            "event_name": event_name,
            "venue_name": venue_name,
            "date": date_str,
            "time": time_str,
            "source": f"Time Out London ({category})",
            "url": event_url,
            "description": description,
            "mood_tags": infer_mood_tags(event_name, venue_name, description)
        }

    def _parse_jsonld_event(self, data: Dict) -> Optional[Dict]:
        """Parse JSON-LD structured event data"""
        try:
            event_name = data.get('name', '')
            venue_data = data.get('location', {})
            venue_name = venue_data.get('name', 'London Venue') if isinstance(venue_data, dict) else str(venue_data)

            start_date = data.get('startDate', '')
            date_str = start_date[:10] if start_date else datetime.now().strftime('%Y-%m-%d')
            time_str = start_date[11:16] if len(start_date) > 16 else "20:00"

            return {
                "event_name": event_name,
                "venue_name": venue_name,
                "date": date_str,
                "time": time_str,
                "source": "Time Out London",
                "url": data.get('url', ''),
                "description": data.get('description', '')[:500],
                "mood_tags": infer_mood_tags(event_name, venue_name, data.get('description', ''))
            }
        except Exception as e:
            logger.debug(f"Error parsing Time Out JSON-LD: {e}")
            return None


def scrape_all_sources(days_ahead: int = 7, sources: Optional[List[str]] = None) -> List[Dict]:
    """
    Scrape events from all or selected sources.

    Args:
        days_ahead: Number of days ahead to scrape
        sources: List of source names to scrape (None = all)

    Returns:
        List of all scraped events
    """
    all_events = []

    scrapers = {
        "ra": ResidentAdvisorScraper,
        "dice": DiceFMScraper,
        "timeout": TimeOutScraper,
    }

    if sources is None:
        sources = list(scrapers.keys())

    for source_name in sources:
        if source_name not in scrapers:
            logger.warning(f"Unknown source: {source_name}")
            continue

        try:
            scraper = scrapers[source_name]()
            events = scraper.scrape(days_ahead=days_ahead)
            all_events.extend(events)
            logger.info(f"")  # Empty line for readability
        except Exception as e:
            logger.error(f"❌ Error scraping {source_name}: {e}")
            continue

    return all_events


def deduplicate_events(events: List[Dict]) -> List[Dict]:
    """
    Remove duplicate events based on name and venue similarity.

    Args:
        events: List of event dictionaries

    Returns:
        Deduplicated list
    """
    seen = set()
    unique_events = []

    for event in events:
        # Create a simple key from event name and venue
        key = (
            event.get('event_name', '').lower()[:50],
            event.get('venue_name', '').lower()[:30],
            event.get('date', '')
        )

        if key not in seen:
            seen.add(key)
            unique_events.append(event)

    logger.info(f"Deduplicated: {len(events)} → {len(unique_events)} events")
    return unique_events


def save_events(events: List[Dict], output_file: str = "scraped_events.json"):
    """
    Save scraped events to JSON file.

    Args:
        events: List of event dictionaries
        output_file: Output filename
    """
    output_path = Path(output_file)

    # Add metadata
    output_data = {
        "scraped_at": datetime.now().isoformat(),
        "event_count": len(events),
        "sources": list(set(e.get('source', 'Unknown') for e in events)),
        "events": events
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"💾 Saved {len(events)} events to {output_path}")


def main():
    """Main entry point for the scraper"""
    parser = argparse.ArgumentParser(
        description="Scrape London events for The London Lark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python local_scraper.py                          # Scrape all sources (7 days)
  python local_scraper.py --source ra              # Scrape only Resident Advisor
  python local_scraper.py --source dice timeout    # Scrape Dice and Time Out
  python local_scraper.py --days 14                # Scrape next 14 days
  python local_scraper.py --output my_events.json  # Custom output file
  python local_scraper.py --verbose                # Enable debug logging
        """
    )

    parser.add_argument(
        '--source',
        nargs='+',
        choices=['ra', 'dice', 'timeout'],
        help='Specific source(s) to scrape (default: all)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days ahead to scrape (default: 7)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='scraped_events.json',
        help='Output JSON file (default: scraped_events.json)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose/debug logging'
    )
    parser.add_argument(
        '--no-dedup',
        action='store_true',
        help='Skip deduplication of events'
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Banner
    print("\n" + "="*60)
    print("  🕊️  THE LONDON LARK - Event Scraper")
    print("  Fetching real events from London's cultural underground...")
    print("="*60 + "\n")

    # Run scrapers
    logger.info(f"Starting scrape for next {args.days} days...")
    events = scrape_all_sources(days_ahead=args.days, sources=args.source)

    if not events:
        logger.warning("⚠️ No events were scraped. This could be due to:")
        logger.warning("   - Websites blocking automated requests")
        logger.warning("   - Network connectivity issues")
        logger.warning("   - Changes in website structure")
        print("\nConsider:")
        print("  1. Try again later (websites may temporarily block)")
        print("  2. Use a VPN if your IP is blocked")
        print("  3. Check the README for manual event import instructions")
        return

    # Deduplicate
    if not args.no_dedup:
        events = deduplicate_events(events)

    # Save results
    save_events(events, args.output)

    # Summary
    print("\n" + "="*60)
    print("  ✅ SCRAPING COMPLETE")
    print("="*60)
    print(f"  Total events: {len(events)}")

    # Breakdown by source
    source_counts = {}
    for event in events:
        source = event.get('source', 'Unknown')
        source_counts[source] = source_counts.get(source, 0) + 1

    for source, count in sorted(source_counts.items()):
        print(f"  • {source}: {count} events")

    print(f"\n  Output file: {args.output}")
    print(f"\n  Next step: Copy {args.output} to your Lark project and run:")
    print(f"    python scrapers/import_events.py {args.output}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
