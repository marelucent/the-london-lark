#!/usr/bin/env python3
# 🕊️ Venue Data Parser
"""
Loads the structured venue data from lark_venues_structured.json.
Applies exclusion filtering and deduplication.
"""

import json

# Venues to exclude (user-specified, not matching Lark curation standards)
EXCLUDED_VENUES = [
    "Streatham Space Project",
    "The Château",
    "Château",
]


def load_parsed_venues():
    """
    Load structured venues from lark_venues_structured.json.

    Applies:
    - Exclusion filtering (removes specific venues)
    - Deduplication (removes duplicate venue entries by name)
    """
    with open('lark_venues_structured.json', 'r', encoding='utf-8') as f:
        raw_venues = json.load(f)

    # Apply exclusion filter and deduplication
    seen_names = set()
    filtered_venues = []

    for venue in raw_venues:
        display_name = venue.get('display_name', venue.get('name', ''))

        # Check exclusion list
        is_excluded = False
        for excluded in EXCLUDED_VENUES:
            if excluded.lower() in display_name.lower():
                is_excluded = True
                break

        if is_excluded:
            continue

        # Check for duplicates
        if display_name in seen_names:
            continue
        seen_names.add(display_name)

        filtered_venues.append(venue)

    return filtered_venues


if __name__ == "__main__":
    venues = load_parsed_venues()
    print(f"Loaded {len(venues)} venues (after filtering and deduplication)")
    print("\nFirst venue:")
    print(json.dumps(venues[0], indent=2, ensure_ascii=False))

    print("\n\nAll unique mood tags:")
    all_moods = set()
    for v in venues:
        all_moods.update(v.get('mood_tags', []))
    for mood in sorted(all_moods):
        print(f"  - {mood}")

    # Verify exclusions
    print("\n\nVerifying exclusions:")
    for excluded in EXCLUDED_VENUES:
        found = any(excluded.lower() in v.get('display_name', '').lower() for v in venues)
        status = "❌ STILL PRESENT" if found else "✅ Excluded"
        print(f"  {excluded}: {status}")
