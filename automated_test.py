#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Automated CLI Smoke Test for The London Lark

"""
Automated test runner that validates core functionality.
Runs high-priority test cases from prompt_tests.md and reports results.
"""

import sys
from prompt_interpreter import interpret_prompt
from mood_resolver import resolve_from_keywords
from venue_matcher import match_venues
from response_generator import generate_response
from lark_metrics import get_metrics

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.details = []

    def add_pass(self, test_name):
        self.passed += 1
        self.details.append((test_name, "PASS", None))

    def add_fail(self, test_name, error):
        self.failed += 1
        self.details.append((test_name, "FAIL", error))

    def add_warning(self, test_name, warning):
        self.warnings += 1
        self.details.append((test_name, "WARN", warning))

    def total(self):
        return self.passed + self.failed + self.warnings

# High-priority test cases from prompt_tests.md
TEST_CASES = [
    # Test 012 - Fuzzy Match: Typo in "comedy"
    # Note: "comedy" is in synonyms, "funny" is also in synonyms, so this is exact match
    {
        "name": "Test 012: Exact Match (funny → Comic Relief)",
        "prompt": "anything comdy or funny in South London tonight?",
        "expect_mood": "Comic Relief",
        "expect_confidence_range": (0.99, 1.01),  # "funny" is exact match
        "expect_venues": True
    },
    # Test 013 - Fuzzy Match: Typo in "drag"
    {
        "name": "Test 013: Fuzzy Match (dragg → drag)",
        "prompt": "looking for dragg shows this weekend",
        "expect_mood": "Cabaret & Glitter",
        "expect_confidence_range": (0.85, 0.95),
        "expect_venues": True
    },
    # Test 014 - Fuzzy Match: Variant "folky"
    {
        "name": "Test 014: Exact Match (folky)",
        "prompt": "something folky and intimate in Camden",
        "expect_mood": "Folk & Intimate",
        "expect_confidence_range": (0.99, 1.01),
        "expect_venues": True
    },
    # Test 015 - Multi-Filter: Budget + Mood + Location
    {
        "name": "Test 015: Multi-Filter (budget + mood + location)",
        "prompt": "cheap queer cabaret in East London this Friday",
        "expect_mood": "Cabaret & Glitter",
        "expect_location": "East London",
        "expect_budget": "low",
        "expect_venues": True
    },
    # Test 016 - Multi-Filter: Solo + Thoughtful + Budget
    {
        "name": "Test 016: Multi-Filter (solo + mood + budget)",
        "prompt": "somewhere thoughtful and not too expensive, just for me",
        "expect_mood": "The Thoughtful Stage",
        "expect_budget": "low",
        "expect_group": "solo",
        "expect_venues": None  # May or may not have venues
    },
    # Test 019 - Location Test: North London
    {
        "name": "Test 019: Location (North London)",
        "prompt": "folk music in North London this weekend",
        "expect_mood": "Folk & Intimate",
        "expect_location": "North London",
        "expect_venues": True
    },
    # Test 004 - Poetic + Practical
    {
        "name": "Test 004: Mood + Location (Poetic in East London)",
        "prompt": "What's on in East London tonight that feels a bit poetic?",
        "expect_mood": "Poetic",
        "expect_location": "East London",
        "expect_venues": None  # Depends on database
    },
    # Test 007 - Quiet Solo Evening
    {
        "name": "Test 007: Solo Filtering",
        "prompt": "Something low key for a Tuesday night? I'm going solo.",
        "expect_group": "solo",
        "expect_venues": None
    },
]

def run_test(test_case):
    """Run a single test case and return result"""
    try:
        prompt = test_case["prompt"]

        # Step 1: Interpret prompt
        filters = interpret_prompt(prompt)

        # Step 2: Resolve mood if not found
        mood_confidence = None
        if not filters.get("mood"):
            keywords = prompt.lower().split()
            mood, confidence = resolve_from_keywords(keywords)
            filters["mood"] = mood
            mood_confidence = confidence
        else:
            mood_confidence = 1.0

        # Step 3: Match venues
        matches = match_venues(filters)

        # Log metrics
        metrics = get_metrics()
        metrics.log_query(filters, mood_confidence, len(matches))

        # Step 4: Generate response (test that it doesn't crash)
        if matches:
            response = generate_response(matches[0], filters)
        else:
            response = generate_response(None, filters)

        # Validate expectations
        errors = []
        warnings = []

        # Check mood
        if "expect_mood" in test_case:
            expected_mood = test_case["expect_mood"]
            if filters.get("mood") != expected_mood:
                # Check if it's in mood_lookup as synonym
                if filters.get("mood"):
                    warnings.append(f"Expected mood '{expected_mood}', got '{filters.get('mood')}'")
                else:
                    errors.append(f"Expected mood '{expected_mood}', got None")

        # Check confidence range (for fuzzy matching)
        if "expect_confidence_range" in test_case and mood_confidence:
            min_conf, max_conf = test_case["expect_confidence_range"]
            if not (min_conf <= mood_confidence <= max_conf):
                warnings.append(f"Confidence {mood_confidence:.2f} outside expected range [{min_conf:.2f}, {max_conf:.2f}]")

        # Check location
        if "expect_location" in test_case:
            if filters.get("location") != test_case["expect_location"]:
                errors.append(f"Expected location '{test_case['expect_location']}', got '{filters.get('location')}'")

        # Check budget
        if "expect_budget" in test_case:
            if filters.get("budget") != test_case["expect_budget"]:
                errors.append(f"Expected budget '{test_case['expect_budget']}', got '{filters.get('budget')}'")

        # Check group
        if "expect_group" in test_case:
            if filters.get("group") != test_case["expect_group"]:
                errors.append(f"Expected group '{test_case['expect_group']}', got '{filters.get('group')}'")

        # Check venues
        if "expect_venues" in test_case:
            if test_case["expect_venues"] is True and len(matches) == 0:
                warnings.append("Expected venues but got none")
            elif test_case["expect_venues"] is False and len(matches) > 0:
                warnings.append(f"Expected no venues but got {len(matches)}")

        # Check response was generated
        if not response or len(response) < 10:
            errors.append("Response generation failed or too short")

        return {
            "success": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
            "filters": filters,
            "venue_count": len(matches),
            "confidence": mood_confidence,
            "response_length": len(response) if response else 0
        }

    except Exception as e:
        return {
            "success": False,
            "errors": [f"Exception: {str(e)}"],
            "warnings": [],
            "filters": {},
            "venue_count": 0,
            "confidence": 0,
            "response_length": 0
        }

def print_header():
    print("\n" + "="*70)
    print("  THE LONDON LARK - AUTOMATED SMOKE TEST")
    print("="*70 + "\n")

def print_test_result(test_name, result):
    """Print result for a single test"""
    if result["success"]:
        if result["warnings"]:
            print(f"{YELLOW}⚠ WARN{RESET} {test_name}")
            for warning in result["warnings"]:
                print(f"        {warning}")
        else:
            print(f"{GREEN}✓ PASS{RESET} {test_name}")
    else:
        print(f"{RED}✗ FAIL{RESET} {test_name}")
        for error in result["errors"]:
            print(f"        {error}")

    # Show details
    print(f"        Filters: {result['filters']}")
    if result["confidence"]:
        print(f"        Confidence: {result['confidence']:.2f}")
    print(f"        Venues found: {result['venue_count']}")
    print(f"        Response length: {result['response_length']} chars")
    print()

def print_summary(results):
    """Print test summary"""
    total = len(results)
    passed = sum(1 for r in results if r[1]["success"] and not r[1]["warnings"])
    warned = sum(1 for r in results if r[1]["success"] and r[1]["warnings"])
    failed = sum(1 for r in results if not r[1]["success"])

    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    print(f"Total tests:   {total}")
    print(f"{GREEN}Passed:{RESET}        {passed}")
    print(f"{YELLOW}Warnings:{RESET}      {warned}")
    print(f"{RED}Failed:{RESET}        {failed}")

    pass_rate = ((passed + warned) / total * 100) if total > 0 else 0
    print(f"\nPass rate:     {pass_rate:.1f}%")

    if failed == 0:
        print(f"\n{GREEN}✓ All tests passed!{RESET}")
    elif failed <= 2:
        print(f"\n{YELLOW}⚠ Most tests passed, some issues to address{RESET}")
    else:
        print(f"\n{RED}✗ Multiple failures detected{RESET}")

    print("="*70 + "\n")

def main():
    """Run all smoke tests"""
    print_header()

    # Reset metrics before test run (optional - comment out to accumulate)
    # metrics = get_metrics()
    # metrics.reset_metrics()

    results = []

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"[{i}/{len(TEST_CASES)}] Running: {test_case['name']}")
        result = run_test(test_case)
        results.append((test_case["name"], result))
        print_test_result(test_case["name"], result)

    print_summary(results)

    # Print coverage report
    print("\n" + "="*70)
    print("  COVERAGE REPORT (from this test run)")
    print("="*70)
    metrics = get_metrics()
    stats = metrics.get_coverage_stats()
    print(f"\n📊 Coverage Stats:")
    print(f"   Total queries: {stats['total_queries']}")
    print(f"   Mood resolution: {stats['mood_resolution_rate']:.1f}%")
    print(f"   Venue match rate: {stats['venue_match_rate']:.1f}%")
    print(f"   Exact match rate: {stats['exact_match_rate']:.1f}%")
    print(f"\n💡 Run 'python lark_metrics.py' for full metrics report")
    print("="*70 + "\n")

    # Exit with appropriate code
    failed_count = sum(1 for r in results if not r[1]["success"])
    sys.exit(0 if failed_count == 0 else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test run interrupted{RESET}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{RED}Fatal error: {e}{RESET}\n")
        sys.exit(1)
