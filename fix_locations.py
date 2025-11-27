#!/usr/bin/env python3
"""
Location Formatting Fix Script
Systematically fixes all 170 location formatting issues identified in the audit
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

VENUES_FILE = "lark_venues_clean.json"
LOCATION_ISSUES_FILE = "outputs/location_issues.json"
OUTPUT_DIR = Path("outputs")

# Approved neighborhoods from VENUE_DATA_STANDARDS.md
APPROVED_NEIGHBORHOODS = {
    # East London (21)
    "Hackney", "Shoreditch", "Dalston", "Bethnal Green", "Whitechapel",
    "Stratford", "Hackney Wick", "Limehouse", "Bow", "Mile End", "Homerton",
    "Haggerston", "Hoxton", "Walthamstow", "Leyton", "Stepney", "Poplar",
    "Canning Town", "Barking", "Fish Island", "Tower Hamlets",

    # South London (28)
    "Peckham", "Brixton", "Camberwell", "Bermondsey", "Deptford", "Lewisham",
    "Catford", "Elephant & Castle", "New Cross", "Nunhead", "Dulwich",
    "Streatham", "Battersea", "Clapham", "Vauxhall", "Kennington", "Stockwell",
    "South Norwood", "Crystal Palace", "Forest Hill", "Greenwich", "Woolwich",
    "Eltham", "Croydon", "Sutton", "Merton", "Tooting", "Balham",

    # North London (28)
    "Camden", "Islington", "Highgate", "Finsbury Park", "Holloway",
    "Crouch End", "Finchley", "Wood Green", "Tottenham", "Kentish Town",
    "King's Cross", "St Pancras", "Hampstead", "Tufnell Park", "Archway",
    "Highbury", "Stoke Newington", "Manor House", "Southgate", "Barnet",
    "Enfield", "Muswell Hill", "Chalk Farm", "Belsize Park", "Gospel Oak",
    "Primrose Hill", "Queens Wood", "Barnsbury",

    # West London (20)
    "Ealing", "Chiswick", "Acton", "Richmond", "Hammersmith", "Shepherd's Bush",
    "Kilburn", "Notting Hill", "Kensington", "West Kensington", "Brentford",
    "Hanwell", "Hounslow", "Twickenham", "Kew", "Park Royal", "East Sheen",
    "Fulham", "Chelsea", "Earl's Court",

    # Central London (17)
    "Soho", "Covent Garden", "Holborn", "King's Cross", "Bloomsbury",
    "Fitzrovia", "Marylebone", "Clerkenwell", "Farringdon", "The Strand",
    "Trafalgar Square", "Westminster", "Victoria", "City of London",
    "Barbican", "St James's", "Leicester Square"
}

# Extended neighborhoods (commonly used but not in official list)
EXTENDED_NEIGHBORHOODS = {
    "Haggerston", "Homerton", "Queens Wood", "Barnsbury", "Gospel Oak",
    "Chalk Farm", "Belsize Park", "Primrose Hill", "East Sheen", "Park Royal",
    "Hanwell", "St Pancras", "St James's"
}

# ============================================================================
# LOCATION FIXING LOGIC
# ============================================================================

def extract_neighborhood_from_address(location):
    """
    Extract neighborhood from full address or complex location string.
    Handles cases like:
    - "Studio in Acton, West London" -> "Acton"
    - "123 High Street, Dalston" -> "Dalston"
    - "St Luke's Church, Hillmarton Road, London N7" -> Try to extract neighborhood
    """
    # First, try to find a known neighborhood in the string
    location_lower = location.lower()

    for neighborhood in sorted(APPROVED_NEIGHBORHOODS | EXTENDED_NEIGHBORHOODS,
                                key=len, reverse=True):  # Check longer names first
        if neighborhood.lower() in location_lower:
            return neighborhood

    # If no known neighborhood, try to extract from common patterns
    # Pattern: "Something in NEIGHBORHOOD, BOROUGH" or "NEIGHBORHOOD, BOROUGH"
    match = re.search(r'in\s+([A-Z][A-Za-z\s&\']+?)(?:,|\(|$)', location)
    if match:
        candidate = match.group(1).strip()
        # Check if it's a valid neighborhood
        if candidate in APPROVED_NEIGHBORHOODS | EXTENDED_NEIGHBORHOODS:
            return candidate

    # Pattern: Last part before comma might be neighborhood
    parts = location.split(',')
    if len(parts) >= 2:
        # Get the part before the last comma
        candidate = parts[-2].strip()
        # Remove common prefixes
        candidate = re.sub(r'^(Studio in|Church of|St\s+)', '', candidate).strip()
        if candidate in APPROVED_NEIGHBORHOODS | EXTENDED_NEIGHBORHOODS:
            return candidate

    return None

def fix_compound_location(location):
    """
    Fix compound locations that use & or /.
    Example: "Hackney & East London" -> "Hackney"
    Take the first/most specific part.
    """
    # Split on & or /
    parts = re.split(r'\s+[&/]\s+', location)

    # Take the first part
    first_part = parts[0].strip()

    # Clean it up
    first_part = re.sub(r'\s+venues?.*$', '', first_part, flags=re.IGNORECASE)
    first_part = re.sub(r'\(.*?\)', '', first_part).strip()

    # Check if it's in approved list
    if first_part in APPROVED_NEIGHBORHOODS | EXTENDED_NEIGHBORHOODS:
        return first_part

    # Try to extract neighborhood from first part
    extracted = extract_neighborhood_from_address(first_part)
    if extracted:
        return extracted

    # If first part doesn't work, try other parts
    for part in parts[1:]:
        part = part.strip()
        part = re.sub(r'\s+venues?.*$', '', part, flags=re.IGNORECASE)
        part = re.sub(r'\(.*?\)', '', part).strip()

        if part in APPROVED_NEIGHBORHOODS | EXTENDED_NEIGHBORHOODS:
            return part

        extracted = extract_neighborhood_from_address(part)
        if extracted:
            return extracted

    return None

def fix_borough_format(location):
    """
    Fix borough format locations.
    Example: "Acton, West London" -> "Acton"
    Strip everything after the comma.
    """
    # Split on comma
    parts = location.split(',')

    # Take first part
    neighborhood = parts[0].strip()

    # Remove "Studio in" and similar prefixes
    neighborhood = re.sub(r'^(Studio in|Church of|Located in)\s+', '', neighborhood, flags=re.IGNORECASE).strip()

    # Remove parentheses
    neighborhood = re.sub(r'\(.*?\)', '', neighborhood).strip()

    # Check if it's valid
    if neighborhood in APPROVED_NEIGHBORHOODS | EXTENDED_NEIGHBORHOODS:
        return neighborhood

    # Try to extract from the full location
    extracted = extract_neighborhood_from_address(location)
    if extracted:
        return extracted

    return neighborhood  # Return it anyway if we can't find better

def fix_not_in_approved_list(location, venue_data):
    """
    Fix locations not in approved list.
    Try to extract a valid neighborhood or flag for manual review.
    """
    # Skip if it's already "Various London venues"
    if location == "Various London venues":
        return location, False  # (fixed_location, needs_manual_review)

    # First, try to extract a known neighborhood
    extracted = extract_neighborhood_from_address(location)
    if extracted:
        return extracted, False

    # Check if it's a generic area descriptor
    generic_areas = [
        "East London", "West London", "North London", "South London",
        "Central London", "North West London", "South East London"
    ]

    if location in generic_areas:
        # Flag for manual review - we need more context
        return location, True

    # Check if location contains a postcode pattern
    if re.search(r'\b[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}\b', location):
        # Has postcode - try to extract neighborhood before it
        before_postcode = re.split(r'\b[A-Z]{1,2}\d{1,2}', location)[0]
        extracted = extract_neighborhood_from_address(before_postcode)
        if extracted:
            return extracted, False

    # Clean up the location string
    cleaned = location

    # Remove common noise
    cleaned = re.sub(r',.*$', '', cleaned)  # Remove everything after comma
    cleaned = re.sub(r'\(.*?\)', '', cleaned)  # Remove parentheses
    cleaned = re.sub(r'^(Studio in|Church of|Located in)\s+', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()

    # Check if cleaned version is in approved list
    if cleaned in APPROVED_NEIGHBORHOODS | EXTENDED_NEIGHBORHOODS:
        return cleaned, False

    # If we still can't fix it, flag for manual review
    return location, True

def apply_location_fix(venue_id, venue_data, issue):
    """
    Apply the appropriate fix based on issue type.
    Returns: (new_location, was_fixed, needs_manual_review, fix_note)
    """
    current_location = venue_data.get("location", "")
    issue_type = issue["issue_type"]

    # Handle different issue types
    if issue_type == "compound_location":
        fixed = fix_compound_location(current_location)
        if fixed:
            return fixed, True, False, f"Extracted '{fixed}' from compound location"
        else:
            return current_location, False, True, "Could not determine primary neighborhood from compound"

    elif issue_type == "borough_format":
        fixed = fix_borough_format(current_location)
        if fixed and fixed != current_location:
            return fixed, True, False, f"Stripped borough format to '{fixed}'"
        else:
            return current_location, False, True, "Could not cleanly extract neighborhood"

    elif issue_type == "not_in_approved_list":
        fixed, needs_review = fix_not_in_approved_list(current_location, venue_data)
        if not needs_review and fixed != current_location:
            return fixed, True, False, f"Extracted '{fixed}' from address"
        elif not needs_review:
            # It's a valid neighborhood not in approved list
            return fixed, False, False, f"Valid neighborhood '{fixed}' (extend approved list)"
        else:
            return current_location, False, True, "Cannot determine specific neighborhood"

    else:
        return current_location, False, False, f"Unknown issue type: {issue_type}"

# ============================================================================
# MAIN PROCESSING
# ============================================================================

def main():
    print("=" * 70)
    print("LOCATION FORMATTING FIX SCRIPT")
    print("=" * 70)
    print()

    # Check backup exists
    backup_files = list(Path(".").glob("lark_venues_clean_BACKUP_*.json"))
    if not backup_files:
        print("ERROR: No backup file found!")
        print("Please create backup first:")
        print("  cp lark_venues_clean.json lark_venues_clean_BACKUP_$(date +%Y%m%d_%H%M%S).json")
        return

    latest_backup = sorted(backup_files)[-1]
    print(f"[OK] Backup found: {latest_backup.name}")
    print()

    # Load venues
    print("Loading venues...")
    with open(VENUES_FILE, "r", encoding="utf-8") as f:
        venues = json.load(f)
    print(f"[OK] Loaded {len(venues)} venues")

    # Load location issues
    print("Loading location issues audit...")
    with open(LOCATION_ISSUES_FILE, "r", encoding="utf-8") as f:
        location_issues = json.load(f)
    print(f"[OK] Loaded {location_issues['total_issues']} location issues")
    print()

    # Group issues by venue_id
    issues_by_venue = defaultdict(list)
    for issue in location_issues["venues_with_issues"]:
        issues_by_venue[issue["venue_id"]].append(issue)

    print(f"Processing {len(issues_by_venue)} unique venues with location issues...")
    print()

    # Track fixes
    fixes_applied = []
    fixes_by_type = defaultdict(int)
    manual_review_needed = []
    new_neighborhoods_found = set()

    # Apply fixes
    for venue_id, issues in sorted(issues_by_venue.items()):
        venue = venues[venue_id]
        original_location = venue.get("location", "")

        # Process the first/most critical issue for this venue
        # (venues may have multiple overlapping issues)
        primary_issue = issues[0]

        # Apply fix
        new_location, was_fixed, needs_review, note = apply_location_fix(
            venue_id, venue, primary_issue
        )

        if needs_review:
            manual_review_needed.append({
                "venue_id": venue_id,
                "venue_name": venue.get("name", "Unknown"),
                "current_location": original_location,
                "reason": note
            })
            print(f"[REVIEW] Venue {venue_id}: {venue.get('name', 'Unknown')}")
            print(f"         Location: '{original_location}' - {note}")

        elif was_fixed:
            # Apply the fix
            venue["location"] = new_location

            fixes_applied.append({
                "venue_id": venue_id,
                "venue_name": venue.get("name", "Unknown"),
                "original_location": original_location,
                "new_location": new_location,
                "issue_type": primary_issue["issue_type"],
                "note": note
            })

            fixes_by_type[primary_issue["issue_type"]] += 1

            print(f"[FIXED] Venue {venue_id}: {venue.get('name', 'Unknown')}")
            print(f"        '{original_location}' -> '{new_location}'")

            # Check if it's a new neighborhood
            if new_location not in APPROVED_NEIGHBORHOODS and new_location != "Various London venues":
                new_neighborhoods_found.add(new_location)

        else:
            # No fix needed (already valid)
            if new_location not in APPROVED_NEIGHBORHOODS and new_location != "Various London venues":
                new_neighborhoods_found.add(new_location)

            print(f"[KEEP]  Venue {venue_id}: '{new_location}' - {note}")

    print()
    print("=" * 70)
    print("FIX SUMMARY")
    print("=" * 70)
    print(f"Total venues processed: {len(issues_by_venue)}")
    print(f"Fixes applied: {len(fixes_applied)}")
    print(f"Manual review needed: {len(manual_review_needed)}")
    print(f"New neighborhoods found: {len(new_neighborhoods_found)}")
    print()

    if fixes_by_type:
        print("Fixes by type:")
        for fix_type, count in fixes_by_type.items():
            print(f"  - {fix_type}: {count}")
        print()

    # Save updated venues
    print("Saving updated venues...")
    with open(VENUES_FILE, "w", encoding="utf-8") as f:
        json.dump(venues, f, indent=2, ensure_ascii=False)
    print(f"[OK] Saved to {VENUES_FILE}")
    print()

    # Generate reports
    print("Generating reports...")

    # JSON report
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "backup_created": latest_backup.name,
        "total_venues_processed": len(issues_by_venue),
        "total_fixes_applied": len(fixes_applied),
        "fixes_by_type": dict(fixes_by_type),
        "manual_review_needed": manual_review_needed,
        "new_neighborhoods_found": sorted(list(new_neighborhoods_found)),
        "detailed_fixes": fixes_applied
    }

    with open(OUTPUT_DIR / "location_fixes_applied.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("[OK] Generated location_fixes_applied.json")

    # Markdown report
    md_lines = []
    md_lines.append("# Location Fixes Applied")
    md_lines.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    md_lines.append("---\n")

    md_lines.append("## Summary\n")
    md_lines.append(f"- **Backup created:** `{latest_backup.name}`")
    md_lines.append(f"- **Total venues processed:** {len(issues_by_venue)}")
    md_lines.append(f"- **Fixes applied:** {len(fixes_applied)}")
    md_lines.append(f"- **Manual review needed:** {len(manual_review_needed)}")
    md_lines.append(f"- **New neighborhoods found:** {len(new_neighborhoods_found)}\n")

    if fixes_by_type:
        md_lines.append("## Fixes by Type\n")
        for fix_type, count in sorted(fixes_by_type.items()):
            md_lines.append(f"- **{fix_type}:** {count} fixes")
        md_lines.append("")

    if new_neighborhoods_found:
        md_lines.append("## New Neighborhoods Found\n")
        md_lines.append("These neighborhoods are valid but not in the approved list (consider adding):\n")
        for neighborhood in sorted(new_neighborhoods_found):
            md_lines.append(f"- {neighborhood}")
        md_lines.append("")

    if manual_review_needed:
        md_lines.append("## Manual Review Needed\n")
        md_lines.append(f"{len(manual_review_needed)} venues need manual review:\n")
        for item in manual_review_needed:
            md_lines.append(f"### Venue {item['venue_id']}: {item['venue_name']}\n")
            md_lines.append(f"- **Current location:** {item['current_location']}")
            md_lines.append(f"- **Reason:** {item['reason']}\n")

    if fixes_applied:
        md_lines.append("## All Fixes Applied\n")
        md_lines.append("| Venue ID | Venue Name | Original Location | New Location | Type |")
        md_lines.append("|----------|------------|-------------------|--------------|------|")
        for fix in fixes_applied:
            md_lines.append(
                f"| {fix['venue_id']} | {fix['venue_name']} | "
                f"{fix['original_location']} | {fix['new_location']} | "
                f"{fix['issue_type']} |"
            )
        md_lines.append("")

    md_lines.append("---\n")
    md_lines.append("*Location data cleaned and standardized*\n")

    with open(OUTPUT_DIR / "location_fixes_applied.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print("[OK] Generated location_fixes_applied.md")
    print()

    print("=" * 70)
    print("COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Review location_fixes_applied.md for summary")
    print("2. Check manual_review_needed for venues requiring attention")
    print("3. Test searches to verify improvements")
    print("4. Consider adding new neighborhoods to approved list")

if __name__ == "__main__":
    main()
