#!/usr/bin/env python3
# 🕊️ Venue Data Parser
"""
Loads the structured venue data from lark.db SQLite database.
Applies exclusion filtering and deduplication.
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

# Database path
DB_PATH = Path(__file__).parent / "lark.db"


def load_parsed_venues():
    """
    Load structured venues from lark.db SQLite database.

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
        "last_verified": str
    }
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. "
            "Please ensure lark.db is in the project folder."
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cur = conn.cursor()

    # Query to get all venues with their moods and genres
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

    # Convert to list of dicts with proper formatting
    venues = []
    seen_names = set()

    for row in rows:
        venue_name = row['name']

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

        # Parse moods and genres (stored as comma-separated strings)
        moods = row['moods'].split(',') if row['moods'] else []
        genres = row['genres'].split(',') if row['genres'] else []

        venue = {
            "name": venue_name,
            "location": row['location'] or "",
            "moods": moods,
            "genres": genres,
            "url": row['url'] or "",
            "blurb": row['blurb'] or "",
            "last_verified": row['last_verified'] or ""
        }

        venues.append(venue)

    return venues


if __name__ == "__main__":
    try:
        venues = load_parsed_venues()
        print(f"✅ Loaded {len(venues)} venues from database (after filtering and deduplication)")
        
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
