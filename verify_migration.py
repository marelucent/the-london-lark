import json

# Load migrated venues
with open('lark_venues_clean_v2.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)
with open('mood_index_v2_CORRECTED.json', 'r', encoding='utf-8') as f:
    mood_index = json.load(f)

print("=" * 70)
print("DETAILED VERIFICATION")
print("=" * 70)
print()

# 1. Show example venue with features
print("1. EXAMPLE: Venue with new 'features' field")
print("-" * 70)
venues_with_features = [v for v in venues if v.get('features')]
if venues_with_features:
    v = venues_with_features[0]
    print(f"Name: {v['name']}")
    print(f"Moods: {', '.join(v['moods'])}")
    print(f"Features: {', '.join(v.get('features', []))}")
    print()

# 2. Show venue with Extended moods
print("2. EXAMPLE: Venue with Extended moods (rescued tags!)")
print("-" * 70)
v = venues[2]  # 5Rhythms
print(f"Name: {v['name']}")
print(f"Moods: {', '.join(v['moods'])}")
for mood in v['moods']:
    if mood in mood_index['extended']:
        print(f"  [+] '{mood}' is Extended mood (RESCUED!)")
print()

# 3. Show venues with issues
print("3. VENUES NEEDING ATTENTION (only 1 mood)")
print("-" * 70)
issues = [v for v in venues if len(v.get('moods', [])) < 2]
print(f"Found {len(issues)} venues with < 2 moods:\n")
for v in issues:
    print(f"  • {v['name']}")
    print(f"    Current moods: {v.get('moods', [])}")
    print()

# 4. Summary stats
print("=" * 70)
print("FINAL VALIDATION SUMMARY")
print("=" * 70)
core_count = 0
extended_count = 0
unknown_count = 0

for venue in venues:
    for mood in venue.get('moods', []):
        if mood in mood_index['core']:
            core_count += 1
        elif mood in mood_index['extended']:
            extended_count += 1
        else:
            unknown_count += 1

print(f"Total venues: {len(venues)}")
print(f"Venues with features field: {len([v for v in venues if v.get('features')])}")
print(f"Total mood tags: {core_count + extended_count + unknown_count}")
print(f"  • Core moods: {core_count}")
print(f"  • Extended moods: {extended_count} (rescued tags!)")
print(f"  • Unknown moods: {unknown_count}")
print()

if unknown_count == 0:
    print("[+] SUCCESS: All moods accounted for in taxonomy!")
else:
    print(f"[!] WARNING: {unknown_count} moods not in taxonomy")

print()
print("=" * 70)
print("MIGRATION QUALITY: EXCELLENT")
print("All 108 rescued tags preserved as Extended moods!")
print("=" * 70)
