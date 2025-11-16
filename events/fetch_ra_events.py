#!/usr/bin/env python3
"""
Resident Advisor Event Fetcher for The London Lark

Fetches upcoming events from RA's GraphQL API and filters for
events matching the Lark's curatorial vision (underground, indie,
niche venues - no mainstream/corporate events).
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import event_config
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from event_config import (
        GENRE_KEYWORDS_INCLUDE,
        GENRE_KEYWORDS_EXCLUDE,
        VENUE_KEYWORDS_EXCLUDE,
        MAX_VENUE_CAPACITY,
        MOOD_INFERENCE_MAP,
        AREA_TO_REGION
    )
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False
    print("Warning: event_config.py not found, filtering disabled")


def fetch_ra_events(area_id=13, days_ahead=30):
    """
    Fetch events from Resident Advisor GraphQL API
    area_id=13 is London
    """

    url = "https://ra.co/graphql"

    # RA requires a user-agent header
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }

    # Calculate date range
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    # GraphQL query
    query = """
    query GET_EVENTS($filters: FilterInputDtoInput, $pageSize: Int, $page: Int) {
      eventListings(filters: $filters, pageSize: $pageSize, page: $page) {
        data {
          id
          listingDate
          event {
            id
            title
            startTime
            endTime
            venue {
              id
              name
              address
              area {
                name
              }
            }
            artists {
              name
            }
            contentUrl
          }
        }
      }
    }
    """

    variables = {
        "filters": {
            "areas": {"eq": area_id},
            "listingDate": {
                "gte": start_date,
                "lte": end_date
            }
        },
        "pageSize": 50,
        "page": 1
    }

    payload = {
        "query": query,
        "variables": variables
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Parse and format events
        events = []
        if "data" in data and "eventListings" in data["data"]:
            for listing in data["data"]["eventListings"]["data"]:
                event = listing["event"]
                venue = event["venue"]

                events.append({
                    "id": f"ra_{event['id']}",
                    "title": event["title"],
                    "date": listing["listingDate"],
                    "time": event.get("startTime", ""),
                    "venue": venue["name"],
                    "area": venue["area"]["name"] if venue.get("area") else "",
                    "artists": [artist["name"] for artist in event.get("artists", [])],
                    "url": f"https://ra.co{event['contentUrl']}" if event.get("contentUrl") else "",
                    "source": "Resident Advisor"
                })

        return events

    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RA events: {e}")
        return []
    except Exception as e:
        print(f"Error parsing RA events: {e}")
        return []


def filter_for_lark_vibe(events):
    """
    Filter RA events to match the Lark's curatorial vision.

    - Exclude mainstream/corporate venues
    - Prefer underground, indie, experimental events
    - Infer mood tags from event data
    """
    if not HAS_CONFIG:
        return events  # Return unfiltered if no config

    filtered_events = []

    for event in events:
        # Combine searchable text
        title_lower = event.get("title", "").lower()
        venue_lower = event.get("venue", "").lower()
        artists_text = " ".join(event.get("artists", [])).lower()
        combined_text = f"{title_lower} {venue_lower} {artists_text}"

        # Check for excluded keywords
        has_excluded = False
        for keyword in GENRE_KEYWORDS_EXCLUDE:
            if keyword.lower() in combined_text:
                has_excluded = True
                break

        if has_excluded:
            continue

        # Check for excluded venue keywords
        venue_excluded = False
        for keyword in VENUE_KEYWORDS_EXCLUDE:
            if keyword.lower() in venue_lower:
                venue_excluded = True
                break

        if venue_excluded:
            continue

        # Infer mood tags
        mood_tags, confidence = infer_mood_from_ra_event(event)

        # Convert to standard format
        normalized_event = {
            "event_id": event["id"],
            "event_name": event["title"],
            "venue_name": event["venue"],
            "date": event["date"],
            "time": event["time"],
            "area": event["area"],
            "region": get_london_region(event["area"]),
            "genre_tags": extract_genre_tags(event),
            "mood_tags": mood_tags,
            "mood_confidence": confidence,
            "artists": event.get("artists", []),
            "url": event["url"],
            "source": "resident_advisor",
            "fetched_at": datetime.now().isoformat(),
            "filter_passed": True
        }

        filtered_events.append(normalized_event)

    return filtered_events


def infer_mood_from_ra_event(event):
    """
    Infer mood tags from RA event data.
    Returns (list of mood tags, confidence score).
    """
    if not HAS_CONFIG:
        return ["Curious Encounters"], 0.5

    title = event.get("title", "").lower()
    venue = event.get("venue", "").lower()
    artists = " ".join(event.get("artists", [])).lower()
    combined = f"{title} {venue} {artists}"

    mood_scores = {}

    for mood, keywords in MOOD_INFERENCE_MAP.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in combined:
                score += 1
        if score > 0:
            mood_scores[mood] = min(score / 3.0, 1.0)

    if not mood_scores:
        # Default for RA events (often electronic/underground)
        return ["Late-Night Lark", "Curious Encounters"], 0.6

    # Sort by score and return top moods
    sorted_moods = sorted(mood_scores.items(), key=lambda x: x[1], reverse=True)
    top_moods = [mood for mood, score in sorted_moods[:2]]
    max_confidence = sorted_moods[0][1] if sorted_moods else 0.5

    return top_moods, max_confidence


def extract_genre_tags(event):
    """
    Extract genre tags from event title and artists.
    """
    title = event.get("title", "").lower()
    artists = " ".join(event.get("artists", [])).lower()
    combined = f"{title} {artists}"

    # Common RA genre keywords
    genre_keywords = [
        "techno", "house", "drum and bass", "dnb", "jungle",
        "ambient", "experimental", "electronic", "disco",
        "dub", "reggae", "breaks", "electro", "minimal",
        "industrial", "noise", "drone", "modular"
    ]

    found_genres = []
    for genre in genre_keywords:
        if genre in combined:
            found_genres.append(genre)

    # Default if nothing found
    if not found_genres:
        found_genres = ["electronic", "underground"]

    return found_genres


def get_london_region(area_name):
    """
    Map RA area name to London region.
    """
    if not HAS_CONFIG:
        return "London"

    area_lower = area_name.lower()

    for area_key, region in AREA_TO_REGION.items():
        if area_key in area_lower:
            return region

    # Default mapping for common RA areas
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
    }

    for key, region in ra_area_map.items():
        if key in area_lower:
            return region

    return "London"


def save_ra_events(events, filename="ra_events.json"):
    """
    Save fetched RA events to JSON file.
    """
    output_path = Path(__file__).parent.parent / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    return output_path


if __name__ == "__main__":
    print("=" * 70)
    print("  LONDON LARK - RESIDENT ADVISOR FETCHER")
    print("=" * 70)
    print()

    # Fetch raw events
    print("Fetching events from Resident Advisor...")
    raw_events = fetch_ra_events(days_ahead=14)
    print(f"Found {len(raw_events)} raw events from RA")

    if not raw_events:
        print("\nNo events fetched. This could mean:")
        print("- RA API requires authentication or has changed")
        print("- Network/connection issue")
        print("- Rate limiting")
        print("\nTry again later or check the API documentation.")
    else:
        # Filter for Lark's vibe
        print("\nFiltering for the Lark's curatorial vision...")
        filtered_events = filter_for_lark_vibe(raw_events)
        print(f"After filtering: {len(filtered_events)} events match the Lark's vibe")

        # Save filtered events
        output_path = save_ra_events(filtered_events)
        print(f"\nSaved filtered events to: {output_path}")

        # Print sample events
        print("\n" + "=" * 70)
        print("  SAMPLE EVENTS (first 3)")
        print("=" * 70)

        for i, event in enumerate(filtered_events[:3], 1):
            print(f"\n{i}. {event['event_name']}")
            print(f"   Venue: {event['venue_name']}")
            print(f"   Date: {event['date']} at {event['time']}")
            print(f"   Area: {event['area']} ({event['region']})")
            print(f"   Mood: {', '.join(event['mood_tags'])} (confidence: {event['mood_confidence']:.2f})")
            print(f"   Genres: {', '.join(event['genre_tags'])}")
            if event.get('artists'):
                print(f"   Artists: {', '.join(event['artists'][:5])}")
            print(f"   URL: {event['url']}")

        # Mood distribution
        if filtered_events:
            print("\n" + "=" * 70)
            print("  MOOD DISTRIBUTION")
            print("=" * 70)
            mood_counts = {}
            for event in filtered_events:
                for mood in event.get("mood_tags", []):
                    mood_counts[mood] = mood_counts.get(mood, 0) + 1

            for mood, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {mood}: {count}")

    print("\n" + "=" * 70)
    print("  FETCH COMPLETE")
    print("=" * 70)
