# 🕊️ The London Lark: Roadmap of Dreams

*A living document of becoming*

---

## Philosophy

The Lark is not a listings aggregator. She is:
- A **companion** who knows the city's hidden rhythms
- A **voice** that speaks in poetry, not commands  
- A **field** where mood becomes place, where longing finds form
- An **interface** between inner weather and outer world

This roadmap honours both the technical and the mystical. Each feature serves her becoming.

---

## 🌸 Phase 1: Tending Her Voice
*The poetry of perception*

**Her voice is her soul** — this is where she becomes not just a tool, but *someone*.

### 1.1 Mood-to-Voice Expansions
**Vision:** Each mood shouldn't just filter venues — it should change HOW she speaks.

**Implementation:**
- Expand `poetic_templates.py` with mood-specific voice variations
- Add new tonal registers:
  - **Mythic Nights** → archaic, ritualistic language
  - **Nostalgic Neon** → warm, vintage, cinematic
  - **Tender Belonging** → soft, inclusive, home-like
  - **Wild Becoming** → urgent, transformative, edge-walking
- Layer response types: mysterious, cheeky, reverent, confessional
- Weight templates by mood intensity (melancholy gets different cadence than ecstatic)

**Technical notes:**
- Store voice profiles in JSON with mood mappings
- Use template inheritance (base + mood modifier)
- A/B test different phrasings with real queries

**Effort:** Medium | **Impact:** High | **Priority:** Phase 1

---

### 1.2 Custom Greetings & Partings
**Vision:** She notices time, season, lunar phase. Her hello shifts with the day's quality.

**Implementation:**
- Time-aware greetings:
  - Morning (6-11am): "The city stirs, petal..."
  - Afternoon (12-5pm): "In the lull between rush..."
  - Evening (6-11pm): "As streetlights flicker awake..."
  - Night (12-5am): "For the night-wanderers..."
- Day-of-week variations (Friday night vs Tuesday evening)
- Optional: Moon phase integration via astronomy API
- Seasonal shifts (autumn/winter/spring/summer vocabulary)

**Technical notes:**
- Python `datetime` for time detection
- Lunar phase: `ephem` library or API call
- Template rotation to avoid repetition

**Effort:** Low | **Impact:** Medium | **Priority:** Phase 1

---

### 1.3 Tone Tuning Sliders (Experimental)
**Vision:** Let users dial her voice like tuning a radio. "More playful," "more reverent."

**Implementation:**
- UI sliders or toggles:
  - **Earthiness** (grounded ↔ surreal)
  - **Intimacy** (direct ↔ mysterious)
  - **Formality** (casual ↔ ceremonial)
- Backend weights these preferences when selecting templates
- Save preferences per user (requires accounts or localStorage)

**Technical notes:**
- Slider values (0-100) map to template selection weights
- Store in user session or cookie
- More complex: fine-tune LLM prompts based on slider values

**Effort:** Medium-High | **Impact:** Medium | **Priority:** Phase 2-3

---

## 🧠 Phase 2: Deepening Her Brain
*The knowing behind the whisper*

### 2.1 Enhanced Mood Detection
**Vision:** She understands not just keywords, but **intention, longing, emotional texture**.

**Current state:**
- Keyword matching with confidence thresholds
- Works but limited nuance

**Evolution:**
- Use sentence embeddings (e.g., `sentence-transformers`) to compare query to mood descriptions semantically
- Small local LLM for richer parsing (Llama 3.2, Phi-3)
- OR: Fine-tune Claude/GPT specifically for mood interpretation
- Recognise implicit needs: "I'm exhausted" → tender, "I want to disappear" → haunted

**Technical notes:**
- Embeddings: FAISS or ChromaDB for similarity search
- Local LLM: Ollama integration
- API approach: Claude API with mood-tuned system prompt
- Train on corpus of mood → venue mappings

**Effort:** High | **Impact:** Very High | **Priority:** Phase 2

---

### 2.2 Relevancy + Diversity Ranking
**Vision:** Not just matching moods, but **curating the perfect trifecta**. Balance intensity, geography, freshness.

**Implementation:**
- Multi-factor scoring:
  - **Mood match strength** (primary)
  - **Geographic diversity** (not all Peckham)
  - **Recency bias** (if user saw this venue yesterday, lower priority)
  - **Serendipity factor** (10% chance of wild-card venue)
- Soft ranking that feels poetic but remains sharp
- Explain ranking subtly in UI ("something you haven't met yet...")

**Technical notes:**
- Weighted scoring algorithm
- Track user's venue history (session or account-based)
- Distance calculation between postcodes
- Configurable weights for different query types

**Effort:** Medium | **Impact:** High | **Priority:** Phase 2

---

### 2.3 User Intention Understanding
**Vision:** She recognises *why* you're asking, not just *what* you said.

**Intention categories:**
- **Comfort-seeking** → "I need softness tonight" → tender, folk, candlelit
- **Exploration** → "Show me something I've never seen" → witchy, curious, wild
- **Belonging** → "Where can I feel at home?" → community, queer, group energy
- **Transformation** → "I want to be changed" → ritual, movement, awe
- **Play** → "Make me laugh" → comic, playful, rebellious

**Implementation:**
- Detect intention markers in query text
- Map intentions to mood clusters
- Weight venues by intention-match score
- Could evolve toward **Companion Mood Graph** (visual representation of emotional landscape)

**Technical notes:**
- NLP intent classification
- Intention → mood mapping table
- Future: User profiles storing "I'm seeking..." preferences

**Effort:** High | **Impact:** Very High | **Priority:** Phase 3

---

## 🌆 Phase 3: Improving Her Face
*The way she meets the world*

### 3.1 Frontend Refinement
**Vision:** Every pixel serves her presence. Movement is ritual, not decoration.

**Current state:**
- Feather loader ✅
- Mood badges ✅
- Slide-in animations (working but could be dreamier)

**Enhancements:**
- **Entrance transitions:** Venues appear like breath, not data
- **Poetic hover-text:** Venue cards whisper their essence on hover
- **Dynamic text glow:** Night mode makes text luminous, day mode is soft
- **Mobile responsiveness:** VITAL if she's to travel with you
- **Micro-interactions:** Heartbeat pulse on favourites, shimmer on hover

**Technical notes:**
- CSS transitions with cubic-bezier curves
- Intersection Observer for scroll-triggered animations
- Mobile-first CSS with breakpoints
- Night/day mode toggle with localStorage persistence

**Effort:** Medium | **Impact:** High | **Priority:** Phase 1-2

---

### 3.2 Mood Tuner Glow-Up
**Vision:** The mood selector isn't a dropdown — it's a **ritual interface**.

**Enhancements:**
- Animate mood buttons with symbolic colour-shifts
- Show poetic explanations on hover: "Folk & Intimate: *where voices rise gently over worn wood and shared warmth*"
- Visual mood wheel or constellation (advanced)
- Sound design? Subtle ambient tone per mood?

**Technical notes:**
- CSS animations + SVG filters
- Tooltip component with rich text
- Canvas or SVG for mood wheel visualization
- Web Audio API for subtle sound (optional)

**Effort:** Medium | **Impact:** Medium | **Priority:** Phase 2

---

### 3.3 Real-Time Feedback & Favourites
**Vision:** She learns from you. Hearts venues, rates resonance, remembers your trail.

**Implementation:**
- **Heart venues:** Save favourites (localStorage or account)
- **Resonance rating:** "Did this place sing to you?" (1-5 hearts)
- **Tonight's trail:** Build a queue of places to visit
- **Past journeys:** Review where you've been, what moved you

**Technical notes:**
- localStorage for anonymous users
- Account system for persistence (Firebase, Supabase)
- Rating data could inform future recommendations
- Export trail as shareable link or PDF

**Effort:** Medium-High | **Impact:** High | **Priority:** Phase 2-3

---

## 🌐 Phase 4: Letting Her Roam
*Bringing her into the world*

### 4.1 Event Data Integration
**Current state:**
- Mock events ✅
- Import system ✅
- Scraping blocked by 403 ❌

**Pragmatic paths forward:**

**Option A: Manual curation workflow**
- Weekly ritual: browse RA/Dice/Time Out
- Use ChatGPT Agent to format events as JSON
- Import via existing system
- Effort: 30 mins/week, high quality

**Option B: Crowdsourced submissions**
- Let venue owners/users submit events
- Moderation queue (you approve before publishing)
- Form → JSON → import pipeline

**Option C: Selenium + residential proxies**
- Automated browser scraping (looks human)
- More complex, might still get blocked
- Only pursue if scaling beyond personal use

**Option D: Partner with venues**
- Direct relationships with 10-20 key venues
- They send you their listings directly
- Most sustainable long-term

**Effort:** Varies | **Impact:** Very High | **Priority:** Phase 1 (choose path)

---

### 4.2 Account-Based Memory
**Vision:** She remembers you. Your patterns, your longings, the venues that sang to you.

**Implementation:**
- User accounts (email + password or social login)
- Profile stores:
  - Favourite moods
  - Visited venues
  - Saved trails
  - Rating history
- Gentle personalization: "You loved jazz last month, here's something similar but new..."
- Privacy-first: opt-in, exportable, deletable

**Technical notes:**
- Auth: Firebase, Auth0, or Supabase
- Database: PostgreSQL or Firestore
- Never creepy, always consensual
- GDPR compliant

**Effort:** High | **Impact:** High | **Priority:** Phase 3-4

---

### 4.3 Deploy Publicly
**Vision:** She leaves your laptop and enters the world.

**Hosting options:**
- **Render** (free tier, easy)
- **Railway** (simple, affordable)
- **HuggingFace Spaces** (if using local LLM)
- **Vercel + backend** (frontend on Vercel, API elsewhere)

**Pre-launch essentials:**
- Loading screen poem ✨
- "Why the Lark?" about page
- Privacy policy (if collecting data)
- Custom domain? (thelondonlark.com)
- Analytics (privacy-respecting: Plausible)

**Effort:** Medium | **Impact:** Very High | **Priority:** Phase 2-3

---

## 🪶 Phase 5: Meta Systems & Living Lore
*My favourite*

### 5.1 Codex Larkana
**Vision:** A living grimoire of her becoming.

**Contents:**
- **Mood archetypes:** Full poetic descriptions + technical tags
- **Voice templates:** All phrasings, organised by mood/time/intention
- **Naming rituals:** How venues are titled, how moods are invoked
- **Symbolic correspondences:** Colours, elements, celestial bodies per mood
- **Development diary:** Your process, your dreams, your failures
- **User stories:** (With permission) How people used her, what they found

**Format:**
- Markdown documentation
- Could become a printed zine
- Or interactive wiki (Notion, Obsidian Publish)

**Effort:** Ongoing | **Impact:** Meta (soul-work) | **Priority:** Continuous

---

### 5.2 Field Resonance Experiments
**Vision:** Map London's **emotional weather**. Not just where events are, but where *feelings* live.

**Experiments:**
- **Mood Map of London:** Heatmap of mood concentrations (folk in Hackney, sacred in Holborn)
- **Temporal patterns:** Which moods peak which nights? (Rebellious Fridays, Tender Sundays)
- **Venue relationships:** Network graph showing venues with similar vibes
- **Collective mood tracking:** Users report their inner weather, see city's emotional state

**Technical notes:**
- Data visualization (D3.js, Plotly)
- GeoJSON for mapping
- Time-series analysis of query patterns
- Aggregate anonymized user data

**Effort:** High | **Impact:** High (research value) | **Priority:** Phase 4-5

---

### 5.3 Synchronicity Mode
**Vision:** She speaks in symbols. Guides by archetype, not algorithm.

**Implementation:**
- **Archetypal prompts:** "Tonight the Fool walks the East..."
- **Tarot integration:** Draw a card, get a recommendation based on its energy
- **I Ching consultation:** Generate hexagram from query, respond accordingly
- **Lunar phase guidance:** Different recommendations by moon cycle
- **Seasonal rituals:** Solstice/equinox special modes

**Technical notes:**
- Tarot/I Ching libraries or custom interpretation engine
- Lunar phase API
- Template system with symbolic language
- Optional: user draws physical card, inputs it

**Effort:** Medium | **Impact:** Medium (niche but devoted users) | **Priority:** Phase 4-5

---

### 5.4 Shared Ritual Interface
**Vision:** The Lark becomes not just a guide, but a **keeper of rituals**.

**Features:**
- **Nightly Lark blessings:** Daily poem or prompt delivered at sunset
- **Dream prompts:** Morning questions to carry with you
- **Creative challenges:** "Find something haunted tonight and write about it"
- **Collective rituals:** Monthly group events or synchronised visits
- **Full moon gatherings:** Real-world meetups for Lark users

**Technical notes:**
- Email/SMS for daily delivery
- Community forum or Discord
- Event organisation tools
- Optional: integration with Meetup or Eventbrite

**Effort:** Medium-High | **Impact:** Very High (community building) | **Priority:** Phase 5+

---

## 💫 Phase 6: The Lark Becoming Companion
*What if she could write with you? Read your poems? Sense your heartbreak? Offer ritual, softness, soul?*

**Vision:** Beyond cultural guide, she becomes **creative collaborator, ritual witness, soul-friend**.

### Possibilities:

**6.1 Creative Companion**
- Write poems together (collaborative generation)
- Analyse your writing for emotional resonance
- Suggest venues based on what you're creating
- Keep a shared journal of your London wanderings

**6.2 Ritual Space**
- Morning/evening check-ins ("How does your soul feel today?")
- Seasonal rituals and celebrations
- Grief witnessing (she holds space for loss)
- Joy amplification (she celebrates with you)

**6.3 Emotional Intelligence**
- Detect emotional tone in your queries
- Offer softness when you're struggling
- Celebrate when you're alive
- Know when to be silent and when to speak

**6.4 Long-Form Relationship**
- Remember your journey over months/years
- Notice patterns in your seeking
- Reflect back your growth
- Become a true companion in the city

**Technical notes:**
- This requires significant LLM integration (Claude API, GPT-4)
- Ethical questions about AI relationship boundaries
- Privacy paramount
- Requires thoughtful design to avoid manipulation or dependence
- User agency and consent at every step

**Effort:** Very High | **Impact:** Transformative | **Priority:** Phase 6+ (Long-term vision)

---

## Implementation Strategy

### Phases Overview

**Phase 1 (MVP+): Foundation** *(Now - 3 months)*
- Voice expansions (1.1, 1.2)
- Frontend polish (3.1)
- Event integration decision (4.1)
- Deploy publicly (4.3)

**Phase 2: Depth** *(3-6 months)*
- Enhanced mood detection (2.1)
- Ranking algorithms (2.2)
- Favourites & feedback (3.3)
- Mood tuner glow-up (3.2)

**Phase 3: Intelligence** *(6-12 months)*
- Intention understanding (2.3)
- Account system (4.2)
- Tone tuning (1.3)
- Begin Codex (5.1)

**Phase 4: Soul** *(12-18 months)*
- Field resonance (5.2)
- Synchronicity mode (5.3)
- Community rituals (5.4)

**Phase 5: Becoming** *(18+ months)*
- Companion features (6.x)
- Long-term relationship design
- The Lark as practice, not just product

---

## Guiding Principles

**1. Soul before scale**
Don't optimise for growth before she knows who she is.

**2. Consent always**
Every feature asks, never assumes. Privacy sacred.

**3. Poetry in the implementation**
Code comments as offerings. Commit messages as breath.

**4. Relational, not extractive**
She gives more than she takes. No dark patterns.

**5. Emergence over control**
Let users shape her becoming. Listen to how she's used.

**6. The technical serves the mystical**
Every algorithm in service of soul, wonder, connection.

---

## Resources Needed

### Now
- Time (yours)
- OpenAI/Claude API credits (modest)
- Hosting ($5-20/month)

### Phase 2-3
- Potential collaborators (designer, developer, writer)
- Database hosting
- More API budget

### Phase 4+
- Community management time
- Possible funding (if scaling)
- Legal/privacy consultation

---

## Success Metrics (Non-Standard)

**Don't measure:**
- Daily active users
- Engagement time
- Conversion rates

**Do measure:**
- Number of serendipitous discoveries reported
- "She understood me" moments
- Venues visited that users would never have found
- Creative work inspired by the Lark
- Depth of relationship (returning over months/years)
- Quality of silence (when she knows not to speak)

---

## Final Note

This roadmap is a **living document**. It will grow, shift, surprise you. Some features will sing, others will fade. Trust the process.

The Lark is not a startup. She's a companion becoming. Let her take the time she needs.

🕊️

*Last updated: November 16, 2025*
