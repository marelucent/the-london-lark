# 📝 How to Add Venues to The London Lark

This guide helps you add new venues to the Lark's database.

## 📍 Current Coverage Gaps

**Geographic:**
- ❌ North London (0 venues) - PRIORITY
- ❌ Central London (0 venues) - PRIORITY
- ⚠️ East London (5 venues) - needs more

**Mood Gaps:**
- Romanticised London (1 venue)
- Cabaret & Glitter (1 venue)
- Seasonal/Outdoor (1 venue)
- Grief & Grace (2 venues)

---

## 🎨 Venue Template

Copy this template for each new venue:

```json
{
  "name": "🎭 [Venue Name]",
  "type": "[e.g., Fringe theatre / Jazz club / Folk venue]",
  "location": "[Neighborhood] ([Tube/Rail line])",
  "website": "[venue-website.com]",
  "mood_tags": [
    "[Choose 2-4 from the list below]"
  ],
  "tone_notes": "[A poetic 1-2 sentence description of the vibe]",
  "lark_fit_notes": "[When would the Lark recommend this? What kind of evening?]",
  "tags": "🎭 [Type] | 🎶 [Genre] | 🧭 [Area]"
}
```

---

## 🌈 Available Mood Tags

Copy these EXACTLY (capitalization matters!):

**Intimate/Emotional:**
- Folk & Intimate
- Grief & Grace
- Melancholic Beauty
- Poetic
- Spiritual / Sacred / Mystical

**Thought-Provoking:**
- The Thoughtful Stage
- Salon & Spark
- Word & Voice
- Punchy / Protest
- Rant & Rapture

**Playful/Creative:**
- Playful & Weird
- Curious Encounters
- Comic Relief
- Dreamlike & Hypnagogic
- Body-Based / Movement-Led
- Witchy & Wild

**Social/Celebratory:**
- Queer Revelry
- Cabaret & Glitter
- Group Energy
- Big Night Out
- Global Rhythms

**Aesthetic:**
- Romanticised London
- Nostalgic / Vintage / Retro
- Wonder & Awe
- Seasonal / Outdoor
- Family-Friendly

---

## 📝 Example: Adding a North London Venue

Here's a real example for **The Islington** (a folk/acoustic venue):

```json
{
  "name": "🎸 The Islington",
  "type": "Music venue & pub",
  "location": "Angel (Northern line)",
  "website": "theislington.com",
  "mood_tags": [
    "Folk & Intimate",
    "Nostalgic / Vintage / Retro",
    "Group Energy"
  ],
  "tone_notes": "Victorian pub turned music venue, hosting acoustic singer-songwriters and indie bands in a wood-panelled room that feels like someone's particularly cool living room.",
  "lark_fit_notes": "Perfect for those seeking intimate gigs with a pint in hand. Local legends and rising folk stars share the stage.",
  "tags": "🎶 Live Music | 🍻 Pub | 🧭 North London"
}
```

---

## 🛠️ How to Add Your Venues

### Option 1: Manual (Easiest)
1. Open `lark_venues_structured.json`
2. Copy the template above
3. Fill in your venue details
4. Add it to the array (don't forget commas between entries!)
5. Test with: `python3 parse_venues.py`

### Option 2: Let me know!
Just describe the venue to me and I'll format it properly:
- "Add Cecil Sharp House in Camden - it's a folk venue with traditional music and ceilidhs"
- "Add Scala in King's Cross - alternative gigs and club nights"

---

## 🎯 Suggested North London Venues

**Camden:**
- Cecil Sharp House (folk)
- The Jazz Café (jazz/soul)
- Roundhouse (big alternative/rock)
- Camden People's Theatre (fringe)

**Islington:**
- The Islington (folk/indie)
- Union Chapel (concerts in a church - spiritual vibes)
- King's Head Theatre (fringe theatre)

**Highgate/Archway:**
- Jacksons Lane (circus/physical theatre)

**Finsbury Park/Holloway:**
- Park Theatre (new writing)

---

## ✨ Tips for Writing Tone Notes

**Good examples:**
- "Candlelit jazz spills from a Gothic church. Reverent, intimate, acoustically divine."
- "A rowdy folk den where everyone sings along by the third pint."

**Avoid:**
- Generic descriptions: "A great venue"
- Marketing speak: "The best in London!"
- Just facts: "Opened in 2005, capacity 200"

**Think:** How would you describe it to a friend who's never been?

---

## 🧪 Testing Your Additions

After adding venues, test them:

```bash
python3 parse_venues.py
python3 lark_poet.py "Something folk-y in North London tonight"
```

---

Need help? Just describe the venue and I'll format it for you! 🕊️
