# 🕊️ Lark Database Audit - Pattern Analysis

*Generated: 2025-11-27 09:21*

---

## Overview

Audited **296 venues** against standards in VENUE_DATA_STANDARDS.md
Found **749 total issues** across **284 venues**

## Location Patterns

**20 venues** have location formatting issues:

- **20 compound locations** (using & or /) - likely need to pick primary neighborhood

**Most common pattern:** Venues use 'Neighborhood, Borough' format instead of just 'Neighborhood'

## Mood Tag Patterns

**195 unique mood tags** in use across all venues:

- **24 approved moods** from mood_index.json
- **171 unapproved moods** (not in current approved list)

**Important:** Many unapproved moods are expressive and poetic - not errors!

**Beautiful unlisted tags** (strong candidates for approval):
- curious
- playful
- craft & making
- rebellious
- ecstatic
- wild
- nostalgic
- epicurean
- intimate
- earthy

**Tags that should be features** (not moods):
- family-friendly
- free-spirited
- boozy
- accessible

## Genre Patterns

**112 venues** have genre count issues (not 3-5 genres)

## Blurb Quality Patterns

**196 venues** have blurb issues:

- **172 too short** (<50 words)

## Geographic Distribution

**Top 10 neighborhoods by venue count:**

- Peckham: 10 venues
- Islington: 8 venues
- Dalston: 7 venues
- Shoreditch: 7 venues
- Camden: 6 venues
- Hackney: 6 venues
- Hackney Wick: 4 venues
- Soho: 4 venues
- King's Cross: 4 venues
- East London: 4 venues

## Issue Severity Breakdown

**CRITICAL:** 218 issues
**IMPORTANT:** 522 issues
**MINOR:** 9 issues

## Recommendations for Batch Fixes

Based on patterns observed:

1. **Location standardization** - Many venues use 'Neighborhood, Borough' format. Create script to extract just neighborhood.
2. **Mood taxonomy review** - Review unapproved moods and decide which to add to mood_index.json
3. **Blurb expansion** - Venues with short blurbs need poetic enhancement in Lark's voice
4. **Verification refresh** - Spot-check stale venues (>6 months) to confirm they're still active
5. **Feature vs Mood** - Move feature-like tags (accessible, family-friendly) to proper feature fields

---

*Remember: Clean data is an act of care* 🕊️✨
