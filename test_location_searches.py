#!/usr/bin/env python3
"""
Test location searches after fixes
Verify that location-based searches now work correctly
"""

import json

def search_by_location(venues, location_query):
    """Simple location search"""
    matches = []
    query_lower = location_query.lower()

    for idx, venue in enumerate(venues):
        venue_location = venue.get("location", "").lower()

        # Exact match or partial match
        if query_lower in venue_location or venue_location in query_lower:
            matches.append({
                "id": idx,
                "name": venue.get("name", "Unknown"),
                "location": venue.get("location", "")
            })

    return matches

def main():
    print("=" * 70)
    print("LOCATION SEARCH TESTS")
    print("=" * 70)
    print()

    # Load venues
    with open("lark_venues_clean.json", "r", encoding="utf-8") as f:
        venues = json.load(f)

    # Test searches that should now work better
    test_searches = [
        ("Ealing", "Should find OPEN Ealing, Questors Theatre, Bija Garden"),
        ("Shepherd's Bush", "Should find Miller's Way Project"),
        ("Hackney", "Should find all Hackney venues (not filtered by compound)"),
        ("Acton", "Should find 4160 Tuesdays perfume studio"),
        ("Peckham", "Should find multiple Peckham venues"),
        ("Shoreditch", "Should find Shoreditch art and workshop venues"),
        ("King's Cross", "Should find venues near King's Cross"),
    ]

    for query, description in test_searches:
        print(f"Search: '{query}'")
        print(f"Expected: {description}")

        results = search_by_location(venues, query)

        print(f"Found: {len(results)} venues")

        if results:
            print("Results:")
            for result in results[:5]:  # Show first 5
                print(f"  - [{result['id']}] {result['name']} ({result['location']})")

            if len(results) > 5:
                print(f"  ... and {len(results) - 5} more")
        else:
            print("  No results found")

        print()

    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
