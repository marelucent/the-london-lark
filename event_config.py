#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Event Filtering Configuration

"""
The London Lark - Event Filter Configuration

Defines what kinds of events align with the Lark's curatorial vision:
niche, indie, underground culture. NOT corporate, mainstream, or generic.

Adjust these filters to refine what events appear in recommendations.
"""

# ============================================================================
# GENRE & CATEGORY FILTERS
# ============================================================================

# Eventbrite category IDs to INCLUDE (whitelist)
# https://www.eventbrite.com/platform/api#/reference/category/list
EVENTBRITE_CATEGORIES_WHITELIST = [
    '103',  # Music
    '105',  # Performing & Visual Arts
    '110',  # Film & Media
    '113',  # Community & Culture
    '119',  # Other (often includes unique/experimental events)
]

# Keywords in event name/description that INCLUDE the event
GENRE_KEYWORDS_INCLUDE = {
    # Music (niche/underground)
    'folk', 'folk-y', 'acoustic', 'singer-songwriter', 'traditional music',
    'jazz', 'blues', 'soul', 'funk',
    'indie', 'indie rock', 'alternative',
    'world music', 'african', 'caribbean', 'latin', 'balkan', 'klezmer',
    'experimental', 'avant-garde', 'noise', 'ambient', 'drone',
    'electronic', 'techno', 'house', 'minimal', 'modular',
    'psych', 'psychedelic', 'krautrock',
    'chamber music', 'early music', 'baroque',

    # Performance
    'fringe theatre', 'new writing', 'experimental theatre', 'devised',
    'cabaret', 'drag', 'burlesque', 'variety show',
    'physical theatre', 'movement', 'dance theatre',
    'contemporary dance', 'experimental dance',
    'circus', 'aerial', 'acrobatics',
    'performance art', 'live art',
    'immersive theatre', 'site-specific',

    # Spoken word
    'poetry', 'spoken word', 'storytelling', 'slam poetry',
    'open mic', 'open mike',

    # Film & arts
    'independent film', 'arthouse', 'film screening', 'documentary screening',
    'art exhibition', 'gallery opening', 'artist talk',

    # Community & culture
    'queer', 'lgbtq+', 'lgbtq', 'lesbian', 'gay', 'trans', 'non-binary',
    'activist', 'activism', 'protest', 'community',
    'ritual', 'spiritual', 'meditation', 'sacred',
    'grassroots', 'co-operative', 'collective',
    'radical', 'alternative', 'underground',
}

# Keywords that EXCLUDE the event (override includes)
GENRE_KEYWORDS_EXCLUDE = {
    # Corporate/business
    'networking', 'business', 'corporate', 'conference', 'seminar', 'webinar',
    'workshop' (unless paired with 'creative' or 'arts'),
    'training', 'professional development', 'leadership',
    'startup', 'entrepreneur', 'pitch', 'investor',

    # Mainstream venues/brands
    'o2 arena', 'wembley', 'alexandra palace', 'royal albert hall',
    'dominion theatre', 'apollo', 'comedy store', 'top secret comedy',
    'ticketmaster presents',

    # Fitness/wellness (unless spiritual)
    'yoga class', 'pilates', 'zumba', 'fitness', 'gym', 'workout',
    'bootcamp', 'marathon', 'running club',

    # Sports
    'football', 'rugby', 'cricket', 'tennis', 'sports',

    # Generic parties/clubbing (not underground)
    'student night', 'freshers', 'pub crawl',
    'bottomless brunch', 'boozy brunch',

    # Children's entertainment (unless arts-focused)
    'kids party', 'bouncy castle', 'face painting',

    # Food festivals (unless cultural)
    'food festival', 'street food market', 'food truck',

    # Generic/commercial
    'speed dating', 'singles event',
    'christmas market', 'craft fair',
}

# ============================================================================
# VENUE FILTERS
# ============================================================================

# Maximum venue capacity (events at larger venues are excluded)
MAX_VENUE_CAPACITY = 300

# Venue name keywords that indicate alignment with Lark's vision
VENUE_KEYWORDS_INCLUDE = {
    'fringe', 'independent', 'indie',
    'community', 'grassroots', 'co-operative', 'co-op',
    'arts centre', 'arts center', 'cultural centre',
    'gallery', 'studio', 'workshop',
    'pub theatre', 'theatre above',
    'basement', 'underground', 'cellar',
    'garden', 'rooftop', 'outdoor',
    'church', 'chapel', 'crypt',
    'warehouse', 'railway arch', 'converted',
    'DIY', 'collective', 'volunteer-run',
}

# Venue name keywords that exclude the event
VENUE_KEYWORDS_EXCLUDE = {
    'o2', 'arena', 'stadium', 'wembley',
    'excel', 'conference centre',
    'hilton', 'marriott', 'holiday inn', 'premier inn',
    'chain', 'corporate',
}

# ============================================================================
# PRICE FILTERS
# ============================================================================

# Price ranges
PRICE_FREE = 0
PRICE_LOW_MAX = 10       # £10 or under
PRICE_MEDIUM_MAX = 20    # £11-20
PRICE_HIGH_MAX = 30      # £21-30
PRICE_VERY_HIGH = 31     # Over £30 (flagged for review)

# Prioritize events under this price
PRICE_PREFERRED_MAX = 20

# ============================================================================
# LOCATION FILTERS
# ============================================================================

# London boroughs (for filtering)
LONDON_BOROUGHS = {
    'camden', 'islington', 'hackney', 'tower hamlets', 'southwark',
    'lambeth', 'wandsworth', 'hammersmith', 'kensington', 'westminster',
    'city of london', 'haringey', 'enfield', 'barnet', 'brent',
    'ealing', 'hounslow', 'richmond', 'kingston', 'merton',
    'croydon', 'bromley', 'lewisham', 'greenwich', 'bexley',
    'havering', 'barking', 'redbridge', 'newham', 'waltham forest',
    'harrow', 'hillingdon', 'sutton',
}

# Area mapping (specific neighborhoods to regions)
AREA_TO_REGION = {
    # North London
    'camden': 'North London',
    'kentish town': 'North London',
    'chalk farm': 'North London',
    'islington': 'North London',
    'angel': 'North London',
    'highbury': 'North London',
    'archway': 'North London',
    'highgate': 'North London',
    'hampstead': 'North London',
    'finsbury park': 'North London',
    'stoke newington': 'North London',

    # East London
    'shoreditch': 'East London',
    'hoxton': 'East London',
    'hackney': 'East London',
    'dalston': 'East London',
    'bethnal green': 'East London',
    'whitechapel': 'East London',
    'stratford': 'East London',
    'bow': 'East London',
    'mile end': 'East London',
    'hackney wick': 'East London',
    'walthamstow': 'East London',

    # South London
    'brixton': 'South London',
    'peckham': 'South London',
    'camberwell': 'South London',
    'deptford': 'South London',
    'new cross': 'South London',
    'lewisham': 'South London',
    'greenwich': 'South London',
    'woolwich': 'South London',
    'tooting': 'South London',
    'streatham': 'South London',
    'clapham': 'South London',
    'battersea': 'South London',

    # West London
    'notting hill': 'West London',
    'portobello': 'West London',
    'shepherds bush': 'West London',
    'hammersmith': 'West London',
    'chiswick': 'West London',
    'acton': 'West London',
    'ealing': 'West London',
    'kensington': 'West London',

    # Central London
    'soho': 'Central London',
    'covent garden': 'Central London',
    'bloomsbury': 'Central London',
    'kings cross': 'Central London',
    'clerkenwell': 'Central London',
    'holborn': 'Central London',
    'barbican': 'Central London',
}

# ============================================================================
# MOOD INFERENCE
# ============================================================================

# Genre/keyword to mood tag mapping
MOOD_INFERENCE_MAP = {
    'Folk & Intimate': [
        'folk', 'folky', 'acoustic', 'singer-songwriter',
        'candlelit', 'intimate', 'unplugged', 'storytelling',
        'traditional music', 'ballad',
    ],
    'Queer Revelry': [
        'queer', 'lgbtq', 'lgbtq+', 'gay', 'lesbian', 'trans',
        'drag', 'pride', 'chosen family',
    ],
    'Cabaret & Glitter': [
        'cabaret', 'drag', 'burlesque', 'variety show',
        'glitter', 'sequins', 'glamour',
    ],
    'Comic Relief': [
        'comedy', 'standup', 'stand-up', 'improv', 'sketch',
        'funny', 'laughter',
    ],
    'Poetic': [
        'poetry', 'spoken word', 'verse', 'slam poetry',
        'poetic', 'lyrical', 'literary',
    ],
    'The Thoughtful Stage': [
        'theatre', 'drama', 'new writing', 'play',
        'thought-provoking', 'intimate theatre',
    ],
    'Melancholic Beauty': [
        'jazz', 'blues', 'melancholic', 'bittersweet',
        'contemplative', 'reflective', 'nocturne',
    ],
    'Playful & Weird': [
        'weird', 'experimental', 'avant-garde', 'strange',
        'surreal', 'absurd', 'playful', 'quirky',
    ],
    'Global Rhythms': [
        'world music', 'african', 'caribbean', 'latin',
        'balkan', 'gypsy', 'klezmer', 'traditional',
    ],
    'Rant & Rapture': [
        'activist', 'protest', 'political', 'radical',
        'passionate', 'fiery',
    ],
    'Spiritual / Sacred / Mystical': [
        'spiritual', 'sacred', 'ritual', 'meditation',
        'mystical', 'shamanic', 'ceremony',
    ],
    'Witchy & Wild': [
        'witchy', 'pagan', 'wild', 'nature',
        'folk horror', 'ritualistic',
    ],
    'Body-Based / Movement-Led': [
        'dance', 'movement', 'physical theatre', 'contemporary dance',
        'circus', 'aerial', 'acrobatics',
    ],
    'Dreamlike & Hypnagogic': [
        'dreamlike', 'hypnotic', 'ambient', 'ethereal',
        'surreal', 'trance', 'meditative',
    ],
    'Curious Encounters': [
        'immersive', 'site-specific', 'participatory',
        'installation', 'interactive', 'unexpected',
    ],
    'Wonder & Awe': [
        'awe-inspiring', 'magnificent', 'breathtaking',
        'spectacle', 'wonder',
    ],
    'Late-Night Lark': [
        'late night', 'midnight', 'after hours',
        'nocturnal', '11pm', '12am',
    ],
    'Nostalgic / Vintage / Retro': [
        'vintage', 'retro', 'nostalgic', '60s', '70s', '80s',
        'throwback', 'classic',
    ],
    'Romanticised London': [
        'victorian', 'edwardian', 'gaslight', 'historical',
        'period', 'heritage',
    ],
}

# Minimum confidence threshold for mood inference
MOOD_CONFIDENCE_THRESHOLD = 0.5  # 0.0 to 1.0

# ============================================================================
# DATA FRESHNESS
# ============================================================================

# How many days ahead to fetch events
FETCH_DAYS_AHEAD = 14

# Minimum hours in the future (filter out events starting in next hour)
MIN_HOURS_AHEAD = 2

# ============================================================================
# API SETTINGS
# ============================================================================

# Maximum events to fetch per API call
MAX_EVENTS_PER_REQUEST = 100

# Maximum total events to fetch
MAX_TOTAL_EVENTS = 500

# Request timeout (seconds)
API_TIMEOUT = 15
