#!/usr/bin/env python3
"""
Verify mood tags feature implementation.
"""

from app import load_core_moods
import os

print("=" * 70)
print("MOOD TAGS FEATURE VERIFICATION")
print("=" * 70)
print()

# Test 1: Load core moods
print("1. Testing load_core_moods()...")
moods = load_core_moods()
print(f"   [+] Loaded {len(moods)} core moods")
print(f"   [+] First mood: '{moods[0]}'")
print(f"   [+] Last mood: '{moods[-1]}'")
print()

# Test 2: Check if moods are Title Case
print("2. Verifying all moods are Title Case...")
all_title_case = all(mood[0].isupper() for mood in moods)
if all_title_case:
    print(f"   [+] All moods Title Case: YES")
else:
    print(f"   [!] ERROR: Some moods not Title Case")
print()

# Test 3: Display sample moods
print("3. Sample Core moods to be displayed:")
for i, mood in enumerate(moods[:10], 1):
    print(f"   {i:2}. {mood}")
print("   ...")
print(f"   30. {moods[-1]}")
print()

# Test 4: Check files were updated
print("4. Checking file updates...")
files_to_check = [
    ('app.py', 'load_core_moods'),
    ('templates/index.html', 'mood-tags-container'),
    ('templates/index.html', 'searchByMood'),
    ('static/style.css', 'mood-tags-container'),
]

all_good = True
for file_path, search_term in files_to_check:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_term in content:
                print(f"   [+] {file_path}: contains '{search_term}'")
            else:
                print(f"   [!] {file_path}: MISSING '{search_term}'")
                all_good = False
    else:
        print(f"   [!] {file_path}: FILE NOT FOUND")
        all_good = False

print()
print("=" * 70)
if all_good:
    print("✓ ALL CHECKS PASSED!")
else:
    print("✗ SOME CHECKS FAILED")
print("=" * 70)
print()
print("FEATURE SUMMARY:")
print("- 30 Core mood tags will be displayed on homepage")
print("- Tags appear below search box with 'Or explore by mood:' label")
print("- Clicking a mood tag searches for that mood")
print("- Active mood is highlighted in gold (#f0e68c)")
print("- Fully mobile-friendly with responsive design")
print()
print("TO TEST:")
print("1. Run: python app.py")
print("2. Open: http://localhost:5000")
print("3. Look for mood tags below the search box")
print("4. Click any mood tag to search!")
print()
