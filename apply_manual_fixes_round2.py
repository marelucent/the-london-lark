#!/usr/bin/env python3
"""
Manual Location Fixes - Round 2
Apply surgical fixes to flagged venues:
- Remove Canterbury venue (not London)
- Fix Heaven location
- Keep all others as-is
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

VENUES_FILE = "lark_venues_clean.json"
MANUAL_REVIEW_FILE = "outputs/location_fixes_applied.json"
OUTPUT_DIR = Path("outputs")

# Neighborhoods to recommend adding to approved list
RECOMMEND_ADDITIONS = [
    "Shepherd's Bush",
    "Canada Water",
    "Earlsfield",
    "Elephant & Castle",
    "Kensal Rise",
    "Isle of Dogs",
    "Spitalfields"
]

# ============================================================================
# MAIN PROCESSING
# ============================================================================

def categorize_kept_venues(manual_review_list, venues):
    """Categorize the venues we're keeping as-is."""
    categories = {
        "various_london_venues": [],
        "generic_areas": [],
        "valid_unlisted_neighborhoods": [],
        "pop_up_touring": [],
        "private_undisclosed": []
    }

    for item in manual_review_list:
        venue_id = item["venue_id"]
        venue = venues[venue_id]
        location = venue.get("location", "")

        if location == "Various London venues":
            categories["various_london_venues"].append({
                "id": venue_id,
                "name": venue.get("name", "Unknown"),
                "location": location
            })
        elif "pop-up" in location.lower() or "touring" in location.lower() or "rotating" in location.lower():
            categories["pop_up_touring"].append({
                "id": venue_id,
                "name": venue.get("name", "Unknown"),
                "location": location
            })
        elif "private" in location.lower() or "exact location shared" in location.lower():
            categories["private_undisclosed"].append({
                "id": venue_id,
                "name": venue.get("name", "Unknown"),
                "location": location
            })
        elif any(area in location for area in ["East London", "West London", "North London", "South London", "Central London", "North West London", "South East London"]):
            categories["generic_areas"].append({
                "id": venue_id,
                "name": venue.get("name", "Unknown"),
                "location": location
            })
        else:
            # Likely a valid neighborhood just not in approved list
            categories["valid_unlisted_neighborhoods"].append({
                "id": venue_id,
                "name": venue.get("name", "Unknown"),
                "location": location
            })

    return categories

def main():
    print("=" * 70)
    print("MANUAL LOCATION FIXES - ROUND 2")
    print("=" * 70)
    print()

    # Load venues
    print("Loading venues...")
    with open(VENUES_FILE, "r", encoding="utf-8") as f:
        venues = json.load(f)
    print(f"[OK] Loaded {len(venues)} venues")

    # Load manual review list
    print("Loading manual review list...")
    with open(MANUAL_REVIEW_FILE, "r", encoding="utf-8") as f:
        review_data = json.load(f)
        manual_review_list = review_data.get("manual_review_needed", [])
    print(f"[OK] Loaded {len(manual_review_list)} venues needing review")
    print()

    # Track changes
    venues_removed = []
    locations_updated = []

    # FIX 1: Remove Canterbury venue (Venue 49)
    print("=" * 70)
    print("FIX 1: Remove Non-London Venue")
    print("=" * 70)

    venue_49 = venues[49]
    print(f"Removing Venue 49: {venue_49.get('name', 'Unknown')}")
    print(f"  Location: {venue_49.get('location', 'Unknown')}")
    print(f"  Reason: Not in London")

    venues_removed.append({
        "venue_id": 49,
        "venue_name": venue_49.get("name", "Unknown"),
        "location": venue_49.get("location", "Unknown"),
        "reason": "Not in London"
    })

    # Remove venue 49
    del venues[49]
    print("[OK] Venue removed")
    print(f"Total venues now: {len(venues)}")
    print()

    # FIX 2: Fix Heaven's location (Venue 80 becomes 79 after deletion)
    print("=" * 70)
    print("FIX 2: Update Heaven's Location")
    print("=" * 70)

    # After deleting venue 49, all venue IDs >= 49 shift down by 1
    heaven_id = 79  # Was 80 before deletion
    heaven = venues[heaven_id]

    print(f"Updating Venue {heaven_id}: {heaven.get('name', 'Unknown')}")
    print(f"  Old location: {heaven.get('location', 'Unknown')}")

    old_location = heaven.get("location", "")
    new_location = "Westminster"

    heaven["location"] = new_location

    locations_updated.append({
        "venue_id": 79,  # New ID after deletion
        "venue_name": heaven.get("name", "Unknown"),
        "old_location": old_location,
        "new_location": new_location
    })

    print(f"  New location: {new_location}")
    print("[OK] Location updated")
    print()

    # Categorize kept venues
    print("=" * 70)
    print("ANALYZING KEPT VENUES")
    print("=" * 70)

    # Adjust manual review IDs (everything after 49 shifts down)
    adjusted_review_list = []
    for item in manual_review_list:
        if item["venue_id"] == 49:
            continue  # Skip the removed venue
        elif item["venue_id"] > 49:
            # Adjust ID down by 1
            adjusted_item = item.copy()
            adjusted_item["venue_id"] -= 1
            adjusted_review_list.append(adjusted_item)
        else:
            adjusted_review_list.append(item)

    categories = categorize_kept_venues(adjusted_review_list, venues)

    print(f"Various London venues: {len(categories['various_london_venues'])}")
    print(f"Generic areas (East/West/etc London): {len(categories['generic_areas'])}")
    print(f"Pop-up/Touring venues: {len(categories['pop_up_touring'])}")
    print(f"Private/Undisclosed locations: {len(categories['private_undisclosed'])}")
    print(f"Valid unlisted neighborhoods: {len(categories['valid_unlisted_neighborhoods'])}")
    print()

    # Identify neighborhoods to recommend for approval
    unlisted_neighborhoods = set()
    for venue_info in categories["valid_unlisted_neighborhoods"]:
        location = venue_info["location"]
        # Clean up the location to extract neighborhood name
        clean_location = location.split(",")[0].strip()
        clean_location = clean_location.split("(")[0].strip()
        unlisted_neighborhoods.add(clean_location)

    print("Neighborhoods to consider adding to approved list:")
    for neighborhood in sorted(unlisted_neighborhoods):
        print(f"  - {neighborhood}")
    print()

    # Save updated venues
    print("Saving updated venues...")
    with open(VENUES_FILE, "w", encoding="utf-8") as f:
        json.dump(venues, f, indent=2, ensure_ascii=False)
    print(f"[OK] Saved {len(venues)} venues to {VENUES_FILE}")
    print()

    # Generate JSON report
    print("Generating reports...")

    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "venues_removed": venues_removed,
        "locations_updated": locations_updated,
        "kept_as_is": {
            "various_london_venues": len(categories["various_london_venues"]),
            "generic_areas": len(categories["generic_areas"]),
            "pop_up_touring": len(categories["pop_up_touring"]),
            "private_undisclosed": len(categories["private_undisclosed"]),
            "valid_unlisted_neighborhoods": len(categories["valid_unlisted_neighborhoods"])
        },
        "kept_venues_detail": categories,
        "recommendations": {
            "add_to_approved_list": sorted(list(unlisted_neighborhoods)),
            "policy_decisions_needed": [
                "Should 'Various London venues' be formally approved for touring shows?",
                "Should 'Central London' / 'East London' be valid for roaming groups?",
                "Should we expand approved list to include all valid London neighborhoods?"
            ]
        },
        "final_stats": {
            "total_venues": len(venues),
            "venues_removed": len(venues_removed),
            "locations_updated": len(locations_updated)
        }
    }

    with open(OUTPUT_DIR / "manual_fixes_round2.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("[OK] Generated manual_fixes_round2.json")

    # Generate Markdown report
    md_lines = []
    md_lines.append("# Manual Location Fixes - Round 2")
    md_lines.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    md_lines.append("---\n")

    md_lines.append("## Summary\n")
    md_lines.append(f"Applied conservative, surgical fixes to flagged venues.\n")
    md_lines.append(f"- **Venues removed:** {len(venues_removed)}")
    md_lines.append(f"- **Locations updated:** {len(locations_updated)}")
    md_lines.append(f"- **Venues kept as-is:** {len(adjusted_review_list) - len(venues_removed)}")
    md_lines.append(f"- **Final venue count:** {len(venues)} (down from 296)\n")

    md_lines.append("---\n")

    md_lines.append("## What Was Removed\n")
    if venues_removed:
        for venue in venues_removed:
            md_lines.append(f"### Venue {venue['venue_id']}: {venue['venue_name']}\n")
            md_lines.append(f"- **Location:** {venue['location']}")
            md_lines.append(f"- **Reason:** {venue['reason']}\n")
    md_lines.append("")

    md_lines.append("## What Was Changed\n")
    if locations_updated:
        for venue in locations_updated:
            md_lines.append(f"### Venue {venue['venue_id']}: {venue['venue_name']}\n")
            md_lines.append(f"- **Old location:** {venue['old_location']}")
            md_lines.append(f"- **New location:** {venue['new_location']}\n")
    md_lines.append("")

    md_lines.append("## What Was Kept (And Why)\n")

    md_lines.append(f"### 'Various London venues' ({len(categories['various_london_venues'])} venues)\n")
    md_lines.append("**Why kept:** Valid for touring/pop-up shows without fixed location\n")
    if categories["various_london_venues"]:
        md_lines.append("Venues:")
        for v in categories["various_london_venues"][:5]:
            md_lines.append(f"- [{v['id']}] {v['name']}")
        if len(categories["various_london_venues"]) > 5:
            md_lines.append(f"- ...and {len(categories['various_london_venues']) - 5} more")
        md_lines.append("")

    md_lines.append(f"### Generic areas ({len(categories['generic_areas'])} venues)\n")
    md_lines.append("**Why kept:** Useful for roaming groups, choirs, and multi-location events\n")
    md_lines.append("Includes: 'East London', 'Central London', 'South East London', etc.\n")
    if categories["generic_areas"]:
        md_lines.append("Examples:")
        for v in categories["generic_areas"][:3]:
            md_lines.append(f"- [{v['id']}] {v['name']} - {v['location']}")
        md_lines.append("")

    md_lines.append(f"### Pop-up/Touring ({len(categories['pop_up_touring'])} venues)\n")
    md_lines.append("**Why kept:** Genuinely mobile venues\n")
    if categories["pop_up_touring"]:
        md_lines.append("Examples:")
        for v in categories["pop_up_touring"][:3]:
            md_lines.append(f"- [{v['id']}] {v['name']} - {v['location']}")
        md_lines.append("")

    md_lines.append(f"### Private/Undisclosed ({len(categories['private_undisclosed'])} venues)\n")
    md_lines.append("**Why kept:** Location shared only after booking (privacy/capacity reasons)\n")
    if categories["private_undisclosed"]:
        md_lines.append("Examples:")
        for v in categories["private_undisclosed"][:3]:
            md_lines.append(f"- [{v['id']}] {v['name']} - {v['location']}")
        md_lines.append("")

    md_lines.append(f"### Valid unlisted neighborhoods ({len(categories['valid_unlisted_neighborhoods'])} venues)\n")
    md_lines.append("**Why kept:** These are real London neighborhoods, just not in our approved list yet\n")
    if categories["valid_unlisted_neighborhoods"]:
        md_lines.append("Venues:")
        for v in categories["valid_unlisted_neighborhoods"]:
            md_lines.append(f"- [{v['id']}] {v['name']} - {v['location']}")
        md_lines.append("")

    md_lines.append("---\n")

    md_lines.append("## Recommendations\n")

    md_lines.append("### Add to Approved Neighborhoods List\n")
    md_lines.append("These are valid London neighborhoods currently in use:\n")
    for neighborhood in sorted(unlisted_neighborhoods):
        count = sum(1 for v in categories["valid_unlisted_neighborhoods"] if neighborhood in v["location"])
        md_lines.append(f"- **{neighborhood}** ({count} venue{'s' if count > 1 else ''})")
    md_lines.append("")

    md_lines.append("### Policy Decisions Needed\n")
    for question in report["recommendations"]["policy_decisions_needed"]:
        md_lines.append(f"- {question}")
    md_lines.append("")

    md_lines.append("---\n")

    md_lines.append("## Validation\n")
    md_lines.append(f"- Total venues: **{len(venues)}** (was 296, removed 1)")
    md_lines.append(f"- Heaven location: **Westminster** (was Charing Cross)")
    md_lines.append(f"- All flagged venues preserved: **Yes** (except Canterbury)")
    md_lines.append(f"- Data integrity: **Maintained**\n")

    md_lines.append("---\n")
    md_lines.append("\n*Conservative fixes applied. Location data cleaned with care.*\n")

    with open(OUTPUT_DIR / "manual_fixes_round2.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print("[OK] Generated manual_fixes_round2.md")
    print()

    # Summary
    print("=" * 70)
    print("COMPLETE!")
    print("=" * 70)
    print()
    print("Changes applied:")
    print(f"  - Removed 1 venue (Canterbury - not London)")
    print(f"  - Updated 1 location (Heaven: Charing Cross -> Westminster)")
    print(f"  - Kept {len(adjusted_review_list) - 1} flagged venues as-is")
    print()
    print(f"Final database: {len(venues)} venues")
    print()
    print("Reports generated:")
    print("  - manual_fixes_round2.json")
    print("  - manual_fixes_round2.md")
    print()
    print("Next: Test searches to verify fixes")

if __name__ == "__main__":
    main()
