#!/usr/bin/env python3
# 🕊️ Venue Data Parser
"""
Loads the structured venue data from lark_venues_clean.json.
Applies exclusion filtering and deduplication.

Note: SQLite database loading is disabled until the database
is updated to include arcana fields. Always uses JSON for now.
"""

import sqlite3
import json
from pathlib import Path

# Venues to exclude (user-specified, not matching Lark curation standards)
EXCLUDED_VENUES = [
    "Streatham Space Project",
    "The Château",
    "Château",
]

# Data sources
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "lark.db"
JSON_PATH = PROJECT_ROOT / "lark_venues_clean.json"


def _filter_and_dedupe(venues):
    """Apply exclusion list and deduplicate by venue name."""
    filtered = []
    seen_names = set()

    for venue in venues:
        venue_name = venue.get("name", "")

        # Check exclusion list
        is_excluded = any(
            excluded.lower() in venue_name.lower()
            for excluded in EXCLUDED_VENUES
        )
        if is_excluded:
            continue

        # Check for duplicates
        if venue_name in seen_names:
            continue
        seen_names.add(venue_name)

        filtered.append(venue)

    return filtered


def _normalize_venue_record(raw):
    """Normalize raw venue dict to the expected schema."""
    return {
        "name": raw.get("name", ""),
        "location": raw.get("location", ""),
        "moods": raw.get("moods", []) or raw.get("mood_tags", []),
        "genres": raw.get("genres", []),
        "url": raw.get("url", ""),
        "blurb": raw.get("blurb", ""),
        "last_verified": raw.get("last_verified", ""),
        # New fields for the arcana card system
        "arcana": raw.get("arcana", None),
        "whisper": raw.get("whisper", ""),
    }


def _load_from_database():
    """Load venues from the SQLite database if available."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cur = conn.cursor()

    query = """
    SELECT
        v.id,
        v.name,
        v.location,
        v.url,
        v.blurb,
        v.last_verified,
        GROUP_CONCAT(DISTINCT m.name) as moods,
        GROUP_CONCAT(DISTINCT g.name) as genres
    FROM venues v
    LEFT JOIN venue_moods vm ON v.id = vm.venue_id
    LEFT JOIN moods m ON vm.mood_id = m.id
    LEFT JOIN venue_genres vg ON v.id = vg.venue_id
    LEFT JOIN genres g ON vg.genre_id = g.id
    GROUP BY v.id
    ORDER BY v.name
    """

    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    venues = []
    for row in rows:
        # Parse moods and genres (stored as comma-separated strings)
        moods = row["moods"].split(",") if row["moods"] else []
        genres = row["genres"].split(",") if row["genres"] else []

        venue = {
            "name": row["name"],
            "location": row["location"] or "",
            "moods": moods,
            "genres": genres,
            "url": row["url"] or "",
            "blurb": row["blurb"] or "",
            "last_verified": row["last_verified"] or "",
            # Database doesn't have arcana yet - would need migration
            "arcana": None,
            "whisper": "",
        }

        venues.append(venue)

    return _filter_and_dedupe(venues)


def _load_from_json():
    """Load venues from the JSON export."""
    if not JSON_PATH.exists():
        raise FileNotFoundError(
            f"No venue data source found. Expected {JSON_PATH.name} in the project folder."
        )

    with JSON_PATH.open("r", encoding="utf-8") as f:
        raw_venues = json.load(f)

    normalized = [_normalize_venue_record(v) for v in raw_venues]
    return _filter_and_dedupe(normalized)


def load_parsed_venues():
    """
    Load structured venues from the JSON file.

    Applies:
    - Exclusion filtering (removes specific venues)
    - Deduplication (removes duplicate venue entries by name)

    Returns venues in format compatible with existing app:
    {
        "name": str,
        "location": str,
        "moods": [str],
        "genres": [str],
        "url": str,
        "blurb": str,
        "last_verified": str,
        "arcana": str or None,
        "whisper": str
    }
    
    Note: Always uses JSON file now (not SQLite) because the database
    predates the arcana system and doesn't have those fields.
    """
    # Always use JSON - it has the arcana and whisper fields
    # The SQLite database is stale and missing the new fields
    return _load_from_json()


if __name__ == "__main__":
    try:
        venues = load_parsed_venues()
        print(f"✅ Loaded {len(venues)} venues from JSON (after filtering and deduplication)")
        
        if venues:
            print("\nFirst venue:")
            print(json.dumps(venues[0], indent=2, ensure_ascii=False))

            print("\n\nAll unique mood tags:")
            all_moods = set()
            for v in venues:
                all_moods.update(v.get('moods', []))
            for mood in sorted(all_moods):
                print(f"  - {mood}")

            print("\n\nAll unique genres:")
            all_genres = set()
            for v in venues:
                all_genres.update(v.get('genres', []))
            for genre in sorted(all_genres):
                print(f"  - {genre}")

            # Check arcana coverage
            print("\n\nArcana coverage:")
            arcana_counts = {}
            missing_arcana = []
            for v in venues:
                arcana = v.get('arcana')
                if arcana:
                    arcana_counts[arcana] = arcana_counts.get(arcana, 0) + 1
                else:
                    missing_arcana.append(v.get('name'))
            
            for arcana in sorted(arcana_counts.keys()):
                print(f"  {arcana}: {arcana_counts[arcana]} venues")
            
            if missing_arcana:
                print(f"\n  ⚠️ {len(missing_arcana)} venues missing arcana")

        # Verify exclusions
        print("\n\nVerifying exclusions:")
        for excluded in EXCLUDED_VENUES:
            found = any(excluded.lower() in v.get('name', '').lower() for v in venues)
            status = "❌ STILL PRESENT" if found else "✅ Excluded"
            print(f"  {excluded}: {status}")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
