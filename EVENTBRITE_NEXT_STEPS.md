# Eventbrite Integration - Status & Next Steps

## ✅ What's Complete

### 1. Filtering Configuration (`event_config.py`)

Complete filtering system ready to preserve the Lark's soul:

**Genre Whitelist (ONLY these):**
- Folk, jazz, acoustic, indie, experimental, ambient
- Fringe theatre, cabaret, drag, physical theatre, contemporary dance
- Poetry, spoken word, open mic
- Independent film, art galleries
- LGBTQ+ events, activist gatherings, spiritual rituals

**Strict Exclusions:**
- Corporate/business/networking events
- Fitness/wellness classes
- Sports events
- Mainstream venues (O2, Wembley, West End)
- Generic club nights
- Children's entertainment (unless arts-focused)
- Food festivals

**Venue Filtering:**
- Max capacity: 300 people
- Preferred keywords: fringe, independent, community, grassroots, pub theatre, gallery, converted warehouse
- Exclude: arenas, stadiums, chain hotels

**Price Tiers:**
- Prioritize: Under £20
- Flag: Over £30 as high-priced
- Always include: Free events

**Location Mapping:**
- London boroughs validated
- Neighborhoods mapped to regions (North/South/East/West + Central)

**Mood Inference:**
- 28 mood categories mapped to keywords
- Genre-to-mood mapping (e.g., "folk" → "Folk & Intimate")
- Description keyword detection (e.g., "candlelit" → intimate moods)

### 2. Eventbrite Setup Guide (`EVENTBRITE_GUIDE.md`)

Simple 5-minute guide:
- How to create Eventbrite app
- Get OAuth token
- Set token in code
- Test setup

### 3. Event Pipeline Infrastructure (from previous session)

Already working:
- `event_fetcher.py` - Base structure (currently uses mock data)
- `event_matcher.py` - Event filtering by mood/location/time/budget
- `events_cache.json` - Event storage
- Mock data generator

## ⏳ What's Next

### Step 1: Implement Filtered Eventbrite Fetching

Update `event_fetcher.py` to:

1. **Fetch from Eventbrite API**
   - Use categories whitelist
   - Apply date range (next 14 days)
   - London geo-filter

2. **Apply Strict Filtering**
   - Check genre keywords (include vs exclude)
   - Validate venue (capacity, keywords)
   - Price tier classification
   - Location mapping

3. **Infer Mood Tags**
   - Match keywords from event name/description
   - Check genre mappings
   - Assign confidence score
   - Flag uncertain matches for review

4. **Track Statistics**
   - Total events fetched
   - Total after filtering
   - Filter rejection reasons
   - Success rate by category

5. **Generate Review Sample**
   - Save `eventbrite_sample.json` (50-100 events)
   - Include mood confidence scores
   - Mark events for manual review

### Step 2: Testing & Refinement

1. Get Eventbrite token (5 mins)
2. Run fetcher with `--real` flag
3. Review `eventbrite_sample.json`
4. Adjust filters in `event_config.py` if needed
5. Refine mood inference rules

### Step 3: Integration

1. Integrate into `app.py` web UI
2. Show "Real events happening tonight"
3. Combine curated venues + live events
4. Set up daily refresh cron job

## 🎯 Expected Outcome

After implementing Step 1:

**Input:** Eventbrite API (thousands of London events)
**Output:** 50-200 culturally aligned events

**Quality:**
- All align with Lark's curatorial vision
- Mood tags inferred (with confidence scores)
- Price/location/time data accurate
- Ready to display in web UI

**Sample event:**
```json
{
  "event_name": "An Evening of English Folk Songs",
  "venue_name": "Cecil Sharp House",
  "date": "2025-11-20",
  "time": "19:30",
  "area": "Camden",
  "mood_tags": ["Folk & Intimate"],
  "mood_confidence": 0.95,
  "price_range": "££",
  "genre_tags": ["folk", "acoustic"],
  "url": "https://...",
  "filtered_reason": null
}
```

## 📋 Implementation Checklist

For the next ClaudeCode session:

- [ ] Import event_config.py into event_fetcher.py
- [ ] Add Eventbrite API fetching with categories filter
- [ ] Implement genre keyword filtering (include/exclude)
- [ ] Add venue filtering (capacity, keywords, exclusions)
- [ ] Implement price classification
- [ ] Add location mapping to Lark's area taxonomy
- [ ] Build mood inference system
- [ ] Track filtering statistics
- [ ] Generate eventbrite_sample.json for review
- [ ] Create EVENTBRITE_FILTERING_REPORT.md
- [ ] Test with real API token

## 🚀 Ready to Launch

**Configuration:** ✅ Complete and comprehensive
**Infrastructure:** ✅ Event pipeline exists
**Documentation:** ✅ Setup guide ready
**Next:** Implement the filtering logic in event_fetcher.py

This can be done in a single focused session (1-2 hours) since all the filtering rules are already defined.

## 📝 Notes for Next Session

**Key files to modify:**
- `event_fetcher.py` - Add filtering logic

**Key files to create:**
- `eventbrite_sample.json` - Sample filtered events
- `EVENTBRITE_FILTERING_REPORT.md` - Statistics and analysis

**Testing command:**
```bash
# With Eventbrite token set
python event_fetcher.py --real --sample

# Review results
cat eventbrite_sample.json
cat EVENTBRITE_FILTERING_REPORT.md
```

**Success criteria:**
- 50-200 events pass filters
- 90%+ feel aligned with Lark's vision
- Mood inference working (confidence scores included)
- Ready to integrate into web UI

---

The foundation is solid. The filters are strict. The Lark's soul is protected.
Time to fetch real events. ✨
