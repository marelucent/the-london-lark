#!/usr/bin/env python3
"""
Event Pipeline for The London Lark

Aggregates events from multiple sources:
- Eventbrite (filtered for Lark's vibe)
- Resident Advisor (underground electronic/dance events)
- Future: Skiddle, DICE, etc.

All events are normalized to a standard format and cached locally.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add events directory to path
sys.path.insert(0, str(Path(__file__).parent / "events"))

# Import fetchers
from event_fetcher import EventFetcher
try:
    from events.fetch_ra_events import fetch_ra_events, filter_for_lark_vibe as filter_ra_events
    HAS_RA_FETCHER = True
except ImportError:
    HAS_RA_FETCHER = False
    print("Note: Resident Advisor fetcher not available")


class EventPipeline:
    """
    Unified event pipeline that aggregates multiple sources.
    """

    def __init__(self, cache_file="pipeline_events.json"):
        """Initialize the pipeline."""
        self.cache_file = Path(cache_file)
        self.events = []
        self.sources_status = {}

    def fetch_all_sources(self, use_mock=True):
        """
        Fetch events from all available sources.

        Args:
            use_mock: If True, use mock data for Eventbrite (no API token needed)

        Returns:
            dict: Status of each source fetch
        """
        print("=" * 70)
        print("  LONDON LARK - EVENT PIPELINE")
        print("=" * 70)
        print()

        all_events = []

        # Source 1: Eventbrite (filtered)
        print("📡 Fetching from Eventbrite...")
        try:
            eb_fetcher = EventFetcher(use_mock=use_mock)
            eb_events = eb_fetcher.fetch_all_events()
            all_events.extend(eb_events)
            self.sources_status["eventbrite"] = {
                "status": "success",
                "count": len(eb_events),
                "mock": use_mock
            }
            print(f"   ✓ Eventbrite: {len(eb_events)} events")
        except Exception as e:
            self.sources_status["eventbrite"] = {
                "status": "error",
                "error": str(e)
            }
            print(f"   ✗ Eventbrite error: {e}")

        # Source 2: Resident Advisor
        if HAS_RA_FETCHER:
            print("\n📡 Fetching from Resident Advisor...")
            try:
                raw_ra_events = fetch_ra_events(days_ahead=14)
                if raw_ra_events:
                    ra_events = filter_ra_events(raw_ra_events)
                    all_events.extend(ra_events)
                    self.sources_status["resident_advisor"] = {
                        "status": "success",
                        "count": len(ra_events),
                        "raw_count": len(raw_ra_events)
                    }
                    print(f"   ✓ Resident Advisor: {len(ra_events)} events (filtered from {len(raw_ra_events)})")
                else:
                    self.sources_status["resident_advisor"] = {
                        "status": "no_data",
                        "count": 0
                    }
                    print("   ⚠ Resident Advisor: No events (API may require auth)")
            except Exception as e:
                self.sources_status["resident_advisor"] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"   ✗ Resident Advisor error: {e}")
        else:
            self.sources_status["resident_advisor"] = {
                "status": "not_available",
                "count": 0
            }
            print("\n⚠ Resident Advisor fetcher not available")

        # Deduplicate events (by event_id)
        seen_ids = set()
        unique_events = []
        for event in all_events:
            event_id = event.get("event_id", event.get("id", ""))
            if event_id and event_id not in seen_ids:
                seen_ids.add(event_id)
                unique_events.append(event)

        self.events = unique_events

        # Sort by date
        self.events.sort(key=lambda x: (x.get("date", ""), x.get("time", "")))

        print(f"\n✓ Total unique events: {len(self.events)}")

        return self.sources_status

    def get_events_by_mood(self, mood):
        """
        Get events matching a specific mood.

        Args:
            mood: Mood tag to filter by (e.g., "Folk & Intimate")

        Returns:
            list: Events with matching mood tags
        """
        matching = []
        for event in self.events:
            mood_tags = event.get("mood_tags", [])
            if mood in mood_tags:
                matching.append(event)
        return matching

    def get_events_by_date(self, date_str):
        """
        Get events on a specific date.

        Args:
            date_str: Date in YYYY-MM-DD format

        Returns:
            list: Events on that date
        """
        return [e for e in self.events if e.get("date") == date_str]

    def get_tonight_events(self):
        """Get events happening tonight."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.get_events_by_date(today)

    def get_weekend_events(self):
        """Get events happening this weekend (Fri-Sun)."""
        today = datetime.now()
        weekend_dates = []

        # Find next Friday, Saturday, Sunday
        for i in range(7):
            check_date = today + timedelta(days=i)
            if check_date.weekday() in [4, 5, 6]:  # Fri=4, Sat=5, Sun=6
                weekend_dates.append(check_date.strftime("%Y-%m-%d"))

        weekend_events = []
        for event in self.events:
            if event.get("date") in weekend_dates:
                weekend_events.append(event)

        return weekend_events

    def get_events_by_region(self, region):
        """
        Get events in a specific London region.

        Args:
            region: e.g., "East London", "South London"

        Returns:
            list: Events in that region
        """
        return [e for e in self.events if e.get("region") == region]

    def get_free_events(self):
        """Get free events."""
        free_events = []
        for event in self.events:
            price_range = event.get("price_range", "").lower()
            price_min = event.get("price_min", 0)
            if price_range == "free" or price_min == 0:
                free_events.append(event)
        return free_events

    def save_cache(self):
        """Save all events to cache file."""
        cache_data = {
            "fetched_at": datetime.now().isoformat(),
            "sources_status": self.sources_status,
            "total_events": len(self.events),
            "events": self.events
        }

        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Saved {len(self.events)} events to {self.cache_file}")
        return self.cache_file

    def load_cache(self):
        """Load events from cache file."""
        if not self.cache_file.exists():
            print(f"Cache file not found: {self.cache_file}")
            return False

        with open(self.cache_file, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

        self.events = cache_data.get("events", [])
        self.sources_status = cache_data.get("sources_status", {})

        fetched_at = cache_data.get("fetched_at", "unknown")
        print(f"Loaded {len(self.events)} events from cache (fetched: {fetched_at})")

        return True

    def get_mood_summary(self):
        """Get summary of mood distribution across all events."""
        mood_counts = {}
        for event in self.events:
            for mood in event.get("mood_tags", []):
                mood_counts[mood] = mood_counts.get(mood, 0) + 1

        return dict(sorted(mood_counts.items(), key=lambda x: x[1], reverse=True))

    def get_source_summary(self):
        """Get summary of events by source."""
        source_counts = {}
        for event in self.events:
            source = event.get("source", "unknown")
            source_counts[source] = source_counts.get(source, 0) + 1
        return source_counts


def main():
    """Main entry point - fetch and cache all events."""
    pipeline = EventPipeline()

    # Fetch from all sources (mock mode for Eventbrite)
    pipeline.fetch_all_sources(use_mock=True)

    # Save to cache
    pipeline.save_cache()

    # Print summaries
    print("\n" + "=" * 70)
    print("  PIPELINE SUMMARY")
    print("=" * 70)

    # Source distribution
    print("\n📊 Events by source:")
    for source, count in pipeline.get_source_summary().items():
        print(f"   - {source}: {count}")

    # Mood distribution
    print("\n🎭 Top moods:")
    mood_summary = pipeline.get_mood_summary()
    for mood, count in list(mood_summary.items())[:10]:
        print(f"   - {mood}: {count}")

    # Tonight's events
    tonight = pipeline.get_tonight_events()
    print(f"\n🌙 Tonight's events: {len(tonight)}")

    # Weekend events
    weekend = pipeline.get_weekend_events()
    print(f"🎉 Weekend events: {len(weekend)}")

    # Free events
    free = pipeline.get_free_events()
    print(f"🎟️  Free events: {len(free)}")

    print("\n" + "=" * 70)
    print("  READY FOR THE LARK")
    print("=" * 70)

    return pipeline


if __name__ == "__main__":
    pipeline = main()
