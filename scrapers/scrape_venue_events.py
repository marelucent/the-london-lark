#!/usr/bin/env python3
"""
Direct Venue Event Scraper

Scrapes events directly from our curated venue websites.
This is more reliable than event aggregators since we control the source.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from mock_event_generator import load_venues

REQUEST_DELAY = 1.5  # Be gentle with venue sites
TIMEOUT = 15

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def scrape_venue_website(venue):
    """
    Attempt to scrape events from a single venue website.

    Args:
        venue: Venue dict from our curated list

    Returns:
        list: Events found at this venue
    """
    website = venue.get("website", "")
    venue_name = venue.get("display_name", venue.get("name", "Unknown"))

    if not website or website.startswith("("):
        # Skip venues without proper websites
        return []

    # Ensure proper URL
    if not website.startswith("http"):
        website = "https://" + website

    print(f"   Checking: {venue_name}")
    print(f"            {website}")

    events = []

    try:
        time.sleep(REQUEST_DELAY)
        response = requests.get(website, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)

        if response.status_code != 200:
            print(f"            Status: {response.status_code}")
            return []

        print(f"            ✓ Status: {response.status_code}, {len(response.text)} chars")

        soup = BeautifulSoup(response.text, "lxml")

        # Strategy 1: Look for JSON-LD structured data (most reliable)
        jsonld_events = extract_jsonld_events(soup, venue)
        if jsonld_events:
            print(f"            Found {len(jsonld_events)} events via JSON-LD")
            events.extend(jsonld_events)

        # Strategy 2: Look for common event listing patterns
        page_events = extract_page_events(soup, venue, website)
        if page_events:
            print(f"            Found {len(page_events)} events in page content")
            events.extend(page_events)

        # Strategy 3: Check for /events or /whats-on subpage
        if not events:
            events_page = check_events_subpage(website, venue)
            if events_page:
                print(f"            Found {len(events_page)} events on subpage")
                events.extend(events_page)

        return events

    except requests.exceptions.Timeout:
        print(f"            Timeout")
        return []
    except requests.exceptions.SSLError:
        print(f"            SSL Error")
        return []
    except Exception as e:
        print(f"            Error: {type(e).__name__}")
        return []


def extract_jsonld_events(soup, venue):
    """Extract events from JSON-LD structured data."""
    events = []

    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            if not script.string:
                continue

            data = json.loads(script.string)

            # Handle single event
            if isinstance(data, dict) and data.get("@type") == "Event":
                events.append(normalize_jsonld_event(data, venue))

            # Handle list of events
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "Event":
                        events.append(normalize_jsonld_event(item, venue))

            # Handle @graph structure
            elif isinstance(data, dict) and "@graph" in data:
                for item in data["@graph"]:
                    if isinstance(item, dict) and item.get("@type") == "Event":
                        events.append(normalize_jsonld_event(item, venue))

        except json.JSONDecodeError:
            pass

    return events


def normalize_jsonld_event(data, venue):
    """Normalize JSON-LD event to our format."""
    # Parse date
    start_date = data.get("startDate", "")
    date_str = ""
    time_str = ""
    if start_date:
        try:
            if "T" in start_date:
                dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M")
            else:
                date_str = start_date[:10]
        except:
            date_str = start_date

    return {
        "event_name": data.get("name", "Untitled Event"),
        "venue_name": venue.get("display_name", ""),
        "venue_emoji": venue.get("emoji", "🎭"),
        "date": date_str,
        "time": time_str,
        "area": venue.get("area", "London"),
        "mood_tags": venue.get("mood_tags", [])[:2],
        "description": data.get("description", "")[:500] if data.get("description") else "",
        "url": data.get("url", venue.get("website", "")),
        "source": "venue_website",
        "fetched_at": datetime.now().isoformat()
    }


def extract_page_events(soup, venue, base_url):
    """Extract events from page content using common patterns."""
    events = []

    # Look for elements with event-like classes
    event_patterns = [
        ("div", "event"),
        ("article", "event"),
        ("li", "event"),
        ("div", "show"),
        ("div", "gig"),
        ("div", "listing"),
    ]

    for tag, pattern in event_patterns:
        elements = soup.find_all(tag, class_=lambda x: x and pattern in x.lower() if x else False)
        for elem in elements[:10]:  # Limit per pattern
            text = elem.get_text(" ", strip=True)
            if len(text) > 10 and len(text) < 500:
                # Try to parse date from text
                date_match = re.search(r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", text, re.I)
                if date_match:
                    events.append({
                        "event_name": text[:100],
                        "venue_name": venue.get("display_name", ""),
                        "venue_emoji": venue.get("emoji", "🎭"),
                        "date": "",  # Would need proper parsing
                        "time": "",
                        "area": venue.get("area", "London"),
                        "mood_tags": venue.get("mood_tags", [])[:2],
                        "description": text[:200],
                        "url": base_url,
                        "source": "venue_website_text",
                        "fetched_at": datetime.now().isoformat()
                    })

    return events[:5]  # Limit results


def check_events_subpage(base_url, venue):
    """Check common subpages for event listings."""
    subpages = ["/events", "/whats-on", "/listings", "/programme", "/calendar", "/shows"]

    # Remove trailing slash
    base_url = base_url.rstrip("/")

    for subpage in subpages:
        try:
            url = base_url + subpage
            time.sleep(0.5)
            response = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "lxml")
                events = extract_jsonld_events(soup, venue)
                if events:
                    return events
        except:
            pass

    return []


def scrape_all_venues(limit=None):
    """
    Scrape events from all curated venues.

    Args:
        limit: Optional limit on number of venues to check

    Returns:
        list: All events found
    """
    venues = load_venues()
    print(f"Loaded {len(venues)} curated venues")

    if limit:
        venues = venues[:limit]
        print(f"Checking first {limit} venues")

    all_events = []

    for i, venue in enumerate(venues, 1):
        print(f"\n[{i}/{len(venues)}] ", end="")
        events = scrape_venue_website(venue)
        all_events.extend(events)

    return all_events


if __name__ == "__main__":
    print("=" * 70)
    print("  VENUE WEBSITE SCRAPER - TESTING")
    print("=" * 70)
    print()

    # Test with first 10 venues
    events = scrape_all_venues(limit=10)

    print(f"\n\n✓ Total events found: {len(events)}")

    # Save results
    output_file = "scraped_venue_events.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved to {output_file}")

    # Show sample
    if events:
        print("\n" + "=" * 70)
        print("  SAMPLE EVENTS")
        print("=" * 70)

        for i, event in enumerate(events[:5], 1):
            print(f"\n{i}. {event['venue_emoji']} {event.get('event_name', 'Unknown')[:60]}")
            print(f"   Venue: {event['venue_name']}")
            print(f"   Date: {event.get('date', 'TBC')} at {event.get('time', 'TBC')}")
            print(f"   Mood: {', '.join(event.get('mood_tags', []))}")

    print("\n" + "=" * 70)
