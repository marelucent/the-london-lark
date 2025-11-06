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

- [ ] Harden prompt interpretation:
  - Expand tokenisation to handle punctuation + multi-word moods
  - Backfill mood synonyms and plural forms in `mood_index.json`
  - Grow the location lexicon beyond the current hard-coded borough list
- [ ] Put parsed filters to work in matching:
  - Teach `venue_matcher.py` to honour budget, time, genre, and group size hints
  - Ensure fallbacks explain what could not be matched when data is missing
- [ ] Enrich venue + event data:
  - Add dated events, indicative prices, and timings to `venue_profiles.md`
  - Extend response templates to surface concrete logistics ("tonight", price, duration)
- [ ] Tighten mood resolution:
  - Improve scoring logic so close moods still land on a poetic match
  - Add regression examples covering edge moods in `prompt_tests.md`
- [ ] Build an evaluation harness:
  - Wire `test_runner.py` into an automated CLI smoke test
  - Log coverage stats (e.g. % prompts with confident mood + venue match)

🎯 *Goal:* Full logic demo from prompt → poetic rec., with resilient parsing, richer data, and measurable confidence.

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
- The Lark’s soul lives in her voice. Protect it always.

---
