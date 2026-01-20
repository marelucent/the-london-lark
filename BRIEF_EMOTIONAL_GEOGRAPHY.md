# Brief for CC: Emotional Geography — Smarter Card Drawing

**Date:** 20 January 2025  
**Task:** Implement adjacency-based card drawing and need-based care pathways  
**Priority:** Medium-High — this transforms how she thinks  
**Reference:** `LARK_EMOTIONAL_GEOGRAPHY.md` (attached)

---

## The Big Picture

Right now, when someone searches "witchy", they get 3 cards from Witchy & Wild. Same arcana, same energy, no variety.

We want her to be smarter:
- **Give them what they asked for** (primary)
- **Plus something nearby** (adjacent)
- **And in care pathways, draw from what they actually need** (therapeutic clusters)

---

## What Needs to Change

### 1. Standard Search Logic

**Current:**
```
Search "witchy" → 3 random venues from Witchy & Wild
```

**New:**
```
Search "witchy" → 
  Card 1: Witchy & Wild venue (primary)
  Card 2: Witchy & Wild venue (primary)
  Card 3: Adjacent arcana venue (from Moon, Death, or Hierophant)
```

The third card comes from a **neighbouring arcana** based on the Tarot Adjacency Map.

---

### 2. Tarot Adjacency Map

Store this mapping (or put it in a config file):

```python
TAROT_ADJACENCY = {
    "Playful & Weird": ["Curious Encounters", "Cabaret & Glitter", "Big Night Out"],
    "Curious Encounters": ["Playful & Weird", "Word & Voice", "Rant & Rapture"],
    "Witchy & Wild": ["Nostalgic / Vintage / Retro", "Grief & Grace", "Spiritual / Sacred / Mystical"],
    "Folk & Intimate": ["Contemplative & Meditative", "Group Energy", "Word & Voice"],
    "The Thoughtful Stage": ["Rant & Rapture", "Curious Encounters", "Spiritual / Sacred / Mystical"],
    "Spiritual / Sacred / Mystical": ["Witchy & Wild", "The Thoughtful Stage", "Wonder & Awe"],
    "Cabaret & Glitter": ["Playful & Weird", "Comic Relief", "Folk & Intimate"],
    "Big Night Out": ["Playful & Weird", "Cabaret & Glitter", "Late-Night Lark"],
    "Punchy / Protest": ["Rant & Rapture", "Body-Based / Movement-Led", "Melancholic Beauty"],
    "Contemplative & Meditative": ["Grief & Grace", "Folk & Intimate", "Nostalgic / Vintage / Retro"],
    "Global Rhythms": ["Wonder & Awe", "Group Energy", "Word & Voice"],
    "Rant & Rapture": ["Punchy / Protest", "The Thoughtful Stage", "Curious Encounters"],
    "Body-Based / Movement-Led": ["Grief & Grace", "Punchy / Protest", "Melancholic Beauty"],
    "Grief & Grace": ["Contemplative & Meditative", "Body-Based / Movement-Led", "Nostalgic / Vintage / Retro"],
    "Word & Voice": ["Folk & Intimate", "Curious Encounters", "Global Rhythms"],
    "Late-Night Lark": ["Big Night Out", "Melancholic Beauty", "Cabaret & Glitter"],
    "Melancholic Beauty": ["Late-Night Lark", "Grief & Grace", "Body-Based / Movement-Led"],
    "Wonder & Awe": ["Nostalgic / Vintage / Retro", "Global Rhythms", "Spiritual / Sacred / Mystical"],
    "Nostalgic / Vintage / Retro": ["Wonder & Awe", "Grief & Grace", "Witchy & Wild"],
    "Comic Relief": ["Cabaret & Glitter", "Group Energy", "Playful & Weird"],
    "Group Energy": ["Folk & Intimate", "Comic Relief", "Global Rhythms"],
    "Queer Revelry": ["Comic Relief", "Group Energy", "Big Night Out"],
    "Romanticised London": ["Wonder & Awe", "Queer Revelry", "Playful & Weird"]
}
```

When drawing the adjacent card, pick randomly from the primary arcana's neighbours.

---

### 3. "I Don't Know" / Surprise Me Detection

If user types something like:
- "I don't know"
- "surprise me"
- "not sure"
- "anything"
- just hits enter with empty/placeholder text

**New response:**
```
Card 1: Random arcana (fate chooses)
Card 2: Adjacent to Card 1
Card 3: Adjacent to Card 1 (different neighbour)
```

Or offer **The Reading Menu** (future feature):
> *"Then let's see what the cards say... How shall I lay them out?"*
> - The Single (1 card, pure fate)
> - The Triad (3 cards, coherent journey)
> - The Spread (5 cards, a full evening)
> - The Shuffle (6-8 random, tap to reveal)

---

### 4. Care Pathway Logic (Tier 2/3)

**Current:** Safety tier triggers → show venues from detected mood + support resources

**New:** Safety tier triggers → draw from **Shared Need Clusters** instead of mood-matching

```python
SHARED_NEEDS = {
    "to_be_held": ["Folk & Intimate", "Group Energy", "Word & Voice"],
    "to_move_through": ["Body-Based / Movement-Led", "Punchy / Protest", "Rant & Rapture"],
    "to_rest": ["Contemplative & Meditative", "Grief & Grace", "Nostalgic / Vintage / Retro"],
    "to_feel_joy": ["Comic Relief", "Cabaret & Glitter", "Playful & Weird"],
    "to_witness_beauty": ["Wonder & Awe", "Melancholic Beauty", "Romanticised London"],
    "to_touch_sacred": ["Spiritual / Sacred / Mystical", "Witchy & Wild", "Contemplative & Meditative"],
    "to_be_with_others": ["Group Energy", "Queer Revelry", "Big Night Out"],
    "to_rage_release": ["Punchy / Protest", "Rant & Rapture", "Body-Based / Movement-Led"],
    "to_feel_curious": ["Curious Encounters", "Playful & Weird", "Witchy & Wild"],
    "to_let_loose": ["Late-Night Lark", "Big Night Out", "Cabaret & Glitter"],
    "to_feel_connected": ["Global Rhythms", "Spiritual / Sacred / Mystical", "Wonder & Awe"],
    "to_think": ["The Thoughtful Stage", "Rant & Rapture", "Word & Voice"]
}
```

For Tier 2/3, instead of matching their sad words to sad venues, draw one card from each of 3 different therapeutic clusters:

**Example — user says "I'm feeling really low":**
```
Card 1: From "to_rest" (Contemplative, Grief, Nostalgic)
Card 2: From "to_be_held" (Folk, Group Energy, Word & Voice)  
Card 3: From "to_witness_beauty" (Wonder, Melancholic, Romanticised)
```

Three different medicines. Not "here's more sadness."

---

## Voice (Already Working)

The HOLDING voice is already wired up for care pathways. No changes needed there.

For adjacent cards, she doesn't need to announce "this one is adjacent" — she just offers them. But she *could* say things like:

> *"The cards sometimes know what we don't. This one found you."*

(Future refinement — not essential for this build)

---

## Summary of Changes

| Feature | Change |
|---------|--------|
| Standard search | 2 primary + 1 adjacent (not 3 primary) |
| "I don't know" | Random + adjacent + adjacent (more variety) |
| Care pathway | Draw from 3 different need clusters (therapeutic spread) |
| New config | `TAROT_ADJACENCY` map |
| New config | `SHARED_NEEDS` clusters |

---

## Files Likely Involved

- `app.py` or `venue_matcher.py` — search logic
- New config file or section for adjacency map + need clusters
- `safety_detector.py` — care pathway card selection

---

## Testing

1. Search "witchy" — should get 2 Witchy & Wild + 1 from (Nostalgic, Grief, or Spiritual)
2. Search "cabaret" — should get 2 Cabaret + 1 from (Playful, Comic, or Folk)
3. Type "surprise me" — should get variety across arcana
4. Type "I'm feeling really low" — should get 3 cards from different therapeutic clusters, not 3 sad venues

---

## Reference Document

See `LARK_EMOTIONAL_GEOGRAPHY.md` for the full vision — voice families, tarot adjacency, shared needs, and how they work together.

---

*"She doesn't give you what you searched for. She gives you what you searched for, and one door you didn't know to ask about."*

🕊️
