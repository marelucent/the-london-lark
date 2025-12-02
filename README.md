# 🕊️ The London Lark

A poetic, personalised cultural companion for London life.

The Lark helps users discover soulful, character-rich events — from fringe theatre to folk gigs, queer cabaret to poetic talks — using mood-matching rather than algorithms.

It interprets natural language prompts like:

- "Take me somewhere candlelit and strange this Friday"
- "Any feminist gigs in Camden tomorrow night?"
- "Surprise me with something I wouldn’t normally pick"

…and returns 1–3 lyrical event suggestions drawn from London’s rich cultural undercurrent.

## 🔍 Metadata / health endpoints

Before wiring up the front end you can quickly check the catalogue state via JSON:

- `GET /api/venues` – full venue list plus a `summary` block
- `GET /api/venues/summary` – just the summary for lightweight monitoring

The summary answers three questions:

1. Which data source is active (`sqlite` vs `json` fallback)?
2. Which mood/genre tags are available for filters and UI labels? (see `summary.tags`)
3. How many venues have a `last_verified` timestamp? (see `summary.verification`)

Example (truncated):

```json
{
  "data_source": "sqlite",
  "counts": {"venues": 300, "moods": 52, "genres": 18},
  "tags": {"moods": ["Tender", "Dreamy"], "genres": ["Folk", "Spoken Word"]},
  "verification": {
    "verified": 240,
    "missing": 60,
    "missing_names": ["Venue A", "Venue B"],
    "recently_verified": [{"name": "Royal Court", "last_verified": "2025-11-01"}]
  }
}
```

This keeps the monitoring payload small while still surfacing tag coverage and verification gaps.

### 🧪 Database health checks

If you're running the SQLite-backed catalogue (Render or local), you can smoke test the schema and links with:

```bash
python database_health.py --db /path/to/lark.db
```

The script confirms the required tables exist, counts moods/genres/venues, flags missing locations/URLs, and checks that mood/genre link tables have no orphaned IDs. It exits non-zero if any check fails so you can wire it into CI or a cron job.

## 🌿 Core Components

- `prompt_parser.py`: Extracts filters from user language (mood, date, location, etc.)
- `mood_index.json`: A living list of moods + synonyms
- `venue_profiles.md`: Poetic venue vibes, tagged with mood fits
- `poetic_templates.md`: Response templates per mood
- `prompt_tests.md`: Examples to simulate user–Lark interactions

## 🎯 MVP Goal

One natural-language prompt → three mood-matched, poetic cultural suggestions → joy.

---

🪶 Designed with care by Catherine + ChatGPT  
Inspired by handwritten letters, vintage field guides, and a city full of wonder.
