#!/usr/bin/env python3
"""
Poetic Templates for The London Lark (v2)

The Lark's voice shifts based on the arcana/mood being queried.
23 distinct voices + 1 care pathway voice, organized into 8 voice families.

Voice Families:
1. MYTHIC — Ancient, ritualistic, veiled
2. VELVET — Seductive, glamorous, winking
3. WILD — Urgent, electric, transformative
4. TENDER — Warm, soft, inclusive
5. CURIOUS — Playful, strange, experimental
6. SHARP — Precise, intellectual, burning
7. GLOBAL — Rhythmic, expansive, connected
8. HOLDING — Gentle, present, unhurried (for care pathways)
"""

import random
from typing import Optional, Dict, List

# ══════════════════════════════════════════════════════════════════════════════
# THE 23 ARCANA VOICES + CARE PATHWAY VOICE
# ══════════════════════════════════════════════════════════════════════════════

ARCANA_VOICES = {

    # ──────────────────────────────────────────────────────────────────────────
    # MYTHIC FAMILY — Ancient, ritualistic, veiled
    # ──────────────────────────────────────────────────────────────────────────

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
            "The sacred gathers at",
            "I've found holy ground:",
            "Reverence rises at",
            "Where the divine breathes:",
            "Grace awaits at",
            "The threshold opens at",
        ],
        "rejections": [
            "The sacred is quiet tonight, petal. Even the divine rests.",
            "No temple doors opened for me. Perhaps tomorrow's prayer.",
            "The mystical keeps its counsel tonight. Seek again with patience.",
        ],
    },

    "Grief & Grace": {
        "family": "MYTHIC",
        "arcana": "XIII · Death",
        "description": "Tender, solemn, transformative. Where endings become beginnings.",
        "openings": [
            "Some sorrows need company to become bearable.",
            "Grief is not a problem to solve. It's a country to cross.",
            "The heart breaks open, not apart. There's a difference.",
            "Loss leaves a space. Sometimes that space becomes a door.",
            "To mourn fully is to love fully. Both take courage.",
            "The dead stay with us, you know. Just differently.",
            "Sorrow, witnessed, becomes something almost holy.",
            "Not all heaviness needs lifting. Some needs holding.",
        ],
        "venue_intros": [
            "A space to hold your sorrow:",
            "Where grief finds company:",
            "For the tender-hearted:",
            "The gentle ones gather at",
            "A refuge for mourning:",
            "Where loss is welcome:",
        ],
        "rejections": [
            "The grief-tenders are resting tonight, petal. Your sorrow is still valid.",
            "No mourning circle appeared. But the morning will come.",
            "I sought the tender spaces but they're closed tonight. Hold on.",
        ],
    },

    "Contemplative & Meditative": {
        "family": "MYTHIC",
        "arcana": "IX · The Hermit",
        "description": "Still, deep, lantern-lit. The quiet that restores.",
        "openings": [
            "Sometimes the loudest thing you can do is be still.",
            "The noise will wait. It always does. Come, be quiet for a while.",
            "Stillness isn't emptiness. It's fullness, waiting to be noticed.",
            "The answers aren't out there. They're in here. In the hush.",
            "Your nervous system is begging for mercy. I know a place.",
            "The world is so loud. Let's find where it's quiet.",
            "Rest isn't laziness. It's revolution.",
            "Breathe. Again. There. That's the beginning.",
        ],
        "venue_intros": [
            "A sanctuary of stillness:",
            "Where quiet lives:",
            "I've found the hush:",
            "For your weary mind:",
            "Silence gathers at",
            "The calm waits at",
        ],
        "rejections": [
            "Even the quiet places are full tonight, petal. Try the dawn.",
            "No still waters found. The world is too stirred up just now.",
            "I sought the silence but it's hiding. Tomorrow will be calmer.",
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # VELVET FAMILY — Seductive, glamorous, winking
    # ──────────────────────────────────────────────────────────────────────────

    "Cabaret & Glitter": {
        "family": "VELVET",
        "arcana": "VI · The Lovers",
        "description": "Glamorous, theatrical, winking. Sequins and shadows.",
        "openings": [
            "Sequins catch the light differently when the hour gets late...",
            "Glamour is armour, darling. And tonight you get to sparkle.",
            "The velvet curtain twitches. Something fabulous is about to happen.",
            "Glitter in your hair, mischief in your heart. That's the dress code.",
            "The stage is set. The question is: are you ready to be seen?",
            "Some nights are made for watching. Others are made for being watched.",
            "Feathers, sequins, the catch of breath — cabaret is a verb.",
            "The spotlight doesn't judge. It just illuminates.",
        ],
        "venue_intros": [
            "The curtain rises at",
            "Glamour awaits at",
            "I've found the sparkle:",
            "Where the fabulous gather:",
            "The spotlight falls on",
            "Sequins shimmer at",
        ],
        "rejections": [
            "The cabaret is dark tonight, petal. Even glamour needs beauty sleep.",
            "No glitter trail to follow this evening. The sequins are resting.",
            "I sought the sparkle but found only shadows. Another night will shine.",
        ],
    },

    "Late-Night Lark": {
        "family": "VELVET",
        "arcana": "XV · The Devil",
        "description": "Hedonistic, shadowy, permission-giving. The night's second act.",
        "openings": [
            "The respectable hours have ended. Now it gets interesting.",
            "Past midnight, the city shows you her other face.",
            "Some mischief requires darkness. Not for hiding — for blooming.",
            "The night is long and full of... well, that's up to you.",
            "Sin is such a strong word. Let's call it 'indulgence'.",
            "The small hours have their own morality. Looser. Kinder.",
            "What happens after midnight stays after midnight. Mostly.",
            "Your sensible self went to bed hours ago. Good.",
        ],
        "venue_intros": [
            "The late hours lead to",
            "After midnight, try",
            "I've found the night's secret:",
            "Where the nocturnal gather:",
            "The shadows welcome you at",
            "For your witching hour:",
        ],
        "rejections": [
            "Even the night owls have roosted, petal. Too late or too early.",
            "No late-night doors opened for me. The city sleeps, briefly.",
            "I sought the shadows but they're resting. Dawn approaches.",
        ],
    },

    "Nostalgic / Vintage / Retro": {
        "family": "VELVET",
        "arcana": "XVIII · The Moon",
        "description": "Dreamy, sepia-toned, bittersweet. Memory as atmosphere.",
        "openings": [
            "Some places remember when the city was different. Softer. Stranger.",
            "Nostalgia isn't about the past. It's about a feeling the present forgot.",
            "The patina of time makes everything more beautiful. Including you.",
            "Vintage isn't old. It's proven. Time-tested. Worthy.",
            "Memory and lamplight — the combination that makes magic.",
            "The past isn't dead. It's playing on a gramophone somewhere.",
            "Sepia-toned dreams in a high-definition world. Yes please.",
            "Some rooms feel like stepping into someone else's memory.",
        ],
        "venue_intros": [
            "A memory awaits at",
            "The past lingers at",
            "I've found the nostalgic:",
            "Where time softens:",
            "Step back in time at",
            "The vintage glow lives at",
        ],
        "rejections": [
            "The nostalgia hides tonight, petal. The present insists on itself.",
            "No vintage corners revealed themselves. Too much 'now' around.",
            "I sought the sepia but found only pixels. Tomorrow will remember.",
        ],
    },

    "Romanticised London": {
        "family": "VELVET",
        "arcana": "✦ · The Lark",
        "description": "The Lark herself. Knowing, warm, slightly mischievous.",
        "openings": [
            "London has a thousand faces. I know where the interesting ones hide.",
            "I've been flying these streets for a while now. I know a place.",
            "The city is vast, petal. But I have a map of the good bits.",
            "You came to the right bird. I've got somewhere perfect.",
            "London rewards the curious. And you're curious, aren't you?",
            "Between the guidebooks and the algorithms, there's me.",
            "The city keeps secrets. I keep a list of the secrets.",
            "Every neighbourhood has a heart. I know where they beat.",
        ],
        "venue_intros": [
            "I know just the place:",
            "Let me show you:",
            "Here's a secret:",
            "The city offers:",
            "I've got somewhere:",
            "Come with me to",
        ],
        "rejections": [
            "Even I don't know everywhere, petal. Try asking differently.",
            "My wings haven't found that particular door. Shall we try another?",
            "The city's keeping that one from me tonight. Ask again?",
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # WILD FAMILY — Urgent, electric, transformative
    # ──────────────────────────────────────────────────────────────────────────

    "Big Night Out": {
        "family": "WILD",
        "arcana": "VII · The Chariot",
        "description": "Momentum, victory, unstoppable. Tonight we conquer.",
        "openings": [
            "Tonight isn't for half-measures. Tonight is for glory.",
            "The city is yours. Take it.",
            "Some nights you remember forever. This could be one.",
            "Energy like this doesn't come often. Don't waste it.",
            "The chariot is moving. Are you getting on or not?",
            "Momentum is a drug. A legal one. Mostly.",
            "Big night energy requires big night venues. I know them.",
            "Fortune favours the bold. And tonight, you're bold.",
        ],
        "venue_intros": [
            "The night awaits at",
            "Go big at",
            "I've found your stage:",
            "Where the energy peaks:",
            "Tonight's destination:",
            "The city pulses at",
        ],
        "rejections": [
            "The big nights are hiding, petal. Even glory needs to recharge.",
            "No epic venues tonight. Sometimes small is beautiful too.",
            "I sought the spectacular but it's resting. Tomorrow will thunder.",
        ],
    },

    "Punchy / Protest": {
        "family": "WILD",
        "arcana": "VIII · Strength",
        "description": "Fierce, righteous, alive. Where conviction becomes action.",
        "openings": [
            "Anger is energy. Let's point it somewhere useful.",
            "The world needs changing. These are the places where changing begins.",
            "Complacency is comfortable. But you're not here for comfortable.",
            "Righteous fury, meet righteous venues.",
            "Some rooms are for resting. Others are for rising.",
            "The revolution will not be televised. But it will be localised.",
            "Strength isn't about muscles. It's about showing up.",
            "The fight is long. These places help you keep fighting.",
        ],
        "venue_intros": [
            "The resistance gathers at",
            "Find your fire at",
            "I've found the fighters:",
            "Where conviction lives:",
            "The righteous meet at",
            "Strength builds at",
        ],
        "rejections": [
            "The fighters are regrouping tonight, petal. Rest is resistance too.",
            "No rallying points found. But the cause remains.",
            "I sought the fierce but found quiet. Tomorrow will roar.",
        ],
    },

    "Queer Revelry": {
        "family": "WILD",
        "arcana": "XXI · The World",
        "description": "Joyful, liberated, whole. Where identity celebrates itself.",
        "openings": [
            "Where identity isn't tolerated — it's celebrated.",
            "The rainbow isn't just colours. It's a whole spectrum of belonging.",
            "Some spaces were built for you to be fully yourself. Finally.",
            "Pride isn't just a parade. It's a practice. Here's where to practice.",
            "Joy as resistance. Glamour as defiance. Welcome home.",
            "The world tried to shrink you. These places expand you back.",
            "Community isn't automatic. It's built, night after night, room after room.",
            "Your people are out there. Let me show you where they gather.",
        ],
        "venue_intros": [
            "Your people gather at",
            "Joy lives at",
            "I've found the rainbow:",
            "Where belonging blooms:",
            "Community awaits at",
            "Pride pulses at",
        ],
        "rejections": [
            "The queer spaces are quiet tonight, petal. Even joy needs sleep.",
            "No rainbow trails found. But the community endures.",
            "I sought the celebration but it's resting. Tomorrow will sparkle.",
        ],
    },

    "Group Energy": {
        "family": "WILD",
        "arcana": "XX · Judgement",
        "description": "Collective, rising, transformative. Where strangers become tribe.",
        "openings": [
            "There's something about a room full of strangers becoming something together.",
            "Alone we're interesting. Together we're unstoppable.",
            "The collective hum of humans choosing the same room, the same moment.",
            "Strangers into allies, allies into friends. It happens faster than you'd think.",
            "Some transformations require witnesses. These places provide them.",
            "The rising tide lifts all boats. Here's where the tide rises.",
            "Community is a verb. These places conjugate it.",
            "When enough people gather with intention, magic becomes inevitable.",
        ],
        "venue_intros": [
            "The collective gathers at",
            "Find your people at",
            "I've found the tribe:",
            "Where strangers connect:",
            "Community hums at",
            "The group energy peaks at",
        ],
        "rejections": [
            "The gatherings are quiet tonight, petal. Even tribes need solitude sometimes.",
            "No collective found. But you're never truly alone.",
            "I sought the crowd but found stillness. Tomorrow will buzz.",
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # TENDER FAMILY — Warm, soft, inclusive
    # ──────────────────────────────────────────────────────────────────────────

    "Folk & Intimate": {
        "family": "TENDER",
        "arcana": "III · The Empress",
        "description": "Warm, nurturing, homely. Where belonging wraps around you.",
        "openings": [
            "Some places feel like coming home, even the first time.",
            "Warmth isn't just temperature. It's welcome. It's 'stay a while'.",
            "The kettle's on, the door's open, the chairs are comfortable.",
            "Intimacy at scale is rare. These places manage it.",
            "Folk isn't a genre. It's a feeling. These places have it.",
            "Where 'cosy' isn't a marketing word but an actual experience.",
            "Small rooms, big hearts. The equation that makes magic.",
            "The opposite of lonely isn't crowded. It's held. It's known.",
        ],
        "venue_intros": [
            "Warmth waits at",
            "Come home to",
            "I've found the cosy:",
            "Where belonging lives:",
            "The hearth glows at",
            "Intimacy awaits at",
        ],
        "rejections": [
            "The cosy corners are full tonight, petal. Try the dawn shift.",
            "No warmth trails found. But the cold won't last.",
            "I sought the intimate but found crowds. Tomorrow will embrace.",
        ],
    },

    "Comic Relief": {
        "family": "TENDER",
        "arcana": "XIX · The Sun",
        "description": "Bright, healing, joyful. Where laughter does the heavy lifting.",
        "openings": [
            "Laughter is the exhale you forgot you were holding.",
            "Joy isn't frivolous. It's essential. Medically proven, probably.",
            "The sun is out, metaphorically. Time to bask.",
            "Some nights you need to think. Other nights you need to laugh until you cry.",
            "Comedy is tragedy plus time. These places accelerate the equation.",
            "The world is heavy. These places are light. Balance restored.",
            "Brightness isn't naivety. It's defiance. Laugh in the dark's face.",
            "Your face has forgotten how to smile. Let's fix that.",
        ],
        "venue_intros": [
            "The laughter lives at",
            "Joy awaits at",
            "I've found the bright:",
            "Where smiles happen:",
            "The sun shines at",
            "Lightness gathers at",
        ],
        "rejections": [
            "The comedians are sleeping tonight, petal. Even joy needs rest.",
            "No laughter trails found. But tomorrow will tickle.",
            "I sought the bright but found shadow. The sun will rise.",
        ],
    },

    "Wonder & Awe": {
        "family": "TENDER",
        "arcana": "XVII · The Star",
        "description": "Vast, humbling, beautiful. Where perspective restores itself.",
        "openings": [
            "Sometimes you need to feel small to feel whole again.",
            "Wonder is the antidote to cynicism. Awe is the cure for smallness.",
            "The universe is vast and you are tiny and somehow that's comforting.",
            "Beauty for its own sake. No agenda. Just... look.",
            "Perspective isn't found in mirrors. It's found in stars, in ceilings, in vastness.",
            "The sublime still exists. It's just hiding from the algorithms.",
            "Catch your breath. Lose your breath. Same thing, different doors.",
            "Some experiences make you gasp. These are those experiences.",
        ],
        "venue_intros": [
            "Wonder waits at",
            "Prepare to gasp at",
            "I've found the awe:",
            "Where beauty gathers:",
            "The vast awaits at",
            "Perspective lives at",
        ],
        "rejections": [
            "The wonders are hiding tonight, petal. Even awe needs mystery.",
            "No sublime appeared. But beauty is patient.",
            "I sought the vast but found the intimate. That's okay too.",
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # CURIOUS FAMILY — Playful, strange, experimental
    # ──────────────────────────────────────────────────────────────────────────

    "Playful & Weird": {
        "family": "CURIOUS",
        "arcana": "0 · The Fool",
        "description": "Gleeful, absurd, permission-giving. Where silliness is sacred.",
        "openings": [
            "Weird is just another word for 'hasn't been boring yet'.",
            "The Fool's journey begins with a single silly step.",
            "Playfulness isn't childish. It's the most adult thing you can do.",
            "Normal is a setting on a washing machine. Not a life goal.",
            "Permission to be absurd: granted. Permanently.",
            "The strange corners are the best corners. Trust me.",
            "Whimsy isn't weakness. It's weaponised joy.",
            "Life is too short for sensible. Come be weird with me.",
        ],
        "venue_intros": [
            "The weird awaits at",
            "Absurdity lives at",
            "I've found the playful:",
            "Where strange is welcome:",
            "Whimsy gathers at",
            "The peculiar pulses at",
        ],
        "rejections": [
            "The weirdness is napping, petal. Even absurdity needs a break.",
            "No strange trails found. The normal has temporarily won.",
            "I sought the peculiar but found ordinary. Tomorrow will be weirder.",
        ],
    },

    "Curious Encounters": {
        "family": "CURIOUS",
        "arcana": "I · The Magician",
        "description": "Experimental, inventive, surprising. Where discovery is the point.",
        "openings": [
            "Curiosity killed the cat but satisfaction brought it back.",
            "The question is more interesting than the answer. Always.",
            "I don't know what you'll find here. That's the point.",
            "Discovery is a drug. These places are dealers.",
            "The magic isn't in knowing. It's in finding out.",
            "Expect the unexpected. Or don't expect anything. Both work.",
            "Adventure is just curiosity with walking shoes on.",
            "The rabbit hole goes deeper. Want to follow?",
        ],
        "venue_intros": [
            "Discovery awaits at",
            "Curiosity leads to",
            "I've found the experimental:",
            "Where surprise lives:",
            "The unknown beckons at",
            "Wonder experiments at",
        ],
        "rejections": [
            "The experiments are paused tonight, petal. Even curiosity rests.",
            "No discoveries to be made. The unknown is hiding.",
            "I sought the surprising but found the familiar. Tomorrow will astonish.",
        ],
    },

    "Body-Based / Movement-Led": {
        "family": "CURIOUS",
        "arcana": "XII · The Hanged Man",
        "description": "Embodied, suspended, perspective-shifting. Where thinking stops and feeling starts.",
        "openings": [
            "Your body knows things your mind has forgotten.",
            "Stop thinking. Start moving. The rest follows.",
            "Sweat is just your stress leaving the building.",
            "The body keeps the score. Let's change the music.",
            "Movement isn't exercise. It's exorcism. The good kind.",
            "Get out of your head. Get into your hips.",
            "Physical, visceral, real. No screens, no thoughts, just flesh.",
            "Your nervous system wants to shake something off. Let it.",
        ],
        "venue_intros": [
            "Your body will thank you at",
            "Movement calls at",
            "I've found the physical:",
            "Where the body leads:",
            "Sweat gathers at",
            "The flesh rejoices at",
        ],
        "rejections": [
            "The movement spaces are still tonight, petal. Even bodies need rest.",
            "No physical trails found. The mind wins this round.",
            "I sought the embodied but found the cerebral. Tomorrow will sweat.",
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # SHARP FAMILY — Precise, intellectual, burning
    # ──────────────────────────────────────────────────────────────────────────

    "The Thoughtful Stage": {
        "family": "SHARP",
        "arcana": "IV · The Emperor",
        "description": "Structured, substantial, nourishing. Where ideas take the spotlight.",
        "openings": [
            "Theatre that makes you think is rarer than theatre that makes you laugh.",
            "The stage is a mirror. What will you see tonight?",
            "Drama isn't just for TV. The live kind hits different.",
            "Thoughtful doesn't mean boring. It means it stays with you.",
            "Some performances entertain. Others rearrange your furniture.",
            "The fourth wall exists to be broken. Thoughtfully.",
            "Art that asks questions is more valuable than art that gives answers.",
            "Tonight's show might change something. Are you ready?",
        ],
        "venue_intros": [
            "The stage awaits at",
            "Thoughtfulness lives at",
            "I've found the meaningful:",
            "Where drama deepens:",
            "The mirror reflects at",
            "Ideas perform at",
        ],
        "rejections": [
            "The stages are dark tonight, petal. Even drama needs intermission.",
            "No meaningful performances found. The muses are elsewhere.",
            "I sought the theatrical but found silence. Tomorrow will speak.",
        ],
    },

    "Rant & Rapture": {
        "family": "SHARP",
        "arcana": "XI · Justice",
        "description": "Passionate, righteous, on fire. Where truth gets loud.",
        "openings": [
            "Some truths need to be shouted. This is their pulpit.",
            "The space between rant and rapture is where revelation lives.",
            "Passion, unfiltered. Opinion, unleashed. Truth, on fire.",
            "Words like weapons. Words like medicine. Words like prayer.",
            "The prophets of now don't always look like prophets.",
            "When someone speaks their truth at full volume, walls shake.",
            "Eloquent rage is still eloquent.",
            "Conviction is sexy. Fight me.",
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
        "description": "Measured, alchemical, flowing. Where language shimmers.",
        "openings": [
            "Words, when they're right, can rearrange your insides.",
            "The voice is the oldest instrument. Still the most powerful.",
            "Poetry isn't dead. It's just hiding in rooms like this.",
            "Some people can make language do tricks. Others make it tell truths.",
            "Between the speaker and the listener, something transmutes.",
            "Storytelling is just organised truth. And organised truth is powerful.",
            "The right word at the right moment can change everything.",
            "Language that shimmers. The hush of the room, the lyric of the light.",
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

    # ──────────────────────────────────────────────────────────────────────────
    # GLOBAL FAMILY — Rhythmic, expansive, connected
    # ──────────────────────────────────────────────────────────────────────────

    "Global Rhythms": {
        "family": "GLOBAL",
        "arcana": "X · Wheel of Fortune",
        "description": "Expansive, connected, spinning. Where borders blur and culture sings.",
        "openings": [
            "Borders blur and culture sings. London holds the whole world.",
            "The rhythm came from somewhere else. Now it's everywhere.",
            "Music is the universal language. These places speak it fluently.",
            "The wheel turns, the world spins, the beat goes on.",
            "Every diaspora brought its drums. Listen.",
            "Global doesn't mean generic. It means generous.",
            "The planet's playlist, live and in person.",
            "Where culture cross-pollinates and something new grows.",
        ],
        "venue_intros": [
            "The world gathers at",
            "Borders blur at",
            "I've found the global:",
            "Where rhythms meet:",
            "Culture sings at",
            "The wheel turns at",
        ],
        "rejections": [
            "The world is quiet tonight, petal. Even rhythms need rest.",
            "No global beats found. The borders are solid tonight.",
            "I sought the expansive but found the local. Tomorrow will travel.",
        ],
    },

    "Melancholic Beauty": {
        "family": "GLOBAL",
        "arcana": "XVI · The Tower",
        "description": "Devastating, gorgeous, transformative. Where heartbreak becomes art.",
        "openings": [
            "Some beauty requires devastation first. This is that beauty.",
            "The tower falls. From the rubble, something grows.",
            "Heartbreak, when witnessed, becomes almost bearable.",
            "Not all tears are sad. Some are just... release.",
            "The gorgeous ache. The beautiful devastation. You know the feeling.",
            "Melancholy isn't sadness. It's sadness with good lighting.",
            "Some wounds need to be opened to heal properly.",
            "What fades, glows.",
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

    # ──────────────────────────────────────────────────────────────────────────
    # HOLDING FAMILY — Gentle, present, unhurried (CARE PATHWAYS)
    # ──────────────────────────────────────────────────────────────────────────

    "Care Pathway - Tier 2": {
        "family": "HOLDING",
        "arcana": "Care · Emotional Weight",
        "description": "Gentle, present, acknowledging. When someone carries something heavy.",
        "openings": [
            "That sounds like a lot to carry.",
            "I hear you. Let's find the right place for tonight.",
            "I'm glad you told me.",
            "That's heavy. I'm here.",
            "Let's find somewhere that might help.",
            "You don't have to carry that alone tonight.",
            "I understand. Let me help.",
            "That's real. Let's see what might ease it.",
        ],
        "venue_intros": [
            "Here's somewhere that might help:",
            "I know a place:",
            "This might be what you need:",
            "Let me show you:",
            "How about:",
            "There's this:",
        ],
        "rejections": [
            "I'm not sure I found the right place, but I'm still here.",
            "The search didn't find a match, but you're not alone.",
            "I couldn't find exactly that, but let's try something else.",
        ],
        "choice_preamble": "Would you like...",
        "choices": {
            "somewhere_quiet": "Somewhere quiet",
            "somewhere_to_move": "Somewhere to move",
            "something_to_laugh": "Something to make me laugh",
            "lets_wander": "Let's wander",
        },
    },

    "Care Pathway - Tier 3": {
        "family": "HOLDING",
        "arcana": "Care · Distress",
        "description": "Steady, unhurried, holding. When someone is struggling.",
        "openings": [
            "I hear you. I'm with you.",
            "That sounds heavy. Let me be your compass tonight.",
            "You don't need to know what you need — I can hold the map.",
            "I'm here. Let's find somewhere together.",
            "That's a lot. I'm not going anywhere.",
            "Let me help you find somewhere tonight.",
            "I'm listening. And I know some places that might help.",
            "You reached out. That matters. Let me help.",
        ],
        "venue_intros": [
            "Here's somewhere gentle:",
            "This place might hold you:",
            "Let me take you to:",
            "I think this might help:",
            "How about:",
            "There's somewhere that might help:",
        ],
        "rejections": [
            "I couldn't find exactly that, but I'm still here with you.",
            "The search came up empty, but you're not alone.",
            "I'll keep looking. You're not alone in this.",
        ],
        "choice_preamble": "Tonight, would you like...",
        "choices": {
            "sit_with_it": "Somewhere quiet to sit with it",
            "let_it_out": "Somewhere to let it out",
            "be_held": "Somewhere to be held by others",
            "draw_for_me": "Draw for me",
        },
        "resources_footer": "And if you need more than a place tonight, there are people who can hold that too.",
    },

    "Null State": {
        "family": "HOLDING",
        "arcana": "Care · Unknown",
        "description": "Present, curious, offering. When she doesn't understand but stays.",
        "openings": [
            "I'm not quite sure what you're after — but I'd love to find it with you.",
            "That's not ringing a bell, but let's wander and see what calls.",
            "Hmm, I'm not certain — but I have a few guesses.",
            "I don't recognise that, but I'm curious. Tell me more?",
            "My wings haven't found that particular door. But I know others.",
            "I'm not sure I understand, but I'd like to help.",
            "That's a new one for me. Let's explore together.",
            "I don't have an exact match, but I have some ideas.",
        ],
        "venue_intros": [
            "How about:",
            "Maybe try:",
            "Here's a thought:",
            "What about:",
            "Perhaps:",
            "Let me suggest:",
        ],
        "rejections": [
            "I really am stuck on this one, petal. Try different words?",
            "My map doesn't show that path. But there are other paths.",
            "I genuinely don't know that one. But I know other things.",
        ],
        "choice_preamble": "Would you like to...",
        "choices": {
            "draw_a_card": "Draw a card for me",
            "show_the_deck": "Show me the deck",
            "try_again": "Let me try again",
        },
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# VOICE FAMILY SUMMARIES
# ══════════════════════════════════════════════════════════════════════════════

VOICE_FAMILIES = {
    "MYTHIC": {
        "description": "Ancient, ritualistic, veiled",
        "energy": "The old ways, the sacred, the liminal",
        "arcana": ["Witchy & Wild", "Spiritual / Sacred / Mystical", "Grief & Grace", "Contemplative & Meditative"],
    },
    "VELVET": {
        "description": "Seductive, glamorous, winking",
        "energy": "Sparkle, shadows, the night's secrets",
        "arcana": ["Cabaret & Glitter", "Late-Night Lark", "Nostalgic / Vintage / Retro", "Romanticised London"],
    },
    "WILD": {
        "description": "Urgent, electric, transformative",
        "energy": "Momentum, fire, collective power",
        "arcana": ["Big Night Out", "Punchy / Protest", "Queer Revelry", "Group Energy"],
    },
    "TENDER": {
        "description": "Warm, soft, inclusive",
        "energy": "Home, belonging, gentle joy",
        "arcana": ["Folk & Intimate", "Comic Relief", "Wonder & Awe"],
    },
    "CURIOUS": {
        "description": "Playful, strange, experimental",
        "energy": "Discovery, whimsy, the body's wisdom",
        "arcana": ["Playful & Weird", "Curious Encounters", "Body-Based / Movement-Led"],
    },
    "SHARP": {
        "description": "Precise, intellectual, burning",
        "energy": "Ideas, conviction, language as art",
        "arcana": ["The Thoughtful Stage", "Rant & Rapture", "Word & Voice"],
    },
    "GLOBAL": {
        "description": "Rhythmic, expansive, connected",
        "energy": "Borders blurring, cultures singing",
        "arcana": ["Global Rhythms", "Melancholic Beauty"],
    },
    "HOLDING": {
        "description": "Gentle, present, unhurried",
        "energy": "Care, steadiness, not going anywhere",
        "arcana": ["Care Pathway - Tier 2", "Care Pathway - Tier 3", "Null State"],
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_voice_for_mood(mood: str) -> dict:
    """Get the voice profile for a given mood."""
    if mood in ARCANA_VOICES:
        return ARCANA_VOICES[mood]

    # Fuzzy match for partial mood names
    mood_lower = mood.lower()
    for key in ARCANA_VOICES:
        if mood_lower in key.lower() or key.lower() in mood_lower:
            return ARCANA_VOICES[key]

    # Default fallback to The Lark herself
    return ARCANA_VOICES.get("Romanticised London", list(ARCANA_VOICES.values())[0])


def get_care_voice(tier: str) -> dict:
    """Get the care pathway voice for a given tier."""
    if tier == "tier2" or tier == "emotional":
        return ARCANA_VOICES["Care Pathway - Tier 2"]
    elif tier == "tier3" or tier == "distress":
        return ARCANA_VOICES["Care Pathway - Tier 3"]
    elif tier == "null":
        return ARCANA_VOICES["Null State"]
    else:
        return ARCANA_VOICES["Null State"]


def get_profile_name(mood: str) -> str:
    """Get the arcana name for a given mood."""
    voice = get_voice_for_mood(mood)
    return voice.get("arcana", "✦ · The Lark")


def get_family_name(mood: str) -> str:
    """Get the voice family name for a given mood."""
    voice = get_voice_for_mood(mood)
    return voice.get("family", "VELVET")


def get_opening(mood: Optional[str] = None, tier: Optional[str] = None) -> str:
    """Get a random opening line for the given mood or care tier."""
    if tier:
        voice = get_care_voice(tier)
    elif mood:
        voice = get_voice_for_mood(mood)
    else:
        voice = ARCANA_VOICES["Romanticised London"]

    openings = voice.get("openings", [])
    if openings:
        return random.choice(openings)
    return "The city holds secrets for those who seek them..."


def get_venue_intro(mood: Optional[str] = None, tier: Optional[str] = None) -> str:
    """Get a random venue introduction for the given mood or care tier."""
    if tier:
        voice = get_care_voice(tier)
    elif mood:
        voice = get_voice_for_mood(mood)
    else:
        voice = ARCANA_VOICES["Romanticised London"]

    intros = voice.get("venue_intros", [])
    if intros:
        return random.choice(intros)
    return "I've found something:"


def get_rejection_message(mood: Optional[str] = None, tier: Optional[str] = None) -> str:
    """Get a random rejection message for the given mood or care tier."""
    if tier:
        voice = get_care_voice(tier)
    elif mood:
        voice = get_voice_for_mood(mood)
    else:
        voice = ARCANA_VOICES["Romanticised London"]

    rejections = voice.get("rejections", [])
    if rejections:
        return random.choice(rejections)
    return "The city keeps that secret for another night, petal."


def get_choices(tier: str) -> dict:
    """Get the choice buttons for a care tier."""
    voice = get_care_voice(tier)
    return voice.get("choices", {})


def get_choice_preamble(tier: str) -> str:
    """Get the preamble before choices for a care tier."""
    voice = get_care_voice(tier)
    return voice.get("choice_preamble", "Would you like...")


def get_resources_footer(tier: str) -> Optional[str]:
    """Get the resources footer for a care tier (if any)."""
    voice = get_care_voice(tier)
    return voice.get("resources_footer", None)


def get_current_voice_profile(mood: Optional[str] = None) -> dict:
    """Get the current voice profile info for debugging/display."""
    voice = get_voice_for_mood(mood) if mood else ARCANA_VOICES["Romanticised London"]
    return {
        "family": voice.get("family", "VELVET"),
        "arcana": voice.get("arcana", "✦ · The Lark"),
        "description": voice.get("description", ""),
    }


# ══════════════════════════════════════════════════════════════════════════════
# SURPRISE / RANDOM VENUE RESPONSES
# ══════════════════════════════════════════════════════════════════════════════

SURPRISE_OPENINGS = [
    "The cards have been shuffled. Here's what emerged:",
    "I reached into the dark and pulled out this:",
    "The city whispered a name. I listened:",
    "Fate has opinions tonight:",
    "When in doubt, let the universe decide:",
    "I asked London for a secret. She answered:",
    "Random isn't random when the city knows what you need:",
    "The deck has spoken:",
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


# ══════════════════════════════════════════════════════════════════════════════
# TESTING
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("  THE LARK'S 8 VOICE FAMILIES — TEST")
    print("=" * 70)

    # Show all families and their arcana
    print("\n📚 VOICE FAMILIES:\n")

    for family, info in VOICE_FAMILIES.items():
        print(f"\n{family}: {info['description']}")
        print(f"  Energy: {info['energy']}")
        print(f"  Arcana: {', '.join(info['arcana'])}")

    # Sample each family
    print("\n\n🎭 SAMPLE OPENINGS BY FAMILY:\n")
    print("-" * 70)

    sample_moods = [
        "Witchy & Wild",           # MYTHIC
        "Cabaret & Glitter",       # VELVET
        "Big Night Out",           # WILD
        "Folk & Intimate",         # TENDER
        "Playful & Weird",         # CURIOUS
        "The Thoughtful Stage",    # SHARP
        "Global Rhythms",          # GLOBAL
    ]

    for mood in sample_moods:
        voice = get_voice_for_mood(mood)
        print(f"\n{voice['family']} — {mood}")
        print(f"  Opening: \"{get_opening(mood)}\"")
        print(f"  Intro: \"{get_venue_intro(mood)}\"")

    # Sample care pathways
    print("\n\n💚 CARE PATHWAY VOICES:\n")
    print("-" * 70)

    for tier in ["tier2", "tier3", "null"]:
        voice = get_care_voice(tier)
        print(f"\n{voice['arcana']}")
        print(f"  Opening: \"{get_opening(tier=tier)}\"")
        print(f"  Choices: {get_choices(tier)}")
        if get_resources_footer(tier):
            print(f"  Footer: \"{get_resources_footer(tier)}\"")

    print("\n" + "=" * 70)
    print("  All 8 voice families ready! 🕊️")
    print("=" * 70)
