#!/usr/bin/env python3
"""
Real Event Fetcher - Multiple Approaches

Tries multiple sources to get REAL event data:
1. RSS feeds (Skiddle, Songkick)
2. Public APIs (Bandsintown)
3. Structured data from accessible sites

Goal: Get at least SOME real events flowing in.
"""

import requests
import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
import sys
import re

sys.path.insert(0, str(Path(__file__).parent.parent))
from mock_event_generator import load_venues

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/xml, */*",
}


def fetch_skiddle_rss():
    """
    Fetch from Skiddle RSS feed - UK event listings.
    """
    print("📡 Trying Skiddle RSS feed...")

    # Skiddle RSS for London area
    url = "https://www.skiddle.com/rss/events/london/"

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            # Parse RSS XML
            root = ET.fromstring(response.content)
            events = []

            for item in root.findall(".//item"):
                title = item.find("title")
                link = item.find("link")
                desc = item.find("description")
                pubdate = item.find("pubDate")

                if title is not None:
                    events.append({
                        "event_name": title.text,
                        "url": link.text if link is not None else "",
                        "description": desc.text if desc is not None else "",
                        "date": pubdate.text if pubdate is not None else "",
                        "source": "skiddle_rss"
                    })

            print(f"   ✓ Found {len(events)} events")
            return events

        return []

    except Exception as e:
        print(f"   Error: {e}")
        return []


def fetch_songkick_london():
    """
    Fetch from Songkick's London page (parse JSON from their API).
    """
    print("\n📡 Trying Songkick metro area...")

    # Songkick London metro area
    url = "https://www.songkick.com/metro-areas/24426-uk-london"

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        print(f"   Status: {response.status_code}")

        if response.status_code != 200:
            return []

        # Look for JSON data embedded in the page
        text = response.text

        # Songkick embeds event data as JSON
        json_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                events = []

                if isinstance(data, list):
                    for item in data:
                        if item.get("@type") == "MusicEvent":
                            events.append({
                                "event_name": item.get("name", ""),
                                "venue_name": item.get("location", {}).get("name", "") if isinstance(item.get("location"), dict) else "",
                                "date": item.get("startDate", ""),
                                "url": item.get("url", ""),
                                "source": "songkick"
                            })

                print(f"   ✓ Found {len(events)} events via JSON-LD")
                return events

            except json.JSONDecodeError:
                pass

        return []

    except Exception as e:
        print(f"   Error: {e}")
        return []


def fetch_bandsintown_for_venue(venue_name):
    """
    Fetch events for a specific venue from Bandsintown.
    They have a public API.
    """
    # Bandsintown API (no key required for basic searches)
    api_url = f"https://rest.bandsintown.com/venues/{venue_name}/events"

    params = {
        "app_id": "london_lark"  # App ID is just identification
    }

    try:
        response = requests.get(api_url, params=params, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data
        return []
    except:
        return []


def fetch_ents24_london():
    """
    Fetch from Ents24 (UK events site).
    """
    print("\n📡 Trying Ents24...")

    url = "https://www.ents24.com/london-events"

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        print(f"   Status: {response.status_code}")

        if response.status_code != 200:
            return []

        # Check if we can access it
        if len(response.text) < 1000:
            print("   Page too small, likely blocked")
            return []

        # Look for JSON-LD data
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "lxml")

        scripts = soup.find_all("script", type="application/ld+json")
        events = []

        for script in scripts:
            try:
                if script.string:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get("@type") == "Event":
                        events.append({
                            "event_name": data.get("name", ""),
                            "venue_name": data.get("location", {}).get("name", "") if isinstance(data.get("location"), dict) else "",
                            "date": data.get("startDate", ""),
                            "url": data.get("url", ""),
                            "source": "ents24"
                        })
            except:
                pass

        print(f"   ✓ Found {len(events)} events")
        return events

    except Exception as e:
        print(f"   Error: {e}")
        return []


def fetch_openstreetmap_events():
    """
    Try to get events from OpenStreetMap events platform.
    """
    print("\n📡 Trying OSM calendar...")

    # This is unlikely to work but worth a try
    url = "https://osmcal.org/api/v2/events/?location=london"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            events = response.json()
            print(f"   ✓ Found {len(events)} events")
            return events

        return []
    except Exception as e:
        print(f"   Error: {e}")
        return []


def match_events_to_venues(events, venues):
    """
    Match scraped events to our curated venue list using fuzzy matching.
    """
    print("\n🔍 Matching events to curated venues...")

    matched_events = []

    # Create lookup of venue names (lowercase for matching)
    venue_map = {}
    for venue in venues:
        name = venue.get("display_name", "").lower()
        venue_map[name] = venue

        # Also add variations
        # Remove "the " prefix
        if name.startswith("the "):
            venue_map[name[4:]] = venue

    for event in events:
        event_venue = event.get("venue_name", "").lower()

        if not event_venue:
            continue

        # Try exact match first
        if event_venue in venue_map:
            matched_event = enrich_event_with_venue(event, venue_map[event_venue])
            matched_events.append(matched_event)
            continue

        # Try partial match
        for venue_name, venue in venue_map.items():
            if venue_name in event_venue or event_venue in venue_name:
                matched_event = enrich_event_with_venue(event, venue)
                matched_events.append(matched_event)
                break

    print(f"   Matched {len(matched_events)} events to curated venues")
    return matched_events


def enrich_event_with_venue(event, venue):
    """
    Add venue metadata to event.
    """
    return {
        "event_id": f"real_{hash(event.get('event_name', '') + event.get('date', '')) % 100000}",
        "event_name": event.get("event_name", "Unknown Event"),
        "venue_name": venue.get("display_name", event.get("venue_name", "")),
        "venue_emoji": venue.get("emoji", "🎭"),
        "date": parse_date(event.get("date", "")),
        "time": parse_time(event.get("date", "")),
        "area": venue.get("area", "London"),
        "region": venue.get("area", "London"),
        "mood_tags": venue.get("mood_tags", ["Curious Encounters"])[:2],
        "mood_confidence": 0.85,
        "genre_tags": ["live music"],
        "price_range": "TBC",
        "price_min": 0,
        "price_max": 0,
        "url": event.get("url", venue.get("website", "")),
        "description": event.get("description", venue.get("tone_notes", ""))[:300],
        "source": event.get("source", "real_event"),
        "fetched_at": datetime.now().isoformat(),
        "filter_passed": True
    }


def parse_date(date_str):
    """Extract date from various formats."""
    if not date_str:
        return ""

    # Try ISO format
    if "T" in date_str:
        return date_str.split("T")[0]

    # Try to extract YYYY-MM-DD
    match = re.search(r"(\d{4}-\d{2}-\d{2})", date_str)
    if match:
        return match.group(1)

    return date_str[:10] if len(date_str) >= 10 else ""


def parse_time(date_str):
    """Extract time from various formats."""
    if not date_str:
        return ""

    # Try ISO format
    if "T" in date_str:
        time_part = date_str.split("T")[1] if "T" in date_str else ""
        return time_part[:5] if len(time_part) >= 5 else ""

    return ""


def main():
    """Main entry point - try all sources."""
    print("=" * 70)
    print("  REAL EVENT FETCHER - ATTEMPTING MULTIPLE SOURCES")
    print("=" * 70)
    print()

    all_events = []

    # Try each source
    skiddle_events = fetch_skiddle_rss()
    all_events.extend(skiddle_events)

    songkick_events = fetch_songkick_london()
    all_events.extend(songkick_events)

    ents24_events = fetch_ents24_london()
    all_events.extend(ents24_events)

    osm_events = fetch_openstreetmap_events()
    all_events.extend(osm_events)

    print(f"\n📊 Total raw events: {len(all_events)}")

    # Load our curated venues
    venues = load_venues()
    print(f"   Curated venues: {len(venues)}")

    # Match events to our venues
    matched_events = match_events_to_venues(all_events, venues)

    # Save all results
    with open("scraped_real_events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved {len(all_events)} raw events to scraped_real_events.json")

    with open("matched_real_events.json", "w", encoding="utf-8") as f:
        json.dump(matched_events, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {len(matched_events)} matched events to matched_real_events.json")

    # Show results
    if matched_events:
        print("\n" + "=" * 70)
        print("  REAL EVENTS MATCHING OUR VENUES")
        print("=" * 70)

        for i, event in enumerate(matched_events[:10], 1):
            print(f"\n{i}. {event['venue_emoji']} {event['event_name'][:60]}")
            print(f"   Venue: {event['venue_name']}")
            print(f"   Date: {event['date']} at {event['time']}")
            print(f"   Mood: {', '.join(event['mood_tags'])}")
            print(f"   Source: {event['source']}")
    else:
        print("\n⚠️  No events matched our curated venues")
        print("   This is expected - aggregators list mainstream venues")
        print("   Our curated list is deliberately niche/underground")

    # Show raw events anyway
    if all_events and not matched_events:
        print("\n" + "=" * 70)
        print("  RAW EVENTS (for reference)")
        print("=" * 70)

        for i, event in enumerate(all_events[:10], 1):
            print(f"\n{i}. {event.get('event_name', 'Unknown')[:60]}")
            if event.get("venue_name"):
                print(f"   Venue: {event['venue_name']}")
            print(f"   Source: {event.get('source', 'unknown')}")

    print("\n" + "=" * 70)

    return all_events, matched_events


if __name__ == "__main__":
    main()
