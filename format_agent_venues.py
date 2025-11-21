#!/usr/bin/env python3
"""
ChatGPT Agent Output to Lark JSON Converter

Converts ChatGPT agent venue research output into clean JSON
matching The London Lark's venue structure (lark_venues_clean.json).

Usage:
    python format_agent_venues.py agent_output.txt
    cat agent_output.txt | python format_agent_venues.py -

Output:
    - new_venues_formatted.json - New venues ready to merge
    - Console summary showing parsed/valid/duplicate counts
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


# Path to existing venues database
EXISTING_VENUES_PATH = Path(__file__).parent / "lark_venues_clean.json"
OUTPUT_PATH = Path(__file__).parent / "new_venues_formatted.json"


def load_existing_venues():
    """Load existing venues from lark_venues_clean.json."""
    if not EXISTING_VENUES_PATH.exists():
        print(f"Warning: {EXISTING_VENUES_PATH} not found. Skipping duplicate check.")
        return []

    try:
        with open(EXISTING_VENUES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse {EXISTING_VENUES_PATH}: {e}")
        return []


def parse_date(date_str):
    """
    Parse various date formats into YYYY-MM-DD.

    Handles:
    - "November 22, 2025"
    - "Nov 22, 2025"
    - "22 November 2025"
    - "2025-11-22"
    - "22/11/2025"
    """
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")

    date_str = date_str.strip()

    # Already in correct format
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return date_str

    # Month name formats
    month_map = {
        "january": "01", "jan": "01",
        "february": "02", "feb": "02",
        "march": "03", "mar": "03",
        "april": "04", "apr": "04",
        "may": "05",
        "june": "06", "jun": "06",
        "july": "07", "jul": "07",
        "august": "08", "aug": "08",
        "september": "09", "sep": "09", "sept": "09",
        "october": "10", "oct": "10",
        "november": "11", "nov": "11",
        "december": "12", "dec": "12",
    }

    # Try "Month DD, YYYY" or "Month DD YYYY"
    match = re.match(r"(\w+)\s+(\d{1,2}),?\s+(\d{4})", date_str, re.IGNORECASE)
    if match:
        month_str, day, year = match.groups()
        month = month_map.get(month_str.lower())
        if month:
            return f"{year}-{month}-{int(day):02d}"

    # Try "DD Month YYYY"
    match = re.match(r"(\d{1,2})\s+(\w+)\s+(\d{4})", date_str, re.IGNORECASE)
    if match:
        day, month_str, year = match.groups()
        month = month_map.get(month_str.lower())
        if month:
            return f"{year}-{month}-{int(day):02d}"

    # Try DD/MM/YYYY
    match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", date_str)
    if match:
        day, month, year = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"

    # Fallback to today's date
    return datetime.now().strftime("%Y-%m-%d")


def validate_url(url):
    """Check if URL is valid format."""
    if not url:
        return False
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


def parse_tags(tags_str):
    """
    Parse comma-separated tags into a list, lowercase and stripped.
    """
    if not tags_str:
        return []

    # Split by comma, strip whitespace, lowercase, remove empty
    tags = [tag.strip().lower() for tag in tags_str.split(",")]
    return [tag for tag in tags if tag]


def extract_verification_info(verification_str, description_str):
    """
    Extract useful info from verification field to add to notes.
    Returns (notes_text, verification_status).
    """
    if not verification_str:
        return "", "unknown"

    # Determine status
    if verification_str.startswith("Y"):
        status = "verified"
    elif verification_str.startswith("!"):
        status = "warning"
    elif verification_str.startswith("X"):
        status = "closed"
    else:
        status = "unknown"

    # Extract useful info (remove emoji prefix)
    notes = verification_str.lstrip("YX!").strip()

    return notes, status


def parse_venue_block(block):
    """
    Parse a single venue block into a dictionary.

    Expected format:
    **[Venue Name]**
    Address: [full address]
    Area: [neighbourhood]
    Borough: [borough name]
    Moods: [comma-separated]
    Genres: [comma-separated]
    Description: [text]
    Why it fits: [text]
    URL: [website]
    Price: [free/GBP/GBPGBP/GBPGBPGBP]
    Capacity: [tiny/small/medium or number]
    Verification: Y/!/X [evidence]
    Last checked: [date]
    """
    venue = {}
    errors = []

    lines = block.strip().split("\n")
    if not lines:
        return None, ["Empty block"]

    # Extract venue name from first line (handles **Name** format)
    name_line = lines[0].strip()
    name_match = re.match(r"\*\*(.+?)\*\*", name_line)
    if name_match:
        venue["name"] = name_match.group(1).strip()
    else:
        # Try without asterisks
        venue["name"] = name_line.strip()

    # Parse remaining lines as key: value pairs
    current_key = None
    current_value = []

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        # Check if this is a new field
        field_match = re.match(r"^(\w[\w\s]*?):\s*(.*)$", line)
        if field_match:
            # Save previous field if exists
            if current_key and current_value:
                venue[current_key.lower()] = " ".join(current_value).strip()

            current_key = field_match.group(1)
            current_value = [field_match.group(2)] if field_match.group(2) else []
        elif current_key:
            # Continuation of previous field
            current_value.append(line)

    # Save last field
    if current_key and current_value:
        venue[current_key.lower()] = " ".join(current_value).strip()

    return venue, errors


def transform_to_lark_format(raw_venue, last_checked_date):
    """
    Transform parsed raw venue data to Lark JSON format.

    Mapping:
    - "name" -> "name"
    - "area" -> "location"
    - "moods" -> "moods" (array)
    - "genres" -> "genres" (array)
    - "url" -> "url"
    - "description" + "verification" -> "notes"
    - "last checked" -> "last_verified" (YYYY-MM-DD)
    """
    transformed = {}
    errors = []

    # Required: name
    name = raw_venue.get("name", "").strip()
    if not name:
        errors.append("Missing venue name")
    else:
        transformed["name"] = name

    # Required: location (from "area")
    location = raw_venue.get("area", "").strip()
    if not location:
        errors.append("Missing location/area")
    else:
        transformed["location"] = location

    # Required: moods (array)
    moods_str = raw_venue.get("moods", "")
    moods = parse_tags(moods_str)
    if not moods:
        errors.append("No mood tags provided")
    else:
        transformed["moods"] = moods

    # Optional but useful: genres (array)
    genres_str = raw_venue.get("genres", "")
    genres = parse_tags(genres_str)
    if genres:
        transformed["genres"] = genres

    # Required: url
    url = raw_venue.get("url", "").strip()
    if not url:
        errors.append("Missing URL")
    elif not validate_url(url):
        errors.append(f"Invalid URL format: {url}")
    else:
        transformed["url"] = url

    # Optional: notes (combine description hints + verification info)
    notes_parts = []

    # Add shortened description if useful
    description = raw_venue.get("description", "").strip()
    # We don't add description to notes - that's for blurb which Catherine writes

    # Add verification info
    verification = raw_venue.get("verification", "").strip()
    if verification:
        # Extract date from "Last checked" field or use fallback
        last_checked = raw_venue.get("last checked", last_checked_date)
        parsed_date = parse_date(last_checked)

        # Clean up verification text
        verif_clean = verification.lstrip("\u2705\u26a0\ufe0f\u274c").strip()
        if verif_clean:
            notes_parts.append(f"Verified {parsed_date}: {verif_clean}")

    if notes_parts:
        transformed["notes"] = " | ".join(notes_parts)

    # Required: last_verified (from "last checked")
    last_checked = raw_venue.get("last checked", "")
    parsed_date = parse_date(last_checked)
    transformed["last_verified"] = parsed_date

    return transformed, errors


def split_venue_blocks(text):
    """
    Split input text into individual venue blocks.
    Each venue starts with **Venue Name** on its own line.
    """
    # Split on venue name pattern (** at start of line)
    pattern = r"(?=^\*\*[^*]+\*\*\s*$)"
    blocks = re.split(pattern, text, flags=re.MULTILINE)

    # Filter out empty blocks
    return [block.strip() for block in blocks if block.strip()]


def check_duplicate(venue_name, existing_venues):
    """
    Check if venue already exists (case-insensitive name match).
    Returns (is_duplicate, existing_venue_name).
    """
    if not venue_name:
        return False, None

    name_lower = venue_name.lower().strip()

    for existing in existing_venues:
        existing_name = existing.get("name", "").lower().strip()
        if name_lower == existing_name:
            return True, existing.get("name")

    return False, None


def format_summary(stats, duplicates, validation_errors):
    """Format the console summary output."""
    lines = [
        "",
        "Venue Formatting Report",
        "==========================",
        "",
        f"Parsed: {stats['parsed']} venues from agent output",
        f"Valid: {stats['valid']} venues passed validation",
        f"Duplicates: {stats['duplicates']} venues already in database",
    ]

    # List duplicates
    if duplicates:
        for dup in duplicates:
            lines.append(f"  - Skipped: {dup} (already exists)")

    lines.append("")

    # Validation errors
    if validation_errors:
        lines.append("Validation Issues:")
        for venue_name, errors in validation_errors.items():
            for error in errors:
                lines.append(f"  - \"{venue_name}\": {error}")
        lines.append("")

    # Final status
    if stats['valid'] > 0:
        lines.append(f"[OK] {stats['valid']} new venues written to: {OUTPUT_PATH.name}")
        lines.append("")
        lines.append("Ready to merge into lark_venues_clean.json")
    else:
        lines.append("[!] No new venues to write")

    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Convert ChatGPT agent venue output to Lark JSON format"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="-",
        help="Input file path (or - for stdin)"
    )
    parser.add_argument(
        "-o", "--output",
        default=str(OUTPUT_PATH),
        help=f"Output file path (default: {OUTPUT_PATH.name})"
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge new venues directly into lark_venues_clean.json"
    )
    parser.add_argument(
        "--skip-duplicates",
        action="store_true",
        default=True,
        help="Skip venues that already exist (default: True)"
    )
    parser.add_argument(
        "--no-skip-duplicates",
        action="store_false",
        dest="skip_duplicates",
        help="Include all venues even if duplicates exist"
    )

    args = parser.parse_args()

    # Read input
    if args.input_file == "-":
        text = sys.stdin.read()
    else:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: File not found: {args.input_file}")
            sys.exit(1)
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

    if not text.strip():
        print("Error: No input provided")
        sys.exit(1)

    # Load existing venues for duplicate check
    existing_venues = load_existing_venues()
    existing_names = {v.get("name", "").lower().strip() for v in existing_venues}

    # Parse venue blocks
    blocks = split_venue_blocks(text)

    # Stats tracking
    stats = {
        "parsed": 0,
        "valid": 0,
        "duplicates": 0,
        "errors": 0
    }
    duplicates_list = []
    validation_errors = {}
    new_venues = []

    today_date = datetime.now().strftime("%Y-%m-%d")

    for block in blocks:
        # Parse raw venue data
        raw_venue, parse_errors = parse_venue_block(block)

        if not raw_venue or not raw_venue.get("name"):
            stats["errors"] += 1
            continue

        stats["parsed"] += 1
        venue_name = raw_venue.get("name", "Unknown")

        # Check for duplicates
        if args.skip_duplicates:
            is_dup, existing_name = check_duplicate(venue_name, existing_venues)
            if is_dup:
                stats["duplicates"] += 1
                duplicates_list.append(existing_name or venue_name)
                continue

        # Transform to Lark format
        transformed, transform_errors = transform_to_lark_format(raw_venue, today_date)

        if transform_errors:
            validation_errors[venue_name] = transform_errors
            # Require: name, location, url, and moods (minimum viable)
            required_fields = ["name", "location", "url", "moods"]
            if not all(k in transformed for k in required_fields):
                stats["errors"] += 1
                continue

        new_venues.append(transformed)
        stats["valid"] += 1

    # Write output
    output_path = Path(args.output)

    if args.merge and new_venues:
        # Merge into existing file
        all_venues = existing_venues + new_venues
        with open(EXISTING_VENUES_PATH, "w", encoding="utf-8") as f:
            json.dump(all_venues, f, indent=2, ensure_ascii=False)
        print(f"[OK] Merged {len(new_venues)} venues into {EXISTING_VENUES_PATH.name}")
    elif new_venues:
        # Write to separate file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(new_venues, f, indent=2, ensure_ascii=False)

    # Print summary
    print(format_summary(stats, duplicates_list, validation_errors))

    # Return appropriate exit code
    if stats["valid"] > 0:
        sys.exit(0)
    elif stats["parsed"] > 0:
        sys.exit(1)  # Parsed but no valid venues
    else:
        sys.exit(2)  # Could not parse any venues


if __name__ == "__main__":
    main()
