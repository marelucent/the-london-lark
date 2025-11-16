#!/usr/bin/env python3
"""
Dice.fm Event Fetcher for The London Lark

Uses Apify's Dice.fm scraper to fetch upcoming events in London.
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
DICE_ACTOR_ID = "lexis-solutions/dice-fm"


def fetch_dice_events_apify(days_ahead=30, max_events=100):
    """
    Fetch events from Dice.fm using Apify scraper.

    Args:
        days_ahead: Number of days to look ahead
        max_events: Maximum number of events to fetch

    Returns:
        list: Raw events from Dice scraper
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

    print(f"   Calling Apify Dice.fm scraper for London events ({start_date} to {end_date})...")

    try:
        # Run the actor and wait for it to finish
        run = client.actor(DICE_ACTOR_ID).call(run_input=run_input)

        # Fetch results from the dataset
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items

        return dataset_items

    except Exception as e:
        print(f"   Error running Apify Dice scraper: {e}")
        return []


def normalize_dice_event(raw_event):
    """
    Convert raw Dice scraper data to our standard event format.

    Args:
        raw_event: Raw event dict from Apify scraper

    Returns:
        dict: Normalized event in Lark format
    """
    # Extract basic info (adjust field names based on actual scraper output)
    event_id = raw_event.get("id", raw_event.get("eventId", str(hash(raw_event.get("title", "")))))
    title = raw_event.get("title", raw_event.get("name", "Untitled Event"))

    # Date and time - Dice often uses ISO format
    date_str = ""
    time_str = ""

    # Try different date field names
    datetime_field = raw_event.get("datetime", raw_event.get("startDate", raw_event.get("date", "")))
    if datetime_field:
        try:
            if isinstance(datetime_field, str):
                # Handle ISO format
                if "T" in datetime_field:
                    dt = datetime.fromisoformat(datetime_field.replace("Z", "+00:00"))
                else:
                    dt = datetime.strptime(datetime_field, "%Y-%m-%d")
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M") if "T" in datetime_field else ""
            else:
                date_str = str(datetime_field)
        except:
            date_str = str(datetime_field)

    if not time_str:
        time_str = raw_event.get("startTime", raw_event.get("time", ""))

    # Venue info - Dice structure may vary
    venue_data = raw_event.get("venue", {})
    if isinstance(venue_data, dict):
        venue_name = venue_data.get("name", "Unknown Venue")
        area = venue_data.get("area", venue_data.get("address", {}).get("area", "London"))
        if isinstance(area, dict):
            area = area.get("name", "London")
    else:
        venue_name = raw_event.get("venueName", str(venue_data) if venue_data else "Unknown Venue")
        area = raw_event.get("area", raw_event.get("location", "London"))

    # Artists/lineup
    artists = raw_event.get("artists", raw_event.get("lineup", []))
    if isinstance(artists, list):
        artist_names = [a.get("name", str(a)) if isinstance(a, dict) else str(a) for a in artists]
    elif isinstance(artists, str):
        artist_names = [artists]
    else:
        artist_names = []

    # URL
    url = raw_event.get("url", raw_event.get("link", ""))
    if url and not url.startswith("http"):
        url = f"https://dice.fm{url}"

    # Description
    description = raw_event.get("description", raw_event.get("about", ""))
    if isinstance(description, list):
        description = " ".join(description)

    # Price - Dice shows ticket prices
    price_info = raw_event.get("price", raw_event.get("tickets", {}))
    price_min = 0
    price_max = 0

    if isinstance(price_info, dict):
        price_min = float(price_info.get("min", price_info.get("from", 0)))
        price_max = float(price_info.get("max", price_info.get("to", price_min)))
    elif isinstance(price_info, (int, float)):
        price_min = float(price_info)
        price_max = price_min
    elif isinstance(price_info, str):
        # Try to parse "£12.50" format
        try:
            price_str = price_info.replace("£", "").replace(",", "").strip()
            if "-" in price_str:
                parts = price_str.split("-")
                price_min = float(parts[0].strip())
                price_max = float(parts[1].strip())
            else:
                price_min = float(price_str)
                price_max = price_min
        except:
            pass

    # Check for free events
    is_free = raw_event.get("isFree", False) or price_min == 0

    # Classify price range
    if is_free:
        price_range = "Free"
    elif price_max <= 10:
        price_range = "£"
    elif price_max <= 20:
        price_range = "££"
    elif price_max <= 35:
        price_range = "£££"
    else:
        price_range = "££££"

    # Genre tags from Dice categories
    genre_tags = extract_genre_tags_dice(raw_event, title, description, artist_names)

    # Infer mood tags
    mood_tags, mood_confidence = infer_mood_from_dice(title, description, artist_names, venue_name, genre_tags)

    # Get region
    region = get_london_region(area)

    normalized = {
        "event_id": f"dice_{event_id}",
        "event_name": title,
        "venue_name": venue_name,
        "date": date_str,
        "time": time_str,
        "area": area,
        "region": region,
        "genre_tags": genre_tags,
        "mood_tags": mood_tags,
        "mood_confidence": mood_confidence,
        "artists": artist_names[:10],
        "price_range": price_range,
        "price_min": price_min,
        "price_max": price_max,
        "url": url,
        "description": description[:500] if description else "",
        "source": "dice_fm",
        "fetched_at": datetime.now().isoformat(),
        "filter_passed": True
    }

    return normalized


def infer_mood_from_dice(title, description, artists, venue, genre_tags):
    """
    Infer mood tags from Dice event data.

    Returns:
        tuple: (list of mood tags, confidence score)
    """
    if not HAS_CONFIG:
        return ["Curious Encounters", "Group Energy"], 0.6

    # Combine all text for analysis
    combined = f"{title} {description} {' '.join(artists)} {venue} {' '.join(genre_tags)}".lower()

    mood_scores = {}

    for mood, keywords in MOOD_INFERENCE_MAP.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in combined:
                score += 1
        if score > 0:
            mood_scores[mood] = min(score / 3.0, 1.0)

    if not mood_scores:
        # Default for Dice events (indie/alternative focus)
        return ["Curious Encounters", "Group Energy"], 0.6

    # Return top 2 moods
    sorted_moods = sorted(mood_scores.items(), key=lambda x: x[1], reverse=True)
    top_moods = [mood for mood, score in sorted_moods[:2]]
    max_confidence = sorted_moods[0][1] if sorted_moods else 0.5

    return top_moods, max_confidence


def extract_genre_tags_dice(raw_event, title, description, artists):
    """
    Extract genre tags from Dice event data.
    """
    # Check for explicit categories/tags from Dice
    categories = raw_event.get("categories", raw_event.get("tags", raw_event.get("genres", [])))
    if isinstance(categories, list):
        genre_tags = [str(c).lower() for c in categories]
    else:
        genre_tags = []

    # Also infer from text
    combined = f"{title} {description} {' '.join(artists)}".lower()

    # Dice-focused genre keywords (more indie/alternative than RA)
    genre_keywords = {
        "indie": ["indie", "independent"],
        "rock": ["rock", "post-punk", "punk"],
        "electronic": ["electronic", "synth"],
        "pop": ["pop", "synth-pop"],
        "hip-hop": ["hip-hop", "hip hop", "rap"],
        "r&b": ["r&b", "rnb", "soul"],
        "jazz": ["jazz"],
        "folk": ["folk", "acoustic"],
        "metal": ["metal", "heavy"],
        "experimental": ["experimental", "avant-garde"],
        "dance": ["dance", "club"],
        "comedy": ["comedy", "stand-up"],
        "spoken word": ["spoken word", "poetry"],
        "theatre": ["theatre", "theater", "performance"],
    }

    for genre, keywords in genre_keywords.items():
        for keyword in keywords:
            if keyword in combined and genre not in genre_tags:
                genre_tags.append(genre)

    if not genre_tags:
        genre_tags = ["live music", "indie"]

    return list(set(genre_tags))[:5]  # Dedupe and limit


def get_london_region(area_name):
    """
    Map area name to London region.
    """
    if not HAS_CONFIG:
        return "London"

    area_lower = str(area_name).lower()

    # Check config mapping first
    for area_key, region in AREA_TO_REGION.items():
        if area_key in area_lower:
            return region

    # Fallback mapping
    dice_area_map = {
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
        "soho": "Central London",
        "kings cross": "Central London",
        "king's cross": "Central London",
    }

    for key, region in dice_area_map.items():
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


def fetch_and_filter_dice_events(days_ahead=30, max_events=100):
    """
    Main function: Fetch Dice events and filter for Lark's vibe.

    Returns:
        list: Filtered and normalized events
    """
    # Fetch raw events
    raw_events = fetch_dice_events_apify(days_ahead=days_ahead, max_events=max_events)

    if not raw_events:
        print("   No events fetched from Dice.fm")
        return []

    print(f"   Fetched {len(raw_events)} raw events from Dice.fm")

    # Normalize events
    normalized_events = []
    for raw_event in raw_events:
        try:
            normalized = normalize_dice_event(raw_event)
            normalized_events.append(normalized)
        except Exception as e:
            print(f"   Warning: Could not normalize event: {e}")
            continue

    print(f"   Normalized {len(normalized_events)} events")

    # Filter for Lark's vibe
    filtered_events = filter_for_lark_vibe(normalized_events)
    print(f"   After filtering: {len(filtered_events)} events match the Lark's vibe")

    return filtered_events


def save_events(events, filename="dice_events.json"):
    """Save events to JSON file."""
    output_path = Path(__file__).parent.parent / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    return output_path


if __name__ == "__main__":
    print("=" * 70)
    print("  LONDON LARK - DICE.FM FETCHER (Apify)")
    print("=" * 70)
    print()

    # Fetch and filter events
    events = fetch_and_filter_dice_events(days_ahead=14, max_events=50)

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
            print(f"   Genres: {', '.join(event['genre_tags'])}")
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
