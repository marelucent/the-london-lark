#!/usr/bin/env python3
"""
Resident Advisor London Event Scraper

Scrapes upcoming events from RA using their listing pages.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

REQUEST_DELAY = 2

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://ra.co/",
}


def fetch_ra_events():
    """
    Fetch events from Resident Advisor London listings.
    """
    events = []

    # RA events listing for London
    url = "https://ra.co/events/uk/london"

    print(f"   Fetching: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")

        if response.status_code == 403:
            print("   403 Forbidden - RA blocks direct scraping")
            print("   Trying alternative approach...")

            # Try their API endpoint directly
            return fetch_ra_api_events()

        response.raise_for_status()
        print(f"   Content length: {len(response.text)} chars")

        soup = BeautifulSoup(response.text, "lxml")

        # Save for debugging
        with open("debug_ra_raw.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("   Saved raw HTML to debug_ra_raw.html")

        # RA uses various patterns - let's explore
        links = soup.find_all("a", href=lambda x: x and "/events/" in x if x else False)
        print(f"   Found {len(links)} event links")

        seen_urls = set()
        for link in links:
            href = link.get("href", "")
            if href.startswith("/events/") and href not in seen_urls:
                seen_urls.add(href)
                event = {
                    "title": link.get_text(strip=True),
                    "url": f"https://ra.co{href}",
                    "source": "ra_web"
                }
                if event["title"] and len(event["title"]) > 3:
                    events.append(event)

        return events

    except requests.exceptions.RequestException as e:
        print(f"   ERROR: {e}")
        return []


def fetch_ra_api_events():
    """
    Try to fetch from RA's internal API (GraphQL).
    """
    print("   Trying RA GraphQL API...")

    url = "https://ra.co/graphql"

    # This is the query structure RA uses internally
    query = """
    query GET_POPULAR_EVENTS($filters: FilterInputDtoInput, $pageSize: Int) {
      eventListings(filters: $filters, pageSize: $pageSize) {
        data {
          event {
            title
            date
            startTime
            venue {
              name
              area {
                name
              }
            }
            contentUrl
          }
        }
      }
    }
    """

    # London area ID is 13
    variables = {
        "filters": {
            "areas": {"eq": 13}
        },
        "pageSize": 20
    }

    headers = {
        **HEADERS,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            url,
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=30
        )
        print(f"   GraphQL Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            events = []

            if "data" in data and "eventListings" in data["data"]:
                for listing in data["data"]["eventListings"]["data"]:
                    event = listing["event"]
                    events.append({
                        "title": event.get("title", ""),
                        "venue": event.get("venue", {}).get("name", ""),
                        "area": event.get("venue", {}).get("area", {}).get("name", ""),
                        "date": event.get("date", ""),
                        "time": event.get("startTime", ""),
                        "url": f"https://ra.co{event.get('contentUrl', '')}",
                        "source": "ra_graphql"
                    })
            return events
        else:
            print(f"   GraphQL failed: {response.text[:200]}")
            return []

    except Exception as e:
        print(f"   GraphQL ERROR: {e}")
        return []


if __name__ == "__main__":
    print("=" * 70)
    print("  RESIDENT ADVISOR SCRAPER - DEBUG RUN")
    print("=" * 70)
    print()

    events = fetch_ra_events()

    print(f"\n✓ Found {len(events)} events")

    # Save results
    output_file = "scraped_ra.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved to {output_file}")

    # Show sample
    print("\n" + "=" * 70)
    print("  SAMPLE EVENTS")
    print("=" * 70)

    for i, event in enumerate(events[:10], 1):
        print(f"\n{i}. {event.get('title', 'No title')[:60]}")
        if event.get("venue"):
            print(f"   Venue: {event['venue']}")
        if event.get("area"):
            print(f"   Area: {event['area']}")
        if event.get("date"):
            print(f"   Date: {event['date']}")
        print(f"   URL: {event.get('url', 'N/A')[:70]}")

    print("\n" + "=" * 70)
