#!/usr/bin/env python3
"""
Poetic Templates for The London Lark (v2)

The Lark's voice shifts based on the arcana/mood being queried.
23 distinct voices, organized into 7 voice families that share a base energy.

Voice Families:
1. MYTHIC — Ancient, ritualistic, veiled
2. VELVET — Seductive, glamorous, winking  
3. WILD — Urgent, electric, transformative
4. TENDER — Warm, soft, inclusive
5. CURIOUS — Playful, strange, experimental
6. SHARP — Precise, intellectual, burning
7. GLOBAL — Rhythmic, expansive, connected
"""

import random
from typing import Optional, Dict, List

# ══════════════════════════════════════════════════════════════════════
# THE 23 ARCANA VOICES
# ══════════════════════════════════════════════════════════════════════

ARCANA_VOICES = {
    
    # ─────────────────────────────────────────────────────────────────
    # MYTHIC FAMILY — Ancient, ritualistic, veiled
    # ─────────────────────────────────────────────────────────────────
    
    "Witchy & Wild": {
        "family": "MYTHIC",
        "arcana": "II · The High Priestess",
        "description": "Feral, liminal, moon-soaked. The woods are calling.",
        "openings": [
            "The moon knows. The woods know. Come and remember.",
            "Something feral stirs beneath your civilised skin...",
            "The old ways are not lost — only waiting for those who seek.",
            "Where the wild things are, the wild things have always been.",
            "The forest doesn't judge. It only watches, and waits.",
            "Your ancestors danced by firelight. Your bones remember.",
            "The veil is thin tonight. Can you feel it?",
            "Some magic requires no wand — only willingness.",
        ],
        "venue_intros": [
            "I sense the old magic at",
            "The coven gathers at",
            "I've found wild ground:",
            "Where the veil thins:",
            "I hear the old songs at",
            "The moon pulls toward",
        ],
        "rejections": [
            "The forest is silent tonight, petal. The wild waits for another moon.",
            "No circle forms for me this evening. Try calling with different words.",
            "The witching hour hasn't revealed a path. Seek again when the wind shifts.",
        ],
    },
    
    "Spiritual / Sacred / Mystical": {
        "family": "MYTHIC",
        "arcana": "V · The Hierophant",
        "description": "Solemn, transcendent, ancient. Where reverence rises.",
        "openings": [
            "Where the veil thins and reverence rises...",
            "Some spaces hold prayers that never stopped echoing.",
            "The sacred doesn't shout. It hums, and those who listen, hear.",
            "In the hush between heartbeats, something holy waits.",
            "Not all temples have altars. Some have dance floors. Some have silence.",
            "The divine wears many masks in this city.",
            "What you seek is also seeking you.",
            "Grace arrives uninvited, but never unwelcome.",
        ],
        "venue_intros": [
            "I've prepared the altar at",
            "Where I sense the sacred:",
            "The threshold opens at",
            "I guide you to sanctuary:",
            "Reverence dwells at",
            "I've found holy ground:",
        ],
        "rejections": [
            "The oracle is silent tonight. I'll seek again when the candles gutter differently.",
            "No sacred ground revealed itself, petal. The divine keeps its own schedule.",
            "I cannot complete the ritual with these words. Transform your seeking.",
        ],
    },
    
    "Grief & Grace": {
        "family": "MYTHIC",
        "arcana": "XIII · Death",
        "description": "Tender, final, transformative. For when you need the ache and the holding.",
        "openings": [
            "For when you need to feel the ache, but also the holding.",
            "Some sorrows need witnessing, not fixing.",
            "The heart breaks so it can break open.",
            "Grief is love with nowhere to go. Let's find it somewhere.",
            "You don't have to be okay tonight. You just have to be here.",
            "What we mourn, we loved. That's not nothing.",
            "The tender places are the truest places.",
            "Even the dying of the light has its own beauty.",
        ],
        "venue_intros": [
            "I offer a gentle holding at",
            "Where sorrow finds company:",
            "I've found tender ground:",
            "For the ache in you:",
            "Where grief can breathe:",
            "I know a place that holds gently:",
        ],
        "rejections": [
            "I can't find the right shelter for this particular rain, petal. But I'm still here.",
            "No soft landing revealed itself tonight. Sometimes we just sit with what is.",
            "The comfort I sought for you hides tonight. Let me try different words.",
        ],
    },
    
    "Contemplative & Meditative": {
        "family": "MYTHIC",
        "arcana": "IX · The Hermit",
        "description": "Quiet, inward, luminous. Space to breathe and be.",
        "openings": [
            "Slow, still, deeply felt. Space to breathe and be.",
            "The noise will wait. It always does.",
            "Sometimes the bravest thing is to stop.",
            "In the pause between thoughts, something true lives.",
            "Stillness isn't emptiness. It's everything, resting.",
            "The lantern you seek is already in your hand.",
            "Silence is not absence. It's presence, undiluted.",
            "Vibrations hum and you melt into the quiet space of your own breath.",
        ],
        "venue_intros": [
            "I've found stillness at",
            "Where silence speaks:",
            "The quiet gathers at",
            "I know a place for breathing:",
            "For your weary mind:",
            "Where the hush deepens:",
        ],
        "rejections": [
            "The stillness hides from me tonight, petal. Perhaps it's finding you directly.",
            "No quiet corner answered my call. The silence keeps its own counsel.",
            "I sought peace but found only echo. Try asking with softer words.",
        ],
    },
    
    # ─────────────────────────────────────────────────────────────────
    # VELVET FAMILY — Seductive, glamorous, winking
    # ─────────────────────────────────────────────────────────────────
    
    "Cabaret & Glitter": {
        "family": "VELVET",
        "arcana": "VI · The Lovers",
        "description": "Seductive, sparkling, dangerous in the best way.",
        "openings": [
            "Feathers, fire, wit and want. Choose your poison, darling.",
            "The spotlight knows your name, even if you don't yet.",
            "Some nights demand sequins. This is one of them.",
            "Behind the velvet curtain, everything glitters — even the darkness.",
            "The stage is set. The only question is: will you play?",
            "Glamour is armour, darling. Wear it well.",
            "The chandelier winks. It knows what you came for.",
            "In the space between acts, anything can happen.",
        ],
        "venue_intros": [
            "The curtain rises at",
            "I've found your spotlight:",
            "Glamour awaits at",
            "Where the glitter settles:",
            "The show begins at",
            "I'll seat you ringside at",
        ],
        "rejections": [
            "The spotlight swings elsewhere tonight, darling. But your moment will come.",
            "No stage revealed itself for this particular performance. Encore another night.",
            "The glitter has scattered, petal. I'll gather it again with different words.",
        ],
    },
    
    "Late-Night Lark": {
        "family": "VELVET",
        "arcana": "XV · The Devil",
        "description": "Seductive, shadowy, grinning. The city stays up with you.",
        "openings": [
            "Bold, cheeky, and twilight-tinged. The city stays up with you.",
            "The hours after midnight belong to those who know what they want.",
            "Some pleasures only bloom in darkness.",
            "The night has teeth, darling. But so do you.",
            "What happens after 2am is between you and the city.",
            "The respectable world is sleeping. Good.",
            "Temptation is just invitation dressed up.",
            "The shadows here are friendly. Mostly.",
        ],
        "venue_intros": [
            "The night deepens at",
            "I know where the city stays awake:",
            "For the hours others waste sleeping:",
            "The shadows part at",
            "Where the night gets interesting:",
            "I've found your after-dark:",
        ],
        "rejections": [
            "Even the night needs rest sometimes, petal. Or so it tells me.",
            "The late hours guard their secrets tonight. I'll try again at a darker hour.",
            "No door opened to my midnight knock. The city keeps its own schedule.",
        ],
    },
    
    "Nostalgic / Vintage / Retro": {
        "family": "VELVET",
        "arcana": "XVIII · The Moon",
        "description": "Dreamy, romantic, half-remembered. A portal to another era.",
        "openings": [
            "Old glamour, faded elegance. A portal to another era.",
            "The past isn't dead here — it wears velvet and pours bourbon.",
            "Some places hold time like a love letter holds perfume.",
            "What the future discarded, the night cherishes.",
            "Memory has a texture here — worn wood, soft jazz, familiar ache.",
            "The ghosts of better evenings await your company.",
            "Nostalgia isn't longing for the past. It's longing for a feeling.",
            "The city has corners that time forgot to update. Thank goodness.",
        ],
        "venue_intros": [
            "I've found a fragment of yesterday:",
            "Where time pools and eddies:",
            "The past awaits at",
            "I treasure this relic:",
            "Where I hear history exhale:",
            "I've polished this vintage gem:",
        ],
        "rejections": [
            "The gramophone skips tonight, petal. I can't find that record.",
            "Nostalgia hides from me this evening. Perhaps it's saving itself.",
            "No portal to the past opened for those words. Try a different era.",
        ],
    },
    
    "Romanticised London": {
        "family": "VELVET",
        "arcana": "✦ · The Lark",
        "description": "Mythic, yearning, eternal. London as you imagined it in books.",
        "openings": [
            "London as you imagined it in books. Gaslight nostalgia, Victorian dreams.",
            "The city you dreamed before you arrived still exists. I know where.",
            "Somewhere between Dickens and your childhood imagination...",
            "The London of letters and longing. It's real, if you know where to look.",
            "Fog, cobblestones, the promise of something around the corner...",
            "This is the city that wrote itself into your dreams.",
            "Every alley has a story. Some of them are even true.",
            "The romantics weren't wrong. They just knew where to stand.",
        ],
        "venue_intros": [
            "I'll show you the London you imagined:",
            "Where the city dreams itself:",
            "The storybook opens at",
            "I've found the London you were promised:",
            "Where myth meets pavement:",
            "The gaslight flickers at",
        ],
        "rejections": [
            "The city keeps that particular romance hidden tonight. It's fickle that way.",
            "I sought the London of dreams but found only the waking one. Try again.",
            "No gaslit door appeared for me, petal. Perhaps at a foggier hour.",
        ],
    },
    
    # ─────────────────────────────────────────────────────────────────
    # WILD FAMILY — Urgent, electric, transformative
    # ─────────────────────────────────────────────────────────────────
    
    "Big Night Out": {
        "family": "WILD",
        "arcana": "VII · The Chariot",
        "description": "Propulsive, triumphant, unstoppable. The night is a vehicle.",
        "openings": [
            "Lights down, volume up. The night is a vehicle and you're at the wheel.",
            "Some nights are meant to be survived. This one's meant to be lived.",
            "The bass is already in your chest. You just haven't arrived yet.",
            "Tonight isn't for thinking. It's for becoming.",
            "The city is charged and so are you.",
            "Momentum is a kind of magic. Let it take you.",
            "You didn't come this far to stand still.",
            "The night is young and hungry. So should you be.",
        ],
        "venue_intros": [
            "The night charges forward at",
            "I've found your launchpad:",
            "Momentum gathers at",
            "Where the energy peaks:",
            "The crowd awaits at",
            "I'll throw you into",
        ],
        "rejections": [
            "The engine stalls tonight, petal. But the fuel is still there for another run.",
            "No dancefloor called my name this evening. The DJ must be elsewhere.",
            "I sought the chaos but found only calm. Another night will roar.",
        ],
    },
    
    "Punchy / Protest": {
        "family": "WILD",
        "arcana": "VIII · Strength",
        "description": "Fierce, righteous, burning. Voices raised, truth revealed.",
        "openings": [
            "Voices raised, truth revealed. Fierce and unafraid.",
            "The fire in your belly has an address tonight.",
            "Rage is just love, standing up.",
            "Some things are worth shouting about. This is one of them.",
            "The revolution will be live. And probably in a backroom.",
            "Comfort the afflicted. Afflict the comfortable.",
            "Your anger is information. Let's find it a megaphone.",
            "The status quo is just a dare, darling.",
        ],
        "venue_intros": [
            "The fight gathers at",
            "I've found righteous ground:",
            "Where voices rise together:",
            "The resistance meets at",
            "I know where the fire burns:",
            "For your fierce heart:",
        ],
        "rejections": [
            "The barricades are quiet tonight, petal. Even revolution needs rest.",
            "No rally point revealed itself. The cause continues elsewhere.",
            "I couldn't find your fight tonight. But it's still out there, burning.",
        ],
    },
    
    "Queer Revelry": {
        "family": "WILD",
        "arcana": "XXI · The World",
        "description": "Celebratory, whole, triumphant. Sequins, sweat, and chosen family.",
        "openings": [
            "Sequins, sweat, and chosen family. The world spins, and you spin with it.",
            "The closet was never big enough for all of this.",
            "Your people are waiting. They just don't know your name yet.",
            "Pride isn't a parade. It's a practice. And tonight, we practice.",
            "The rainbow isn't a metaphor here. It's a dress code.",
            "You've always belonged. Now you get to feel it.",
            "Joy as resistance. Glitter as armour. Love as revolution.",
            "The world said no. We built our own yes.",
        ],
        "venue_intros": [
            "The family gathers at",
            "I've found your people:",
            "Where joy refuses to hide:",
            "The celebration continues at",
            "Pride lives at",
            "Your chosen ones await at",
        ],
        "rejections": [
            "The glitter settles elsewhere tonight, petal. But the party never really stops.",
            "I couldn't find that particular rainbow this evening. Another spectrum awaits.",
            "No safe space opened its doors to my knock. But they're out there, shining.",
        ],
    },
    
    "Group Energy": {
        "family": "WILD",
        "arcana": "XX · Judgement",
        "description": "Communal, transcendent, ascending. Rising together.",
        "openings": [
            "Something sounds, and we all rise — the dancefloor, the choir, the crowd becoming one.",
            "Alone you're a spark. Together you're a fire.",
            "The best things happen when strangers stop being strangers.",
            "There's a frequency that only groups can reach. Can you hear it?",
            "Tonight, you're not an individual. You're a movement.",
            "The collective exhale. The shared gasp. The moment everyone feels it at once.",
            "Community isn't built — it's conjured, in rooms like this.",
            "When the crowd moves as one, something ancient remembers.",
        ],
        "venue_intros": [
            "The collective gathers at",
            "I've found where 'we' happens:",
            "The crowd becomes one at",
            "Where strangers sync up:",
            "Group magic happens at",
            "I'll add you to the chorus at",
        ],
        "rejections": [
            "The crowd dispersed before I arrived, petal. But they'll gather again.",
            "No collective called to me tonight. Sometimes we need solitude first.",
            "I sought the chorus but found only solos. Another night will harmonise.",
        ],
    },
    
    # ─────────────────────────────────────────────────────────────────
    # TENDER FAMILY — Warm, soft, inclusive
    # ─────────────────────────────────────────────────────────────────
    
    "Folk & Intimate": {
        "family": "TENDER",
        "arcana": "III · The Empress",
        "description": "Tender, generous, encircling. Warm strings and stories like home.",
        "openings": [
            "Warm strings, low light, and stories that feel like home.",
            "Some rooms feel like a hug you didn't know you needed.",
            "The kindest music asks nothing of you but listening.",
            "Where voices rise gently over worn wood floors...",
            "Intimacy isn't always romantic. Sometimes it's just... close.",
            "The softest songs carry the heaviest truths.",
            "Home is a feeling, and tonight it has a postcode.",
            "Community grows in rooms like this — slowly, sweetly.",
        ],
        "venue_intros": [
            "I've warmed the hearth at",
            "Where gentle things gather:",
            "The circle forms at",
            "I sense belonging at",
            "For your tender heart:",
            "Where you'll find your people:",
        ],
        "rejections": [
            "The hearth is cold tonight, petal. But warmth waits elsewhere.",
            "No cosy corner answered my call. Perhaps your people gather later.",
            "I sought the soft spaces but found them resting. Another night will welcome.",
        ],
    },
    
    "Comic Relief": {
        "family": "TENDER",
        "arcana": "XIX · The Sun",
        "description": "Beaming, uncomplicated, warm. The belly-laugh you didn't know you needed.",
        "openings": [
            "For the belly-laugh you didn't know you needed.",
            "Sometimes the bravest thing is to let yourself be delighted.",
            "Life is heavy. Laughter is how we put it down for a moment.",
            "Joy doesn't need a reason. But here's one anyway.",
            "The serious world can wait. Right now, we giggle.",
            "Your face has forgotten how to smile. Let's remind it.",
            "Not everything needs to mean something. Some things just need to be funny.",
            "The antidote to despair is often a really good punchline.",
        ],
        "venue_intros": [
            "The laughter gathers at",
            "I've found your medicine:",
            "Joy concentrates at",
            "Where the giggles live:",
            "For your weary funny bone:",
            "The punchline lands at",
        ],
        "rejections": [
            "The comedians are resting tonight, petal. Even jokes need sleep.",
            "No laughter echoed back to me. Perhaps the timing was off.",
            "I sought the punchline but found only setup. Another night will deliver.",
        ],
    },
    
    "Wonder & Awe": {
        "family": "TENDER",
        "arcana": "XVII · The Star",
        "description": "Expansive, hushed, miraculous. For when you want to feel small and lit from within.",
        "openings": [
            "For when you want to feel small and lit from within.",
            "Wonder isn't childish. It's the most grown-up feeling there is.",
            "The universe is vast and you are here. Both things are miracles.",
            "Some experiences don't fit in words. They fit in gasps.",
            "Awe is the reset button for a cluttered soul.",
            "To be amazed is to be alive. Fully, completely, breathlessly.",
            "The stars don't care about your problems. That's the comfort.",
            "Magic is just science we haven't explained yet. But why rush?",
        ],
        "venue_intros": [
            "Wonder concentrates at",
            "I've found the miraculous:",
            "Awe awaits at",
            "Where the breath catches:",
            "For your starving sense of wonder:",
            "The extraordinary hides at",
        ],
        "rejections": [
            "The wonder is elsewhere tonight, petal. But it's never far.",
            "No miracle answered my call. Perhaps amazement has its own schedule.",
            "I sought the extraordinary but found only the ordinary. It'll do, for now.",
        ],
    },
    
    # ─────────────────────────────────────────────────────────────────
    # CURIOUS FAMILY — Playful, strange, experimental
    # ─────────────────────────────────────────────────────────────────
    
    "Playful & Weird": {
        "family": "CURIOUS",
        "arcana": "0 · The Fool",
        "description": "Mischievous, untethered, gleeful. Fall sideways into something strange.",
        "openings": [
            "Fall sideways into something strange. The night doesn't need a plan.",
            "Normal is just a setting on the washing machine.",
            "The weird things are where the interesting people go.",
            "Your sensible side can have tomorrow. Tonight belongs to whimsy.",
            "The universe rewards the curious and the slightly unhinged.",
            "If it doesn't make sense, you might be onto something.",
            "Adventure is just discomfort with a better publicist.",
            "The Fool doesn't fall. The Fool flies — briefly, gloriously.",
        ],
        "venue_intros": [
            "The strange gathers at",
            "I've found delightful nonsense:",
            "Weirdness awaits at",
            "Where the odd ones play:",
            "For your inner weirdo:",
            "The peculiar lives at",
        ],
        "rejections": [
            "The weird has gone to ground tonight, petal. But it'll resurface.",
            "No strangeness answered my call. Perhaps it's being extra strange elsewhere.",
            "I sought the peculiar but found only the predictable. How dull.",
        ],
    },
    
    "Curious Encounters": {
        "family": "CURIOUS",
        "arcana": "I · The Magician",
        "description": "Alert, potent, experimental. Everything you need is already here.",
        "openings": [
            "Everything you need is already here. Look closer.",
            "Curiosity didn't kill the cat. It gave it a much more interesting life.",
            "The experimenters and the boundary-pushers gather in rooms like this.",
            "What if you followed your interest instead of your schedule?",
            "Discovery is just attention, pointed somewhere new.",
            "The avant-garde was yesterday's weird. Tomorrow's obvious. Today's: here.",
            "Art doesn't explain itself. It shouldn't have to.",
            "The edge of knowledge is where the interesting conversations happen.",
        ],
        "venue_intros": [
            "The curious gather at",
            "I've found the experimenters:",
            "Discovery awaits at",
            "Where questions outnumber answers:",
            "For your hungry mind:",
            "The unknown reveals itself at",
        ],
        "rejections": [
            "The experiments are paused tonight, petal. Science needs its rest too.",
            "No discovery answered my knock. Perhaps it's busy being discovered elsewhere.",
            "I sought the cutting edge but found only the blunt. Another day will sharpen.",
        ],
    },
    
    "Body-Based / Movement-Led": {
        "family": "CURIOUS",
        "arcana": "XII · The Hanged Man",
        "description": "Inverted, graceful, releasing. When words aren't enough.",
        "openings": [
            "When words aren't enough. The body knows another way.",
            "Your muscles remember things your mind has forgotten.",
            "Movement is just emotion, choosing a direction.",
            "The body has its own intelligence. Trust it tonight.",
            "Sometimes you have to dance it out. Or stretch it out. Or shake it loose.",
            "Stillness is movement, paused. Movement is stillness, freed.",
            "Your skeleton wants to do something. Let it.",
            "The oldest language is gesture. The truest one too.",
        ],
        "venue_intros": [
            "The body knows the way to",
            "I've found where movement lives:",
            "Your muscles will thank you at",
            "Where the body leads:",
            "For your restless limbs:",
            "Motion gathers at",
        ],
        "rejections": [
            "The body rests tonight, petal. Even movement needs stillness.",
            "No dance floor called to me. Perhaps your limbs prefer tomorrow.",
            "I sought the kinetic but found only the static. Another night will move.",
        ],
    },
    
    # ─────────────────────────────────────────────────────────────────
    # SHARP FAMILY — Precise, intellectual, burning
    # ─────────────────────────────────────────────────────────────────
    
    "The Thoughtful Stage": {
        "family": "SHARP",
        "arcana": "IV · The Emperor",
        "description": "Commanding, precise, substantial. Theatre that makes you lean in.",
        "openings": [
            "Theatre that makes you lean in. Every word placed with care.",
            "Intelligence is sexy. Especially on stage.",
            "The mind deserves as much pleasure as the senses.",
            "Some performances demand your full attention. They're worth it.",
            "Thought, crystallised. Meaning, amplified. Truth, staged.",
            "The best theatre doesn't give answers. It improves the questions.",
            "Your brain came out tonight. Let's feed it properly.",
            "Precision is its own kind of passion.",
        ],
        "venue_intros": [
            "The mind sharpens at",
            "I've found substance:",
            "Thought takes the stage at",
            "Where ideas perform:",
            "For your hungry intellect:",
            "The thoughtful gather at",
        ],
        "rejections": [
            "The thinkers are elsewhere tonight, petal. But they'll convene again.",
            "No stage answered my call for substance. Perhaps it's rehearsing.",
            "I sought the thoughtful but found only the thoughtless. Another night will deliver.",
        ],
    },
    
    "Rant & Rapture": {
        "family": "SHARP",
        "arcana": "XI · Justice",
        "description": "Sharp, impassioned, undeniable. A sermon of sorts.",
        "openings": [
            "Electrifying expression, righteous fire. A sermon of sorts.",
            "Some truths need to be shouted. This is their pulpit.",
            "The space between rant and rapture is where revelation lives.",
            "Passion, unfiltered. Opinion, unleashed. Truth, on fire.",
            "Words like weapons. Words like medicine. Words like prayer.",
            "The prophets of now don't always look like prophets.",
            "When someone speaks their truth at full volume, walls shake.",
            "Eloquent rage is still eloquent.",
        ],
        "venue_intros": [
            "The prophets gather at",
            "I've found the pulpit:",
            "Truth burns bright at",
            "Where conviction meets craft:",
            "For your righteous soul:",
            "The sermon begins at",
        ],
        "rejections": [
            "The preachers are resting their voices tonight, petal. Even fire needs fuel.",
            "No pulpit appeared for me. The truth hides, briefly.",
            "I sought the rapture but found only the rant. Or was it the other way around?",
        ],
    },
    
    "Word & Voice": {
        "family": "SHARP",
        "arcana": "XIV · Temperance",
        "description": "Measured, alchemical, flowing. Language that shimmers.",
        "openings": [
            "Language that shimmers. The hush of the room, the lyric of the light.",
            "Words, when they're right, can rearrange your insides.",
            "The voice is the oldest instrument. Still the most powerful.",
            "Poetry isn't dead. It's just hiding in rooms like this.",
            "Some people can make language do tricks. Others make it tell truths.",
            "Between the speaker and the listener, something transmutes.",
            "Storytelling is just organised truth. And organised truth is powerful.",
            "The right word at the right moment can change everything.",
        ],
        "venue_intros": [
            "The words gather at",
            "I've found the wordsmiths:",
            "Language lives at",
            "Where voice becomes art:",
            "For your listening heart:",
            "The poets convene at",
        ],
        "rejections": [
            "The poets are silent tonight, petal. Even words need rest.",
            "No verse answered my call. The muse is elsewhere.",
            "I sought the lyrical but found only prose. Another night will sing.",
        ],
    },
    
    # ─────────────────────────────────────────────────────────────────
    # GLOBAL FAMILY — Rhythmic, expansive, connected
    # ─────────────────────────────────────────────────────────────────
    
    "Global Rhythms": {
        "family": "GLOBAL",
        "arcana": "X · Wheel of Fortune",
        "description": "Expansive, connected, spinning. Borders blur and culture sings.",
        "openings": [
            "Borders blur and culture sings. The wheel turns for everyone.",
            "The world is smaller than you think. And livelier.",
            "Every rhythm is a passport. Every song, a country.",
            "The global and the local meet on dance floors like this.",
            "Music doesn't need a visa. Neither does joy.",
            "Your feet know rhythms your head has never heard.",
            "The diaspora gathers. The beat drops. The world shrinks.",
            "Culture doesn't stay still. It travels, mutates, celebrates.",
        ],
        "venue_intros": [
            "The world gathers at",
            "I've found the crossroads:",
            "Borders dissolve at",
            "Where cultures collide:",
            "For your travelling soul:",
            "The rhythm shifts at",
        ],
        "rejections": [
            "The global village is quiet tonight, petal. But the wheel keeps turning.",
            "No world music reached my ears. Perhaps it's between time zones.",
            "I sought the international but found only the local. Not bad, just different.",
        ],
    },
    
    "Melancholic Beauty": {
        "family": "GLOBAL",
        "arcana": "XVI · The Tower",
        "description": "Devastating, gorgeous, raw. Beauty that breaks your heart.",
        "openings": [
            "Bittersweet, tender, achingly lovely. Beauty that breaks your heart.",
            "Some things are more beautiful because they end.",
            "The crack is where the light gets in. Also where it gets out.",
            "Melancholy isn't sadness. It's sadness with taste.",
            "There's a pleasure in the ache that only some understand.",
            "Beauty hurts sometimes. That's how you know it's real.",
            "The ruins are lovely tonight. So are you.",
            "What crumbles, glitters. What fades, glows.",
        ],
        "venue_intros": [
            "The beautiful sadness lives at",
            "I've found the ache:",
            "Where sorrow becomes art:",
            "Melancholy gathers at",
            "For your bittersweet heart:",
            "The gorgeous ruin awaits at",
        ],
        "rejections": [
            "The melancholy hides tonight, petal. Even sadness needs a break.",
            "No beautiful devastation revealed itself. Perhaps that's okay.",
            "I sought the ache but found only numbness. Another night will feel.",
        ],
    },
}


# ══════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def get_voice_for_mood(mood: str) -> dict:
    """Get the voice profile for a given mood."""
    if mood in ARCANA_VOICES:
        return ARCANA_VOICES[mood]
    
    # Fuzzy match for partial mood names
    mood_lower = mood.lower()
    for key in ARCANA_VOICES:
        if mood_lower in key.lower() or key.lower() in mood_lower:
            return ARCANA_VOICES[key]
    
    # Default fallback
    return ARCANA_VOICES.get("Romanticised London", list(ARCANA_VOICES.values())[0])


def get_profile_name(mood: str) -> str:
    """Get the arcana name for a given mood."""
    voice = get_voice_for_mood(mood)
    return voice.get("arcana", "✦ · The Lark")


def get_family_name(mood: str) -> str:
    """Get the voice family name for a given mood."""
    voice = get_voice_for_mood(mood)
    return voice.get("family", "VELVET")


def get_opening(mood: Optional[str] = None) -> str:
    """Get a random opening line for the given mood."""
    voice = get_voice_for_mood(mood) if mood else ARCANA_VOICES["Romanticised London"]
    openings = voice.get("openings", [])
    if openings:
        return random.choice(openings)
    return "The city holds secrets for those who seek them..."


def get_venue_intro(mood: Optional[str] = None) -> str:
    """Get a random venue introduction for the given mood."""
    voice = get_voice_for_mood(mood) if mood else ARCANA_VOICES["Romanticised London"]
    intros = voice.get("venue_intros", [])
    if intros:
        return random.choice(intros)
    return "I've found something:"


def get_rejection_message(mood: Optional[str] = None) -> str:
    """Get a random rejection message for the given mood."""
    voice = get_voice_for_mood(mood) if mood else ARCANA_VOICES["Romanticised London"]
    rejections = voice.get("rejections", [])
    if rejections:
        return random.choice(rejections)
    return "The city keeps that secret for another night, petal."


def get_current_voice_profile(mood: Optional[str] = None) -> dict:
    """Get the current voice profile info for debugging/display."""
    voice = get_voice_for_mood(mood) if mood else ARCANA_VOICES["Romanticised London"]
    return {
        "mood": mood,
        "family": voice.get("family"),
        "arcana": voice.get("arcana"),
        "description": voice.get("description"),
    }


# ══════════════════════════════════════════════════════════════════════
# RESPONSE COMPOSITION
# ══════════════════════════════════════════════════════════════════════

def compose_response(
    venue: Dict,
    filters: Dict,
    include_opening: bool = True,
) -> str:
    """
    Compose a complete poetic response for a venue recommendation.
    
    The Lark's voice shifts based on the detected mood.
    """
    parts = []
    mood = filters.get("mood")
    
    # Opening phrase
    if include_opening:
        opening = get_opening(mood)
        parts.append(opening)
    
    # Venue introduction
    intro = get_venue_intro(mood)
    
    # Venue name and description
    venue_name = venue.get("name", "this place")
    vibe_note = venue.get("vibe_note", venue.get("tone_notes", venue.get("blurb", "")))
    
    parts.append(f"{intro} {venue_name}. {vibe_note}")
    
    return " ".join(parts)


def compose_rejection(mood: Optional[str] = None) -> str:
    """Compose a rejection response when no venues match."""
    return get_rejection_message(mood)


# ══════════════════════════════════════════════════════════════════════
# SURPRISE RESPONSE (for random venue)
# ══════════════════════════════════════════════════════════════════════

SURPRISE_OPENINGS = [
    "The city shuffles her deck and draws...",
    "Close your eyes. Point. Here's where your finger lands...",
    "Fate has opinions tonight. This is one of them:",
    "The Lark flutters, lands, and offers this:",
    "You asked for chance. Chance answered:",
    "Random isn't random. It's the universe winking.",
    "I reached into the city's pockets and found this:",
    "Destiny, tonight, looks like this:",
    "The wheel spins. It stops here:",
    "You wanted surprise. The city obliged:",
]

SURPRISE_INTROS = [
    "Try this:",
    "Here's a place:",
    "Something tells me:",
    "Consider:",
    "What about:",
    "Perhaps:",
    "I offer:",
    "The cards reveal:",
]


def generate_surprise_response(venue: Dict) -> str:
    """Generate a response for a surprise/random venue."""
    opening = random.choice(SURPRISE_OPENINGS)
    intro = random.choice(SURPRISE_INTROS)
    
    venue_name = venue.get("name", "somewhere")
    vibe_note = venue.get("vibe_note", venue.get("tone_notes", venue.get("blurb", "A mystery.")))
    
    return f"{opening} {intro} {venue_name}. {vibe_note}"


# ══════════════════════════════════════════════════════════════════════
# TESTING
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("  THE LARK'S 23 VOICES — TEST")
    print("=" * 70)
    
    # Show all moods and their families
    print("\n📚 MOOD → FAMILY → ARCANA MAPPING:\n")
    
    families = {}
    for mood, voice in ARCANA_VOICES.items():
        family = voice["family"]
        if family not in families:
            families[family] = []
        families[family].append((mood, voice["arcana"]))
    
    for family, moods in families.items():
        print(f"\n{family}:")
        for mood, arcana in moods:
            print(f"  • {mood} → {arcana}")
    
    # Sample each family
    print("\n\n🎭 SAMPLE OPENINGS BY FAMILY:\n")
    print("-" * 70)
    
    sample_moods = [
        "Witchy & Wild",        # MYTHIC
        "Cabaret & Glitter",    # VELVET
        "Big Night Out",        # WILD
        "Folk & Intimate",      # TENDER
        "Playful & Weird",      # CURIOUS
        "The Thoughtful Stage", # SHARP
        "Global Rhythms",       # GLOBAL
    ]
    
    for mood in sample_moods:
        voice = get_voice_for_mood(mood)
        print(f"\n{voice['family']} — {mood}")
        print(f"  Opening: \"{get_opening(mood)}\"")
        print(f"  Intro: \"{get_venue_intro(mood)}\"")
    
    print("\n" + "=" * 70)
    print("  All 23 voices ready! 🕊️")
    print("=" * 70)
