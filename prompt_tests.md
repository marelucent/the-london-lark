# 🧪 prompt_tests.md

Test prompts for The London Lark — covering a range of mood tones, filter clarity, and poetic response styles. 
Each test includes:
- The user's natural language input
- Extracted filters
- Expected response type
- Sample poetic beginning (optional)

---

## Test 001 – The Soft Ache
**Prompt:** “I want something beautiful but sad this weekend. Somewhere small, not loud.”  
**Extracted Filters:**
- Mood: Grief & Grace
- Time: Weekend (date-based resolution needed)
- Venue Type: Intimate
**Response Type:** MoodMirror  
**Opening Sample:** “I hear the hush in your voice, the ache for something soft...”

---

## Test 002 – High Energy Friday
**Prompt:** “Got mates visiting Friday — what’s loud, cheap, and fun?”  
**Extracted Filters:**
- Mood: Group Energy, Playful & Weird
- Time: Friday
- Budget: Affordable
**Response Type:** Matchmaker or Shortlist
**Opening Sample:** “Here are three little lanterns to light your way...”

---

## Test 003 – Surprise Me
**Prompt:** “Honestly I’ve no idea. Surprise me, petal.”  
**Extracted Filters:**
- Mood: Something I Wouldn’t Normally Pick
- User Consent: High
**Response Type:** Wildcard  
**Opening Sample:** “Alright, Lark off-script. No rules, just resonance.”

---

## Test 004 – Poetic + Practical
**Prompt:** “What’s on in East London tonight that feels a bit poetic?”  
**Extracted Filters:**
- Area: East London
- Mood: Poetic
- Time: Tonight
**Response Type:** Matchmaker
**Opening Sample:** “How about this, petal? A poetic night in East London awaits...”

---

## Test 005 – Frustrated Searcher
**Prompt:** “Nothing’s ever on when I’m free. Try again, Lark.”  
**Extracted Filters:**
- Frustration signal
- Possibly a repeat search with time filter previously set
**Response Type:** Gentle Refusal (or new shortlist)
**Opening Sample:** “The city’s quiet on that front tonight, petal...”

---

## Test 006 – Niche Genre Request
**Prompt:** “Any experimental theatre going on this weekend?”  
**Extracted Filters:**
- Genre: Experimental Theatre
- Time: Weekend
**Response Type:** Matchmaker or Shortlist
**Opening Sample:** “Here’s something strange and stirring just beneath the surface...”

---

## Test 007 – Quiet Solo Evening
**Prompt:** “Something low key for a Tuesday night? I’m going solo.”  
**Extracted Filters:**
- Time: Tuesday night
- Mood: Solo-friendly, Thoughtful Stage, Word & Voice
**Response Type:** MoodMirror or Matchmaker
**Opening Sample:** “A quiet seat, a gentle voice — I think this one’s for you...”

---

## Test 008 – Notting Hill Wanderer
**Prompt:** “I’m in Notting Hill this afternoon, anything nearby?”  
**Extracted Filters:**
- Location: Notting Hill
- Time: This afternoon
**Response Type:** Matchmaker (Location-priority)
**Opening Sample:** “Just around the corner, a little wonder awaits...”

---

## Test 009 – Edge Mood: Spiritual/Sacred
**Prompt:** "Looking for something sacred or spiritual in Central London"
**Extracted Filters:**
- Mood: Spiritual / Sacred / Mystical
- Location: Central London
**Response Type:** MoodMirror
**Expected Behavior:** Should match venues with spiritual/sacred tags
**Opening Sample:** "Where the veil thins and reverence rises..."

---

## Test 010 – Edge Mood: Witchy & Wild
**Prompt:** "Anything witchy or pagan happening this weekend?"
**Extracted Filters:**
- Mood: Witchy & Wild
- Time: Weekend
**Response Type:** MoodMirror
**Expected Behavior:** Should match venues with folk/witchy/pagan vibes
**Opening Sample:** "For when you want to howl at something..."

---

## Test 011 – Edge Mood: Romanticised London
**Prompt:** "Something atmospheric and Victorian, like old gaslight London"
**Extracted Filters:**
- Mood: Romanticised London
**Response Type:** MoodMirror
**Expected Behavior:** Should match historic venues with candlelit/atmospheric tags
**Opening Sample:** "London as you imagined it in books..."

---

## Test 012 – Fuzzy Match: Typo in "comedy"
**Prompt:** "anything comdy or funny in South London tonight?"
**Extracted Filters:**
- Mood: Comic Relief (fuzzy match: 91%)
- Location: South London
- Time: Tonight
**Response Type:** Matchmaker
**Expected Behavior:** "comdy" should fuzzy-match to "comedy" with confidence ~0.91
**Opening Sample:** "Something to make you laugh..."

---

## Test 013 – Fuzzy Match: Typo in "drag"
**Prompt:** "looking for dragg shows this weekend"
**Extracted Filters:**
- Mood: Cabaret & Glitter (fuzzy match: 89%)
- Time: Weekend
**Response Type:** Matchmaker
**Expected Behavior:** "dragg" should fuzzy-match to "drag" with confidence ~0.89
**Opening Sample:** "Something glittering..."

---

## Test 014 – Fuzzy Match: Variant "folky"
**Prompt:** "something folky and intimate in Camden"
**Extracted Filters:**
- Mood: Folk & Intimate (exact match: 100%)
- Location: Camden
**Response Type:** Matchmaker
**Expected Behavior:** "folky" is already in synonyms, should be exact match
**Opening Sample:** "Something warm..."

---

## Test 015 – Multi-Filter: Budget + Mood + Location
**Prompt:** "cheap queer cabaret in East London this Friday"
**Extracted Filters:**
- Budget: Low
- Mood: Queer Revelry or Cabaret & Glitter
- Location: East London
- Time: Friday
**Response Type:** Matchmaker
**Expected Behavior:** Should filter for affordable venues matching mood in East London
**Opening Sample:** "Something glittering..."

---

## Test 016 – Multi-Filter: Solo + Thoughtful + Budget
**Prompt:** "somewhere thoughtful and not too expensive, just for me"
**Extracted Filters:**
- Mood: The Thoughtful Stage
- Budget: Low
- Group: Solo
**Response Type:** MoodMirror
**Expected Behavior:** Should exclude group-only venues and expensive opera houses
**Opening Sample:** "Something that makes you lean in..."

---

## Test 017 – Conflicting Filters: Cheap + Opera
**Prompt:** "any cheap opera tonight?"
**Extracted Filters:**
- Genre: Opera (implied by "opera")
- Budget: Low
**Response Type:** Gentle Refusal
**Expected Behavior:** Opera is expensive - should return no matches or suggest alternatives
**Opening Sample:** "The city's quiet on that front tonight, petal..."

---

## Test 018 – No Match Scenario: Unavailable Location
**Prompt:** "anything weird in Greenwich tomorrow"
**Extracted Filters:**
- Mood: Playful & Weird
- Location: Greenwich
- Time: Tomorrow
**Response Type:** Gentle Refusal
**Expected Behavior:** No Greenwich venues in database - suggest broadening search
**Opening Sample:** "Hmm, the city's being shy about this one..."

---

## Test 019 – Location Test: North London
**Prompt:** "folk music in North London this weekend"
**Extracted Filters:**
- Mood: Folk & Intimate
- Location: North London
- Time: Weekend
**Response Type:** Matchmaker
**Expected Behavior:** Should match Cecil Sharp House, Union Chapel
**Opening Sample:** "Something warm..."

---

## Test 020 – Location Test: East London
**Prompt:** "what's happening in Shoreditch tonight?"
**Extracted Filters:**
- Location: East London (Shoreditch maps to East)
- Time: Tonight
**Response Type:** Matchmaker (Location-priority)
**Expected Behavior:** Should match venues in East London area
**Opening Sample:** "Just around the corner..."

---

## Test 021 – Location Test: West London
**Prompt:** "anything in Notting Hill or West London?"
**Extracted Filters:**
- Location: West London
**Response Type:** Matchmaker (Location-priority)
**Expected Behavior:** Should match West London venues
**Opening Sample:** "Just around the corner..."

---

## Test 022 – Genre Test: Theatre
**Prompt:** "what theatre is on in Central London?"
**Extracted Filters:**
- Genre: Theatre
- Location: Central London
**Response Type:** Matchmaker
**Expected Behavior:** Should filter for theatre venues
**Opening Sample:** "Here's something just off the usual path..."

---

## Test 023 – Genre Test: Live Music
**Prompt:** "any gigs or live music happening tonight?"
**Extracted Filters:**
- Genre: Music
- Time: Tonight
**Response Type:** Matchmaker
**Expected Behavior:** Should match music venues (jazz, folk, etc.)
**Opening Sample:** "The city's heart beats softer tonight..."

---

## Test 024 – Edge Mood: Body-Based / Movement
**Prompt:** "looking for dance or physical theatre this weekend"
**Extracted Filters:**
- Mood: Body-Based / Movement-Led
- Time: Weekend
**Response Type:** MoodMirror
**Expected Behavior:** Should match venues with dance/circus/movement tags
**Opening Sample:** "When words aren't enough..."

---

## Test 025 – Edge Mood: Curious Encounters
**Prompt:** "I want to see something experimental and unusual"
**Extracted Filters:**
- Mood: Curious Encounters
**Response Type:** Wildcard/MoodMirror
**Expected Behavior:** Should match experimental/unusual/offbeat venues
**Opening Sample:** "You never quite know what you'll find..."

---

## Test 026 – Seasonal Test: Outdoor/Summer
**Prompt:** "anything outdoors or in a garden this summer?"
**Extracted Filters:**
- Mood: Seasonal / Outdoor
- Time: Summer
**Response Type:** Matchmaker
**Expected Behavior:** Should match outdoor/garden/rooftop venues
**Opening Sample:** "For when the city needs sky..."

---

## Test 027 – Edge Mood: Family-Friendly
**Prompt:** "what's good for kids this weekend?"
**Extracted Filters:**
- Mood: Family-Friendly
- Time: Weekend
**Response Type:** Matchmaker
**Expected Behavior:** Should match all-ages/family venues
**Opening Sample:** "Where wonder has no age limit..."

---

## Test 028 – Multi-Word Mood: Spoken Word
**Prompt:** "any spoken word or poetry tonight?"
**Extracted Filters:**
- Mood: Word & Voice or Poetic
- Time: Tonight
**Response Type:** MoodMirror
**Expected Behavior:** Should handle multi-word synonym "spoken word"
**Opening Sample:** "The hush of the room, the lyric of the light..."

---

## Test 029 – Ambiguous: Multiple Mood Matches
**Prompt:** "something intimate and spiritual"
**Extracted Filters:**
- Mood: Folk & Intimate (first match) OR Spiritual / Sacred / Mystical
**Response Type:** MoodMirror
**Expected Behavior:** Should pick first matching mood or combine
**Opening Sample:** Will vary based on chosen mood

---

## Test 030 – Vague Request: No Clear Filters
**Prompt:** "I want to go out tonight but I don't know what"
**Extracted Filters:**
- Time: Tonight
- Mood: None
**Response Type:** Wildcard or Prompt for more info
**Expected Behavior:** Should either suggest random venue or ask for preferences
**Opening Sample:** "Alright, Lark off-script..."

---

## Regression Test Summary

### Coverage by Category:
- **Edge Moods:** Tests 009-011, 024-027 (7 tests)
- **Fuzzy Matching:** Tests 012-014 (3 tests)
- **Multi-Filter:** Tests 015-016 (2 tests)
- **Conflicting Filters:** Test 017 (1 test)
- **No Match Scenarios:** Test 018 (1 test)
- **Location Coverage:** Tests 019-021 (3 tests)
- **Genre Filtering:** Tests 022-023 (2 tests)
- **Multi-Word Synonyms:** Test 028 (1 test)
- **Ambiguous Inputs:** Tests 029-030 (2 tests)

### Testing Priority:
1. **High Priority:** Tests 012-016 (fuzzy matching + multi-filter core functionality)
2. **Medium Priority:** Tests 009-011, 019-023 (edge moods + location coverage)
3. **Low Priority:** Tests 024-030 (rare edge cases + ambiguous inputs)

### Expected Pass Rate:
- **Current Implementation:** 85-90% (most core functionality working)
- **After Full Phase 2:** 95%+ (with all refinements complete)

---

## Notes:
- All test prompts should eventually link to automated tests in code
- Priority: fuzzy matching (Tests 012-014) and multi-filter (Tests 015-016) are most critical
- Edge moods need venue database expansion to pass fully
- Keep the tone lived-in, local, and lyrically plausible

---
