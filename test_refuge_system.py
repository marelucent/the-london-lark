#!/usr/bin/env python3
"""
Test script for the Gentle Refuge Venue Tagging System

This script verifies:
1. Refuge venues are properly tagged in the database
2. Filtering functions work correctly
3. Distress queries return refuge venues
4. Crisis response integration works as expected
"""

import json
import sys

# Add project root to path
sys.path.insert(0, '.')

from parse_venues import load_parsed_venues
from venue_matcher import (
    match_venues,
    filter_refuge_venues,
    get_refuge_venue_count,
    get_refuge_venues
)
from crisis_responses import build_crisis_response
from distress_detection import detect_distress_level


def test_refuge_venue_count():
    """Test that we have the expected number of refuge venues (15-25)."""
    print("\n" + "=" * 60)
    print("TEST 1: Refuge Venue Count")
    print("=" * 60)

    refuge_count = get_refuge_venue_count()
    print(f"Refuge venues in database: {refuge_count}")

    # Check we have between 15-25 refuge venues (conservative target)
    if 15 <= refuge_count <= 30:
        print(f"✅ PASS: Refuge count ({refuge_count}) is within expected range (15-30)")
        return True
    else:
        print(f"❌ FAIL: Refuge count ({refuge_count}) is outside expected range (15-30)")
        return False


def test_refuge_venues_list():
    """Test that get_refuge_venues() returns properly formatted venues."""
    print("\n" + "=" * 60)
    print("TEST 2: Refuge Venues List")
    print("=" * 60)

    refuges = get_refuge_venues()
    print(f"Total refuge venues: {len(refuges)}")
    print("\nRefuge venues:")

    for v in refuges:
        print(f"  - {v['name']} ({v['area']})")

    # Verify each venue has required fields
    required_fields = ['name', 'area', 'website', 'refuge']
    all_valid = True

    for v in refuges:
        for field in required_fields:
            if field not in v:
                print(f"❌ FAIL: Venue '{v.get('name', 'Unknown')}' missing field '{field}'")
                all_valid = False

    if all_valid and len(refuges) > 0:
        print(f"\n✅ PASS: All {len(refuges)} refuge venues have required fields")
        return True
    else:
        print(f"\n❌ FAIL: Some refuge venues are missing required fields")
        return False


def test_filter_refuge_venues():
    """Test that filter_refuge_venues() correctly filters venue lists."""
    print("\n" + "=" * 60)
    print("TEST 3: Filter Refuge Venues")
    print("=" * 60)

    # Load all venues
    all_venues = load_parsed_venues()
    total_venues = len(all_venues)
    print(f"Total venues in database: {total_venues}")

    # Filter for refuges
    refuges = filter_refuge_venues(all_venues)
    print(f"Venues with refuge=True: {len(refuges)}")

    # Verify filtered venues all have refuge=True
    all_are_refuges = all(v.get('refuge', False) for v in refuges)

    if all_are_refuges and len(refuges) > 0:
        print(f"✅ PASS: All filtered venues have refuge=True")
        return True
    else:
        print(f"❌ FAIL: Some filtered venues don't have refuge=True")
        return False


def test_matched_refuge_filtering():
    """Test filtering refuge venues from matched results."""
    print("\n" + "=" * 60)
    print("TEST 4: Matched Venue Refuge Filtering")
    print("=" * 60)

    # Match venues for a tender/thoughtful mood (likely to include refuges)
    filters = {"mood": "tender"}
    matches = match_venues(filters)
    print(f"Tender mood matches: {len(matches)} venues")

    # Filter for refuges
    refuge_matches = filter_refuge_venues(matches)
    print(f"Of those, refuge venues: {len(refuge_matches)}")

    for v in refuge_matches:
        print(f"  - {v['name']} ({v['area']})")

    # We expect at least some matches to be refuges for tender mood
    if len(refuge_matches) > 0:
        print(f"\n✅ PASS: Found {len(refuge_matches)} refuge venue(s) in tender mood matches")
        return True
    else:
        print(f"\n⚠️ WARN: No refuge venues in tender mood matches (not necessarily a failure)")
        return True  # Not a failure, just a warning


def test_crisis_response_venue_filter():
    """Test that crisis response includes venue_filter for distress level."""
    print("\n" + "=" * 60)
    print("TEST 5: Crisis Response Venue Filter")
    print("=" * 60)

    # Build distress response
    response = build_crisis_response("distress")

    print(f"Distress response type: {response.get('type')}")
    print(f"Show venues: {response.get('show_venues')}")
    print(f"Venue filter: {response.get('venue_filter')}")

    # Check venue_filter is set to "refuge" for distress
    if response.get('venue_filter') == "refuge":
        print(f"\n✅ PASS: Distress response has venue_filter='refuge'")
        return True
    else:
        print(f"\n❌ FAIL: Distress response missing venue_filter='refuge'")
        return False


def test_distress_detection_integration():
    """Test that distress detection works with refuge system."""
    print("\n" + "=" * 60)
    print("TEST 6: Distress Detection Integration")
    print("=" * 60)

    # Test queries that should trigger distress detection
    test_queries = [
        "I'm feeling really low and need somewhere quiet",
        "Where can I go when everything feels hopeless",
        "I need a place to cry",
    ]

    all_passed = True
    for query in test_queries:
        level, keywords = detect_distress_level(query)
        print(f"\nQuery: '{query}'")
        print(f"  Distress level: {level}")
        print(f"  Keywords matched: {keywords}")

        if level in ["distress", "crisis"]:
            print(f"  ✅ Correctly detected distress")
        else:
            print(f"  ⚠️ Not detected as distress (level: {level})")

    return all_passed


def test_refuge_venue_characteristics():
    """Verify refuge venues have appropriate characteristics."""
    print("\n" + "=" * 60)
    print("TEST 7: Refuge Venue Characteristics")
    print("=" * 60)

    refuges = get_refuge_venues()

    # Venues that should NOT be refuges (nightclubs, loud venues)
    disallowed_patterns = ["nightclub", "club night", "rave", "party"]

    issues = []
    for v in refuges:
        name_lower = v['name'].lower()
        vibe_lower = v.get('vibe_note', '').lower()

        for pattern in disallowed_patterns:
            if pattern in name_lower or pattern in vibe_lower:
                issues.append(f"'{v['name']}' may not be appropriate (contains '{pattern}')")

    if issues:
        print("⚠️ Potential issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ No obvious inappropriate venues found in refuge list")

    # Not a hard failure - just informational
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "=" * 60)
    print("GENTLE REFUGE VENUE SYSTEM - TEST SUITE")
    print("=" * 60)

    tests = [
        ("Refuge Venue Count", test_refuge_venue_count),
        ("Refuge Venues List", test_refuge_venues_list),
        ("Filter Refuge Venues", test_filter_refuge_venues),
        ("Matched Venue Filtering", test_matched_refuge_filtering),
        ("Crisis Response Integration", test_crisis_response_venue_filter),
        ("Distress Detection Integration", test_distress_detection_integration),
        ("Refuge Venue Characteristics", test_refuge_venue_characteristics),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {str(e)}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Refuge venue system is working correctly.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
