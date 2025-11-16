#!/usr/bin/env python3
"""
Event Import System for The London Lark

Since web scraping is blocked, this provides a way to:
1. Import event data from CSV/JSON files
2. Match events to our curated venue list
3. Infer mood tags and filter appropriately

This is a pragmatic solution that WILL work.
"""

import json
import csv
import sys
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher

sys.path.insert(0, str(Path(__file__).parent.parent))
from mock_event_generator import load_venues


def fuzzy_match_venue(event_venue_name, curated_venues, threshold=0.6):
    """
    Fuzzy match an event venue name to our curated list.

    Args:
        event_venue_name: Name of venue from scraped event
        curated_venues: List of our curated venue dicts
        threshold: Minimum similarity score (0-1)

    Returns:
        tuple: (matched_venue_dict, score) or (None, 0)
    """
    best_match = None
    best_score = 0

    event_name_lower = event_venue_name.lower().strip()

    for venue in curated_venues:
        venue_display = venue.get("display_name", "").lower()

        # Try exact match first
        if event_name_lower == venue_display:
            return venue, 1.0

        # Try "the" prefix variations
        if event_name_lower.startswith("the ") and event_name_lower[4:] == venue_display:
            return venue, 0.95
        if venue_display.startswith("the ") and venue_display[4:] == event_name_lower:
            return venue, 0.95

        # Fuzzy match
        score = SequenceMatcher(None, event_name_lower, venue_display).ratio()
        if score > best_score:
            best_score = score
            best_match = venue

        # Also check if one is substring of other
        if event_name_lower in venue_display or venue_display in event_name_lower:
            substring_score = len(min(event_name_lower, venue_display, key=len)) / len(max(event_name_lower, venue_display, key=len))
            if substring_score > best_score:
                best_score = substring_score
                best_match = venue

    if best_score >= threshold:
        return best_match, best_score

    return None, 0


def infer_mood_from_text(text):
    """
    Infer mood tags from event description/title.

    Returns:
        tuple: (list of mood tags, confidence)
    """
    text_lower = text.lower()

    # Simple keyword-based mood inference
    mood_keywords = {
        "Folk & Intimate": ["folk", "acoustic", "singer-songwriter", "intimate", "candlelit"],
        "Queer Revelry": ["queer", "lgbtq", "drag", "pride", "gay"],
        "The Thoughtful Stage": ["theatre", "theater", "play", "drama", "new writing"],
        "Poetic": ["poetry", "spoken word", "verse", "poet"],
        "Global Rhythms": ["afrobeat", "world music", "latin", "reggae", "ska"],
        "Melancholic Beauty": ["blues", "torch songs", "melancholy", "sad songs"],
        "Jazz & Contemplation": ["jazz", "bebop", "improvisation"],
        "Curious Encounters": ["experimental", "avant-garde", "strange", "unusual"],
        "Cabaret & Glitter": ["cabaret", "burlesque", "sequins", "variety"],
        "Big Night Out": ["live band", "rock", "indie", "dance"],
        "Comic Relief": ["comedy", "stand-up", "improv", "funny"],
        "Late-Night Lark": ["midnight", "late night", "after hours"],
    }

    found_moods = []
    for mood, keywords in mood_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_moods.append(mood)
                break

    if found_moods:
        return found_moods[:2], min(0.6 + 0.1 * len(found_moods), 0.9)

    return ["Curious Encounters"], 0.5


def import_from_json(json_file):
    """
    Import events from a JSON file.

    Supports two formats:
    1. Direct list of events:
       [{"event_name": ..., "venue_name": ..., "date": ...}, ...]

    2. Wrapped with metadata (from local_scraper.py):
       {"scraped_at": ..., "events": [...]}
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle wrapped format (from local_scraper.py)
    if isinstance(data, dict) and "events" in data:
        raw_events = data["events"]
        print(f"  Detected scraper output format (scraped at {data.get('scraped_at', 'unknown')})")
    elif isinstance(data, list):
        raw_events = data
    else:
        raise ValueError("Unsupported JSON format. Expected list or dict with 'events' key.")

    events = []
    for item in raw_events:
        # Support multiple field name conventions
        events.append({
            "event_name": item.get("event_name", item.get("name", item.get("title", "Unknown"))),
            "venue_name": item.get("venue_name", item.get("venue", "")),
            "date": item.get("date", ""),
            "time": item.get("time", item.get("start_time", "20:00")),
            "description": item.get("description", ""),
            "url": item.get("url", item.get("link", "")),
            "source": item.get("source", "json_import"),
            "mood_tags": item.get("mood_tags", [])  # Preserve if already set
        })

    return events


def import_from_csv(csv_file):
    """
    Import events from a CSV file.

    Expected columns: name, venue, date, time, description, url
    """
    events = []

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append({
                "event_name": row.get("name", row.get("title", "Unknown")),
                "venue_name": row.get("venue", row.get("venue_name", "")),
                "date": row.get("date", ""),
                "time": row.get("time", row.get("start_time", "")),
                "description": row.get("description", ""),
                "url": row.get("url", row.get("link", "")),
                "source": "csv_import"
            })

    return events


def match_and_enrich_events(raw_events, curated_venues):
    """
    Match imported events to curated venues and enrich with metadata.

    Returns:
        tuple: (matched_events, unmatched_events)
    """
    matched = []
    unmatched = []

    for event in raw_events:
        venue_name = event.get("venue_name", "")

        if not venue_name:
            unmatched.append(event)
            continue

        # Try to match to curated venue
        matched_venue, score = fuzzy_match_venue(venue_name, curated_venues)

        if matched_venue:
            # Enrich with venue data
            description = event.get("description", "") + " " + matched_venue.get("tone_notes", "")
            mood_tags, mood_confidence = infer_mood_from_text(description)

            # Priority: 1. Venue mood tags, 2. Scraper mood tags, 3. Inferred
            if matched_venue.get("mood_tags"):
                mood_tags = matched_venue["mood_tags"][:2]
                mood_confidence = 0.9
            elif event.get("mood_tags") and len(event.get("mood_tags", [])) > 0:
                # Use mood tags from scraper if no venue tags
                mood_tags = event["mood_tags"][:2]
                mood_confidence = 0.8

            enriched_event = {
                "event_id": f"import_{hash(event['event_name'] + event['date']) % 100000}",
                "event_name": event["event_name"],
                "venue_name": matched_venue.get("display_name", venue_name),
                "venue_emoji": matched_venue.get("emoji", "🎭"),
                "date": event["date"],
                "time": event["time"],
                "area": matched_venue.get("area", "London"),
                "region": matched_venue.get("area", "London"),
                "location": matched_venue.get("location", ""),
                "genre_tags": extract_genres(event["event_name"] + " " + event.get("description", "")),
                "mood_tags": mood_tags,
                "mood_confidence": mood_confidence,
                "price_range": "TBC",
                "price_min": 0,
                "price_max": 0,
                "url": event.get("url", matched_venue.get("website", "")),
                "description": event.get("description", matched_venue.get("tone_notes", ""))[:500],
                "lark_fit": matched_venue.get("lark_fit_notes", ""),
                "source": "imported_real",
                "venue_match_score": round(score, 2),
                "fetched_at": datetime.now().isoformat(),
                "filter_passed": True
            }
            matched.append(enriched_event)
        else:
            unmatched.append(event)

    return matched, unmatched


def extract_genres(text):
    """Extract genre tags from text."""
    text_lower = text.lower()
    genres = []

    genre_keywords = {
        "folk": ["folk", "acoustic"],
        "jazz": ["jazz"],
        "theatre": ["theatre", "theater", "play"],
        "comedy": ["comedy", "stand-up"],
        "electronic": ["electronic", "techno", "house"],
        "rock": ["rock", "indie", "punk"],
        "poetry": ["poetry", "spoken word"],
        "world music": ["world", "afro", "latin"],
    }

    for genre, keywords in genre_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                genres.append(genre)
                break

    return genres if genres else ["live performance"]


def create_sample_import_data():
    """
    Create sample import data for testing.

    This simulates what you'd get from manually copying events from websites.
    """
    # Load venues to get real venue names
    venues = load_venues()

    # Create events for some of our actual venues
    sample_events = []

    # Pick 15 random venues and create events for them
    import random
    selected_venues = random.sample(venues, min(15, len(venues)))

    event_types = [
        "Live Music Night",
        "Open Mic Session",
        "Jazz Evening",
        "Folk Acoustic Set",
        "Comedy Night",
        "Poetry Reading",
        "Theatre Performance",
        "DJ Set",
        "Band Showcase",
        "Acoustic Sessions",
    ]

    from datetime import timedelta
    today = datetime.now()

    for i, venue in enumerate(selected_venues):
        # Create 1-2 events per venue
        num_events = random.choice([1, 2])

        for j in range(num_events):
            days_ahead = random.randint(0, 10)
            event_date = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            event_time = random.choice(["19:00", "19:30", "20:00", "20:30", "21:00"])

            event_name = random.choice(event_types)

            # Add venue-specific flavor
            if "jazz" in venue.get("type", "").lower():
                event_name = "Jazz: " + random.choice(["Quartet Night", "Trio Session", "Standards Evening"])
            elif "folk" in venue.get("type", "").lower():
                event_name = "Folk: " + random.choice(["Acoustic Circle", "Singalong", "Open Floor"])
            elif "theatre" in venue.get("type", "").lower():
                event_name = random.choice(["New Writing Showcase", "One-Act Plays", "Devised Theatre"])

            sample_events.append({
                "name": event_name,
                "venue": venue.get("display_name", venue.get("name", "")),
                "date": event_date,
                "time": event_time,
                "description": f"An evening at {venue.get('display_name', '')}. {venue.get('tone_notes', '')}",
                "url": venue.get("website", "")
            })

    return sample_events


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Import events from JSON/CSV files into The London Lark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scrapers/import_events.py scraped_events.json     # Import from scraper output
  python scrapers/import_events.py events.csv             # Import from CSV
  python scrapers/import_events.py --demo                 # Run demo with sample data
        """
    )

    parser.add_argument(
        'input_file',
        nargs='?',
        help='JSON or CSV file to import (or use --demo for sample data)'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demo with generated sample data'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='imported_real_events.json',
        help='Output file for matched events (default: imported_real_events.json)'
    )

    args = parser.parse_args()

    # Run demo mode or import from file
    if args.demo or not args.input_file:
        print("=" * 70)
        print("  EVENT IMPORT SYSTEM - DEMO")
        print("=" * 70)
        print()

        # Create sample data
        print("Creating sample import data (simulated real events)...")
        sample_events = create_sample_import_data()

        # Save sample for inspection
        with open("sample_import_data.json", "w", encoding="utf-8") as f:
            json.dump(sample_events, f, indent=2, ensure_ascii=False)
        print(f"✓ Created {len(sample_events)} sample events")
        print("  Saved to sample_import_data.json")

        input_file = "sample_import_data.json"
    else:
        input_file = args.input_file
        print("=" * 70)
        print("  EVENT IMPORT SYSTEM")
        print("=" * 70)
        print()

    # Load curated venues
    print("Loading curated venues...")
    venues = load_venues()
    print(f"✓ Loaded {len(venues)} curated venues")

    # Import the data
    print(f"\nImporting events from {input_file}...")
    if input_file.endswith('.csv'):
        imported_events = import_from_csv(input_file)
    else:
        imported_events = import_from_json(input_file)
    print(f"✓ Imported {len(imported_events)} events")

    if not imported_events:
        print("❌ No events found in file!")
        sys.exit(1)

    # Match to venues
    print("\nMatching to curated venues...")
    matched, unmatched = match_and_enrich_events(imported_events, venues)
    print(f"✓ Matched: {len(matched)} events")
    print(f"  Unmatched: {len(unmatched)} events")

    if unmatched:
        print(f"\n⚠️ Unmatched venues (not in curated list):")
        for i, event in enumerate(unmatched[:10], 1):
            print(f"  {i}. {event.get('venue_name', 'Unknown')} - {event.get('event_name', 'Unknown')}")
        if len(unmatched) > 10:
            print(f"  ... and {len(unmatched) - 10} more")

    # Save matched events
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(matched, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved matched events to {args.output}")

    # Show sample
    if matched:
        print("\n" + "=" * 70)
        print("  MATCHED REAL EVENTS (first 10)")
        print("=" * 70)

        for i, event in enumerate(matched[:10], 1):
            print(f"\n{i}. {event['venue_emoji']} {event['event_name']}")
            print(f"   Venue: {event['venue_name']} (match: {event['venue_match_score']})")
            print(f"   Date: {event['date']} at {event['time']}")
            print(f"   Area: {event['area']}")
            print(f"   Mood: {', '.join(event['mood_tags'])} (conf: {event['mood_confidence']})")

        # Show mood distribution
        print("\n" + "=" * 70)
        print("  MOOD DISTRIBUTION")
        print("=" * 70)

        mood_counts = {}
        for event in matched:
            for mood in event.get("mood_tags", []):
                mood_counts[mood] = mood_counts.get(mood, 0) + 1

        for mood, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {mood}: {count}")

    print("\n" + "=" * 70)
    print("  IMPORT COMPLETE - REAL DATA READY")
    print("=" * 70)
    print(f"\n✅ The Lark can now use events from {args.output}")
    print("   Start app.py and test queries to see real event recommendations!")
