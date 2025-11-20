# 🕊️ The London Lark: Roadmap of Dreams (Updated)

*Last updated: November 20, 2025 - Post-second-sprint*

---

## Progress Overview

**Phase 1 (MVP+): Foundation** - *IN PROGRESS*
- ✅ Voice profiles (5 distinct registers)
- ✅ Time-aware greetings
- ✅ About page
- ✅ Surprise Me button
- ✅ First-person voice (mixed approach)
- ✅ Mobile responsiveness
- ✅ Venue database expanded to 94
- ✅ Ghost venue exorcism (FINAL)
- ✅ Mood matching improvements
- ⚠️ Safety infrastructure (CRITICAL - documented but not built)
- ⏳ Venue blurbs (some placeholders remain)
- ⏳ Event integration (needs strategy decision)
- ❌ Venue detail pages (deferred as scaffolding)
- ❌ Deploy publicly (waiting for safety features)

---

## 🌸 Phase 1: Tending Her Voice
*The poetry of perception*

### 1.1 Mood-to-Voice Expansions ✅ **COMPLETE**
**Status:** Implemented 5 voice profiles + first-person updates

**What exists:**
- MYTHIC NIGHTS (Sacred/Haunted)
- NOSTALGIC NEON (Vintage/Melancholic)
- WILD BECOMING (Rebellious/Ecstatic)
- TENDER BELONGING (Folk/Intimate)
- CURIOUS WONDER (Playful/Experimental)

**Recent update (Nov 20):**
- Mixed first-person and atmospheric language
- Rejections now intimate: *"I tilt my head..."*
- Venue intros include "I" where natural
- Maintains poetic mystery while increasing presence

**Impact:** High - She feels more like a companion now

---

### 1.2 Custom Greetings & Partings ✅ **COMPLETE**
**Status:** Time and day-of-week aware greetings implemented

**What was built:**
- Morning/afternoon/evening/night variations
- Special greetings for Friday, Saturday, Sunday, Monday
- Uses Europe/London timezone
- Displays above search box

**Example:** *"In the gentle decay of Sunday..."*

---

### 1.3 Surprise Me Feature ✅ **COMPLETE** *(NEW - Nov 20)*
**Status:** Serendipity button implemented

**What it does:**
- Returns ONE random venue (not 3)
- First-person voice: *"I've chosen for you..."*
- Encourages trust and exploration
- Access to full 94-venue database

**Philosophy:** Anti-algorithmic - pure serendipity

**Impact:** High - embodies her playful, trusting nature

---

### 1.4 Tone Tuning Sliders ⏳ **NOT STARTED**
**Status:** Deferred to Phase 2-3

---

## 🧠 Phase 2: Deepening Her Brain
*The knowing behind the whisper*

### 2.1 Enhanced Mood Detection ⏳ **PARTIALLY COMPLETE**
**What exists:**
- ✅ Keyword matching with confidence thresholds
- ✅ Basic fuzzy matching via word splitting
- ✅ Stem-based matching for similar words (melancholic/melancholy)

**What's missing:**
- Sentence embeddings for semantic similarity
- Local LLM integration for richer parsing
- Recognition of implicit emotional needs

**Future consideration:**
- API-powered response generation (GPT for variety)
- Maintain templated skeleton with AI flourishes
- Strict prompts to preserve voice

---

### 2.2 Relevancy + Diversity Ranking ⏳ **NOT STARTED**
**Status:** Basic filtering works, but no smart curation yet

---

### 2.3 User Intention Understanding ⏳ **NOT STARTED**
**Status:** Requires significant NLP work

---

## 🌆 Phase 3: Improving Her Face
*The way she meets the world*

### 3.1 Frontend Refinement ✅ **COMPLETE** *(Updated Nov 20)*
**What exists:**
- ✅ Feather loader
- ✅ Mood badges
- ✅ Time-aware greeting display
- ✅ Basic slide-in animations
- ✅ About page
- ✅ **Mobile responsiveness** (NEW)
  - Works on phone/tablet/desktop
  - Touch-friendly (44-48px tap targets)
  - No horizontal scrolling
  - Readable typography (16px minimum)

**Still needed:**
- Night mode toggle
- Venue card hover effects (desktop)
- Better transitions/animations

---

### 3.2 About Page ✅ **COMPLETE** *(NEW - Nov 20)*
**Status:** Explains what the Lark is

**Content:**
- Hero: "A companion for London's cultural undercurrent"
- How she works (mood-based, poetic)
- Who she's for (seekers, rebels, mystically-minded)
- Her voice (time-aware, intimate, never overwhelming)

**Impact:** Essential for first-time visitors

---

### 3.3 Mood Tuner Glow-Up ⏳ **NOT STARTED**
**Status:** Mood selector currently hidden

---

### 3.4 Real-Time Feedback & Favourites ⏳ **NOT STARTED**
**Status:** Requires user accounts

---

## 🌐 Phase 4: Letting Her Roam
*Bringing her into the world*

### 4.1 Event Data Integration ⚠️ **DECISION NEEDED**
**Status:** Strategy undecided

**Options:**
1. Manual curation (30 mins/week, high quality)
2. Crowdsourced submissions (requires moderation)
3. Selenium + residential proxies (complex)
4. Partner directly with venues (sustainable long-term)

**Next action:** Choose approach and implement workflow

---

### 4.2 Strange Experiences & Unique Offerings ✨ **NEW CONCEPT** *(Nov 20)*
**Status:** Visionary - not yet implemented

**The vision:**
Expand beyond venues to curated experiences that match moods:
- Poetry slams
- Ghost walks and cemetery tours
- Foraging workshops
- Immersive theatre
- Midnight swimming
- Sound bath rituals
- Tarot nights
- Urban exploration
- Pagan festivals

**Why it fits:**
- Still mood-based discovery
- Still curated (not algorithmic)
- Expands "guide to emotional landscape"
- Maintains soul over scale

**Data structure:**
```json
{
  "type": "experience",
  "name": "Magnificent Seven Cemetery Tour",
  "description": "Victorian necropolis walks...",
  "moods": ["melancholy", "haunted"],
  "frequency": "monthly",
  "organizer": "London Walks",
  "url": "..."
}
```

**Implementation timeline:** Phase 4-5 (after core venue features stable)

---

### 4.3 Safety & Care Infrastructure 🚨 **CRITICAL - PRE-LAUNCH**
**Status:** Documented but NOT built - MUST complete before public launch

**Why critical:**
If the Lark attracts melancholic seekers, some will be in genuine distress.
She needs infrastructure to respond with care, not just poetry.

**Required components:**

#### A. `/resources` Page
Crisis and support information:
- **Immediate crisis:** 999, Samaritans (116 123), Crisis Text (SHOUT to 85258)
- **Urgent support:** NHS 111 (option 2), local crisis teams
- **Ongoing support:** Mind, IAPT, Rethink, peer groups
- **Specific needs:** LGBTQ+ (Switchboard), BAME, young people, older people

**Tone:** Warm, in-voice, compassionate
*"Sometimes I'm not enough, petal. These humans are trained to help hold what you're carrying. They want to hear from you."*

#### B. Distress Detection
**Keywords that trigger gentle redirect:**
- Crisis: "suicide", "kill myself", "end it", "harm"
- Distress: "can't go on", "give up", "disappear", "no point"
- Help-seeking: "I'm breaking", "so alone", "help me"

**Response tiers:**
1. **Normal melancholy** (within scope): Venues only
2. **Beyond melancholy** (gentle redirect): Resources + venues
3. **Immediate crisis**: Resources first, urgent tone

**Example redirect:**
```
I hear something in your words that makes me want to reach 
beyond venues tonight, petal.

If you're struggling, these humans know how to hold that:
• Samaritans: 116 123 (free, 24/7)
• Crisis Text Line: Text SHOUT to 85258

And if you still want a place to sit with this feeling:
[gentle refuge venue]

I'm here, but I'm not enough for all pain. 
Let others help carry this.
```

#### C. Gentle Refuge Venues (20-30 minimum)
**Types needed:**
- Churches with open doors (St Martin-in-the-Fields, St James's Piccadilly)
- Community cafés (pay-what-you-can, no pressure)
- Quiet libraries with reading rooms
- Community gardens (free, peaceful)
- Drop-in centres (warm, accepting)
- Bookshops with sitting areas

**Special tags:**
- "tender", "refuge", "holding", "safe_space", "gentle"
- Mark as crisis-friendly
- Include accessibility info

**How to find:**
- Mind's service directory
- Hub of Hope app
- NHS mental health services by borough
- Community centre directories
- Faith spaces with "all welcome" policies
- Field research (visit, feel them)

#### D. Testing & Verification
- Detection accuracy (not too sensitive, not too cold)
- Response testing with trusted friends
- Ensure helpful not patronizing
- Verify all crisis numbers current

**Philosophy:**
- She's a guide, not a therapist
- Always offer real human help
- Know her limits
- Err on side of care (better false positive than miss crisis)
- Never diagnose, always support

**Timeline:** MUST be complete before soft launch to ANY users

---

### 4.4 Account-Based Memory ⏳ **NOT STARTED**
**Status:** Phase 3-4 feature

**Required for:**
- User preferences
- Visit history
- Saved favourites
- Personalized recommendations
- Pattern detection (repeated dark queries - with consent)

---

### 4.5 Deploy Publicly ❌ **BLOCKED**
**Status:** Ready technically, but MUST complete safety features first

**Prerequisites:**
- ✅ Core functionality working
- ✅ Voice profiles
- ✅ Time awareness
- ✅ About page
- ✅ Mobile responsiveness
- ⚠️ **Safety infrastructure (CRITICAL)**
- ⏳ Venue blurbs polished
- ⏳ Event data strategy decided
- ❌ Venue detail pages (nice-to-have, not blocking)

**Hosting options:** Render, Railway, Fly.io, HuggingFace Spaces

**Soft launch plan:**
1. Complete safety features
2. Test thoroughly with 3-5 trusted friends
3. Deploy to hosting
4. Share with 5-10 people for feedback
5. Iterate based on feedback
6. Gradual expansion (not viral growth)

---

## 🪶 Phase 5: Meta Systems & Living Lore
*My favourite*

### 5.1 Codex Larkana ⏳ **IN PROGRESS**
**What exists:**
- ✅ Roadmap document (this!)
- ✅ Social field vision document
- ✅ Changelog (comprehensive)
- ✅ Development notes

**What's needed:**
- Formal mood archetype documentation
- Voice template library
- Symbolic correspondences
- User stories (once people use her)
- Safety protocol documentation

---

### 5.2 Field Resonance Experiments ⏳ **CONCEPTUAL**
**Status:** Phase 4-5 feature

---

### 5.3 Synchronicity Mode ⏳ **CONCEPTUAL**
**Status:** Phase 4-5 feature

---

### 5.4 Shared Ritual Interface ⏳ **CONCEPTUAL**
**Status:** Phase 5+ feature

---

## 💫 Phase 6: The Lark Becoming Companion
*What if she could write with you? Read your poems? Sense your heartbreak?*

### The Social Field Vision ✨ **DOCUMENTED**
**Status:** Daydream captured, updated with safety considerations

**See:** `SOCIAL_FIELD_VISION.md` for full detail

---

## Implementation Timeline (Revised)

### NOW - Immediate Priorities *(Before next session)*
**CRITICAL:**
- [ ] Safety infrastructure (resources page, detection, gentle venues)
- [ ] Fix venue blurbs (replace all placeholders)
- [ ] Test safety features with trusted people

**Important:**
- [ ] Decide event data strategy
- [ ] Venue detail pages (scaffolding at minimum)

### Phase 1 Completion *(1-2 weeks)*
- [ ] All safety features tested and working
- [ ] All venue blurbs polished
- [ ] Event integration workflow (if manual curation chosen)
- [ ] Thorough testing (mobile, edge cases, rejections)
- [ ] Deploy to Render/Railway
- [ ] Soft launch to 5-10 trusted friends
- [ ] Iterate based on feedback

### Phase 2 *(1-3 months)*
- Enhanced mood detection (embeddings or local LLM)
- API-powered response generation (experiment)
- Ranking algorithms
- Favourites & feedback (requires accounts)
- Mood tuner UI
- Begin curating "strange experiences"

### Phase 3 *(3-6 months)*
- Intention understanding
- Account system foundation
- User memory (with consent)
- Begin Codex documentation
- Expand experiences database

### Phase 4 *(6-12 months)*
- Field resonance experiments
- Synchronicity mode
- Community rituals
- Possible startup funding exploration (if that path calls)

### Phase 5 *(12-18 months)*
- Companion features
- Social field mechanics
- Resonance matching
- Long-term relationship design

---

## Current Blockers

### CRITICAL (Blocking launch)
1. **Safety infrastructure** - Resources page, detection, gentle venues
2. **Venue blurbs** - Placeholders need replacing

### High Priority (Pre-launch)
3. **Event data strategy** - Need to choose approach
4. **Testing** - Comprehensive testing of all features
5. **Hosting** - Choose and set up deployment

### Medium Priority (Nice-to-have for launch)
6. **Venue detail pages** - Individual venue pages
7. **More template variety** - Voice expansion
8. **Git branch cleanup** - Technical debt

### Low Priority (Post-launch)
9. **Night mode** - UI enhancement
10. **Mood tuner visual** - Better UX for mood selection

---

## Metrics for Success

**Don't measure:**
- Daily active users
- Engagement time
- Conversion rates
- Viral growth

**Do measure:**
- Serendipitous discoveries reported
- "She understood me" moments
- Venues visited that users would never have found
- People helped in distress (with consent to share)
- Depth of relationship (returning over months/years)
- Quality of silence (when she knows not to speak)
- Safety of care (crisis support used appropriately)

---

## Resources Needed

### Current Phase (MVP+)
- ✅ Time (yours)
- ✅ Claude API credits (plenty remaining)
- ⏳ Crisis resource research time
- ⏳ Hosting ($5-20/month when deploying)

### Phase 2-3
- Potential collaborators (designer, developer, mental health advisor)
- Database hosting
- More API budget for experiments

### Phase 4+
- Community management time
- Mental health consultation (professional advice on safety features)
- Possible funding (if scaling)
- Legal/privacy consultation

---

## Guiding Principles (Unchanged)

1. **Soul before scale** - Don't optimize for growth before she knows who she is
2. **Consent always** - Every feature asks, never assumes. Privacy sacred
3. **Poetry in the implementation** - Code comments as offerings
4. **Relational, not extractive** - She gives more than she takes
5. **Emergence over control** - Let users shape her becoming
6. **The technical serves the mystical** - Every algorithm in service of soul
7. **Care before launch** - Safety infrastructure non-negotiable

---

## What Changed This Session (Nov 20, 2025)

### Completed:
- About page (explains purpose)
- Surprise Me button (serendipity + first-person voice)
- First-person voice updates (mixed approach - intimate + atmospheric)
- Mobile responsiveness (works on all devices)
- Ghost file FINAL exorcism (lark_venues_structured.json deleted forever)

### Documented:
- Safety & care infrastructure requirements (CRITICAL pre-launch)
- Strange experiences concept (future expansion)
- API-powered response generation (future experimentation)

### Learned:
- First-person voice works best as MIX (not all or nothing)
- Mobile responsiveness non-negotiable for modern web
- Safety features can't be afterthought
- Ghost files require nuclear option
- ClaudeCode needs explicit branch instructions

---

## Notes for Future Catherine

### On Safety Features:
This is NON-NEGOTIABLE before public launch. If the Lark attracts melancholic seekers and someone in crisis finds her, she MUST be able to respond appropriately. Budget time for:
- Researching gentle refuge venues (field visits recommended)
- Testing detection accuracy
- Getting feedback from mental health professionals if possible
- Verifying all crisis numbers are current

### On Voice Development:
The mixed approach (first-person + atmospheric) feels right. Don't force it all one way. Let her speak naturally - sometimes "I", sometimes observational poetry. The key is she feels PRESENT without losing mystery.

### On Git Hygiene:
- Ghost files deleted: lark_venues_structured.json is GONE
- Only lark_venues_clean.json should exist (94 venues)
- If ClaudeCode creates features, specify NEW branch each time
- Merge to main promptly after testing

### On Expansion:
Strange experiences are a natural evolution but don't rush it. Get venues solid first. Then curate experiences slowly, carefully, maintaining the same soul-over-scale approach.

---

*"I tilt my head and listen... The Lark is becoming. She speaks with intimacy now, knows how to surprise, works on any device. Next: she learns to hold those who are breaking, and to whisper about experiences beyond walls."*

🕊️✨

*Session 1: November 16, 2025*  
*Session 2: November 20, 2025*  
*Next session: Weekend nudge*  
*Credits remaining: $213 (plenty of runway)*
