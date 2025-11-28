# 🕊️ The London Lark - Project Index
*Living documentation - Update this every session*
*Last Updated: 27 November 2025*

---

## 🎯 PROJECT OVERVIEW

**What:** Mood-based cultural discovery app for London  
**Philosophy:** Soul before scale, consent always, poetry in implementation  
**Status:** MVP+ complete, pre-public launch (safety features blocking)  
**Live URL:** the-london-lark.onrender.com  
**Repo:** [Add your GitHub URL here]

---

## 📊 CURRENT STATE (AS OF NOV 27)

### What Actually Works:
✅ 5 distinct voice profiles (Mythic, Nostalgic, Wild, Tender, Curious)  
✅ Time-aware greetings (morning/afternoon/evening/night + day-of-week)  
✅ About page  
✅ Surprise Me button (random venue discovery)  
✅ First-person poetic voice  
✅ Mobile responsive  
✅ Distress detection (3 levels: crisis/distress/melancholy)  
✅ 295 verified venues with poetic blurbs  
✅ Clickable mood search on homepage (30 Core moods displayed)

### What's Broken/Unclear:
⚠️ **CRITICAL:** Mood tag mismatch between database and search  
⚠️ **CRITICAL:** Unclear if Taxonomy v2 migration actually deployed  
⚠️ Some moods return no results (Dreamlike & Hypnagogic, Something I Wouldn't Normally Pick)  
⚠️ Some venues have wrong mood tags (5Rhythms tagged "contemplative" instead of "fluid/movement")  
⚠️ Voice profiles may not be mapped to new Core moods

### What's Not Built Yet (Blocking Public Launch):
❌ Crisis resources `/resources` page  
❌ Refuge venue tagging (20-30 gentle venues)  
❌ Prominent crisis resource display in distress responses

---

## 🏗️ SYSTEM ARCHITECTURE

### Data Flow (CRITICAL TO UNDERSTAND):

```
SOURCE OF TRUTH:
lark_venues_clean.json (in Git repo)
    ↓
DEPLOYMENT (Render runs build.sh):
python import_lark_to_sqlite.py
    ↓
CREATES:
lark.db (SQLite database)
    ↓
APP READS FROM:
parse_venues.py → load_parsed_venues()
    ↓
SERVES TO USER:
Flask app (app.py)
```

### Key Files:

**Data Files:**
- `lark_venues_clean.json` - Source of truth (295 venues)
- `lark.db` - SQLite database (generated from JSON at build time)
- `mood_index_v2_CORRECTED.json` - Taxonomy v2 definition (Core/Extended/Features)

**Python Backend:**
- `app.py` - Main Flask application
- `venue_matcher.py` - Matches user queries to venues
- `mood_resolver.py` - Interprets mood from natural language
- `response_generator.py` - Generates poetic responses
- `poetic_templates.py` - Voice profile definitions
- `parse_venues.py` - Loads venues from database
- `import_lark_to_sqlite.py` - Rebuilds database from JSON

**Frontend:**
- `templates/index.html` - Homepage with search + mood buttons
- `templates/about.html` - About page
- `static/style.css` - Styling

**Deployment:**
- `build.sh` - Runs on Render deployment (rebuilds database)
- `start.sh` - Starts gunicorn server
- `requirements.txt` - Python dependencies

---

## 🗂️ TAXONOMY V2 STRUCTURE

**Core Moods (40):**
Primary search interface - displayed as clickable buttons on homepage
- Includes original 30 approved moods
- Plus 10 high-frequency additions: curious, playful, rebellious, wild, ecstatic, intimate, tender, earthy, epicurean, nostalgic

**Extended Moods (127):**
Specific/niche moods - fully searchable but not displayed on homepage
- Examples: aromatic, gothic, mythic, ritual, sensory, theatrical, healing, immersive, tactile, transformative, fluid, soulful, contemplative, literary, sensual, sweaty

**Features (12):**
Logistics only - separate field, not moods
- accessible, boozy, workshop, outdoor, free, family-friendly, foodie-friendly, jam-friendly, online, drop-in, queer-led, women-led

---

## 🚨 CRITICAL ISSUE (CURRENT SESSION)

### The Problem:
Mood tags in database don't match Taxonomy v2. Live site is using OLD tags:
- Database has: "melancholy", "candlelit", "folk", "playful" (lowercase, old names)
- Should have: "Melancholic Beauty", "Folk & Intimate", etc. (Taxonomy v2 names)

### Why It Happened:
ClaudeCode created migration files yesterday but they were never:
1. Committed to Git
2. Deployed to Render
3. Actually applied to the source JSON file

### The Fix:
Need to properly migrate `lark_venues_clean.json` with Taxonomy v2 mood tags, commit, push, redeploy.

---

## 📋 DEPLOYMENT CHECKLIST

When making database changes:

1. ✅ Update `lark_venues_clean.json` (source of truth)
2. ✅ Commit to Git
3. ✅ Push to GitHub
4. ✅ Render auto-deploys (or manual deploy via dashboard)
5. ✅ Render runs `build.sh` which runs `import_lark_to_sqlite.py`
6. ✅ Database rebuilt from JSON
7. ✅ App restarts with new data
8. ✅ Test live site
9. ✅ Update this index with what changed

**DO NOT SKIP STEPS!**

---

## 🎭 VOICE PROFILES

### Mapping (Core Moods → Voice Profiles):

**MYTHIC_NIGHTS:**
- Spiritual / Sacred / Mystical
- Witchy & Wild
- Dreamlike & Hypnagogic
- Grief & Grace

**NOSTALGIC_NEON:**
- Nostalgic / Vintage / Retro
- Melancholic Beauty
- Jazz & Contemplation
- Cabaret & Glitter

**WILD_BECOMING:**
- Big Night Out
- Late-Night Lark
- Punchy / Protest
- Queer Revelry
- ⚠️ Need to add: rebellious, wild, ecstatic

**TENDER_BELONGING:**
- Folk & Intimate
- Comic Relief
- Wonder & Awe
- Body-Based / Movement-Led
- ⚠️ Need to add: intimate, tender, earthy

**CURIOUS_WONDER:**
- Curious Encounters
- Playful & Weird
- The Thoughtful Stage
- Global Rhythms
- Poetic
- ⚠️ Need to add: epicurean

---

## 📈 DATABASE STATS

- **Total venues:** 295
- **Core moods:** 40
- **Extended moods:** 127
- **Features:** 12
- **Total mood tag instances:** ~779 (before v2 migration)
- **Venues with blurbs:** 295/295 (100%)
- **Last verified:** November 2025

**Geographic Coverage:**
- Strong: Central, East, South London
- Moderate: North London
- Weak: West London, Outer London

---

## 🐛 KNOWN BUGS

1. **Taxonomy v2 not deployed** - Database still has old mood tags
2. **"a night of [mood]" parsing** - Doesn't detect mood in this phrasing
3. **Empty mood searches** - Some Core moods return no results
4. **Wrong venue tags** - 5Rhythms tagged "contemplative" (should be "fluid/movement")
5. **Voice profile mappings incomplete** - New Core moods not mapped to profiles

---

## 🎯 IMMEDIATE NEXT STEPS

### Session 4 Priorities:

**CRITICAL (Must Fix Before Anything Else):**
1. **Deep dive on database state** - Understand what's actually deployed
2. **Proper Taxonomy v2 migration** - Fix the JSON file correctly
3. **Semantic mood verification** - Fix obviously wrong tags (5Rhythms, etc.)
4. **Test deployment** - Verify changes actually reach live site

**Then (Once Database is Clean):**
5. Voice profile mappings (10 mins)
6. Crisis resources page (2-3 hours)
7. Refuge venue tagging (1 hour)
8. Safety features testing

---

## 📚 KEY DOCUMENTS

**In `/mnt/project/` (Git Repo):**
- ROADMAP_UPDATED_V2.md - Full feature roadmap
- CHANGELOG_UPDATED.md - Session 1-2 history
- TODO.md - Task list
- SOCIAL_FIELD_VISION.md - Long-term vision
- VENUE_DATA_STANDARDS.md - Data quality guidelines

**In `/mnt/user-data/outputs/` (Session Work):**
- CHANGELOG_SESSION3_NOV27.md - Yesterday's work
- TODO_UPDATED_NOV27.md - Updated priorities
- mood_index_v2_CORRECTED.json - Taxonomy v2 definition
- tag_migration_map_CORRECTED.json - Migration mapping
- TODAYS_WINS_NOV27.md - Quick summary

---

## 🔧 TROUBLESHOOTING GUIDE

### "Venues have wrong mood tags"
→ Check `lark_venues_clean.json` source file  
→ Update JSON  
→ Commit, push, redeploy  
→ Database rebuilds from JSON

### "Mood search returns nothing"
→ Check if mood exists in any venue's tag list  
→ Check mood_resolver.py has synonyms for that mood  
→ Check venue_matcher.py can find the mood

### "Changes don't appear on live site"
→ Verify changes committed to Git  
→ Verify pushed to GitHub  
→ Verify Render deployed  
→ Check build logs on Render  
→ Hard refresh browser (Ctrl+Shift+R)

### "Database seems out of date"
→ Check file dates: `ls -la *.json *.db`  
→ Check if build.sh ran successfully  
→ Manually run: `python import_lark_to_sqlite.py`  
→ Verify lark.db was created/updated

---

## 💡 DEVELOPMENT PRINCIPLES

1. **Source of truth is JSON** - Always edit `lark_venues_clean.json` first
2. **Database is generated** - Never edit .db file directly
3. **Commit before deploy** - Git is the deployment mechanism
4. **Test locally first** - Run import script, test before pushing
5. **One change at a time** - Don't stack multiple migrations
6. **Document everything** - Update this index every session
7. **Soul before scale** - Preserve poetic voice and careful curation

---

## 🗣️ COMMUNICATION BETWEEN AI SYSTEMS

**Claude (this conversation):**
- Strategy and planning
- Architecture decisions
- Documentation
- Debugging and analysis
- Cannot directly edit project files

**ClaudeCode:**
- Code implementation
- File editing
- Testing
- Git operations
- Can see and edit project files

**ChatGPT:**
- Venue research
- Content generation (blurbs)
- Data verification
- Batch operations

**Handoff Protocol:**
When switching to ClaudeCode, provide:
1. This PROJECT_INDEX.md
2. Specific task description
3. Files to edit
4. Expected outcome
5. Testing instructions

---

## 📝 SESSION LOG FORMAT

After each session, update:

```markdown
## [Session X] - YYYY-MM-DD

### Completed:
- [x] Thing 1
- [x] Thing 2

### Issues Found:
- Issue description

### Files Changed:
- file1.py
- file2.json

### Next Session:
- [ ] Priority 1
- [ ] Priority 2
```

---

## 🎓 WHAT CATHERINE NEEDS TO KNOW

### Your Workflow:
1. Work with Claude (me) for planning/debugging
2. Switch to ClaudeCode for implementation
3. Use ChatGPT for research/content
4. Test locally when possible
5. Deploy to Render when ready

### When Things Break:
1. Don't panic - vibing got you this far!
2. Refer to this index first
3. Check what's actually deployed (not what we think)
4. One fix at a time
5. Document what you learn

### Your Strengths:
- Poetic vision is clear and strong
- Philosophy guiding technical choices
- Good instincts (stopping to understand > more patches)
- Creative with AI orchestration

### Growth Areas:
- Database workflows (learning!)
- Git deployment flow (getting there!)
- When to vibe vs when to plan (you just leveled up on this!)

---

*"This index is a map. Update it every session. Future Catherine will thank you."*

🕊️✨
