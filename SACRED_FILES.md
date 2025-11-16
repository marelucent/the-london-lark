# 🕊️ DO NOT MODIFY THESE FILES

The following files contain the Lark's voice, mood taxonomy, and poetic templates. 
They are LOCKED and should never be edited by automated tools without explicit human review.

## Voice & Templates (SACRED)
- `instructions_panel.md`
- `poetic_templates.md` 
- `response_templates.md`
- `birdsong_lexicon.json`
- `mood_index.json`

Any changes to these files must be:
1. Reviewed line-by-line by Catherine
2. Tested against the existing voice/tone
3. Approved before commit

## Data & Logic (MODIFIABLE WITH CARE)
- `lark_venues_clean.json` (can append new venues, but don't overwrite existing curated blurbs without review)
- `venue_matcher.py` (matching logic)
- `prompt_parser.py` (parsing logic)
- Data pipeline scripts
- Web UI code

**Rule: Before making changes, read this file. When in doubt, ask Catherine.**
```
