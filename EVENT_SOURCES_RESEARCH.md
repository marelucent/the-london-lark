# Event Data Pipeline Research

## Investigated Sources

### 1. Eventbrite
- **API Status:** Free public API available
- **Authentication:** OAuth token required (can use personal token)
- **Coverage:** Wide range of events (music, theatre, art, talks)
- **London Filter:** Yes (by location coordinates or area)
- **Rate Limits:** 1000 requests/hour (generous)
- **Event Data Quality:** Good (name, date, time, price, venue, category)
- **Implementation Difficulty:** Easy ⭐⭐⭐⭐⭐
- **Decision:** ✅ IMPLEMENT

### 2. Dice
- **API Status:** No public API
- **Scraping:** Possible but requires headless browser (JavaScript-heavy site)
- **Coverage:** Excellent for underground gigs, club nights, electronic music
- **Implementation Difficulty:** Medium ⭐⭐⭐
- **Decision:** ⚠️ Consider for Phase 2 (scraping required)

### 3. Resident Advisor
- **API Status:** No public API
- **Scraping:** Possible via RSS feeds or HTML parsing
- **Coverage:** Excellent for electronic music, club culture
- **Implementation Difficulty:** Medium ⭐⭐⭐
- **Decision:** ⚠️ Consider for Phase 2

### 4. Songkick
- **API Status:** API exists but registration closed to new developers
- **Decision:** ❌ SKIP

### 5. Time Out London
- **API Status:** No public API
- **Scraping:** Possible via HTML parsing
- **Coverage:** Broad cultural events
- **Implementation Difficulty:** Medium ⭐⭐⭐
- **Decision:** ⚠️ Consider for Phase 2

### 6. Skiddle
- **API Status:** Free API available
- **Coverage:** Music events, club nights, festivals
- **London Filter:** Yes
- **Implementation Difficulty:** Easy ⭐⭐⭐⭐
- **Decision:** ✅ IMPLEMENT

### 7. Ents24
- **API Status:** API available (requires registration)
- **Coverage:** Wide range of live events
- **Decision:** ⚠️ Backup option

## Implementation Plan

### Phase 1 (NOW - Easy Wins)
1. **Eventbrite API** - Primary source
2. **Skiddle API** - Secondary source
3. **Simple web scraping** for 1-2 targeted venues

### Phase 2 (Later - More Complex)
- Resident Advisor scraping
- Dice scraping
- Time Out scraping

## Data Structure Design

```json
{
  "event_id": "unique_id",
  "source": "eventbrite",
  "event_name": "An Evening of Folk Music",
  "venue_name": "Green Note",
  "matched_venue_id": "venue_12",  // If matches our curated venue
  "date": "2025-11-20",
  "time": "20:00",
  "area": "Camden",
  "genre_tags": ["folk", "live music", "acoustic"],
  "mood_tags": ["Folk & Intimate"],  // Can be null for manual curation
  "price_range": "££",
  "price_min": 12,
  "price_max": 15,
  "url": "https://...",
  "description": "Brief description...",
  "fetched_at": "2025-11-15T10:30:00Z"
}
```

## Next Steps

1. Get Eventbrite API credentials (or use demo mode)
2. Build eventbrite_fetcher.py
3. Build skiddle_fetcher.py (if API key available)
4. Create event normalizer
5. Build event_matcher.py
6. Implement caching
7. Test with real queries
