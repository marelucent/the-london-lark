
import json
import sqlite3

# Load JSON data
with open("lark_venues_merged_217.json", "r", encoding="utf-8") as f:
    venues_data = json.load(f)

# Connect to SQLite database
conn = sqlite3.connect("lark.db")
cur = conn.cursor()

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
conn.close()

print("Data imported successfully into lark.db")
