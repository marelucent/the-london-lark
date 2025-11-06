#!/usr/bin/env python3
# 🕊️ Venue Data Parser
"""
Parses the lark_venues_clean.json file and converts it to a usable format.
"""

import json
import re

def parse_venue_string(venue_str):
    """Parse a venue string from lark_venues_clean.json into structured data"""
    lines = venue_str.split('\n')

    venue = {}

    # Extract name (first line)
    venue['name'] = lines[0].strip()

    # Extract other fields using regex
    for line in lines[1:]:
        if line.startswith('Type:'):
            venue['type'] = line.replace('Type:', '').strip()
        elif line.startswith('Location:'):
            venue['location'] = line.replace('Location:', '').strip()
            # Extract area from location (text before parentheses)
            area_match = re.match(r'^([^(]+)', venue['location'])
            if area_match:
                venue['area'] = area_match.group(1).strip()
        elif line.startswith('Website:'):
            venue['website'] = line.replace('Website:', '').strip()
        elif line.startswith('Mapped Mood Tags:'):
            tags_str = line.replace('Mapped Mood Tags:', '').strip()
            venue['mood_tags'] = [tag.strip() for tag in tags_str.split(',')]
        elif line.startswith('Tone Notes:'):
            venue['tone_notes'] = line.replace('Tone Notes:', '').strip()
        elif line.startswith('Lark Fit Notes:'):
            venue['lark_fit_notes'] = line.replace('Lark Fit Notes:', '').strip()
        elif line.startswith('Tags:'):
            venue['tags'] = line.replace('Tags:', '').strip()
        elif line.startswith('Typical Start Time:'):
            venue['typical_start_time'] = line.replace('Typical Start Time:', '').strip()
        elif line.startswith('Typical Price:'):
            venue['price'] = line.replace('Typical Price:', '').strip()

    return venue

def load_parsed_venues():
    """Load and parse all venues from lark_venues_clean.json"""
    with open('lark_venues_clean.json', 'r', encoding='utf-8') as f:
        raw_venues = json.load(f)

    parsed_venues = []
    for raw_venue in raw_venues:
        venue_str = raw_venue.get('name', '')
        if venue_str:
            parsed = parse_venue_string(venue_str)
            parsed_venues.append(parsed)

    return parsed_venues

if __name__ == "__main__":
    venues = load_parsed_venues()
    print(f"Parsed {len(venues)} venues")
    print("\nFirst venue:")
    print(json.dumps(venues[0], indent=2, ensure_ascii=False))

    print("\n\nAll unique mood tags:")
    all_moods = set()
    for v in venues:
        all_moods.update(v.get('mood_tags', []))
    for mood in sorted(all_moods):
        print(f"  - {mood}")
