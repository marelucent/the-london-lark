#!/usr/bin/env python3
"""
Quick fix for 3 venues with only 1 mood.
"""

import json

# Load venues
with open('lark_venues_clean.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

print("=" * 70)
print("FIXING 3 VENUES WITH SINGLE MOODS")
print("=" * 70)
print()

# Fix 1: Bush Theatre
for venue in venues:
    if venue.get('name') == 'Bush Theatre':
        print(f"1. Bush Theatre")
        print(f"   BEFORE: {venue['moods']}")
        venue['moods'] = ['rant', 'rebellious', 'activist']
        print(f"   AFTER:  {venue['moods']}")
        print()
        break

# Fix 2: Miller's Way Project
for venue in venues:
    if 'Miller' in venue.get('name', '') and 'Way Project' in venue.get('name', ''):
        print(f"2. {venue['name']}")
        print(f"   BEFORE: {venue['moods']}")
        venue['moods'] = ['restorative', 'healing', 'gentle']
        print(f"   AFTER:  {venue['moods']}")
        print()
        break

# Fix 3: Park Theatre
for venue in venues:
    if venue.get('name') == 'Park Theatre':
        print(f"3. Park Theatre")
        print(f"   BEFORE: {venue['moods']}")
        venue['moods'] = ['thoughtful', 'contemplative', 'The Thoughtful Stage']
        print(f"   AFTER:  {venue['moods']}")
        print()
        break

# Save updated venues
with open('lark_venues_clean.json', 'w', encoding='utf-8') as f:
    json.dump(venues, f, indent=2, ensure_ascii=False)

print("=" * 70)
print("[+] FIXES APPLIED SUCCESSFULLY")
print("=" * 70)
print()
print("All 3 venues now have 3 moods each.")
print("File updated: lark_venues_clean.json")
