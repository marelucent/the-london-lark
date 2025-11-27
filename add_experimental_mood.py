#!/usr/bin/env python3
"""
Add 'Experimental / Avant-garde' mood to mood_index.json
"""

import json
from pathlib import Path

# Load existing mood index
mood_file = Path("mood_index.json")
with open(mood_file, 'r', encoding='utf-8') as f:
    mood_index = json.load(f)

# Add new mood
new_mood = {
    "Experimental / Avant-garde": {
        "description": "Boundary-pushing, risk-taking work that refuses to behave. Where art tests its own limits.",
        "synonyms": [
            "experimental",
            "avant-garde",
            "avant garde",
            "avantgarde",
            "scratch",
            "work-in-progress",
            "work in progress",
            "wip",
            "boundary-pushing",
            "cutting-edge",
            "cutting edge",
            "progressive",
            "radical",
            "bold",
            "daring",
            "unconventional",
            "innovative",
            "pioneering",
            "edgy",
            "provocative",
            "challenging",
            "unfinished",
            "raw",
            "rough",
            "in development",
            "testing",
            "試行"
        ],
        "vibe_notes": "Tiny universes at ignition, mid-moult."
    }
}

# Add to mood index
mood_index.update(new_mood)

# Save back
with open(mood_file, 'w', encoding='utf-8') as f:
    json.dump(mood_index, f, indent=2, ensure_ascii=False)

print("✅ Added 'Experimental / Avant-garde' to mood_index.json")
print(f"📊 Total moods now: {len(mood_index)}")
print("\nNew mood synonyms:")
for synonym in new_mood["Experimental / Avant-garde"]["synonyms"][:10]:
    print(f"  - {synonym}")
print(f"  ... and {len(new_mood['Experimental / Avant-garde']['synonyms'])-10} more")
