#!/usr/bin/env python3
"""
Mock Event Generator for The London Lark

Generates realistic mock events using venues from lark_venues_clean.json.
Creates diverse events with proper mood tags, dates, and prices.
"""

import json
import random
import re
from datetime import datetime, timedelta
from pathlib import Path

# Load from the CLEAN venue list
VENUES_FILE = Path(__file__).parent / "lark_venues_clean.json"

# Venues to EXCLUDE (removed from curation)
EXCLUDED_VENUES = [
    "Streatham Space Project",
    "The Château",
    "Château",
]


def parse_multiline_venue(venue_obj):
    """
    Parse a venue from lark_venues_clean.json format.

    The format is:
    {
      "name": "🌿 Hootananny Brixton\nType: Live music pub\nLocation: ..."
    }
    """
    if not venue_obj or "name" not in venue_obj:
        return None

    raw_text = venue_obj["name"]
    lines = raw_text.split("\n")

    if not lines:
        return None

    # First line is the full name with emoji
    full_name = lines[0].strip()

    # Extract emoji from the start
    emoji = ""
    display_name = full_name
    if full_name and len(full_name) > 0:
        # Check if first character is an emoji (non-ASCII)
        first_char = full_name[0]
        if ord(first_char) > 127:
            emoji = first_char
            display_name = full_name[1:].strip()
        elif len(full_name) > 1 and ord(full_name[1]) > 127:
            # Sometimes emoji is second char
            emoji = full_name[:2]
            display_name = full_name[2:].strip()

    # Parse other fields
    venue_data = {
        "name": full_name,
        "emoji": emoji,
        "display_name": display_name,
        "type": "",
        "location": "",
        "website": "",
        "mood_tags": [],
        "tone_notes": "",
        "lark_fit_notes": "",
        "tags": [],
        "area": "London"
    }

    for line in lines[1:]:
        line = line.strip()
        if line.startswith("Type:"):
            venue_data["type"] = line.replace("Type:", "").strip()
        elif line.startswith("Location:"):
            venue_data["location"] = line.replace("Location:", "").strip()
        elif line.startswith("Website:"):
            website = line.replace("Website:", "").strip()
            # Clean up website
            if website and not website.startswith("http"):
                if not website.startswith("("):  # Skip placeholders like "(venue social media...)"
                    website = "https://" + website
            venue_data["website"] = website
        elif line.startswith("Mapped Mood Tags:"):
            tags_str = line.replace("Mapped Mood Tags:", "").strip()
            venue_data["mood_tags"] = [t.strip() for t in tags_str.split(",")]
        elif line.startswith("Tone Notes:"):
            venue_data["tone_notes"] = line.replace("Tone Notes:", "").strip()
        elif line.startswith("Lark Fit Notes:"):
            venue_data["lark_fit_notes"] = line.replace("Lark Fit Notes:", "").strip()
        elif line.startswith("Tags:"):
            tags_str = line.replace("Tags:", "").strip()
            venue_data["tags"] = [t.strip() for t in tags_str.split("|")]

    # Extract area from tags (look for "🧭 South London" etc.)
    for tag in venue_data["tags"]:
        if "🧭" in tag:
            area = tag.replace("🧭", "").strip()
            venue_data["area"] = area
            break

    return venue_data


def load_venues():
    """Load and parse venues from lark_venues_clean.json."""
    if not VENUES_FILE.exists():
        print(f"Error: {VENUES_FILE} not found")
        return []

    with open(VENUES_FILE, "r", encoding="utf-8") as f:
        raw_venues = json.load(f)

    parsed_venues = []
    seen_names = set()  # Track duplicates

    for raw_venue in raw_venues:
        parsed = parse_multiline_venue(raw_venue)
        if not parsed:
            continue

        # Check for excluded venues
        is_excluded = False
        for excluded in EXCLUDED_VENUES:
            if excluded.lower() in parsed["display_name"].lower():
                is_excluded = True
                break

        if is_excluded:
            continue

        # Check for duplicates
        if parsed["display_name"] in seen_names:
            continue
        seen_names.add(parsed["display_name"])

        parsed_venues.append(parsed)

    return parsed_venues


# Event templates by mood/genre
EVENT_TEMPLATES = {
    "Folk & Intimate": [
        "Candlelit Folk Session",
        "Acoustic Night: Singer-Songwriters",
        "Folk & Ale Evening",
        "Intimate Storytelling Circle",
        "Fireside Folk Songs",
    ],
    "Queer Revelry": [
        "Queer Open Mic Night",
        "Drag Cabaret Spectacular",
        "LGBTQ+ Performance Evening",
        "Queer Variety Show",
        "Pride in Song: Community Showcase",
    ],
    "The Thoughtful Stage": [
        "New Writing Night",
        "One-Act Play Festival",
        "Emerging Playwrights Showcase",
        "Theatre Workshop: Stories from the Margins",
        "Monologue Night",
    ],
    "Poetic": [
        "Poetry Open Mic",
        "Spoken Word & Jazz",
        "Verses in the Dark",
        "Poetry Slam Championships",
        "Words & Wine: Poets Gather",
    ],
    "Global Rhythms": [
        "Afrobeat Live",
        "World Music Night",
        "Balkan Brass Party",
        "Caribbean Rhythms",
        "Global Sounds Collective",
    ],
    "Melancholic Beauty": [
        "Torch Songs & Tales",
        "Evening of Blues & Soul",
        "Melancholy Monday: Sad Songs",
        "Late Night Jazz: The Quiet Hours",
        "Atmospheric Ambient Set",
    ],
    "Curious Encounters": [
        "Experimental Sound Night",
        "Strange Frequencies: Electronic Exploration",
        "The Unexpected: Mystery Performance",
        "Avant-Garde Showcase",
        "Sound Art Installation Opening",
    ],
    "Cabaret & Glitter": [
        "Cabaret Extravaganza",
        "Burlesque & Variety Night",
        "Sequins & Songs",
        "The Glitter Ball: Cabaret Showcase",
        "Feathers & Folly",
    ],
    "Punchy / Protest": [
        "Activist Voices Open Mic",
        "Songs of Resistance",
        "Political Poetry Slam",
        "Radical Folk Night",
        "Punk Poetry & Protest Songs",
    ],
    "Big Night Out": [
        "Live Band Night",
        "Indie Rock Showcase",
        "Saturday Night Live Music Marathon",
        "Multi-Genre Music Festival",
        "Dance Floor Sessions",
    ],
    "Late-Night Lark": [
        "Midnight Jazz Session",
        "After Dark: Electronic Sets",
        "Night Owl's Delight",
        "2am Improv Sessions",
        "Late Night Listening Party",
    ],
    "Dreamlike & Hypnagogic": [
        "Ambient Drone Night",
        "Hypnotic Soundscapes",
        "Dream State: Visual & Audio",
        "Twilight Performance Art",
        "Ethereal Evening",
    ],
    "Wonder & Awe": [
        "Immersive Theatre Experience",
        "Spectacle Night: Circus & Fire",
        "Magic & Music Evening",
        "Awe-Inspiring Performances",
        "The Extraordinary Showcase",
    ],
    "Comic Relief": [
        "Comedy Night",
        "Stand-Up Showcase",
        "Improv Comedy Jam",
        "Funny Folk Songs",
        "Laugh & Listen: Comedy & Music",
    ],
    "Playful & Weird": [
        "Weird & Wonderful Variety Night",
        "Experimental Comedy",
        "The Oddball Showcase",
        "Surreal Performance Evening",
        "Games Night with Live Music",
    ],
}

# Price ranges
PRICE_OPTIONS = [
    ("Free", 0, 0),
    ("£", 5, 8),
    ("£", 8, 10),
    ("££", 10, 15),
    ("££", 12, 18),
    ("£££", 18, 25),
]


def generate_mock_events(num_events=30, days_ahead=14):
    """
    Generate mock events using real venues from lark_venues_clean.json.

    Args:
        num_events: Number of events to generate
        days_ahead: How far ahead to generate events

    Returns:
        list: Mock events in standard format
    """
    venues = load_venues()
    if not venues:
        return []

    print(f"   Loaded {len(venues)} venues from lark_venues_clean.json")

    events = []
    today = datetime.now()

    # Generate events spread across venues and dates
    for i in range(num_events):
        # Pick a random venue
        venue = random.choice(venues)

        # Pick mood tags from the venue
        venue_moods = venue.get("mood_tags", ["Curious Encounters"])
        primary_mood = venue_moods[0] if venue_moods else "Curious Encounters"

        # Get event templates for this mood (or default)
        templates = EVENT_TEMPLATES.get(primary_mood, EVENT_TEMPLATES["Curious Encounters"])
        event_name = random.choice(templates)

        # Generate date (weight towards this week)
        days_offset = random.choices(
            range(days_ahead),
            weights=[max(1, days_ahead - d) for d in range(days_ahead)]
        )[0]
        event_date = today + timedelta(days=days_offset)

        # Generate time (evening focus: 19:00-21:30)
        hour = random.choice([19, 19, 20, 20, 20, 21])
        minute = random.choice([0, 0, 30])
        time_str = f"{hour:02d}:{minute:02d}"

        # Price
        price_range, price_min, price_max = random.choice(PRICE_OPTIONS)

        # Extract genre tags from venue type
        venue_type = venue.get("type", "").lower()
        genre_tags = []
        if "folk" in venue_type or "acoustic" in venue_type:
            genre_tags.append("folk")
        if "jazz" in venue_type:
            genre_tags.append("jazz")
        if "theatre" in venue_type or "theater" in venue_type:
            genre_tags.append("theatre")
        if "music" in venue_type:
            genre_tags.append("live music")
        if not genre_tags:
            genre_tags = ["live performance"]

        # Confidence based on how well event matches venue
        mood_confidence = round(random.uniform(0.75, 0.98), 2)

        # Create event
        event = {
            "event_id": f"mock_{i+1:03d}",
            "event_name": event_name,
            "venue_name": venue.get("display_name", venue.get("name", "Unknown Venue")),
            "venue_emoji": venue.get("emoji", "🎭"),
            "date": event_date.strftime("%Y-%m-%d"),
            "time": time_str,
            "area": venue.get("area", "London"),
            "region": venue.get("area", "London"),
            "location": venue.get("location", ""),
            "genre_tags": genre_tags,
            "mood_tags": venue_moods[:2],  # Top 2 moods
            "mood_confidence": mood_confidence,
            "price_range": price_range,
            "price_min": price_min,
            "price_max": price_max,
            "url": venue.get("website", ""),
            "description": venue.get("tone_notes", ""),
            "lark_fit": venue.get("lark_fit_notes", ""),
            "source": "lark_venues",
            "fetched_at": datetime.now().isoformat(),
            "filter_passed": True
        }

        events.append(event)

    # Sort by date and time
    events.sort(key=lambda x: (x["date"], x["time"]))

    return events


def get_tonight_events(events):
    """Get events happening tonight."""
    today = datetime.now().strftime("%Y-%m-%d")
    return [e for e in events if e["date"] == today]


def get_weekend_events(events):
    """Get events this weekend (Fri-Sun)."""
    today = datetime.now()
    weekend_dates = []

    for i in range(7):
        check_date = today + timedelta(days=i)
        if check_date.weekday() in [4, 5, 6]:  # Fri=4, Sat=5, Sun=6
            weekend_dates.append(check_date.strftime("%Y-%m-%d"))

    return [e for e in events if e["date"] in weekend_dates]


def get_events_by_mood(events, mood):
    """Get events matching a specific mood."""
    return [e for e in events if mood in e.get("mood_tags", [])]


def save_events(events, filename="mock_events.json"):
    """Save events to JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    return filename


if __name__ == "__main__":
    print("=" * 70)
    print("  LONDON LARK - MOCK EVENT GENERATOR")
    print("=" * 70)
    print()
    print(f"  Loading from: {VENUES_FILE}")
    print(f"  Excluding: {', '.join(EXCLUDED_VENUES)}")
    print()

    # Generate events
    events = generate_mock_events(num_events=30, days_ahead=14)
    print(f"✓ Generated {len(events)} mock events")

    # Verify excluded venues are NOT present
    excluded_found = []
    for event in events:
        for excluded in EXCLUDED_VENUES:
            if excluded.lower() in event["venue_name"].lower():
                excluded_found.append(event["venue_name"])

    if excluded_found:
        print(f"⚠️  WARNING: Found excluded venues in events: {excluded_found}")
    else:
        print("✓ Confirmed: No excluded venues in generated events")

    # Save events
    output_file = save_events(events)
    print(f"✓ Saved to {output_file}")

    # Show unique venues used
    unique_venues = set(e["venue_name"] for e in events)
    print(f"✓ Used {len(unique_venues)} unique venues")

    # Show sample
    print("\n" + "=" * 70)
    print("  SAMPLE EVENTS (first 5)")
    print("=" * 70)

    for i, event in enumerate(events[:5], 1):
        print(f"\n{i}. {event['venue_emoji']} {event['event_name']}")
        print(f"   Venue: {event['venue_name']}")
        print(f"   Date: {event['date']} at {event['time']}")
        print(f"   Area: {event['area']}")
        print(f"   Mood: {', '.join(event['mood_tags'])} (conf: {event['mood_confidence']})")
        print(f"   Price: {event['price_range']} (£{event['price_min']}-£{event['price_max']})")
        print(f"   URL: {event['url']}")

    # Tonight's events
    tonight = get_tonight_events(events)
    print(f"\n🌙 Tonight's events: {len(tonight)}")
    for e in tonight[:3]:
        print(f"   - {e['event_name']} at {e['venue_name']} ({e['time']})")

    # Weekend events
    weekend = get_weekend_events(events)
    print(f"\n🎉 Weekend events: {len(weekend)}")

    # Mood distribution
    print("\n🎭 Mood distribution:")
    mood_counts = {}
    for event in events:
        for mood in event.get("mood_tags", []):
            mood_counts[mood] = mood_counts.get(mood, 0) + 1

    for mood, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   - {mood}: {count}")

    print("\n" + "=" * 70)
    print("  GENERATION COMPLETE")
    print("=" * 70)
