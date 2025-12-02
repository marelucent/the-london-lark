import sqlite3
import tempfile
import unittest
from pathlib import Path

from database_health import CheckResult, run_checks, summarize


class DatabaseHealthTests(unittest.TestCase):
    def build_temp_db(self, with_missing_table: bool = False, strip_locations: bool = False) -> Path:
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        conn = sqlite3.connect(temp_db.name)
        cur = conn.cursor()

        cur.execute("CREATE TABLE venues (id INTEGER PRIMARY KEY, name TEXT, location TEXT, url TEXT, blurb TEXT, last_verified TEXT)")
        cur.execute("CREATE TABLE moods (id INTEGER PRIMARY KEY, name TEXT)")
        cur.execute("CREATE TABLE genres (id INTEGER PRIMARY KEY, name TEXT)")

        if not with_missing_table:
            cur.execute("CREATE TABLE venue_moods (venue_id INTEGER, mood_id INTEGER)")
        # Always create genre links table so we can selectively omit the mood mapping only
        cur.execute("CREATE TABLE venue_genres (venue_id INTEGER, genre_id INTEGER)")

        cur.execute(
            "INSERT INTO venues (id, name, location, url, blurb, last_verified) VALUES (1, 'Test Venue', ?, 'https://example.com', 'A cosy spot', '2024-01-01')",
            ("" if strip_locations else "Camden",),
        )
        cur.execute("INSERT INTO moods (id, name) VALUES (1, 'Dreamy')")
        cur.execute("INSERT INTO genres (id, name) VALUES (1, 'Poetry')")

        if not with_missing_table:
            cur.execute("INSERT INTO venue_moods (venue_id, mood_id) VALUES (1, 1)")
        cur.execute("INSERT INTO venue_genres (venue_id, genre_id) VALUES (1, 1)")

        conn.commit()
        conn.close()
        temp_db.close()
        return Path(temp_db.name)

    def test_all_checks_pass_on_complete_db(self):
        db_path = self.build_temp_db()
        results = run_checks(db_path)

        self.assertTrue(all(check.passed for check in results))
        self.assertIn("required_tables_present", [check.name for check in results])

    def test_missing_tables_are_reported(self):
        db_path = self.build_temp_db(with_missing_table=True)
        results = run_checks(db_path)

        table_check = next(check for check in results if check.name == "required_tables_present")
        self.assertFalse(table_check.passed)

    def test_missing_locations_are_detected(self):
        db_path = self.build_temp_db(strip_locations=True)
        results = run_checks(db_path)

        location_check = next(check for check in results if check.name == "venue_locations_populated")
        self.assertFalse(location_check.passed)

    def test_summary_formatting(self):
        fake_results = [
            CheckResult(name="a", passed=True, detail="ok"),
            CheckResult(name="b", passed=False, detail="bad"),
        ]
        summary = summarize(fake_results)
        self.assertIn("✅ a: ok", summary)
        self.assertIn("❌ b: bad", summary)


if __name__ == "__main__":
    unittest.main()
