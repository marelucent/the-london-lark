#!/usr/bin/env python3
# 🕊️ Venue Data Parser
"""
Loads the structured venue data from lark_venues_clean.json.
Previously parsed messy format; now just loads clean structured JSON.
"""

import json

def load_parsed_venues():
    """Load structured venues from lark_venues_clean.json"""
    with open('lark_venues_clean.json', 'r', encoding='utf-8') as f:
        venues = json.load(f)
    return venues

if __name__ == "__main__":
    venues = load_parsed_venues()
    print(f"Loaded {len(venues)} venues")
    print("\nFirst venue:")
    print(json.dumps(venues[0], indent=2, ensure_ascii=False))

    print("\n\nAll unique mood tags:")
    all_moods = set()
    for v in venues:
        all_moods.update(v.get('mood_tags', []))
    for mood in sorted(all_moods):
        print(f"  - {mood}")
