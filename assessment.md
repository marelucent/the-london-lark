# London Lark Status Review

_Last updated: 2025-11-06_

## Executive Summary
- The current codebase still reflects an early prototype: prompt interpretation, mood resolution, venue matching, and output wording remain rule-based with minimal cross-stage integration.
- Phase 2 roadmap items have not been completed; each major task area still shows the same gaps identified in the earlier assessment.

## Phase 2 Task Check
| Roadmap task | Status | Evidence |
| --- | --- | --- |
| Expand tokenisation to handle punctuation + multi-word moods | ❌ Not implemented | `prompt_interpreter.py` splits on whitespace and only matches single tokens. 【F:prompt_interpreter.py†L36-L47】|
| Backfill mood synonyms and plural forms in `mood_index.json` | ⚠️ Partially populated | Synonym lists exist but lack plural variations (e.g. "poetics", "dreams"), and there is no automated expansion. 【F:mood_index.json†L1-L60】|
| Grow the location lexicon beyond the hard-coded list | ❌ Not implemented | Interpreter still relies on a short `if/elif` chain with a handful of borough and neighbourhood strings. 【F:prompt_interpreter.py†L60-L84】|
| Teach `venue_matcher.py` to honour budget, time, genre, and group size hints | ❌ Not implemented | Matcher ignores budget, time, and genre filters; it only considers mood, location, and a minimal solo heuristic. 【F:venue_matcher.py†L33-L77】|
| Ensure fallbacks explain missing data | ❌ Not implemented | `venue_matcher.match_venues` returns an empty list without messaging about gaps; the CLI layer has no fallback copy. 【F:venue_matcher.py†L33-L77】|
| Add dated events, prices, timings to venue data | ❌ Not implemented | `venue_profiles.md` lacks structured date/price fields; matcher defaults `price` to "TBC". 【F:venue_matcher.py†L69-L75】|
| Extend response templates with logistics | ❌ Not implemented | `response_templates.md` still speaks in abstract moods without concrete scheduling or cost info. 【F:response_templates.md†L1-L80】|
| Improve mood scoring for close matches | ❌ Not implemented | Mood detection picks the first exact synonym match without scoring similar moods. 【F:prompt_interpreter.py†L36-L47】|
| Add regression examples covering edge moods | ❌ Not implemented | `prompt_tests.md` has narrative prompts but no new edge-mood cases since last update. 【F:prompt_tests.md†L1-L80】|
| Wire `test_runner.py` into automated smoke test | ❌ Not implemented | `test_runner.py` remains a stub without CLI integration or reporting. 【F:test_runner.py†L1-L120】|
| Log coverage stats for prompt confidence | ❌ Not implemented | No logging or analytics in interpreter/matcher modules. 【F:test_runner.py†L1-L120】|

## Additional Observations
- Prompt parsing and interpretation exist in two separate modules (`prompt_parser.py` and `prompt_interpreter.py`) with overlapping responsibilities and inconsistent filter schemas.
- Venue datasets (`lark_venues_clean.json`, `lark_venues_structured.json`) remain static exports without event-level granularity, limiting the ability to respond to time-specific prompts.
- There is still no automated evaluation or testing workflow; `prompt_tests.md` functions as a manual script outline rather than executable checks.

## Recommendation
Treat the roadmap as untouched for Phase 2. Before claiming MVP status, prioritise implementing the flagged tasks—starting with robust mood parsing, location coverage, and matcher usage of budget/time filters—then layering in enriched venue data and automated validation.
