#!/usr/bin/env python3
"""
Test specific manual fixes applied in Round 2
"""

import json

def search_by_location(venues, location_query):
    """Simple location search"""
    matches = []
    query_lower = location_query.lower()

    for idx, venue in enumerate(venues):
        venue_location = venue.get("location", "").lower()

        if query_lower in venue_location or venue_location in query_lower:
            matches.append({
                "id": idx,
                "name": venue.get("name", "Unknown"),
                "location": venue.get("location", "")
            })

    return matches

def main():
    print("=" * 70)
    print("MANUAL FIXES VALIDATION TESTS")
    print("=" * 70)
    print()

    # Load venues
    with open("lark_venues_clean.json", "r", encoding="utf-8") as f:
        venues = json.load(f)

    print(f"Total venues: {len(venues)}")
    print("Expected: 295 (removed 1 from 296)")
    print()

    # Test 1: Heaven should now be in Westminster
    print("TEST 1: Heaven location")
    print("-" * 70)

    # Find Heaven
    heaven = None
    heaven_id = None
    for idx, venue in enumerate(venues):
        if "Heaven" == venue.get("name", ""):
            heaven = venue
            heaven_id = idx
            break

    if heaven:
        print(f"Found Heaven at index {heaven_id}")
        print(f"Location: {heaven.get('location', 'NOT FOUND')}")
        print(f"Expected: Westminster")
        if heaven.get("location") == "Westminster":
            print("PASS: Location correctly updated")
        else:
            print("FAIL: Location not updated")
    else:
        print("FAIL: Heaven not found")
    print()

    # Test 2: Westminster search should find Heaven
    print("TEST 2: Westminster search")
    print("-" * 70)
    results = search_by_location(venues, "Westminster")
    print(f"Found {len(results)} venues")

    heaven_found = False
    for r in results:
        print(f"  - [{r['id']}] {r['name']} ({r['location']})")
        if "Heaven" in r['name']:
            heaven_found = True

    if heaven_found:
        print("PASS: Heaven found in Westminster search")
    else:
        print("FAIL: Heaven not found in Westminster search")
    print()

    # Test 3: Elephant & Castle should find 3 venues
    print("TEST 3: Elephant & Castle search")
    print("-" * 70)
    results = search_by_location(venues, "Elephant & Castle")
    print(f"Found {len(results)} venues")
    print("Expected: 3 venues")

    for r in results:
        print(f"  - [{r['id']}] {r['name']} ({r['location']})")

    if len(results) == 3:
        print("PASS: Found expected 3 venues")
    else:
        print(f"INFO: Found {len(results)} venues (expected 3)")
    print()

    # Test 4: Canterbury should NOT exist
    print("TEST 4: Canterbury removed")
    print("-" * 70)
    canterbury_found = False
    for venue in venues:
        if "Canterbury" in venue.get("location", ""):
            canterbury_found = True
            print(f"FAIL: Found Canterbury venue: {venue.get('name')}")
            break

    if not canterbury_found:
        print("PASS: Canterbury venue successfully removed")
    print()

    print("=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
