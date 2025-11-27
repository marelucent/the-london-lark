#!/usr/bin/env python3
"""
Merge new venue JSON files into lark_venues_clean.json

This script:
1. Loads the main venue file (255 venues)
2. Loads the 4 new corrected files (41 venues)
3. Checks for duplicates by venue name
4. Validates JSON structure
5. Creates merged file for review
6. Saves as lark_venues_clean_MERGED.json
"""

import json
from pathlib import Path

def load_json(filepath):
    """Load and parse JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Save data as formatted JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def check_duplicates(venues):
    """Check for duplicate venue names"""
    names = [v.get('name', '').lower() for v in venues]
    duplicates = [name for name in names if names.count(name) > 1]
    return list(set(duplicates))

def main():
    print("🕊️ MERGING VENUE FILES\n")
    print("=" * 60)
    
    # File paths
    main_file = Path("lark_venues_clean.json")
    new_files = [
        Path("choirs_corrected.json"),
        Path("scratch_nights_corrected.json"),
        Path("night_libraries_corrected.json"),
        Path("solace_spaces_corrected.json")
    ]
    output_file = Path("lark_venues_clean_MERGED.json")
    
    # Load main venue file
    print(f"\n📂 Loading main file: {main_file}")
    main_venues = load_json(main_file)
    print(f"   ✓ Loaded {len(main_venues)} venues")
    
    # Load new venue files
    all_new_venues = []
    for filepath in new_files:
        print(f"\n📂 Loading: {filepath}")
        try:
            venues = load_json(filepath)
            print(f"   ✓ Loaded {len(venues)} venues")
            all_new_venues.extend(venues)
        except FileNotFoundError:
            print(f"   ⚠️  File not found, skipping")
            continue
    
    print(f"\n📊 Total new venues to add: {len(all_new_venues)}")
    
    # Combine all venues
    combined_venues = main_venues + all_new_venues
    print(f"📊 Combined total: {len(combined_venues)} venues")
    
    # Check for duplicates
    print("\n🔍 Checking for duplicates...")
    duplicates = check_duplicates(combined_venues)
    if duplicates:
        print(f"   ⚠️  Found duplicates: {duplicates}")
        print("   Review and remove manually if needed")
    else:
        print("   ✓ No duplicates found!")
    
    # Validate JSON structure
    print("\n🔍 Validating venue structure...")
    required_fields = ['name', 'location', 'moods', 'genres', 'url']
    issues = []
    for i, venue in enumerate(combined_venues):
        missing = [field for field in required_fields if field not in venue]
        if missing:
            issues.append(f"Venue #{i+1} ({venue.get('name', 'UNKNOWN')}) missing: {missing}")
    
    if issues:
        print(f"   ⚠️  Found {len(issues)} venues with missing fields:")
        for issue in issues[:5]:  # Show first 5
            print(f"      {issue}")
        if len(issues) > 5:
            print(f"      ... and {len(issues)-5} more")
    else:
        print("   ✓ All venues have required fields!")
    
    # Save merged file
    print(f"\n💾 Saving merged file: {output_file}")
    save_json(combined_venues, output_file)
    print(f"   ✓ Saved!")
    
    # Summary
    print("\n" + "=" * 60)
    print("✨ MERGE COMPLETE!")
    print("=" * 60)
    print(f"\n📊 SUMMARY:")
    print(f"   Original venues: {len(main_venues)}")
    print(f"   New venues added: {len(all_new_venues)}")
    print(f"   Total venues: {len(combined_venues)}")
    print(f"\n📝 NEXT STEPS:")
    print(f"   1. Review {output_file}")
    print(f"   2. If looks good, rename to lark_venues_clean.json")
    print(f"   3. git add lark_venues_clean.json")
    print(f"   4. git commit -m 'Add 41 new venues (choirs, scratch, libraries, grief)'")
    print(f"   5. git push")
    print(f"\n🕊️ The Lark grows her flock!\n")

if __name__ == "__main__":
    main()
