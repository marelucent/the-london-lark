import json

# Load ClaudeCode's version (with refuge tags)
with open('claude_refuge_version.json', 'r', encoding='utf-8') as f:
    claude_venues = json.load(f)

# Load your current version (139 venues)
with open('lark_venues_clean.json', 'r', encoding='utf-8') as f:
    current_venues = json.load(f)

print(f"ClaudeCode version: {len(claude_venues)} venues")
print(f"Your current version: {len(current_venues)} venues")

# Count refuge tags in ClaudeCode's version
refuge_venues = [v for v in claude_venues if v.get('refuge')]
print(f"Refuge-tagged venues: {len(refuge_venues)}")

# Show which venues got refuge tags
print(f"\nVenues tagged as refuges:")
for v in refuge_venues[:10]:
    print(f"  - {v['name']}")
if len(refuge_venues) > 10:
    print(f"  ... and {len(refuge_venues) - 10} more")
