#!/usr/bin/env python3
"""
check_unmapped_moods.py — Mood Tag Housekeeping Script

Scans all venue moods in lark_venues_clean.json and compares them
against mood_index.json to find any mood tags that won't be found
by the primary search (mood-to-arcana matching).

Note: As of the text search fix, unmapped moods ARE still searchable
via the text fallback — but they won't map to an arcana for primary
mood-based matching. This script helps identify gaps to fix.

Usage:
    python scripts/check_unmapped_moods.py
    python scripts/check_unmapped_moods.py --verbose
    python scripts/check_unmapped_moods.py --suggest
"""

import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
VENUES_PATH = PROJECT_ROOT / "lark_venues_clean.json"
MOOD_INDEX_PATH = PROJECT_ROOT / "mood_index.json"


def load_json(path):
    """Load a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_synonym_set(mood_index):
    """
    Build a set of all known synonyms from mood_index.json.
    Returns (synonym_set, synonym_to_arcana_map)
    """
    all_synonyms = set()
    synonym_to_arcana = {}

    for arcana_name, data in mood_index.items():
        # Add the arcana name itself
        all_synonyms.add(arcana_name.lower())
        synonym_to_arcana[arcana_name.lower()] = arcana_name

        # Add all synonyms
        for synonym in data.get("synonyms", []):
            syn_lower = synonym.lower()
            all_synonyms.add(syn_lower)
            synonym_to_arcana[syn_lower] = arcana_name

    return all_synonyms, synonym_to_arcana


def extract_venue_moods(venues):
    """
    Extract all mood tags from venues.
    Returns (mood_counter, mood_to_venues_map)
    """
    mood_counter = Counter()
    mood_to_venues = defaultdict(list)

    for venue in venues:
        venue_name = venue.get("name", "Unknown")
        moods = venue.get("moods", []) or venue.get("mood_tags", [])

        for mood in moods:
            if mood:
                mood_lower = mood.lower().strip()
                mood_counter[mood_lower] += 1
                mood_to_venues[mood_lower].append(venue_name)

    return mood_counter, mood_to_venues


def suggest_arcana(mood, synonym_to_arcana):
    """
    Suggest which arcana a mood might belong to based on partial matches.
    """
    suggestions = []
    mood_lower = mood.lower()

    # Check for partial matches in existing synonyms
    for synonym, arcana in synonym_to_arcana.items():
        # Check if mood contains or is contained by a synonym
        if len(mood_lower) >= 4 and len(synonym) >= 4:
            if mood_lower in synonym or synonym in mood_lower:
                suggestions.append((arcana, synonym, "partial match"))
            elif mood_lower[:4] == synonym[:4]:
                suggestions.append((arcana, synonym, "prefix match"))

    # Dedupe by arcana
    seen = set()
    unique_suggestions = []
    for arcana, synonym, match_type in suggestions:
        if arcana not in seen:
            seen.add(arcana)
            unique_suggestions.append((arcana, synonym, match_type))

    return unique_suggestions[:3]  # Top 3 suggestions


def main():
    parser = argparse.ArgumentParser(
        description="Find venue mood tags not mapped in mood_index.json"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show which venues use each unmapped mood"
    )
    parser.add_argument(
        "--suggest", "-s",
        action="store_true",
        help="Suggest which arcana unmapped moods might belong to"
    )
    parser.add_argument(
        "--min-count", "-m",
        type=int,
        default=1,
        help="Only show moods used by at least N venues (default: 1)"
    )
    args = parser.parse_args()

    # Load data
    print("Loading venue data...")
    venues = load_json(VENUES_PATH)
    mood_index = load_json(MOOD_INDEX_PATH)

    print(f"  → {len(venues)} venues loaded")
    print(f"  → {len(mood_index)} arcana in mood_index.json")

    # Build synonym set
    known_synonyms, synonym_to_arcana = build_synonym_set(mood_index)
    print(f"  → {len(known_synonyms)} known synonyms")

    # Extract venue moods
    mood_counter, mood_to_venues = extract_venue_moods(venues)
    unique_moods = set(mood_counter.keys())
    print(f"  → {len(unique_moods)} unique mood tags in venues")

    # Find unmapped moods
    unmapped = unique_moods - known_synonyms
    unmapped_filtered = {m for m in unmapped if mood_counter[m] >= args.min_count}

    # Sort by frequency (most common first)
    unmapped_sorted = sorted(
        unmapped_filtered,
        key=lambda m: (-mood_counter[m], m)
    )

    # Report
    print("\n" + "=" * 60)
    print("UNMAPPED MOOD TAGS")
    print("=" * 60)

    if not unmapped_sorted:
        print("\n✅ All mood tags are mapped! No gaps found.")
        return

    print(f"\n⚠️  Found {len(unmapped_sorted)} unmapped mood tags")
    print(f"   (out of {len(unique_moods)} unique moods, {len(unmapped_sorted)/len(unique_moods)*100:.1f}% unmapped)")
    print("\nNote: These moods ARE still searchable via text search,")
    print("but won't map to an arcana for primary mood-based matching.\n")

    if args.min_count > 1:
        print(f"Showing moods used by {args.min_count}+ venues:\n")

    for mood in unmapped_sorted:
        count = mood_counter[mood]
        venues_using = mood_to_venues[mood]

        print(f"  • \"{mood}\" ({count} venue{'s' if count != 1 else ''})")

        if args.verbose:
            for venue_name in venues_using[:5]:
                print(f"      → {venue_name}")
            if len(venues_using) > 5:
                print(f"      → ... and {len(venues_using) - 5} more")

        if args.suggest:
            suggestions = suggest_arcana(mood, synonym_to_arcana)
            if suggestions:
                print(f"      💡 Maybe add to: ", end="")
                print(", ".join(f"{arcana}" for arcana, _, _ in suggestions))

        if args.verbose or args.suggest:
            print()

    # Summary by frequency
    print("\n" + "-" * 60)
    print("SUMMARY BY FREQUENCY")
    print("-" * 60)

    freq_buckets = {
        "10+ venues": [m for m in unmapped_sorted if mood_counter[m] >= 10],
        "5-9 venues": [m for m in unmapped_sorted if 5 <= mood_counter[m] < 10],
        "2-4 venues": [m for m in unmapped_sorted if 2 <= mood_counter[m] < 5],
        "1 venue": [m for m in unmapped_sorted if mood_counter[m] == 1],
    }

    for bucket_name, moods in freq_buckets.items():
        if moods:
            print(f"\n{bucket_name}: {len(moods)} moods")
            if bucket_name != "1 venue" or len(moods) <= 10:
                print(f"  {', '.join(moods[:20])}")
                if len(moods) > 20:
                    print(f"  ... and {len(moods) - 20} more")

    # Actionable output for adding to mood_index.json
    print("\n" + "-" * 60)
    print("QUICK ADD (most common unmapped moods)")
    print("-" * 60)
    print("\nConsider adding these to mood_index.json:\n")

    top_unmapped = unmapped_sorted[:15]
    for mood in top_unmapped:
        count = mood_counter[mood]
        suggestions = suggest_arcana(mood, synonym_to_arcana)
        if suggestions:
            arcana = suggestions[0][0]
            print(f'  "{mood}",  # {count} venues → {arcana}?')
        else:
            print(f'  "{mood}",  # {count} venues')


if __name__ == "__main__":
    import sys
    try:
        main()
    except BrokenPipeError:
        # Handle piping to head/less gracefully
        sys.stderr.close()
        sys.exit(0)
