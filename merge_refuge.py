import json

# Read both files
with open('lark_venues_clean.json', 'r', encoding='utf-8') as f:
    current = json.load(f)

# Get refuge tags from ClaudeCode's branch via git
import subprocess
result = subprocess.run(
    ['git', 'show', 'origin/claude/gentle-refuge-tagging-012RKwLhN7Q3emNVX1p2Ri6e:lark_venues_clean.json'],
    capture_output=True
)

# Parse as JSON (try different encodings)
try:
    claude = json.loads(result.stdout.decode('utf-8'))
except:
    claude = json.loads(result.stdout.decode('utf-16'))

print(f"Your current: {len(current)} venues")
print(f"ClaudeCode: {len(claude)} venues")

# Find refuge tags
refuge_map = {v['name']: v.get('refuge', False) for v in claude}
refuge_count = sum(1 for r in refuge_map.values() if r)
print(f"Refuge tags: {refuge_count}")

# Apply refuge tags to your venues
for venue in current:
    if venue['name'] in refuge_map and refuge_map[venue['name']]:
        venue['refuge'] = True

# Save
with open('lark_venues_clean_with_refuge.json', 'w', encoding='utf-8') as f:
    json.dump(current, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved to: lark_venues_clean_with_refuge.json")
print(f"Venues with refuge tag: {sum(1 for v in current if v.get('refuge'))}")