
import json
import sqlite3

# Load JSON data
with open("lark_venues_clean.json", "r", encoding="utf-8") as f:
    venues_data = json.load(f)

# Connect to SQLite database
conn = sqlite3.connect("lark.db")
cur = conn.cursor()

# Drop existing tables to ensure clean import
# This prevents duplicate/stale data from previous imports
cur.executescript("""
    DROP TABLE IF EXISTS venue_genres;
    DROP TABLE IF EXISTS venue_moods;
    DROP TABLE IF EXISTS genres;
    DROP TABLE IF EXISTS moods;
    DROP TABLE IF EXISTS venues;
""")

print("Cleared old database tables")

# Create fresh tables
cur.executescript("""
    CREATE TABLE venues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        url TEXT,
        blurb TEXT,
        last_verified TEXT
    );

    CREATE TABLE moods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE genres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE venue_moods (
        venue_id INTEGER,
        mood_id INTEGER,
        PRIMARY KEY (venue_id, mood_id),
        FOREIGN KEY (venue_id) REFERENCES venues(id),
        FOREIGN KEY (mood_id) REFERENCES moods(id)
    );

    CREATE TABLE venue_genres (
        venue_id INTEGER,
        genre_id INTEGER,
        PRIMARY KEY (venue_id, genre_id),
        FOREIGN KEY (venue_id) REFERENCES venues(id),
        FOREIGN KEY (genre_id) REFERENCES genres(id)
    );
""")

print("Created fresh database tables")

# Prepare helper functions
def get_or_create_id(table, name):
    cur.execute(f"SELECT id FROM {table} WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(f"INSERT INTO {table} (name) VALUES (?)", (name,))
    return cur.lastrowid

# Insert data
for entry in venues_data:
    name = entry.get("name", "").strip()
    location = entry.get("location", "").strip()
    url = entry.get("url", "").strip()
    blurb = entry.get("blurb", "").strip()
    last_verified = entry.get("last_verified", "").strip()

    # Insert into venues
    cur.execute(
        "INSERT INTO venues (name, location, url, blurb, last_verified) VALUES (?, ?, ?, ?, ?)",
        (name, location, url, blurb, last_verified),
    )
    venue_id = cur.lastrowid

    # Insert moods
    for mood in entry.get("moods", []):
        mood = mood.strip()
        mood_id = get_or_create_id("moods", mood)
        cur.execute("INSERT INTO venue_moods (venue_id, mood_id) VALUES (?, ?)", (venue_id, mood_id))

    # Insert genres
    for genre in entry.get("genres", []):
        genre = genre.strip()
        genre_id = get_or_create_id("genres", genre)
        cur.execute("INSERT INTO venue_genres (venue_id, genre_id) VALUES (?, ?)", (venue_id, genre_id))

# Commit and close
conn.commit()

# Verify the import
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM venues")
venue_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM moods")
mood_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM genres")
genre_count = cur.fetchone()[0]

conn.close()

print(f"Data imported successfully into lark.db")
print(f"  {venue_count} venues")
print(f"  {mood_count} unique moods")
print(f"  {genre_count} unique genres")
