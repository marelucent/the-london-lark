# 🕊️ The London Lark - Venue Data Standards
*Version 1.0 - Created: 25 November 2025*

---

## PURPOSE

This document serves three functions:
1. **Audit Checklist** - Standards for reviewing existing venues
2. **Entry Guidelines** - Rules for adding new venues
3. **User Submission Form** - Framework for "Recommend a Venue" feature

**Philosophy:** Clean, consistent data = simple, reliable search = better user experience

---

## REQUIRED FIELDS

Every venue MUST have these fields:

### 1. NAME
**Format:** Official venue name as it appears publicly

**Rules:**
- Use proper capitalization
- Include full name (don't abbreviate)
- No extra punctuation or formatting

**Examples:**
- ✅ "Pink Singers"
- ✅ "F*Choir"
- ✅ "The London Library"
- ❌ "pink singers" (wrong capitalization)
- ❌ "LRB" (abbreviated, should be "London Review Bookshop")

---

### 2. LOCATION
**Format:** Specific neighborhood name OR "Various London venues" for touring

**Rules:**
- Use ONE specific neighborhood name (not compound locations)
- Choose from 114 approved neighborhoods (see Appendix A)
- If venue has multiple locations, choose PRIMARY location
- If truly touring/various: "Various London venues"
- Include borough/area in parentheses only if needed for clarity

**Examples:**
- ✅ "Peckham"
- ✅ "Shoreditch"
- ✅ "Ealing"
- ✅ "Hackney" (not "Hackney (E5)")
- ✅ "Various London venues" (for touring shows)
- ❌ "Hackney & East London venues (varies)" (too vague)
- ❌ "South East London (various cosy spaces)" (not specific enough)
- ❌ "Shepherd's Bush, West London" (pick one: "Shepherd's Bush")

**Special Cases:**
- Touring venues: "Various London venues"
- Multiple permanent locations: Choose where they started/are best known
- Pop-ups: Use where they're currently running

---

### 3. MOODS
**Format:** Array of 2-4 mood tags that match mood_index.json EXACTLY

**Rules:**
- Must match mood_index.json spelling/capitalization exactly
- Choose 2-4 moods (not just 1, not more than 4)
- Select moods that genuinely match the venue's vibe
- Check mood_index.json for approved moods (currently 30)

**Current Approved Moods:**
- Folk & Intimate
- Queer Revelry
- Dreamlike & Hypnagogic
- Wonder & Awe
- Grief & Grace
- Playful & Weird
- Punchy / Protest
- Poetic
- The Thoughtful Stage
- Something I Wouldn't Normally Pick
- Cabaret & Glitter
- Late-Night Lark
- Comic Relief
- Group Energy
- Word & Voice
- Salon & Spark
- Rant & Rapture
- Big Night Out
- Global Rhythms
- Romanticised London
- Nostalgic / Vintage / Retro
- Spiritual / Sacred / Mystical
- Body-Based / Movement-Led
- Melancholic Beauty
- Curious Encounters
- Seasonal / Outdoor
- Witchy & Wild
- Family-Friendly
- Contemplative & Meditative
- Experimental / Avant-garde

**Examples:**
- ✅ ["Grief & Grace", "Spiritual / Sacred / Mystical", "Folk & Intimate"]
- ✅ ["Queer Revelry", "Group Energy", "Word & Voice"]
- ❌ ["grief and grace"] (wrong capitalization/spelling)
- ❌ ["Grief & Grace"] (only 1 mood - need 2-4)
- ❌ ["Folk", "Intimate", "Cozy", "Warm", "Gentle"] (too many, use "Folk & Intimate")

---

### 4. GENRES
**Format:** Array of 3-5 specific genre/category keywords

**Rules:**
- Use standardized genre keywords (see Appendix B for approved list)
- Choose 3-5 genres (not too few, not too many)
- Be specific but not redundant
- Include venue type + content type

**Approved Genre Keywords (partial list):**

**Venue Types:**
- theatre, music venue, gallery, bookshop, cinema, cafe, pub, club, community centre, church, library, studio, garden

**Music Genres:**
- jazz, folk, electronic, techno, indie, punk, reggae, soul, classical, world music, hip-hop, house, experimental, choir, singing circle

**Performance:**
- comedy, cabaret, drag, burlesque, dance, contemporary dance, physical theatre, scratch night, work-in-progress, spoken word, poetry

**Activities:**
- workshop, class, ritual, ceremony, grief circle, death cafe, book club, discussion, salon, film screening

**Themes:**
- queer, LGBTQ+, community, activist, radical, witchy, mystical, therapeutic, grief support, wellness

**Examples:**
- ✅ ["LGBT+ community choir", "choral concerts"]
- ✅ ["grief circles", "community ritual", "embodied grief tending"]
- ✅ ["scratch night", "new writing", "performance experiments"]
- ❌ ["music"] (too vague - what kind?)
- ❌ ["theatre venue that does experimental work in the round"] (too wordy - use ["theatre", "experimental", "in-the-round"])

---

### 5. URL
**Format:** Full website URL starting with https://

**Rules:**
- Must be complete URL (include https://)
- Link to venue's official website or primary online presence
- If no official site, use: Facebook page, Instagram, Eventbrite, or booking platform

**Examples:**
- ✅ "https://www.pinksingers.co.uk/"
- ✅ "https://fchoir.com/about/"
- ✅ "https://www.instagram.com/thelossproject1/" (if no website)
- ❌ "pinksingers.co.uk" (missing https://)
- ❌ "www.pinksingers.co.uk" (missing https://)

---

### 6. BLURB
**Format:** 2-4 sentences, poetic but practical, written in the Lark's voice

**Rules:**
- Length: 50-120 words (2-4 sentences)
- Voice: Poetic, tender, specific, evocative
- Include: What happens there, what it feels like, who it's for
- Use first-person ("I") sparingly and naturally
- Incorporate sensory details
- End with a gentle invitation or observation
- NO generic placeholders ("An experience beyond words")

**Voice Guidelines:**
- Poetic but not purple prose
- Specific details over vague feelings
- Metaphor is welcome but not required
- Can use birdsong lexicon phrases naturally
- Address reader as "petal" if it feels right

**Examples:**

✅ GOOD:
"In Kilburn, Healing Choir treats song as a kind of shared medicine: free to attend, open to all abilities, rooted in breath, movement and communal vocalisation. Sessions are more about how it feels in the body than how it sounds from the back row. If life has left you hoarse and you're looking for a room that will simply let you exhale and hum, this one waits with open arms."

✅ GOOD:
"F*Choir is less hymn book, more spell book: a 60-plus strong, all-genders choir singing about gender, sexuality, freedom and rage. Rehearsals are sweaty, laughing, political; performance nights feel like a gig crossed with a ritual, a cry soft as wingbeat and sometimes as loud as a siren. Ideal for the petal who wants their harmonies with teeth, their choruses circling closer to something true."

❌ BAD:
"A great venue for music lovers. Check it out!" (too generic, no soul)

❌ BAD:
"An experience beyond words where magic happens and dreams come true." (vague placeholder language)

❌ BAD:
"I absolutely adore this venue and think you will too! It's simply divine and offers the most extraordinary performances you've ever seen in your entire life, guaranteed to transform you completely!" (over-the-top, not grounded)

---

### 7. LAST_VERIFIED
**Format:** Date in YYYY-MM-DD format

**Rules:**
- Must be recent (within last 3 months for new entries)
- Update when venue details change
- Use format: "YYYY-MM-DD"

**Examples:**
- ✅ "2025-11-25"
- ✅ "2025-11-20"
- ❌ "November 25, 2025" (wrong format)
- ❌ "25/11/2025" (wrong format)

---

## OPTIONAL FIELDS

These enhance the venue but aren't required:

### NOTES
**Purpose:** Additional context, temporary info, warnings

**When to use:**
- Venue temporarily relocated
- Seasonal/limited operation
- Special booking requirements
- Accessibility considerations

**Examples:**
- "Currently running ground-floor pop-up while roof garden renovates (reopening spring 2026)"
- "Books may be closed to new singers at times"
- "Summer only, must book ahead"

### TYPICAL_START_TIME
**Purpose:** When events typically begin (for time-aware features)

**Format:** "HH:MM" (24-hour) or descriptive

**Examples:**
- "19:00"
- "20:30"
- "varies by event"

### PRICE
**Purpose:** Cost information

**Format:** Free text, but keep concise

**Examples:**
- "Free"
- "£5-15"
- "Pay what you can"
- "£20 advance, £25 door"

### ACCESSIBILITY
**Purpose:** Important access info

**Format:** Array of accessibility features

**Examples:**
- ["step-free access", "wheelchair accessible", "gender-neutral toilets"]
- ["quiet space available", "sensory-friendly"]
- ["BSL interpreted events"]

---

## APPENDIX A: APPROVED NEIGHBORHOODS

**East London (21):**
Hackney, Shoreditch, Dalston, Bethnal Green, Whitechapel, Stratford, Hackney Wick, Limehouse, Bow, Mile End, Homerton, Haggerston, Hoxton, Walthamstow, Leyton, Stepney, Poplar, Canning Town, Barking, Fish Island, Tower Hamlets

**South London (28):**
Peckham, Brixton, Camberwell, Bermondsey, Deptford, Lewisham, Catford, Elephant & Castle, New Cross, Nunhead, Dulwich, Streatham, Battersea, Clapham, Vauxhall, Kennington, Stockwell, South Norwood, Crystal Palace, Forest Hill, Greenwich, Woolwich, Eltham, Croydon, Sutton, Merton, Tooting, Balham

**North London (28):**
Camden, Islington, Highgate, Finsbury Park, Holloway, Crouch End, Finchley, Wood Green, Tottenham, Kentish Town, King's Cross, St Pancras, Hampstead, Tufnell Park, Archway, Highbury, Stoke Newington, Manor House, Southgate, Barnet, Enfield, Muswell Hill, Chalk Farm, Belsize Park, Gospel Oak, Primrose Hill, Queens Wood, Barnsbury

**West London (20):**
Ealing, Chiswick, Acton, Richmond, Hammersmith, Shepherd's Bush, Kilburn, Notting Hill, Kensington, West Kensington, Brentford, Hanwell, Hounslow, Twickenham, Kew, Park Royal, East Sheen, Fulham, Chelsea, Earl's Court

**Central London (17):**
Soho, Covent Garden, Holborn, King's Cross, Bloomsbury, Fitzrovia, Marylebone, Clerkenwell, Farringdon, The Strand, Trafalgar Square, Westminster, Victoria, City of London, Barbican, St James's, Leicester Square

---

## APPENDIX B: APPROVED GENRE KEYWORDS

### Venue Types
theatre, music venue, gallery, art space, bookshop, bookshop bar, cinema, cafe, pub, club, nightclub, community centre, church, chapel, library, reading room, studio, garden, outdoor space, warehouse, railway arch, basement venue

### Music Genres
jazz, folk, acoustic, electronic, techno, house, indie, punk, rock, reggae, soul, R&B, classical, opera, choral, world music, hip-hop, experimental, ambient, drone, improvised, sacred harp, shape-note, choir, singing circle, community choir, queer choir

### Performance Types
theatre, contemporary theatre, physical theatre, new writing, scratch night, work-in-progress, comedy, stand-up, improv, cabaret, drag, burlesque, drag king, drag queen, variety, circus, dance, contemporary dance, ballet, movement, spoken word, poetry, storytelling, performance art

### Activities & Events
workshop, class, course, ritual, ceremony, grief circle, grief support, death cafe, book club, reading group, discussion, salon, talk, lecture, film screening, exhibition, open mic, jam session, social dance, ceilidh

### Themes & Communities
queer, LGBTQ+, LGBT+, gay, lesbian, trans, non-binary, community, grassroots, activist, radical, political, protest, witchy, mystical, spiritual, pagan, therapeutic, wellness, grief tending, embodied, somatic, feminist, inclusive, accessible, family-friendly, intergenerational, diaspora, refugee, migrant, Black-led, POC-led

### Special Categories
24-hour, late-night, all-night, members-only, private, free entry, pay-what-you-can, donation-based, co-working, study space, touring, pop-up, seasonal, outdoor, indoor

---

## AUDIT CHECKLIST

Use this when reviewing existing venues:

**For each venue, check:**
- [ ] Name: Properly capitalized, official name
- [ ] Location: Single neighborhood from approved list OR "Various London venues"
- [ ] Moods: 2-4 moods, match mood_index.json exactly
- [ ] Genres: 3-5 genres from approved list
- [ ] URL: Complete with https://
- [ ] Blurb: 50-120 words, poetic, specific, in Lark's voice
- [ ] Last_verified: Recent date in YYYY-MM-DD format
- [ ] No placeholder language ("An experience beyond words")
- [ ] No duplicate entries

**Flag for review if:**
- Location is vague or compound
- Only 1 mood or more than 4 moods
- Genres too vague or too numerous
- Blurb is generic or placeholder
- Last verified more than 6 months ago
- Venue might be closed/moved

---

## "RECOMMEND A VENUE" FORM STRUCTURE

When building the user submission form, use these standards:

**Required Fields:**
- Venue Name (text input)
- Location (dropdown: approved neighborhoods + "Various/touring")
- Website/Social Media (URL input with https:// prefix)
- Brief Description (textarea, 200 char max, explain in plain language)

**Optional Fields:**
- Your suggested moods (multi-select from approved list)
- Your suggested genres (multi-select from approved list)
- Why you love it (textarea, for creating poetic blurb)
- Your email (for follow-up questions)

**Validation Rules:**
- Name required, max 100 chars
- Location required (must select from dropdown)
- URL required, must start with http:// or https://
- Description required, 50-200 chars
- At least 1 mood suggested
- At least 2 genres suggested

**Submission Flow:**
1. User submits form
2. Goes to moderation queue
3. Catherine/team reviews and enhances
4. Writes poetic blurb in Lark's voice
5. Verifies venue is active
6. Adds to database with proper standards

---

## MAINTENANCE

**Regular Reviews:**
- Quarterly: Spot-check 20 random venues for accuracy
- Bi-annually: Full database audit
- As needed: Update when venues close/move

**When to Update Venue:**
- Venue moves location
- Venue changes name
- Programming significantly changes
- Venue closes (mark as closed, don't delete)
- New information becomes available

---

*"Clean data is an act of care. Every standardized field makes the Lark's whispers more reliable."*

🕊️✨
