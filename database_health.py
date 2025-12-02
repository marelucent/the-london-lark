"""Database health checks for the London Lark SQLite catalogue.

The checks are designed to be lightweight so they can run in CI or a cron job.
They verify that the required tables exist, basic counts are non-zero, and
relationship tables do not contain orphaned references. The module can be
imported for programmatic use or executed directly as a CLI.
"""

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "lark.db"

REQUIRED_TABLES = {
    "venues",
    "moods",
    "genres",
    "venue_moods",
    "venue_genres",
}


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


def _record(results: List[CheckResult], name: str, passed: bool, detail: str) -> None:
    results.append(CheckResult(name=name, passed=passed, detail=detail))


def _table_names(cur: sqlite3.Cursor) -> set[str]:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return {row[0] for row in cur.fetchall()}


def run_checks(db_path: Path | str = DB_PATH) -> List[CheckResult]:
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found at {db_path}. Provide --db to point at your lark.db file."
        )

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    results: List[CheckResult] = []

    existing_tables = _table_names(cur)
    missing_tables = REQUIRED_TABLES - existing_tables
    _record(
        results,
        "required_tables_present",
        not missing_tables,
        "Missing: " + ", ".join(sorted(missing_tables)) if missing_tables else "All present",
    )

    # Bail out early if schema is incomplete to avoid noisy downstream failures.
    if missing_tables:
        conn.close()
        return results

    venue_count = cur.execute("SELECT COUNT(*) FROM venues").fetchone()[0]
    _record(results, "venues_present", venue_count > 0, f"{venue_count} venues found")

    mood_count = cur.execute("SELECT COUNT(*) FROM moods").fetchone()[0]
    _record(results, "moods_present", mood_count > 0, f"{mood_count} moods found")

    genre_count = cur.execute("SELECT COUNT(*) FROM genres").fetchone()[0]
    _record(results, "genres_present", genre_count > 0, f"{genre_count} genres found")

    missing_locations = cur.execute(
        "SELECT COUNT(*) FROM venues WHERE location IS NULL OR TRIM(location) = ''"
    ).fetchone()[0]
    _record(
        results,
        "venue_locations_populated",
        missing_locations == 0,
        f"{missing_locations} venues missing a location",
    )

    missing_urls = cur.execute(
        "SELECT COUNT(*) FROM venues WHERE url IS NULL OR TRIM(url) = ''"
    ).fetchone()[0]
    _record(
        results,
        "venue_urls_populated",
        missing_urls == 0,
        f"{missing_urls} venues missing a URL",
    )

    orphaned_venue_links = cur.execute(
        """
        SELECT COUNT(*)
        FROM venue_moods vm
        LEFT JOIN venues v ON vm.venue_id = v.id
        WHERE v.id IS NULL
        """
    ).fetchone()[0]
    _record(
        results,
        "venue_mood_links_valid",
        orphaned_venue_links == 0,
        f"{orphaned_venue_links} orphaned venue->mood links",
    )

    orphaned_mood_links = cur.execute(
        """
        SELECT COUNT(*)
        FROM venue_moods vm
        LEFT JOIN moods m ON vm.mood_id = m.id
        WHERE m.id IS NULL
        """
    ).fetchone()[0]
    _record(
        results,
        "mood_links_valid",
        orphaned_mood_links == 0,
        f"{orphaned_mood_links} orphaned mood references",
    )

    orphaned_genre_venue_links = cur.execute(
        """
        SELECT COUNT(*)
        FROM venue_genres vg
        LEFT JOIN venues v ON vg.venue_id = v.id
        WHERE v.id IS NULL
        """
    ).fetchone()[0]
    _record(
        results,
        "venue_genre_links_valid",
        orphaned_genre_venue_links == 0,
        f"{orphaned_genre_venue_links} orphaned venue->genre links",
    )

    orphaned_genre_links = cur.execute(
        """
        SELECT COUNT(*)
        FROM venue_genres vg
        LEFT JOIN genres g ON vg.genre_id = g.id
        WHERE g.id IS NULL
        """
    ).fetchone()[0]
    _record(
        results,
        "genre_links_valid",
        orphaned_genre_links == 0,
        f"{orphaned_genre_links} orphaned genre references",
    )

    verified = cur.execute(
        "SELECT COUNT(*) FROM venues WHERE last_verified IS NOT NULL AND TRIM(last_verified) <> ''"
    ).fetchone()[0]
    coverage = (verified / venue_count) * 100 if venue_count else 0
    _record(
        results,
        "venue_verification_tracked",
        verified > 0,
        f"{verified}/{venue_count} venues have a verification timestamp ({coverage:.1f}% coverage)",
    )

    conn.close()
    return results


def summarize(results: Iterable[CheckResult]) -> str:
    lines = []
    for check in results:
        status = "✅" if check.passed else "❌"
        lines.append(f"{status} {check.name}: {check.detail}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SQLite health checks for the London Lark database")
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help="Path to lark.db (defaults to ./lark.db)",
    )
    args = parser.parse_args()

    try:
        results = run_checks(args.db)
    except FileNotFoundError as exc:
        print(f"❌ {exc}")
        return 1

    report = summarize(results)
    print(report)

    if all(check.passed for check in results):
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
