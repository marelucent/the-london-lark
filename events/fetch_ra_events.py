#!/usr/bin/env python3
"""
Resident Advisor Event Fetcher for The London Lark

Uses Apify's RA scraper to fetch upcoming events in London.
Filters and normalizes events to match the Lark's curatorial vision.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from apify_client import ApifyClient
    HAS_APIFY = True
except ImportError:
    HAS_APIFY = False
    print("Warning: apify-client not installed. Run: pip install apify-client")

try:
    from event_config import (
        GENRE_KEYWORDS_EXCLUDE,
        VENUE_KEYWORDS_EXCLUDE,
        MOOD_INFERENCE_MAP,
        AREA_TO_REGION
    )
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False
    print("Warning: event_config.py not found, filtering disabled")

# Apify API Token - set via environment variable in production
# Get token from: https://my.apify.com/account/integrations
APIFY_TOKEN = ""  # Set your token here or use environment variable
RA_ACTOR_ID = "augeas/resident-advisor"


def fetch_ra_events_apify(days_ahead=30, max_events=100):
    """
    Fetch events from Resident Advisor using Apify scraper.

    Args:
        days_ahead: Number of days to look ahead
        max_events: Maximum number of events to fetch

    Returns:
        list: Raw events from RA scraper
    """
    if not HAS_APIFY:
        print("Error: apify-client not installed")
        return []

    client = ApifyClient(APIFY_TOKEN)

    # Calculate date range
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    # Configure the actor run
    run_input = {
        "location": "London",
        "startDate": start_date,
        "endDate": end_date,
        "maxItems": max_events,
    }

    print(f"   Calling Apify RA scraper for London events ({start_date} to {end_date})...")

    try:
        # Run the actor and wait for it to finish
        run = client.actor(RA_ACTOR_ID).call(run_input=run_input)

        # Fetch results from the dataset
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items

        return dataset_items

    except Exception as e:
        print(f"   Error running Apify RA scraper: {e}")
        return []


def normalize_ra_event(raw_event):
    """
    Convert raw RA scraper data to our standard event format.

    Args:
        raw_event: Raw event dict from Apify scraper

    Returns:
        dict: Normalized event in Lark format
    """
    # Extract basic info (adjust field names based on actual scraper output)
    event_id = raw_event.get("id", raw_event.get("url", "").split("/")[-1])
    title = raw_event.get("title", raw_event.get("name", "Untitled Event"))

    # Date and time
    date_str = raw_event.get("date", "")
    time_str = raw_event.get("startTime", raw_event.get("time", ""))

    # Try to parse date if it's in a different format
    if not date_str and raw_event.get("datetime"):
        try:
            dt = datetime.fromisoformat(raw_event["datetime"].replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M")
        except:
            pass

    # Venue info
    venue_name = raw_event.get("venue", {}).get("name", raw_event.get("venueName", "Unknown Venue"))
    if isinstance(venue_name, dict):
        venue_name = venue_name.get("name", "Unknown Venue")

    area = raw_event.get("venue", {}).get("area", raw_event.get("area", "London"))
    if isinstance(area, dict):
        area = area.get("name", "London")

    # Artists
    artists = raw_event.get("artists", raw_event.get("lineup", []))
    if isinstance(artists, list):
        artist_names = [a.get("name", a) if isinstance(a, dict) else str(a) for a in artists]
    else:
        artist_names = []

    # URL
    url = raw_event.get("url", "")
    if url and not url.startswith("http"):
        url = f"https://ra.co{url}"

    # Description
    description = raw_event.get("description", raw_event.get("content", ""))

    # Price (RA often shows ticket info)
    price_info = raw_event.get("tickets", raw_event.get("price", {}))
    price_min = 0
    price_max = 0
    if isinstance(price_info, dict):
        price_min = float(price_info.get("min", 0))
        price_max = float(price_info.get("max", price_min))
    elif isinstance(price_info, (int, float)):
        price_min = float(price_info)
        price_max = price_min

    # Classify price range
    if price_min == 0:
        price_range = "Free"
    elif price_max <= 10:
        price_range = "£"
    elif price_max <= 20:
        price_range = "££"
    elif price_max <= 35:
        price_range = "£££"
    else:
        price_range = "££££"

    # Infer mood and genre tags
    mood_tags, mood_confidence = infer_mood_from_ra(title, description, artist_names, venue_name)
    genre_tags = extract_genre_tags_ra(title, description, artist_names)

    # Get region
    region = get_london_region(area)

    normalized = {
        "event_id": f"ra_{event_id}",
        "event_name": title,
        "venue_name": venue_name,
        "date": date_str,
        "time": time_str,
        "area": area,
        "region": region,
        "genre_tags": genre_tags,
        "mood_tags": mood_tags,
        "mood_confidence": mood_confidence,
        "artists": artist_names[:10],  # Limit to 10 artists
        "price_range": price_range,
        "price_min": price_min,
        "price_max": price_max,
        "url": url,
        "description": description[:500] if description else "",
        "source": "resident_advisor",
        "fetched_at": datetime.now().isoformat(),
        "filter_passed": True
    }

    return normalized


def infer_mood_from_ra(title, description, artists, venue):
    """
    Infer mood tags from RA event data.

    Returns:
        tuple: (list of mood tags, confidence score)
    """
    if not HAS_CONFIG:
        return ["Late-Night Lark", "Curious Encounters"], 0.6

    # Combine all text for analysis
    combined = f"{title} {description} {' '.join(artists)} {venue}".lower()

    mood_scores = {}

    for mood, keywords in MOOD_INFERENCE_MAP.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in combined:
                score += 1
        if score > 0:
            mood_scores[mood] = min(score / 3.0, 1.0)

    if not mood_scores:
        # Default for RA events (electronic/dance focus)
        return ["Late-Night Lark", "Group Energy"], 0.65

    # Return top 2 moods
    sorted_moods = sorted(mood_scores.items(), key=lambda x: x[1], reverse=True)
    top_moods = [mood for mood, score in sorted_moods[:2]]
    max_confidence = sorted_moods[0][1] if sorted_moods else 0.5

    return top_moods, max_confidence


def extract_genre_tags_ra(title, description, artists):
    """
    Extract genre tags from RA event data.
    """
    combined = f"{title} {description} {' '.join(artists)}".lower()

    # RA-specific genre keywords
    genre_keywords = {
        "techno": ["techno"],
        "house": ["house", "deep house", "tech house"],
        "drum and bass": ["drum and bass", "dnb", "jungle"],
        "ambient": ["ambient", "atmospheric"],
        "experimental": ["experimental", "avant-garde"],
        "electronic": ["electronic", "electronica"],
        "disco": ["disco", "nu-disco"],
        "dub": ["dub", "dubstep"],
        "breaks": ["breaks", "breakbeat"],
        "minimal": ["minimal"],
        "industrial": ["industrial", "ebm"],
        "trance": ["trance", "psytrance"],
        "garage": ["garage", "uk garage"],
        "grime": ["grime"],
    }

    found_genres = []
    for genre, keywords in genre_keywords.items():
        for keyword in keywords:
            if keyword in combined:
                found_genres.append(genre)
                break

    if not found_genres:
        found_genres = ["electronic", "underground"]

    return list(set(found_genres))[:5]  # Dedupe and limit


def get_london_region(area_name):
    """
    Map area name to London region.
    """
    if not HAS_CONFIG:
        return "London"

    area_lower = area_name.lower()

    # Check config mapping first
    for area_key, region in AREA_TO_REGION.items():
        if area_key in area_lower:
            return region

    # Fallback mapping
    ra_area_map = {
        "east london": "East London",
        "south london": "South London",
        "north london": "North London",
        "west london": "West London",
        "central london": "Central London",
        "shoreditch": "East London",
        "hackney": "East London",
        "dalston": "East London",
        "brixton": "South London",
        "peckham": "South London",
        "camden": "North London",
        "islington": "North London",
        "vauxhall": "South London",
    }

    for key, region in ra_area_map.items():
        if key in area_lower:
            return region

    return "London"


def filter_for_lark_vibe(events):
    """
    Filter events to match the Lark's curatorial vision.
    Excludes mainstream/corporate events.
    """
    if not HAS_CONFIG:
        return events

    filtered = []

    for event in events:
        # Combine searchable text
        title = event.get("event_name", "").lower()
        venue = event.get("venue_name", "").lower()
        description = event.get("description", "").lower()
        combined = f"{title} {venue} {description}"

        # Check for excluded keywords
        excluded = False
        for keyword in GENRE_KEYWORDS_EXCLUDE:
            if keyword.lower() in combined:
                excluded = True
                break

        if excluded:
            continue

        # Check venue exclusions
        for keyword in VENUE_KEYWORDS_EXCLUDE:
            if keyword.lower() in venue:
                excluded = True
                break

        if excluded:
            continue

        filtered.append(event)

    return filtered


def fetch_and_filter_ra_events(days_ahead=30, max_events=100):
    """
    Main function: Fetch RA events and filter for Lark's vibe.

    Returns:
        list: Filtered and normalized events
    """
    # Fetch raw events
    raw_events = fetch_ra_events_apify(days_ahead=days_ahead, max_events=max_events)

    if not raw_events:
        print("   No events fetched from RA")
        return []

    print(f"   Fetched {len(raw_events)} raw events from RA")

    # Normalize events
    normalized_events = []
    for raw_event in raw_events:
        try:
            normalized = normalize_ra_event(raw_event)
            normalized_events.append(normalized)
        except Exception as e:
            print(f"   Warning: Could not normalize event: {e}")
            continue

    print(f"   Normalized {len(normalized_events)} events")

    # Filter for Lark's vibe
    filtered_events = filter_for_lark_vibe(normalized_events)
    print(f"   After filtering: {len(filtered_events)} events match the Lark's vibe")

    return filtered_events


def save_events(events, filename="ra_events.json"):
    """Save events to JSON file."""
    output_path = Path(__file__).parent.parent / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    return output_path


if __name__ == "__main__":
    print("=" * 70)
    print("  LONDON LARK - RESIDENT ADVISOR FETCHER (Apify)")
    print("=" * 70)
    print()

    # Fetch and filter events
    events = fetch_and_filter_ra_events(days_ahead=14, max_events=50)

    if events:
        # Save events
        output_path = save_events(events)
        print(f"\n✓ Saved {len(events)} events to {output_path}")

        # Show sample
        print("\n" + "=" * 70)
        print("  SAMPLE EVENTS (first 3)")
        print("=" * 70)

        for i, event in enumerate(events[:3], 1):
            print(f"\n{i}. {event['event_name']}")
            print(f"   Venue: {event['venue_name']}")
            print(f"   Date: {event['date']} at {event['time']}")
            print(f"   Area: {event['area']} ({event['region']})")
            print(f"   Mood: {', '.join(event['mood_tags'])} (conf: {event['mood_confidence']:.2f})")
            print(f"   Price: {event['price_range']}")
            if event.get('artists'):
                print(f"   Artists: {', '.join(event['artists'][:3])}")
            print(f"   URL: {event['url']}")

        # Mood distribution
        print("\n" + "=" * 70)
        print("  MOOD DISTRIBUTION")
        print("=" * 70)
        mood_counts = {}
        for event in events:
            for mood in event.get("mood_tags", []):
                mood_counts[mood] = mood_counts.get(mood, 0) + 1

        for mood, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {mood}: {count}")
    else:
        print("\nNo events fetched. Check Apify token and actor availability.")

    print("\n" + "=" * 70)
    print("  FETCH COMPLETE")
    print("=" * 70)
