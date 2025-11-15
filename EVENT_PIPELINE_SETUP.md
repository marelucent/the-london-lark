# Event Data Pipeline - Setup & Usage

## Overview

The London Lark can now fetch and display live event listings from various London sources, making "happening tonight" a reality instead of aspirational.

**Current Status:**
- ✅ Infrastructure built and tested
- ✅ Mock data generator working
- ⏳ Real API integration ready (requires API keys)

## Quick Start (Mock Data)

The system works out of the box with realistic mock data:

```bash
# 1. Generate mock events
python event_fetcher.py

# 2. Test event matching
python event_matcher.py

# 3. Check the cache
cat events_cache.json
```

## Real Data Sources

### Eventbrite API (Recommended)

**Setup:**
1. Create account at https://www.eventbrite.com
2. Get OAuth token from https://www.eventbrite.com/platform/api#/introduction/authentication
3. Set in `event_fetcher.py`:
   ```python
   EVENTBRITE_TOKEN = "your_token_here"
   ```

**Coverage:** Wide range (music, theatre, talks, art events)
**Rate Limit:** 1000 requests/hour
**Cost:** Free

### Skiddle API

**Setup:**
1. Register at https://www.skiddle.com/api/
2. Get API key
3. Set in `event_fetcher.py`:
   ```python
   SKIDDLE_API_KEY = "your_key_here"
   ```

**Coverage:** Live music, club nights, festivals
**Cost:** Free (with registration)

### Future Sources (Requires Scraping)

- **Resident Advisor:** Electronic music, club culture
- **Dice:** Underground gigs, club nights
- **Time Out London:** Broad cultural events

These require web scraping (not yet implemented).

## Event Data Structure

Events are stored in `events_cache.json` with this schema:

```json
{
  "event_id": "unique_id",
  "source": "eventbrite",
  "event_name": "An Evening of Folk Music",
  "venue_name": "Green Note",
  "matched_venue_id": null,
  "date": "2025-11-20",
  "time": "20:00",
  "area": "Camden",
  "genre_tags": ["folk", "live music", "acoustic"],
  "mood_tags": ["Folk & Intimate"],
  "price_range": "££",
  "price_min": 12,
  "price_max": 15,
  "url": "https://...",
  "description": "Brief description...",
  "fetched_at": "2025-11-15T10:30:00Z"
}
```

## Using the Event Matcher

The `event_matcher.py` module works like `venue_matcher.py` but for time-specific events:

```python
from event_matcher import match_events

filters = {
    'mood': 'Folk & Intimate',
    'location': 'Camden',
    'time': 'tonight',
    'budget': 'low',
    'group': 'solo'
}

events = match_events(filters)
```

**Supported filters:**
- `mood`: Any mood from mood_index.json
- `location`: Area or region (e.g., "Camden", "North London")
- `time`: "tonight", "tomorrow", "this weekend", "Friday", etc.
- `budget`: "low" (free/cheap) or "high" (splurge)
- `group`: "solo" or "group"

## Refreshing Event Data

**Manual refresh:**
```bash
python event_fetcher.py
```

**Automated (cron example):**
```bash
# Run daily at 6am
0 6 * * * cd /path/to/the-london-lark && python event_fetcher.py
```

**Cache behavior:**
- Events older than today are automatically filtered out
- Fetched data includes `fetched_at` timestamp
- Recommended refresh: Daily or every 2-3 days

## Integration with Lark Web UI

The event pipeline is ready to integrate with `app.py`. To enable:

1. **Parallel querying:** Query both venues AND events
2. **Mixed results:** Return curated venues + live events
3. **Preference logic:** Events take priority if date filter is used

**Example integration in app.py:**
```python
from event_matcher import match_events

# In /ask route:
venue_matches = match_venues(filters)
event_matches = match_events(filters)

# Combine or choose based on context
if filters.get('time'):
    # User wants time-specific results, prioritize events
    responses = event_matches + venue_matches
else:
    # General query, show curated venues
    responses = venue_matches
```

## Testing Queries

**Command line:**
```bash
python event_matcher.py
```

**Test cases:**
- "folk music tonight" → Should return tonight's folk events
- "queer events in East London" → Should filter by mood + location
- "something experimental this weekend" → Should filter by time
- "free events" → Should show budget='low' events

## Current Coverage (Mock Data)

The mock data generator creates 5 realistic events:

1. **Folk songs** (Camden, ££, Folk & Intimate)
2. **Late night jazz** (Camden, ££, Melancholic Beauty)
3. **Queer cabaret** (Haggerston, £, Queer Revelry)
4. **Experimental theatre** (Camden, ££, Curious Encounters)
5. **Open mic** (Tooting, Free, Folk & Intimate)

**With real API:** Expect 50-200 events for next 14 days.

## Mood Tag Inference

Events from external sources may not have mood tags. The matcher includes basic genre-to-mood mapping:

- `folk`, `acoustic` → Folk & Intimate
- `queer`, `drag`, `cabaret` → Queer Revelry, Cabaret & Glitter
- `comedy`, `standup` → Comic Relief
- `theatre`, `drama` → The Thoughtful Stage
- `jazz`, `classical` → Melancholic Beauty
- `experimental`, `weird` → Playful & Weird

**Manual curation:** Edit `mood_tags` in `events_cache.json` for better accuracy.

## Error Handling

**API failures:** Falls back to mock data
**No events found:** Returns empty list (web UI shows curated venues)
**Rate limiting:** Catches and logs errors
**Network issues:** Timeout after 10 seconds

## Files Created

- `event_fetcher.py` - Fetches events from APIs
- `event_matcher.py` - Matches events to filters
- `events_cache.json` - Cached event data
- `EVENT_SOURCES_RESEARCH.md` - Source evaluation
- `EVENT_PIPELINE_SETUP.md` - This file

## Limitations & Future Work

**Current limitations:**
- Mock data only (until API keys added)
- No Dice/RA/Time Out scraping yet
- Basic mood inference (manual curation recommended)
- Events only (no automatic venue matching)

**Future enhancements:**
- Web scraping for Dice, Resident Advisor
- Automatic venue matching (link events to curated venues)
- Smarter mood inference using NLP
- User feedback loop (upvote/downvote recommendations)
- Event database (instead of JSON cache)

## Troubleshooting

**"No events cache found"**
→ Run `python event_fetcher.py` first

**"API error: 401"**
→ Check your API token/key is set correctly

**"No events match filters"**
→ Try broader filters (remove location/time constraints)

**Past events showing up**
→ Events are auto-filtered by date, check system clock

## Success Metrics

**Phase 1 (Current):**
- ✅ Infrastructure working
- ✅ Mock data generating
- ✅ Event matching functional
- ✅ Ready for API integration

**Phase 2 (Real Data):**
- Get Eventbrite token
- Fetch 50-200 real events
- Test with real queries
- Integrate with web UI

**Phase 3 (Enhancement):**
- Add web scraping
- Improve mood inference
- Automatic venue matching
- User feedback

## Next Steps

1. **Get API keys** (Eventbrite recommended)
2. **Test with real data**
3. **Integrate with app.py** (parallel querying)
4. **Update web UI** to show "Real events happening tonight"
5. **Set up automated refresh** (daily cron job)

---

The infrastructure is ready. The Lark can now speak truth when she says "happening tonight." ✨
