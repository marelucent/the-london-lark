#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Venue Data Restructuring Script

"""
Parses lark_venues_clean.json from messy multiline format into proper structured JSON.
Extracts all fields into separate keys for easier querying and display.
"""

import json
import re

def extract_emoji(text):
    """Extract the first emoji from text"""
    # Common emoji pattern
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001F9FF"  # Misc Symbols and Pictographs
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F680-\U0001F6FF"  # Transport and Map
        "\U0001F1E0-\U0001F1FF"  # Flags
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )

    match = emoji_pattern.search(text)
    return match.group(0) if match else ""

def clean_website(website):
    """Clean and format website URL"""
    if not website or website.strip() == "" or "n/a" in website.lower():
        return ""

    website = website.strip()

    # Add https:// if no protocol
    if not website.startswith('http://') and not website.startswith('https://'):
        website = 'https://' + website

    return website

def extract_area_from_tags(tags_str):
    """Extract area/region from tags string (usually marked with 🧭)"""
    if not tags_str:
        return ""

    # Look for 🧭 followed by location
    match = re.search(r'🧭\s*([^|]+)', tags_str)
    if match:
        return match.group(1).strip()

    # Fallback: check for common London areas
    areas = ['South London', 'North London', 'East London', 'West London',
             'Central London', 'South East London']
    for area in areas:
        if area in tags_str:
            return area

    return ""

def parse_venue_multiline(venue_str):
    """Parse a multiline venue string into structured data"""
    lines = venue_str.split('\n')

    venue = {}

    # First line is the name with emoji
    full_name = lines[0].strip()
    emoji = extract_emoji(full_name)

    # Remove emoji from display name
    display_name = full_name
    if emoji:
        display_name = display_name.replace(emoji, '').strip()

    venue['name'] = full_name
    venue['emoji'] = emoji
    venue['display_name'] = display_name

    # Parse remaining fields
    for line in lines[1:]:
        line = line.strip()

        if line.startswith('Type:'):
            venue['type'] = line.replace('Type:', '').strip()

        elif line.startswith('Location:'):
            venue['location'] = line.replace('Location:', '').strip()

        elif line.startswith('Website:'):
            raw_website = line.replace('Website:', '').strip()
            venue['website'] = clean_website(raw_website)

        elif line.startswith('Mapped Mood Tags:'):
            tags_str = line.replace('Mapped Mood Tags:', '').strip()
            # Split by comma and clean
            venue['mood_tags'] = [tag.strip() for tag in tags_str.split(',') if tag.strip()]

        elif line.startswith('Tone Notes:'):
            venue['tone_notes'] = line.replace('Tone Notes:', '').strip()

        elif line.startswith('Lark Fit Notes:'):
            venue['lark_fit_notes'] = line.replace('Lark Fit Notes:', '').strip()

        elif line.startswith('Tags:'):
            tags_str = line.replace('Tags:', '').strip()
            # Split by pipe and clean
            venue['tags'] = [tag.strip() for tag in tags_str.split('|') if tag.strip()]
            # Extract area from tags
            if 'area' not in venue or not venue.get('area'):
                venue['area'] = extract_area_from_tags(tags_str)

        elif line.startswith('Typical Start Time:'):
            venue['typical_start_time'] = line.replace('Typical Start Time:', '').strip()

        elif line.startswith('Typical Price:'):
            venue['price'] = line.replace('Typical Price:', '').strip()

    # If area not found yet, try to extract from location
    if 'area' not in venue or not venue.get('area'):
        location = venue.get('location', '')
        # Extract text before parentheses as area
        area_match = re.match(r'^([^(]+)', location)
        if area_match:
            venue['area'] = area_match.group(1).strip()
        else:
            venue['area'] = ""

    # Set defaults for missing fields
    venue.setdefault('website', '')
    venue.setdefault('mood_tags', [])
    venue.setdefault('tags', [])
    venue.setdefault('tone_notes', '')
    venue.setdefault('lark_fit_notes', '')
    venue.setdefault('type', '')
    venue.setdefault('location', '')
    venue.setdefault('area', '')

    return venue

def parse_all_venues(input_file):
    """Parse all venues from the messy JSON format"""
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_venues = json.load(f)

    structured_venues = []
    errors = []

    for i, raw_venue in enumerate(raw_venues):
        try:
            venue_str = raw_venue.get('name', '')
            if venue_str:
                parsed = parse_venue_multiline(venue_str)
                structured_venues.append(parsed)
            else:
                errors.append(f"Venue {i}: Empty name field")
        except Exception as e:
            errors.append(f"Venue {i}: {str(e)}")

    return structured_venues, errors

def validate_venues(venues):
    """Validate the parsed venues"""
    stats = {
        'total': len(venues),
        'with_website': 0,
        'with_mood_tags': 0,
        'with_area': 0,
        'missing_tone_notes': 0,
        'missing_lark_notes': 0
    }

    for v in venues:
        if v.get('website'):
            stats['with_website'] += 1
        if v.get('mood_tags'):
            stats['with_mood_tags'] += 1
        if v.get('area'):
            stats['with_area'] += 1
        if not v.get('tone_notes'):
            stats['missing_tone_notes'] += 1
        if not v.get('lark_fit_notes'):
            stats['missing_lark_notes'] += 1

    return stats

if __name__ == '__main__':
    print("="*70)
    print("  LONDON LARK VENUE DATA RESTRUCTURING")
    print("="*70)
    print()

    # Parse venues
    print("📖 Parsing lark_venues_clean.json...")
    venues, errors = parse_all_venues('lark_venues_clean.json')

    print(f"✓ Parsed {len(venues)} venues")

    if errors:
        print(f"\n⚠ Encountered {len(errors)} errors:")
        for error in errors[:5]:  # Show first 5
            print(f"  - {error}")

    # Validate
    print("\n📊 Validation:")
    stats = validate_venues(venues)
    print(f"  Total venues: {stats['total']}")
    print(f"  With websites: {stats['with_website']} ({stats['with_website']/stats['total']*100:.1f}%)")
    print(f"  With mood tags: {stats['with_mood_tags']} ({stats['with_mood_tags']/stats['total']*100:.1f}%)")
    print(f"  With area: {stats['with_area']} ({stats['with_area']/stats['total']*100:.1f}%)")
    print(f"  Missing tone notes: {stats['missing_tone_notes']}")
    print(f"  Missing lark notes: {stats['missing_lark_notes']}")

    # Show sample
    print("\n📝 Sample venue (first):")
    if venues:
        print(json.dumps(venues[0], indent=2, ensure_ascii=False))

    # Save to new file
    output_file = 'lark_venues_structured.json'
    print(f"\n💾 Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(venues, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved {len(venues)} structured venues")
    print("\n" + "="*70)
    print("✅ RESTRUCTURING COMPLETE")
    print("="*70)
