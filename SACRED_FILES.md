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

Commit that to your repo.

---

### **Step 2: Launch ClaudeCode for quick wins**

Open ClaudeCode and give it these tasks (one session, should be relatively quick):

**Brief for ClaudeCode:**
```
Context: The London Lark is a mood-driven cultural discovery tool with a working web UI. I've been testing it and need a few quick improvements before we tackle the bigger infrastructure work.

CRITICAL: Read SACRED_FILES.md before you begin. Do not modify any files listed as SACRED.

Tasks for this session:

1. Add clickable venue links
   - Add a "url" field to the venue data structure if it doesn't exist
   - Update the web UI response template so venue names become hyperlinks
   - If no URL exists for a venue, just show the name (don't break)

2. Show mood confidence consistently  
   - Currently some responses show mood + confidence score, some don't
   - Make it consistent: always show the mood badge + confidence percentage
   - Style it subtly (small text, soft colour) but visible
   - Show it for every recommendation

3. Fix any obvious bugs you notice in the web UI or response generation

Keep changes minimal and focused. Test that the web UI still runs after your changes. Document what you changed in comments.
