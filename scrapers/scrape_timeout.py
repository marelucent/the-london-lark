#!/usr/bin/env python3
"""
Time Out London Event Scraper

Scrapes upcoming events from Time Out London.
Simple, reliable approach using requests + BeautifulSoup.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Rate limiting
REQUEST_DELAY = 2  # seconds between requests

# User agent to avoid blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def fetch_timeout_events():
    """
    Fetch events from Time Out London.

    Returns:
        list: Raw event data from Time Out
    """
    events = []

    # Time Out events page
    base_url = "https://www.timeout.com/london/things-to-do/events-in-london-today"

    print(f"   Fetching: {base_url}")

    try:
        response = requests.get(base_url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        print(f"   Status: {response.status_code}")
        print(f"   Content length: {len(response.text)} chars")

        soup = BeautifulSoup(response.text, "lxml")

        # Debug: Save raw HTML for inspection
        with open("debug_timeout_raw.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("   Saved raw HTML to debug_timeout_raw.html")

        # Try to find event listings
        # Time Out uses various class structures, let's find them

        # Look for article elements (common pattern)
        articles = soup.find_all("article")
        print(f"   Found {len(articles)} article elements")

        # Look for specific patterns
        event_cards = soup.find_all("div", class_=lambda x: x and "card" in x.lower() if x else False)
        print(f"   Found {len(event_cards)} card elements")

        # Look for links with event-like patterns
        event_links = soup.find_all("a", href=lambda x: x and "/event/" in x if x else False)
        print(f"   Found {len(event_links)} event links")

        # Try to extract event info from whatever structure we find
        for i, link in enumerate(event_links[:20]):  # Limit to 20 for safety
            event_data = {
                "title": link.get_text(strip=True),
                "url": link.get("href", ""),
                "source": "timeout"
            }

            # Make URL absolute
            if event_data["url"] and not event_data["url"].startswith("http"):
                event_data["url"] = "https://www.timeout.com" + event_data["url"]

            if event_data["title"]:
                events.append(event_data)
                print(f"   [{i+1}] {event_data['title'][:50]}...")

        # Also try to find structured data (JSON-LD)
        scripts = soup.find_all("script", type="application/ld+json")
        print(f"\n   Found {len(scripts)} JSON-LD scripts")

        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "Event":
                    print(f"   Found Event JSON-LD: {data.get('name', 'Unknown')[:50]}")
                    events.append({
                        "title": data.get("name", ""),
                        "venue": data.get("location", {}).get("name", "") if isinstance(data.get("location"), dict) else "",
                        "date": data.get("startDate", ""),
                        "url": data.get("url", ""),
                        "description": data.get("description", ""),
                        "source": "timeout_jsonld"
                    })
            except json.JSONDecodeError:
                pass

        return events

    except requests.exceptions.RequestException as e:
        print(f"   ERROR: {e}")
        return []


def fetch_timeout_event_details(event_url):
    """
    Fetch detailed info for a single event.

    Args:
        event_url: URL of the event page

    Returns:
        dict: Event details
    """
    print(f"   Fetching details: {event_url}")
    time.sleep(REQUEST_DELAY)  # Rate limiting

    try:
        response = requests.get(event_url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        details = {
            "url": event_url,
            "source": "timeout"
        }

        # Try to find title
        title = soup.find("h1")
        if title:
            details["title"] = title.get_text(strip=True)

        # Try to find venue
        venue_elem = soup.find(class_=lambda x: x and "venue" in x.lower() if x else False)
        if venue_elem:
            details["venue"] = venue_elem.get_text(strip=True)

        # Try to find date/time
        time_elem = soup.find("time")
        if time_elem:
            details["date"] = time_elem.get("datetime", time_elem.get_text(strip=True))

        # Try to find description
        desc = soup.find("meta", {"name": "description"})
        if desc:
            details["description"] = desc.get("content", "")

        return details

    except Exception as e:
        print(f"   ERROR fetching details: {e}")
        return {"url": event_url, "error": str(e)}


if __name__ == "__main__":
    print("=" * 70)
    print("  TIME OUT LONDON SCRAPER - DEBUG RUN")
    print("=" * 70)
    print()

    # Test basic fetch
    events = fetch_timeout_events()

    print(f"\n✓ Found {len(events)} potential events")

    # Save results
    output_file = "scraped_timeout.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved to {output_file}")

    # Show sample
    print("\n" + "=" * 70)
    print("  SAMPLE EVENTS")
    print("=" * 70)

    for i, event in enumerate(events[:5], 1):
        print(f"\n{i}. {event.get('title', 'No title')[:60]}")
        if event.get("venue"):
            print(f"   Venue: {event['venue']}")
        if event.get("date"):
            print(f"   Date: {event['date']}")
        if event.get("url"):
            print(f"   URL: {event['url'][:70]}...")

    print("\n" + "=" * 70)
