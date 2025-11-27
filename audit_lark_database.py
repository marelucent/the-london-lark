#!/usr/bin/env python3
"""
Complete Lark Database Audit Script
Audits all 296 venues against VENUE_DATA_STANDARDS.md
Generates 5 comprehensive reports for database quality assessment
"""

import json
import csv
import re
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

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

# Placeholder blurb patterns to detect
PLACEHOLDER_PATTERNS = [
    r"An experience beyond words",
    r"magic happens",
    r"dreams come true",
    r"simply divine",
    r"most extraordinary",
    r"guaranteed to transform",
    r"you've ever seen in your entire life"
]

# Output directory
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# DATA LOADING
# ============================================================================

def load_venues():
    """Load venues from JSON file."""
    with open("lark_venues_clean.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_approved_moods():
    """Load approved moods from mood_index.json."""
    with open("mood_index.json", "r", encoding="utf-8") as f:
        mood_data = json.load(f)
        return set(mood_data.keys())

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def check_location_format(location):
    """Check location for formatting issues."""
    issues = []

    # Check for compound locations
    if " & " in location or " / " in location:
        issues.append({
            "type": "compound_location",
            "severity": "CRITICAL",
            "detail": "Contains compound delimiter (& or /)"
        })

    # Check for borough format
    borough_patterns = [
        r",\s*(East|West|South|North|Central)\s+London",
        r"(East|West|South|North|Central)\s+London\s*\(",
    ]
    for pattern in borough_patterns:
        if re.search(pattern, location):
            issues.append({
                "type": "borough_format",
                "severity": "CRITICAL",
                "detail": "Contains borough/area format"
            })
            break

    # Check if location is in approved list (unless it's "Various London venues")
    if location != "Various London venues":
        # Extract the neighborhood name (before any comma or parenthesis)
        neighborhood = re.split(r'[,\(]', location)[0].strip()
        if neighborhood not in APPROVED_NEIGHBORHOODS:
            issues.append({
                "type": "not_in_approved_list",
                "severity": "CRITICAL",
                "detail": f"'{neighborhood}' not in approved neighborhoods list"
            })

    return issues

def check_mood_count(moods):
    """Check if mood count is 2-4."""
    count = len(moods) if moods else 0
    if count < 2 or count > 4:
        return {
            "type": "mood_count_wrong",
            "severity": "CRITICAL",
            "detail": f"Has {count} moods (need 2-4)"
        }
    return None

def check_moods_validity(moods, approved_moods):
    """Check if moods match approved list."""
    invalid_moods = []
    for mood in (moods or []):
        if mood not in approved_moods:
            invalid_moods.append(mood)

    if invalid_moods:
        return {
            "type": "moods_not_approved",
            "severity": "IMPORTANT",
            "detail": f"Unapproved moods: {', '.join(invalid_moods)}"
        }
    return None

def check_genre_count(genres):
    """Check if genre count is 3-5."""
    count = len(genres) if genres else 0
    if count < 3 or count > 5:
        return {
            "type": "genre_count_wrong",
            "severity": "IMPORTANT",
            "detail": f"Has {count} genres (recommended 3-5)"
        }
    return None

def check_blurb_length(blurb):
    """Check if blurb is 50-120 words."""
    if not blurb:
        return {
            "type": "blurb_missing",
            "severity": "CRITICAL",
            "detail": "Blurb is missing"
        }

    word_count = len(blurb.split())
    if word_count < 50:
        return {
            "type": "blurb_too_short",
            "severity": "IMPORTANT",
            "detail": f"Only {word_count} words (need 50-120)"
        }
    elif word_count > 120:
        return {
            "type": "blurb_too_long",
            "severity": "IMPORTANT",
            "detail": f"{word_count} words (recommended 50-120)"
        }
    return None

def check_blurb_quality(blurb):
    """Check for placeholder text in blurb."""
    if not blurb:
        return None

    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, blurb, re.IGNORECASE):
            return {
                "type": "blurb_placeholder",
                "severity": "IMPORTANT",
                "detail": f"Contains placeholder text: '{pattern}'"
            }
    return None

def check_url_format(url):
    """Check if URL has proper format."""
    if not url:
        return {
            "type": "url_missing",
            "severity": "CRITICAL",
            "detail": "URL is missing"
        }

    if not url.startswith("http://") and not url.startswith("https://"):
        return {
            "type": "url_missing_protocol",
            "severity": "MINOR",
            "detail": "URL missing http:// or https://"
        }
    return None

def check_required_fields(venue):
    """Check if all required fields are present."""
    required = ["name", "location", "moods", "genres", "url", "blurb", "last_verified"]
    missing = []

    for field in required:
        if field not in venue or not venue[field]:
            missing.append(field)

    if missing:
        return {
            "type": "missing_required_fields",
            "severity": "CRITICAL",
            "detail": f"Missing: {', '.join(missing)}"
        }
    return None

def check_staleness(last_verified):
    """Check if venue verification is stale (>6 months)."""
    if not last_verified:
        return {
            "type": "verification_missing",
            "severity": "CRITICAL",
            "detail": "No verification date"
        }

    try:
        verified_date = datetime.strptime(last_verified, "%Y-%m-%d")
        six_months_ago = datetime.now() - timedelta(days=180)

        if verified_date < six_months_ago:
            days_old = (datetime.now() - verified_date).days
            return {
                "type": "stale_verification",
                "severity": "IMPORTANT",
                "detail": f"Last verified {days_old} days ago"
            }
    except ValueError:
        return {
            "type": "invalid_date_format",
            "severity": "CRITICAL",
            "detail": f"Invalid date format: {last_verified}"
        }

    return None

# ============================================================================
# MOOD CENSUS ANALYSIS
# ============================================================================

def generate_mood_census(venues, approved_moods):
    """Generate comprehensive mood tag census."""
    mood_usage = defaultdict(lambda: {"count": 0, "venues": []})

    # Count mood usage
    for idx, venue in enumerate(venues):
        moods = venue.get("moods", [])
        for mood in moods:
            mood_usage[mood]["count"] += 1
            mood_usage[mood]["venues"].append(idx)
            mood_usage[mood]["status"] = "approved" if mood in approved_moods else "not_in_approved_list"

    # Sort by frequency
    moods_by_frequency = sorted(
        [
            {
                "tag": mood,
                "count": data["count"],
                "venues": data["venues"],
                "status": data["status"]
            }
            for mood, data in mood_usage.items()
        ],
        key=lambda x: x["count"],
        reverse=True
    )

    # Categorize unapproved moods
    unapproved_moods = [m for m in moods_by_frequency if m["status"] == "not_in_approved_list"]

    # Heuristic categorization
    canon_like = []
    beautiful_unlisted = []
    should_be_features = []

    for mood_data in unapproved_moods:
        mood = mood_data["tag"].lower()

        # Feature-like tags
        if any(word in mood for word in ["accessible", "family", "boozy", "sober", "free", "paid", "wheelchair"]):
            should_be_features.append(mood_data["tag"])
        # Expressive/poetic tags
        elif len(mood_data["tag"].split()) <= 4 and mood_data["count"] >= 3:
            beautiful_unlisted.append(mood_data["tag"])
        else:
            canon_like.append(mood_data["tag"])

    census = {
        "total_unique_moods": len(mood_usage),
        "moods_by_frequency": moods_by_frequency,
        "approved_moods_in_use": len([m for m in moods_by_frequency if m["status"] == "approved"]),
        "unapproved_moods_in_use": len(unapproved_moods),
        "summary": {
            "canon_like": canon_like[:20],  # Top candidates
            "beautiful_unlisted": beautiful_unlisted[:20],
            "should_be_features": should_be_features
        }
    }

    return census

# ============================================================================
# LOCATION ISSUES ANALYSIS
# ============================================================================

def generate_location_issues(venues):
    """Generate location issues report."""
    location_issues = []
    issue_counts = defaultdict(int)

    for idx, venue in enumerate(venues):
        location = venue.get("location", "")
        issues = check_location_format(location)

        if issues:
            for issue in issues:
                issue_counts[issue["type"]] += 1

                # Suggest fix
                suggested_fix = location
                if issue["type"] == "borough_format":
                    # Extract neighborhood before comma or borough
                    suggested_fix = re.split(r',|\(', location)[0].strip()
                elif issue["type"] == "compound_location":
                    # Take first part
                    suggested_fix = re.split(r'\s+[&/]\s+', location)[0].strip()

                location_issues.append({
                    "venue_id": idx,
                    "venue_name": venue.get("name", "Unknown"),
                    "current_location": location,
                    "issue_type": issue["type"],
                    "suggested_fix": suggested_fix,
                    "severity": issue["severity"]
                })

    report = {
        "total_issues": len(location_issues),
        "issues_by_type": dict(issue_counts),
        "venues_with_issues": location_issues
    }

    return report

# ============================================================================
# FULL VALIDATION
# ============================================================================

def generate_validation_summary(venues, approved_moods):
    """Generate comprehensive validation summary."""
    all_issues = []
    issue_counts = defaultdict(int)
    severity_counts = defaultdict(int)
    venues_with_issues = set()

    for idx, venue in enumerate(venues):
        venue_issues = []

        # Check all validation criteria
        checks = [
            check_required_fields(venue),
            check_location_format(venue.get("location", "")),
            check_mood_count(venue.get("moods", [])),
            check_moods_validity(venue.get("moods", []), approved_moods),
            check_genre_count(venue.get("genres", [])),
            check_blurb_length(venue.get("blurb", "")),
            check_blurb_quality(venue.get("blurb", "")),
            check_url_format(venue.get("url", "")),
            check_staleness(venue.get("last_verified", ""))
        ]

        # Flatten issues (some checks return lists)
        for check_result in checks:
            if check_result:
                if isinstance(check_result, list):
                    venue_issues.extend(check_result)
                else:
                    venue_issues.append(check_result)

        # Record issues
        if venue_issues:
            venues_with_issues.add(idx)
            for issue in venue_issues:
                issue_counts[issue["type"]] += 1
                severity_counts[issue["severity"]] += 1
                all_issues.append({
                    "venue_id": idx,
                    "venue_name": venue.get("name", "Unknown"),
                    "issue": issue
                })

    # Pattern analysis
    pattern_notes = analyze_patterns(venues, all_issues)

    summary = {
        "total_venues": len(venues),
        "venues_with_issues": len(venues_with_issues),
        "issues_by_type": dict(issue_counts),
        "issues_by_severity": dict(severity_counts),
        "pattern_notes": pattern_notes
    }

    return summary, all_issues

def analyze_patterns(venues, all_issues):
    """Analyze patterns in the issues."""
    patterns = []

    # Count location issues
    location_issues = [i for i in all_issues if "location" in i["issue"]["type"]]
    if location_issues:
        patterns.append(f"{len(location_issues)} venues have location formatting issues")

    # Mood validity issues
    mood_unapproved = [i for i in all_issues if i["issue"]["type"] == "moods_not_approved"]
    if mood_unapproved:
        patterns.append(f"{len(mood_unapproved)} venues use unapproved mood tags (expected - many are expressive/poetic)")

    # Blurb issues
    blurb_issues = [i for i in all_issues if "blurb" in i["issue"]["type"]]
    if blurb_issues:
        patterns.append(f"{len(blurb_issues)} venues have blurb quality/length issues")

    # Staleness
    stale = [i for i in all_issues if "stale" in i["issue"]["type"]]
    if stale:
        patterns.append(f"{len(stale)} venues have verification dates >6 months old")

    return patterns

# ============================================================================
# DETAILED ISSUES TABLE
# ============================================================================

def generate_issues_table(venues, approved_moods):
    """Generate detailed issues table (CSV and Markdown)."""
    issues_rows = []

    for idx, venue in enumerate(venues):
        venue_name = venue.get("name", "Unknown")

        # Run all checks
        location_issues = check_location_format(venue.get("location", ""))
        mood_count_issue = check_mood_count(venue.get("moods", []))
        mood_validity_issue = check_moods_validity(venue.get("moods", []), approved_moods)
        genre_count_issue = check_genre_count(venue.get("genres", []))
        blurb_length_issue = check_blurb_length(venue.get("blurb", ""))
        blurb_quality_issue = check_blurb_quality(venue.get("blurb", ""))
        url_issue = check_url_format(venue.get("url", ""))
        required_fields_issue = check_required_fields(venue)
        staleness_issue = check_staleness(venue.get("last_verified", ""))

        # Add location issues
        if location_issues:
            for issue in location_issues:
                suggested_fix = venue.get("location", "")
                if issue["type"] == "borough_format":
                    suggested_fix = re.split(r',|\(', suggested_fix)[0].strip()
                elif issue["type"] == "compound_location":
                    suggested_fix = re.split(r'\s+[&/]\s+', suggested_fix)[0].strip()

                issues_rows.append({
                    "venue_id": idx,
                    "venue_name": venue_name,
                    "issue_type": "Location",
                    "severity": issue["severity"],
                    "field": "location",
                    "current_value": venue.get("location", ""),
                    "suggested_fix": suggested_fix,
                    "notes": issue["detail"]
                })

        # Add other issues
        if mood_count_issue:
            issues_rows.append({
                "venue_id": idx,
                "venue_name": venue_name,
                "issue_type": "Moods",
                "severity": mood_count_issue["severity"],
                "field": "moods",
                "current_value": str(venue.get("moods", [])),
                "suggested_fix": "Add or remove moods to reach 2-4 total",
                "notes": mood_count_issue["detail"]
            })

        if mood_validity_issue:
            issues_rows.append({
                "venue_id": idx,
                "venue_name": venue_name,
                "issue_type": "Moods",
                "severity": mood_validity_issue["severity"],
                "field": "moods",
                "current_value": str(venue.get("moods", [])),
                "suggested_fix": "Review against approved mood list",
                "notes": mood_validity_issue["detail"]
            })

        if genre_count_issue:
            issues_rows.append({
                "venue_id": idx,
                "venue_name": venue_name,
                "issue_type": "Genres",
                "severity": genre_count_issue["severity"],
                "field": "genres",
                "current_value": str(venue.get("genres", [])),
                "suggested_fix": "Adjust to 3-5 genres",
                "notes": genre_count_issue["detail"]
            })

        if blurb_length_issue:
            issues_rows.append({
                "venue_id": idx,
                "venue_name": venue_name,
                "issue_type": "Blurb",
                "severity": blurb_length_issue["severity"],
                "field": "blurb",
                "current_value": venue.get("blurb", "")[:50] + "...",
                "suggested_fix": "Expand or condense to 50-120 words",
                "notes": blurb_length_issue["detail"]
            })

        if blurb_quality_issue:
            issues_rows.append({
                "venue_id": idx,
                "venue_name": venue_name,
                "issue_type": "Blurb",
                "severity": blurb_quality_issue["severity"],
                "field": "blurb",
                "current_value": venue.get("blurb", "")[:50] + "...",
                "suggested_fix": "Rewrite without placeholder language",
                "notes": blurb_quality_issue["detail"]
            })

        if url_issue:
            issues_rows.append({
                "venue_id": idx,
                "venue_name": venue_name,
                "issue_type": "URL",
                "severity": url_issue["severity"],
                "field": "url",
                "current_value": venue.get("url", ""),
                "suggested_fix": f"https://{venue.get('url', '')}" if venue.get("url") else "Add URL",
                "notes": url_issue["detail"]
            })

        if required_fields_issue:
            issues_rows.append({
                "venue_id": idx,
                "venue_name": venue_name,
                "issue_type": "Required Fields",
                "severity": required_fields_issue["severity"],
                "field": "multiple",
                "current_value": "N/A",
                "suggested_fix": "Add missing required fields",
                "notes": required_fields_issue["detail"]
            })

        if staleness_issue:
            issues_rows.append({
                "venue_id": idx,
                "venue_name": venue_name,
                "issue_type": "Verification",
                "severity": staleness_issue["severity"],
                "field": "last_verified",
                "current_value": venue.get("last_verified", ""),
                "suggested_fix": f"{datetime.now().strftime('%Y-%m-%d')}",
                "notes": staleness_issue["detail"]
            })

    # Sort by severity, then venue_id
    severity_order = {"CRITICAL": 0, "IMPORTANT": 1, "MINOR": 2}
    issues_rows.sort(key=lambda x: (severity_order[x["severity"]], x["venue_id"]))

    return issues_rows

# ============================================================================
# PATTERN ANALYSIS
# ============================================================================

def generate_pattern_analysis(venues, all_issues, mood_census):
    """Generate human-readable pattern analysis."""
    analysis = []

    analysis.append("# 🕊️ Lark Database Audit - Pattern Analysis")
    analysis.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    analysis.append("---\n")

    # Overview
    analysis.append("## Overview")
    analysis.append(f"\nAudited **{len(venues)} venues** against standards in VENUE_DATA_STANDARDS.md")
    analysis.append(f"Found **{len(all_issues)} total issues** across **{len(set(i['venue_id'] for i in all_issues))} venues**\n")

    # Location patterns
    analysis.append("## Location Patterns\n")
    location_issues = [i for i in all_issues if "location" in i["issue"]["type"]]
    if location_issues:
        analysis.append(f"**{len(location_issues)} venues** have location formatting issues:\n")

        compound = [i for i in location_issues if "compound" in i["issue"]["type"]]
        borough = [i for i in location_issues if "borough" in i["issue"]["type"]]
        not_approved = [i for i in location_issues if "not_in_approved" in i["issue"]["type"]]

        if compound:
            analysis.append(f"- **{len(compound)} compound locations** (using & or /) - likely need to pick primary neighborhood")
        if borough:
            analysis.append(f"- **{len(borough)} borough format** (e.g., 'Acton, West London') - should be just neighborhood")
        if not_approved:
            analysis.append(f"- **{len(not_approved)} not in approved list** - may need to map to standard neighborhood or add to approved list")

        analysis.append("\n**Most common pattern:** Venues use 'Neighborhood, Borough' format instead of just 'Neighborhood'\n")

    # Mood patterns
    analysis.append("## Mood Tag Patterns\n")
    analysis.append(f"**{mood_census['total_unique_moods']} unique mood tags** in use across all venues:\n")
    analysis.append(f"- **{mood_census['approved_moods_in_use']} approved moods** from mood_index.json")
    analysis.append(f"- **{mood_census['unapproved_moods_in_use']} unapproved moods** (not in current approved list)\n")

    analysis.append("**Important:** Many unapproved moods are expressive and poetic - not errors!\n")

    if mood_census['summary']['beautiful_unlisted']:
        analysis.append(f"**Beautiful unlisted tags** (strong candidates for approval):")
        for mood in mood_census['summary']['beautiful_unlisted'][:10]:
            analysis.append(f"- {mood}")
        analysis.append("")

    if mood_census['summary']['should_be_features']:
        analysis.append(f"**Tags that should be features** (not moods):")
        for mood in mood_census['summary']['should_be_features'][:10]:
            analysis.append(f"- {mood}")
        analysis.append("")

    # Genre patterns
    genre_issues = [i for i in all_issues if "genre" in i["issue"]["type"]]
    if genre_issues:
        analysis.append(f"## Genre Patterns\n")
        analysis.append(f"**{len(genre_issues)} venues** have genre count issues (not 3-5 genres)\n")

    # Blurb patterns
    blurb_issues = [i for i in all_issues if "blurb" in i["issue"]["type"]]
    if blurb_issues:
        analysis.append(f"## Blurb Quality Patterns\n")
        analysis.append(f"**{len(blurb_issues)} venues** have blurb issues:\n")

        too_short = [i for i in blurb_issues if "too_short" in i["issue"]["type"]]
        too_long = [i for i in blurb_issues if "too_long" in i["issue"]["type"]]
        placeholder = [i for i in blurb_issues if "placeholder" in i["issue"]["type"]]

        if too_short:
            analysis.append(f"- **{len(too_short)} too short** (<50 words)")
        if too_long:
            analysis.append(f"- **{len(too_long)} too long** (>120 words)")
        if placeholder:
            analysis.append(f"- **{len(placeholder)} contain placeholders** (generic language)")
        analysis.append("")

    # Temporal patterns
    stale = [i for i in all_issues if "stale" in i["issue"]["type"]]
    if stale:
        analysis.append(f"## Verification Freshness\n")
        analysis.append(f"**{len(stale)} venues** haven't been verified in >6 months")
        analysis.append("These should be spot-checked to ensure they're still active\n")

    # Geographic clustering
    analysis.append("## Geographic Distribution\n")
    location_counts = defaultdict(int)
    for venue in venues:
        location = venue.get("location", "Unknown")
        # Extract neighborhood
        neighborhood = re.split(r'[,\(]', location)[0].strip()
        location_counts[neighborhood] += 1

    top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    analysis.append("**Top 10 neighborhoods by venue count:**\n")
    for location, count in top_locations:
        analysis.append(f"- {location}: {count} venues")
    analysis.append("")

    # Severity breakdown
    analysis.append("## Issue Severity Breakdown\n")
    severity_counts = defaultdict(int)
    for issue in all_issues:
        severity_counts[issue["issue"]["severity"]] += 1

    for severity in ["CRITICAL", "IMPORTANT", "MINOR"]:
        count = severity_counts.get(severity, 0)
        analysis.append(f"**{severity}:** {count} issues")
    analysis.append("")

    # Recommendations
    analysis.append("## Recommendations for Batch Fixes\n")
    analysis.append("Based on patterns observed:\n")
    analysis.append("1. **Location standardization** - Many venues use 'Neighborhood, Borough' format. Create script to extract just neighborhood.")
    analysis.append("2. **Mood taxonomy review** - Review unapproved moods and decide which to add to mood_index.json")
    analysis.append("3. **Blurb expansion** - Venues with short blurbs need poetic enhancement in Lark's voice")
    analysis.append("4. **Verification refresh** - Spot-check stale venues (>6 months) to confirm they're still active")
    analysis.append("5. **Feature vs Mood** - Move feature-like tags (accessible, family-friendly) to proper feature fields\n")

    analysis.append("---")
    analysis.append("\n*Remember: Clean data is an act of care* 🕊️✨\n")

    return "\n".join(analysis)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("Starting Lark Database Audit...")
    print()

    # Load data
    print("Loading venues...")
    venues = load_venues()
    print(f"[OK] Loaded {len(venues)} venues")

    print("Loading approved moods...")
    approved_moods = load_approved_moods()
    print(f"[OK] Loaded {len(approved_moods)} approved moods")
    print()

    # Generate reports
    print("Analyzing mood tags...")
    mood_census = generate_mood_census(venues, approved_moods)
    with open(OUTPUT_DIR / "mood_census.json", "w", encoding="utf-8") as f:
        json.dump(mood_census, f, indent=2, ensure_ascii=False)
    print(f"[OK] Generated mood_census.json ({mood_census['total_unique_moods']} unique moods)")

    print("Analyzing location issues...")
    location_issues = generate_location_issues(venues)
    with open(OUTPUT_DIR / "location_issues.json", "w", encoding="utf-8") as f:
        json.dump(location_issues, f, indent=2, ensure_ascii=False)
    print(f"[OK] Generated location_issues.json ({location_issues['total_issues']} issues)")

    print("Running full validation...")
    validation_summary, all_issues = generate_validation_summary(venues, approved_moods)
    with open(OUTPUT_DIR / "validation_summary.json", "w", encoding="utf-8") as f:
        json.dump(validation_summary, f, indent=2, ensure_ascii=False)
    print(f"[OK] Generated validation_summary.json ({len(all_issues)} total issues)")

    print("Generating detailed issues table...")
    issues_table = generate_issues_table(venues, approved_moods)

    # CSV output
    with open(OUTPUT_DIR / "issues_table.csv", "w", encoding="utf-8", newline="") as f:
        if issues_table:
            writer = csv.DictWriter(f, fieldnames=issues_table[0].keys())
            writer.writeheader()
            writer.writerows(issues_table)
    print(f"[OK] Generated issues_table.csv ({len(issues_table)} rows)")

    # Markdown table output
    with open(OUTPUT_DIR / "issues_table.md", "w", encoding="utf-8") as f:
        f.write("# Lark Database - Detailed Issues Table\n\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")

        if issues_table:
            # Write header
            headers = list(issues_table[0].keys())
            f.write("| " + " | ".join(headers) + " |\n")
            f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")

            # Write rows
            for row in issues_table:
                values = [str(row[h]).replace("|", "\\|") for h in headers]
                f.write("| " + " | ".join(values) + " |\n")
    print(f"[OK] Generated issues_table.md")

    print("Generating pattern analysis...")
    pattern_analysis = generate_pattern_analysis(venues, all_issues, mood_census)
    with open(OUTPUT_DIR / "patterns.md", "w", encoding="utf-8") as f:
        f.write(pattern_analysis)
    print(f"[OK] Generated patterns.md")

    print()
    print("=" * 60)
    print("AUDIT COMPLETE")
    print("=" * 60)
    print()
    print("Generated 5 reports in outputs/ directory:")
    print("  1. mood_census.json - Mood tag usage analysis")
    print("  2. location_issues.json - Location formatting problems")
    print("  3. validation_summary.json - Overall validation stats")
    print("  4. issues_table.csv - Detailed issues (spreadsheet)")
    print("  5. issues_table.md - Detailed issues (markdown)")
    print("  6. patterns.md - Human-readable pattern analysis")
    print()
    print("Quick Stats:")
    print(f"  Total venues: {len(venues)}")
    print(f"  Venues with issues: {validation_summary['venues_with_issues']}")
    print(f"  Total issues found: {len(all_issues)}")
    print(f"  Unique moods in use: {mood_census['total_unique_moods']}")
    print(f"  Location formatting issues: {location_issues['total_issues']}")
    print()
    print("Next steps: Review patterns.md for insights and issues_table.csv for fixes")

if __name__ == "__main__":
    main()
