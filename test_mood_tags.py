#!/usr/bin/env python3
"""
Quick test to verify mood tags feature works correctly.
"""

from app import app, load_core_moods

print("=" * 70)
print("MOOD TAGS FEATURE TEST")
print("=" * 70)
print()

# Test 1: Load core moods
print("1. Testing load_core_moods()...")
moods = load_core_moods()
print(f"   [+] Loaded {len(moods)} core moods")
print(f"   [+] First mood: {moods[0]}")
print(f"   [+] Last mood: {moods[-1]}")
print()

# Test 2: Check if moods are Title Case
print("2. Verifying all moods are Title Case...")
all_title_case = all(mood[0].isupper() for mood in moods)
print(f"   [+] All moods Title Case: {all_title_case}")
print()

# Test 3: Test Flask app context
print("3. Testing Flask app home route...")
with app.test_client() as client:
    response = client.get('/')
    if response.status_code == 200:
        print(f"   [+] Homepage loads successfully (200 OK)")

        # Check if mood tags HTML is present
        html = response.data.decode('utf-8')
        if 'mood-tags-container' in html:
            print(f"   [+] Mood tags container found in HTML")
        else:
            print(f"   [!] WARNING: Mood tags container NOT found")

        if 'searchByMood' in html:
            print(f"   [+] searchByMood() function found in JavaScript")
        else:
            print(f"   [!] WARNING: searchByMood() function NOT found")

        # Count mood tag buttons
        mood_tag_count = html.count('class="mood-tag"')
        print(f"   [+] Found {mood_tag_count} mood tag buttons in HTML")
    else:
        print(f"   [!] ERROR: Homepage failed to load (status {response.status_code})")

print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print()
print("To see the mood tags in action:")
print("1. Run: python app.py")
print("2. Open: http://localhost:5000")
print("3. Scroll down to see 'Or explore by mood:' section")
print("4. Click any mood tag to search!")
print()
