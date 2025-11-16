#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate scraped events JSON file before importing to the Lark.

Usage:
    python validate_output.py scraped_events.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def validate_event(event, index):
    """Validate a single event object"""
    errors = []
    warnings = []

    # Required fields
    if not event.get("event_name"):
        errors.append(f"Event #{index}: Missing event_name")
    elif len(event["event_name"]) < 3:
        warnings.append(f"Event #{index}: event_name too short: '{event['event_name']}'")
    elif len(event["event_name"]) > 200:
        warnings.append(f"Event #{index}: event_name very long ({len(event['event_name'])} chars)")

    if not event.get("venue_name"):
        errors.append(f"Event #{index}: Missing venue_name")
    elif event["venue_name"] == "London Venue":
        warnings.append(f"Event #{index}: Generic venue name 'London Venue' for '{event.get('event_name', 'Unknown')}'")

    if not event.get("date"):
        errors.append(f"Event #{index}: Missing date")
    else:
        try:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d")
            if event_date < datetime.now():
                warnings.append(f"Event #{index}: Past date {event['date']} for '{event.get('event_name', 'Unknown')}'")
        except ValueError:
            errors.append(f"Event #{index}: Invalid date format '{event['date']}' (expected YYYY-MM-DD)")

    # Optional but good to have
    if not event.get("time"):
        warnings.append(f"Event #{index}: Missing time, will default to 20:00")
    elif event.get("time"):
        try:
            datetime.strptime(event["time"], "%H:%M")
        except ValueError:
            warnings.append(f"Event #{index}: Invalid time format '{event['time']}' (expected HH:MM)")

    if not event.get("mood_tags") or len(event.get("mood_tags", [])) == 0:
        warnings.append(f"Event #{index}: No mood_tags for '{event.get('event_name', 'Unknown')}'")

    if not event.get("source"):
        warnings.append(f"Event #{index}: Missing source for '{event.get('event_name', 'Unknown')}'")

    return errors, warnings


def validate_file(filepath):
    """Validate the entire JSON file"""
    print(f"\n🔍 Validating: {filepath}")
    print("=" * 60)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

    # Check structure
    if "events" not in data:
        print("❌ Missing 'events' key in JSON root")
        return False

    events = data.get("events", [])
    if not events:
        print("⚠️ No events found in file!")
        return False

    print(f"📊 Found {len(events)} events")

    # Validate metadata
    if "scraped_at" in data:
        print(f"⏰ Scraped at: {data['scraped_at']}")
    if "sources" in data:
        print(f"📡 Sources: {', '.join(data['sources'])}")

    # Validate each event
    all_errors = []
    all_warnings = []

    for i, event in enumerate(events, 1):
        errors, warnings = validate_event(event, i)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    # Report errors
    if all_errors:
        print(f"\n❌ ERRORS ({len(all_errors)}):")
        for error in all_errors[:20]:  # Show first 20
            print(f"  • {error}")
        if len(all_errors) > 20:
            print(f"  ... and {len(all_errors) - 20} more errors")

    # Report warnings
    if all_warnings:
        print(f"\n⚠️ WARNINGS ({len(all_warnings)}):")
        for warning in all_warnings[:20]:  # Show first 20
            print(f"  • {warning}")
        if len(all_warnings) > 20:
            print(f"  ... and {len(all_warnings) - 20} more warnings")

    # Summary
    print("\n" + "=" * 60)
    if all_errors:
        print("❌ VALIDATION FAILED - Fix errors before importing")
        return False
    elif all_warnings:
        print(f"⚠️ VALIDATION PASSED with {len(all_warnings)} warnings")
        print("   Consider reviewing warnings, but import should work.")
        return True
    else:
        print("✅ VALIDATION PASSED - All events look good!")
        return True

    # Statistics
    print("\n📈 Event Statistics:")

    # Count by source
    sources = {}
    for event in events:
        src = event.get("source", "Unknown")
        sources[src] = sources.get(src, 0) + 1

    for src, count in sorted(sources.items()):
        print(f"  • {src}: {count} events")

    # Count by date
    dates = {}
    for event in events:
        date = event.get("date", "Unknown")
        dates[date] = dates.get(date, 0) + 1

    print("\n📅 Events by date:")
    for date in sorted(dates.keys())[:7]:
        print(f"  • {date}: {dates[date]} events")

    # Count by mood
    moods = {}
    for event in events:
        for mood in event.get("mood_tags", []):
            moods[mood] = moods.get(mood, 0) + 1

    print("\n🎭 Most common moods:")
    sorted_moods = sorted(moods.items(), key=lambda x: x[1], reverse=True)
    for mood, count in sorted_moods[:10]:
        print(f"  • {mood}: {count} events")

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_output.py <json_file>")
        print("Example: python validate_output.py scraped_events.json")
        sys.exit(1)

    filepath = sys.argv[1]
    success = validate_file(filepath)

    if success:
        print("\n✅ Ready to import! Run:")
        print(f"   python scrapers/import_events.py {filepath}")
    else:
        print("\n❌ Please fix errors before importing.")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
