#!/usr/bin/env python3
"""
Migrate The London Lark venue database to new mood taxonomy v2.

PHILOSOPHY: Extended moods are NOT errors - they're beautiful, specific,
poetic variations. They're fully searchable, just more nuanced than Core moods.

This script:
1. Loads CORRECTED taxonomy files
2. Migrates all venues according to tag_migration_map
3. Preserves all venue data
4. Generates detailed migration report
"""

import json
from collections import defaultdict
from typing import Dict, List, Any

def load_json(filepath: str) -> Any:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath: str, data: Any) -> None:
    """Save JSON file with pretty formatting."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def migrate_venue(venue: Dict, migration_map: Dict, mood_index: Dict) -> Dict:
    """
    Migrate a single venue to new taxonomy.

    Returns: (migrated_venue, stats_dict)
    """
    migrated = venue.copy()

    # Track what happened
    stats = {
        'to_core': [],
        'to_extended': [],
        'to_features': [],
        'unmapped': []
    }

    old_moods = venue.get('moods', [])
    new_moods = []
    new_features = []

    for old_tag in old_moods:
        if old_tag in migration_map:
            action = migration_map[old_tag]['action']

            if action == 'map_to_core':
                new_moods.append(old_tag)
                stats['to_core'].append(old_tag)

            elif action == 'map_to_extended':
                new_moods.append(old_tag)
                stats['to_extended'].append(old_tag)

            elif action == 'move_to_features':
                new_features.append(old_tag)
                stats['to_features'].append(old_tag)

        else:
            # Tag not in migration map - keep it as extended mood for safety
            new_moods.append(old_tag)
            stats['unmapped'].append(old_tag)

    # Update venue
    migrated['moods'] = new_moods
    if new_features:
        migrated['features'] = new_features

    return migrated, stats

def main():
    """Run the migration."""

    print("=" * 70)
    print("LONDON LARK TAXONOMY V2 MIGRATION")
    print("=" * 70)
    print()

    # Load files
    print("[*] Loading files...")
    mood_index = load_json('mood_index_v2_CORRECTED.json')
    migration_map = load_json('tag_migration_map_CORRECTED.json')
    venues = load_json('lark_venues_clean.json')

    print(f"   [+] Mood index: {mood_index['metadata']['total_core']} Core, "
          f"{mood_index['metadata']['total_extended']} Extended, "
          f"{mood_index['metadata']['total_features']} Features")
    print(f"   [+] Migration map: {len(migration_map)} tag mappings")
    print(f"   [+] Venues: {len(venues)} to migrate")
    print()

    # Migrate all venues
    print("[*] Migrating venues...")
    migrated_venues = []

    # Track global stats
    global_stats = {
        'venues_processed': 0,
        'venues_with_features': 0,
        'total_to_core': 0,
        'total_to_extended': 0,
        'total_to_features': 0,
        'total_unmapped': 0,
        'mood_distribution': defaultdict(int),
        'feature_distribution': defaultdict(int),
        'unmapped_tags': set()
    }

    samples_before_after = []

    for i, venue in enumerate(venues, 1):
        migrated_venue, stats = migrate_venue(venue, migration_map, mood_index)
        migrated_venues.append(migrated_venue)

        # Update global stats
        global_stats['venues_processed'] += 1
        if migrated_venue.get('features'):
            global_stats['venues_with_features'] += 1

        global_stats['total_to_core'] += len(stats['to_core'])
        global_stats['total_to_extended'] += len(stats['to_extended'])
        global_stats['total_to_features'] += len(stats['to_features'])
        global_stats['total_unmapped'] += len(stats['unmapped'])

        # Track mood distribution
        for mood in migrated_venue.get('moods', []):
            global_stats['mood_distribution'][mood] += 1

        # Track feature distribution
        for feature in migrated_venue.get('features', []):
            global_stats['feature_distribution'][feature] += 1

        # Track unmapped
        for tag in stats['unmapped']:
            global_stats['unmapped_tags'].add(tag)

        # Collect samples (first 5)
        if i <= 5:
            samples_before_after.append({
                'name': venue.get('name', 'Unknown'),
                'before_moods': venue.get('moods', []),
                'after_moods': migrated_venue.get('moods', []),
                'new_features': migrated_venue.get('features', []),
                'stats': stats
            })

        # Progress
        if i % 50 == 0:
            print(f"   ... processed {i}/{len(venues)} venues")

    print(f"   [+] Migrated {global_stats['venues_processed']} venues")
    print()

    # Save migrated data
    print("[*] Saving migrated data...")
    save_json('lark_venues_clean_v2.json', migrated_venues)
    print("   [+] Saved to lark_venues_clean_v2.json")
    print()

    # Generate report
    print("=" * 70)
    print("MIGRATION REPORT")
    print("=" * 70)
    print()

    print("OVERALL STATISTICS:")
    print(f"   * Venues processed: {global_stats['venues_processed']}")
    print(f"   * Venues with new 'features' field: {global_stats['venues_with_features']}")
    print()

    print("TAG MIGRATION BREAKDOWN:")
    print(f"   * Tags mapped to Core: {global_stats['total_to_core']}")
    print(f"   * Tags mapped to Extended: {global_stats['total_to_extended']}")
    print(f"   * Tags moved to Features: {global_stats['total_to_features']}")
    print(f"   * Unmapped tags (kept as Extended): {global_stats['total_unmapped']}")
    print()

    # Mood distribution - top 20
    print("TOP 20 MOODS (after migration):")
    sorted_moods = sorted(global_stats['mood_distribution'].items(),
                         key=lambda x: x[1], reverse=True)
    for mood, count in sorted_moods[:20]:
        # Check if Core or Extended
        if mood in mood_index['core']:
            label = "[CORE]"
        elif mood in mood_index['extended']:
            label = "[EXTENDED]"
        else:
            label = "[?]"
        print(f"   {label:12} {mood:40} ({count:3} venues)")
    print()

    # Features distribution
    if global_stats['feature_distribution']:
        print("FEATURES DISTRIBUTION:")
        sorted_features = sorted(global_stats['feature_distribution'].items(),
                                key=lambda x: x[1], reverse=True)
        for feature, count in sorted_features:
            print(f"   * {feature:30} ({count:3} venues)")
        print()

    # Unmapped tags
    if global_stats['unmapped_tags']:
        print("UNMAPPED TAGS (kept as Extended moods):")
        for tag in sorted(global_stats['unmapped_tags']):
            print(f"   * {tag}")
        print()

    # Sample venues
    print("=" * 70)
    print("SAMPLE VENUES (First 5)")
    print("=" * 70)
    print()

    for i, sample in enumerate(samples_before_after, 1):
        print(f"{i}. {sample['name']}")
        print(f"   BEFORE: {', '.join(sample['before_moods'])}")
        print(f"   AFTER:  {', '.join(sample['after_moods'])}")
        if sample['new_features']:
            print(f"   FEATURES: {', '.join(sample['new_features'])}")
        print(f"   Stats: Core={len(sample['stats']['to_core'])}, "
              f"Extended={len(sample['stats']['to_extended'])}, "
              f"Features={len(sample['stats']['to_features'])}, "
              f"Unmapped={len(sample['stats']['unmapped'])}")
        print()

    # Validation checks
    print("=" * 70)
    print("VALIDATION CHECKS")
    print("=" * 70)
    print()

    issues = []

    for venue in migrated_venues:
        mood_count = len(venue.get('moods', []))
        if mood_count < 2:
            issues.append(f"[!] {venue.get('name')}: Only {mood_count} mood(s)")
        elif mood_count > 4:
            issues.append(f"[!] {venue.get('name')}: {mood_count} moods (>4)")

    if issues:
        print("VENUES NEEDING REVIEW:")
        for issue in issues[:10]:  # Show first 10
            print(f"   {issue}")
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more")
    else:
        print("[+] All venues have 2-4 moods!")

    print()
    print("=" * 70)
    print("MIGRATION COMPLETE!")
    print("=" * 70)
    print()
    print("NEXT STEPS:")
    print("1. Review the report above")
    print("2. Check lark_venues_clean_v2.json")
    print("3. If satisfied, replace lark_venues_clean.json with v2")
    print()
    print("REMEMBER: Extended moods are beautiful! They're not errors.")
    print("They're just more specific and nuanced than Core moods.")
    print()

if __name__ == '__main__':
    main()
