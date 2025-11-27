import json

with open('lark_venues_clean_v2.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)
with open('mood_index_v2_CORRECTED.json', 'r', encoding='utf-8') as f:
    mood_index = json.load(f)

all_taxonomy_moods = set(mood_index['core'] + mood_index['extended'])
unknown_moods = set()

for venue in venues:
    for mood in venue.get('moods', []):
        if mood not in all_taxonomy_moods:
            unknown_moods.add(mood)

print("UNKNOWN MOODS (not in taxonomy):")
print(f"Total: {len(unknown_moods)}\n")
for mood in sorted(unknown_moods):
    # Count how many venues use it
    count = sum(1 for v in venues if mood in v.get('moods', []))
    print(f"  {mood:45} ({count:3} venues)")
