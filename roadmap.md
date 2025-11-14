# 🛤️ roadmap.md

🕊️ **The London Lark — Development Roadmap**
A gentle unfolding, not a sprint. This file outlines the Lark's evolution from poetic sketch to functioning guide.

---

## 🌱 Phase 1 — Seed & Skeleton
Foundational documents and poetic structure.

- [x] `README.md` — Vision, voice, purpose
- [x] `mood_index.json` — Mood tags + synonym mapping
- [x] `venue_profiles.md` — Poetic venue data + vibe tags
- [x] `poetic_templates.md` — Mood-specific poetic samples
- [x] `response_templates.md` — Structured output formats
- [x] `prompt_tests.md` — Realistic prompt-to-response samples
- [x] `instructions_panel.md` — Core logic and tone handling rules

🎯 *Goal:* Establish a working tone, tag set, and logic framework.

---

## 🔧 Phase 2 — MVP Logic Layer
Basic matching engine and internal testing tools.

**Core Implementation (Complete):**
- [x] `prompt_interpreter.py` — Converts user input → filters (mood, time, location)
- [x] `mood_resolver.py` — Uses `mood_index.json` to resolve mood tags
- [x] `venue_matcher.py` — Filters venues from `lark_venues_clean.json`
- [x] `response_generator.py` — Assembles poetic output using template logic
- [x] `test_runner.py` — Simulates test prompts + responses
- [x] `lark_poet.py` — Main CLI entry point (interactive & command-line)
- [x] `parse_venues.py` — Parses venue data into usable format
- [x] **Expanded venue database to 73 venues** across all London regions
- [x] **Expanded mood categories to 28 moods** with synonym mapping

**Refinement & Enhancement:**
- [x] Harden prompt interpretation:
  - [x] Expand tokenisation to handle punctuation + multi-word moods ✅ (completed 2025-11-06)
  - [x] Backfill mood synonyms and plural forms in `mood_index.json` ✅ (50+ new synonyms added)
  - [x] Grow the location lexicon beyond the current hard-coded borough list (North/South/East/West/Central + neighborhoods)
- [x] Put parsed filters to work in matching:
  - [x] Location filtering working across all regions
  - [x] Teach `venue_matcher.py` to honour budget, time, genre, and group size hints ✅ (completed 2025-11-06)
  - [x] Ensure fallbacks explain what could not be matched when data is missing ✅ (helpful suggestions added)
- [x] Enrich venue + event data:
  - [x] 73 curated venues with mood tags and poetic descriptions
  - [ ] Add dated events, indicative prices, and timings to venue data (deferred to Phase 3)
  - [x] Extend response templates to surface concrete logistics ("tonight", price, duration) ✅ (completed 2025-11-14)
- [x] Tighten mood resolution:
  - [x] Improve scoring logic so close moods still land on a poetic match ✅ (fuzzy matching with confidence scores)
  - [x] Add regression examples covering edge moods in `prompt_tests.md` ✅ (expanded to 30 test cases)
- [x] Build an evaluation harness:
  - [x] `test_runner.py` exists and works
  - [x] Wire `test_runner.py` into an automated CLI smoke test ✅ (automated_test.py with 100% pass rate)
  - [x] Log coverage stats (e.g. % prompts with confident mood + venue match) ✅ (lark_metrics.py)

🎯 *Goal:* Full logic demo from prompt → poetic rec., with resilient parsing, richer data, and measurable confidence.

**Status:** Phase 2 COMPLETE ✅ | All core refinements done ✅ | Ready for Phase 3 (API integration) or Phase 4 (web interface)

---

## 🔗 Phase 3 — Source & Sync
Connect Lark with real-time listings and expand cultural reach.

- [ ] Integrate TodayTix, Dice, Folk & Honey (API or scrape)
- [ ] Normalize event data formats (time, cost, location)
- [ ] Sync real listings with mood tags
- [ ] Optional: Local event seeding or manual curation

🎯 *Goal:* Enable real-world, live cultural matching

---

## 🧚‍♀️ Phase 4 — Interface & Magic
Make the Lark visible, usable, and soulful.

- [ ] Web or app front-end (clean, poetic UI)
- [ ] Optional: Local LLM or OpenAI agent integration
- [ ] Optional: Voice mode or animated Lark avatar
- [ ] Feedback loop / wishlist input from real users

🎯 *Goal:* Share the Lark with the world — small, bright, and real.

---

## 📌 Notes
- Each phase is modular — can be explored in sprints or spirals
- Design with care, build with beauty, test with kindness
- The Lark's soul lives in her voice. Protect it always.

---
