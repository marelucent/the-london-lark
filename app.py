#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# The London Lark - Web Interface

"""
A simple web interface for The London Lark.
Run this, then open http://localhost:5000 in your browser.
"""

from flask import Flask, render_template, request, jsonify
from prompt_interpreter import interpret_prompt
from mood_resolver import resolve_from_keywords
from safety_detector import (
    detect_emotional_state,
    detect_care_state,
    get_tier_response_config,
    get_null_state_config,
    get_therapeutic_arcana,
    get_therapeutic_spread_arcana,
    get_care_pathway_arcana_spread,
    get_state_preamble,
    get_state_textures,
    get_texture_arcana_pool,
    THERAPEUTIC_ARCANA,
    TEXTURE_ARCANA_MAPPING
)
from venue_matcher import match_venues, match_venues_with_adjacency, match_surprise_with_adjacency
from emotional_geography import is_surprise_me_query
from response_generator import generate_response, get_current_voice_profile, generate_surprise_response
from parse_venues import load_parsed_venues
from lark_metrics import get_metrics
from lark_mind import chat_with_lark, get_time_aware_greeting as get_lark_mind_greeting
from card_parser import parse_response as parse_card_response
from datetime import datetime
from zoneinfo import ZoneInfo
import random
import json
import os
import time

# Import logging and protection
from lark_logger import (
    get_conversation_logger,
    get_usage_tracker,
    get_abuse_logger,
    get_feedback_logger,
    log_chat_interaction,
    log_ask_interaction,
    generate_session_id
)
from lark_protection import (
    get_rate_limiter,
    get_budget_guard,
    get_client_ip,
    hash_ip,
    check_and_flag_content,
    validate_input,
    validate_conversation_length,
    rate_limited,
    budget_protected,
    validate_input_length,
    protected_endpoint,
    get_rate_limit_message,
    MAX_INPUT_LENGTH,
    MAX_TURNS_PER_CONVERSATION
)

# Import voice profile system for debug info (v2 with 8 voice families)
try:
    from poetic_templates_v2 import get_profile_name, get_opening
    HAS_VOICE_PROFILES = True
except ImportError:
    HAS_VOICE_PROFILES = False
    get_profile_name = lambda x: "GENERAL"
    get_opening = lambda x: None

app = Flask(__name__)

def load_core_moods():
    """Load the 23 core mood buttons from mood_index.json"""
    try:
        # Try different possible paths
        possible_paths = [
            'mood_index.json',
            os.path.join(os.path.dirname(__file__), 'mood_index.json'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    mood_index = json.load(f)
                return list(mood_index.keys())
        
        return []
    except Exception as e:
        print(f"Warning: Could not load mood_index.json: {e}")
        return []

def get_time_aware_greeting():
    """Generate a poetic greeting based on current time and day in London"""
    london_tz = ZoneInfo('Europe/London')
    now = datetime.now(london_tz)
    hour = now.hour
    day_name = now.strftime('%A')

    # Check for special day/time combinations first
    if day_name == 'Friday' and 18 <= hour <= 23:
        return "The weekend threshold... where will you cross over?"
    elif day_name == 'Saturday' and (hour >= 20 or hour < 2):
        return "When the city is most alive..."
    elif day_name == 'Sunday' and 12 <= hour <= 17:
        return "In the gentle decay of Sunday..."
    elif day_name == 'Monday' and 6 <= hour <= 11:
        return "A new week unfolds..."

    # Default time-of-day greetings
    if 6 <= hour <= 11:
        return "The city stirs, petal. What calls to you this morning?"
    elif 12 <= hour <= 17:
        return "In the lull between rush... what does your afternoon need?"
    elif 18 <= hour <= 23:
        return "As streetlights flicker awake... where will you wander tonight?"
    else:  # 0-5 (midnight to 5am)
        return "For the night-wanderers and the sleepless... the city holds space for you."

def get_input_helper():
    """Generate input placeholder and helper text"""
    helpers = [
        {
            "main": "Tell me what you're craving—a mood, a feeling, a type of night.",
            "sub": "I'll find the corners of London that match."
        },
        {
            "main": "What kind of evening calls to you?",
            "sub": "Describe a feeling, a vibe, a longing."
        },
        {
            "main": "Whisper your mood to me, petal.",
            "sub": "I know the city's secret corners."
        }
    ]
    return random.choice(helpers)

def get_placeholder():
    """Generate input placeholder text"""
    placeholders = [
        "Something folk and intimate...",
        "I need queer joy tonight...",
        "Somewhere melancholy but beautiful...",
        "A late-night place with good energy...",
        "Somewhere to feel alive..."
    ]
    return random.choice(placeholders)


def handle_surprise_me_query():
    """
    Handle "I don't know" / "surprise me" queries with fate-based drawing.

    Returns 3 venues:
    - Card 1: Random arcana (fate chooses)
    - Card 2: Adjacent to Card 1
    - Card 3: Adjacent to Card 1 (different neighbor)

    Maximum variety across arcana.
    """
    # Get surprise matches with adjacency
    matches = match_surprise_with_adjacency()

    if not matches:
        return jsonify({
            'responses': [{
                'text': "The cards are silent tonight, petal. Try whispering something else?",
                'venue_name': None,
                'area': None,
                'website': None
            }],
            'mood': None,
            'confidence': 1.0,
            'venue_count': 0,
            'is_surprise': True
        })

    # Generate responses for each venue
    responses = []
    first_arcana = None

    for i, venue in enumerate(matches):
        # Get the arcana for voice profile
        raw_data = venue.get('raw_data', {})
        venue_arcana = raw_data.get('arcana', 'Romanticised London')

        if i == 0:
            first_arcana = venue_arcana

        response_text = generate_response(venue, {'mood': venue_arcana})
        responses.append({
            'text': response_text,
            'venue_name': venue.get('name', ''),
            'area': venue.get('area', ''),
            'website': venue.get('website', ''),
            'whisper': venue.get('whisper', ''),
            'arcana': venue_arcana,  # Include each venue's arcana for proper card styling
            'is_adjacent': venue.get('is_adjacent', False),
            'is_fate_draw': venue.get('is_fate_draw', False)
        })

    # Surprise me opening lines
    surprise_openings = [
        "Then let's see what the cards say...",
        "The deck knows what you need, even if you don't.",
        "Fate deals you these three...",
        "Close your eyes. Point. Here's where your finger lands.",
        "When you don't know, the city knows for you."
    ]

    return jsonify({
        'responses': responses,
        'mood': first_arcana,
        'confidence': 1.0,
        'venue_count': len(matches),
        'is_surprise': True,
        'opening_line': random.choice(surprise_openings),
        'safety': {
            'tier': None,
            'show_soft_footer': False,
            'show_support_box': False,
            'show_crisis_resources': False,
            'lark_preamble': None
        },
        'debug': {
            'reason': 'surprise_me_query',
            'drawing_method': 'fate_with_adjacency'
        }
    })


@app.route('/')
def home():
    """Serve the main page"""
    greeting = get_time_aware_greeting()
    helper = get_input_helper()
    placeholder = get_placeholder()
    core_moods = load_core_moods()
    
    return render_template('index.html', 
                          greeting=greeting,
                          helper=helper,
                          placeholder=placeholder,
                          core_moods=core_moods)

@app.route('/about')
def about():
    """Serve the about page"""
    return render_template('about.html')

@app.route('/resources')
def resources():
    """Serve the support resources page"""
    return render_template('resources.html')

@app.route('/arcana', methods=['GET'])
def get_all_arcana():
    """Return all 23 arcana with their venue counts for the Full Deck view"""
    try:
        all_venues = load_parsed_venues()
        
        # Count venues per arcana
        arcana_counts = {}
        for venue in all_venues:
            arcana = venue.get('arcana', 'Romanticised London')
            if arcana not in arcana_counts:
                arcana_counts[arcana] = 0
            arcana_counts[arcana] += 1
        
        # Build response list
        arcana_list = []
        for mood, count in arcana_counts.items():
            arcana_list.append({
                'mood': mood,
                'venue_count': count
            })
        
        # Sort by the standard arcana order
        arcana_order = [
            'Playful & Weird', 'Curious Encounters', 'Witchy & Wild', 'Folk & Intimate',
            'The Thoughtful Stage', 'Spiritual / Sacred / Mystical', 'Cabaret & Glitter',
            'Big Night Out', 'Punchy / Protest', 'Contemplative & Meditative', 'Global Rhythms',
            'Rant & Rapture', 'Body-Based / Movement-Led', 'Grief & Grace', 'Word & Voice',
            'Late-Night Lark', 'Melancholic Beauty', 'Wonder & Awe', 'Nostalgic / Vintage / Retro',
            'Comic Relief', 'Group Energy', 'Queer Revelry', 'Romanticised London'
        ]
        
        # Create ordered list, including any arcana with 0 venues
        ordered_list = []
        for mood in arcana_order:
            count = arcana_counts.get(mood, 0)
            ordered_list.append({
                'mood': mood,
                'venue_count': count
            })
        
        return jsonify({
            'arcana': ordered_list,
            'total_venues': len(all_venues)
        })
        
    except Exception as e:
        return jsonify({
            'error': f"Could not load arcana: {str(e)}"
        }), 500

@app.route('/arcana/<path:mood>', methods=['GET'])
def get_arcana_venues(mood):
    """Return all venues for a specific arcana"""
    try:
        all_venues = load_parsed_venues()
        
        # Filter venues by arcana
        matching_venues = [v for v in all_venues if v.get('arcana') == mood]
        
        # Format for frontend
        venues_list = []
        for venue in matching_venues:
            venues_list.append({
                'name': venue.get('display_name', venue.get('name', 'Unnamed')),
                'area': venue.get('area', venue.get('location', 'London')),
                'whisper': venue.get('whisper', ''),
                'blurb': venue.get('blurb', venue.get('tone_notes', '')),
                'website': venue.get('website', venue.get('url', ''))
            })
        
        # Sort alphabetically by name
        venues_list.sort(key=lambda v: v['name'].lower())
        
        return jsonify({
            'mood': mood,
            'venue_count': len(venues_list),
            'venues': venues_list
        })
        
    except Exception as e:
        return jsonify({
            'error': f"Could not load venues: {str(e)}"
        }), 500

@app.route('/surprise', methods=['POST'])
@rate_limited
def surprise_me():
    """Return a single random venue with first-person poetic response"""
    try:
        # Load all venues
        all_venues = load_parsed_venues()

        if not all_venues:
            return jsonify({
                'response': "I'm out of surprises right now, petal. Try asking me something specific?",
                'venue_name': None,
                'area': None,
                'website': None,
                'mood': None
            })

        # Check if a specific arcana was requested (for filtered draws)
        requested_arcana = request.json.get('arcana') if request.json else None

        # Filter venues by arcana if specified
        if requested_arcana:
            filtered_venues = [v for v in all_venues if v.get('arcana') == requested_arcana]
            if not filtered_venues:
                # Fallback to all venues if no matches for the arcana
                filtered_venues = all_venues
        else:
            filtered_venues = all_venues

        # Pick a random venue from the (possibly filtered) pool
        random_venue_raw = random.choice(filtered_venues)

        # Get the venue's arcana for display (this is the key fix!)
        venue_arcana = random_venue_raw.get("arcana", None)

        # Normalize to expected format
        normalized_venue = {
            "name": random_venue_raw.get("display_name", random_venue_raw.get("name", "Unnamed venue")),
            "area": random_venue_raw.get("area", random_venue_raw.get("location", "London")),
            "vibe_note": random_venue_raw.get("tone_notes", random_venue_raw.get("blurb", "An experience beyond words")),
            "typical_start_time": random_venue_raw.get("typical_start_time", ""),
            "price": random_venue_raw.get("price", "TBC"),
            "website": random_venue_raw.get("website", random_venue_raw.get("url", "")),
            "mood_tags": random_venue_raw.get("moods", random_venue_raw.get("mood_tags", []))
        }

        # Generate first-person surprise response
        response_text = generate_surprise_response(normalized_venue)

        # Return the venue's arcana as 'mood' (this is what the frontend expects for arcanaMap lookup)
        return jsonify({
            'response': response_text,
            'venue_name': normalized_venue["name"],
            'area': normalized_venue["area"],
            'website': normalized_venue["website"],
            'mood': venue_arcana,
            'is_surprise': True
        })

    except Exception as e:
        return jsonify({
            'error': f"Something went awry: {str(e)}",
            'response': "I stumbled, petal. Try again?"
        }), 500

@app.route('/ask', methods=['POST'])
@rate_limited
@validate_input_length
def ask_lark():
    """
    Process a query and return the Lark's response.

    Protected by:
    - Rate limiting (per IP)
    - Input length validation
    """
    start_time = time.time()
    session_id = request.json.get('session_id') or generate_session_id()
    ip = get_client_ip()
    ip_hash = hash_ip(ip)

    try:
        user_prompt = request.json.get('prompt', '').strip()

        # Check for prompt injection/abuse (flag, don't block)
        if user_prompt:
            content_check = check_and_flag_content(user_prompt, session_id, ip_hash)
            if content_check['flags']:
                print(f"   Flags detected: {content_check['flags']}")

        # Safety check — detect emotional state before venue matching
        emotional_tier, safety_keywords = detect_emotional_state(user_prompt)
        safety_config = get_tier_response_config(emotional_tier)
        
        if emotional_tier:
            print(f"   🛡️ Safety tier: {emotional_tier} (keywords: {safety_keywords})")

        if not user_prompt:
            return jsonify({
                'response': "I'm listening... but I heard only silence. Speak, petal.",
                'mood': None,
                'confidence': 0,
                'venue_count': 0
            })

        # Check for "I don't know" / "surprise me" queries BEFORE normal processing
        if is_surprise_me_query(user_prompt):
            print(f"   🎲 Surprise me query detected: '{user_prompt}'")
            return handle_surprise_me_query()

        # Process through the pipeline
        filters = interpret_prompt(user_prompt)

        # Debug: Log what was extracted
        print(f"\n🔍 DEBUG: Interpreting '{user_prompt}'")
        print(f"   Initial filters: {filters}")

        # Resolve mood if not found
        mood_confidence = 1.0
        if not filters.get("mood"):
            keywords = user_prompt.lower().split()
            mood, confidence = resolve_from_keywords(keywords)
            filters["mood"] = mood
            mood_confidence = confidence
            print(f"   Mood resolution: mood={mood}, confidence={confidence}")
        else:
            print(f"   Direct mood match: {filters.get('mood')}")

        # =====================================================================
        # CONVERSATIONAL FALLBACKS (Upgrade 4)
        # Handle location-only, vague, or unclear queries with helpful questions
        # =====================================================================

        # Location-only query: "Brixton", "Hackney", "Peckham"
        if filters.get("location_only") and emotional_tier is None:
            location = filters.get("location")
            print(f"   💬 Location-only query detected: '{location}'")

            # Lark asks for mood/intent
            location_prompts = [
                f"{location} hums with secrets. What kind of night are you dreaming of?",
                f"{location} has many doors. What are you seeking tonight?",
                f"Ah, {location}... but what mood calls you there? Tell me more.",
                f"{location} holds multitudes. Are you after something wild? Quiet? Strange?"
            ]
            import random
            chosen_prompt = random.choice(location_prompts)

            return jsonify({
                'responses': [{
                    'text': chosen_prompt,
                    'venue_name': None,
                    'area': None,
                    'website': None
                }],
                'mood': None,
                'confidence': 0.0,
                'venue_count': 0,
                'filters': filters,
                'needs_clarification': True,
                'clarification_type': 'location_only',
                'safety': {
                    'tier': emotional_tier,
                    'show_soft_footer': False,
                    'show_support_box': False,
                    'show_crisis_resources': False,
                    'lark_preamble': None
                },
                'debug': {
                    'reason': 'location_only_query',
                    'location': location
                }
            })

        # Vague query: "something nice", "somewhere different", "anything interesting"
        if filters.get("is_vague") and not filters.get("mood") and emotional_tier is None:
            print(f"   💬 Vague query detected: '{user_prompt}'")

            # Check for specific vague patterns
            prompt_lower = user_prompt.lower()
            if "nice" in prompt_lower:
                clarification = "Nice can mean so many things... Cosy? Fancy? Quiet? Alive? Tell me more, darling."
            elif "different" in prompt_lower:
                clarification = "Different how? Stranger? Softer? Wilder? I'm all ears."
            elif "interesting" in prompt_lower:
                clarification = "Interesting... but in which direction? Curious? Challenging? Playful?"
            elif "something" in prompt_lower or "somewhere" in prompt_lower:
                clarification = "Something... but what kind? Help me find your door."
            else:
                clarification = "I'm intrigued, but I need a little more. What feeling are you chasing tonight?"

            return jsonify({
                'responses': [{
                    'text': clarification,
                    'venue_name': None,
                    'area': None,
                    'website': None
                }],
                'mood': None,
                'confidence': 0.0,
                'venue_count': 0,
                'filters': filters,
                'needs_clarification': True,
                'clarification_type': 'vague_query',
                'safety': {
                    'tier': emotional_tier,
                    'show_soft_footer': False,
                    'show_support_box': False,
                    'show_crisis_resources': False,
                    'lark_preamble': None
                },
                'debug': {
                    'reason': 'vague_query',
                    'prompt': user_prompt
                }
            })

        # =====================================================================
        # SAFETY TIER PRIORITY CHECK
        # If distress or crisis detected, handle that FIRST before mood checks
        # =====================================================================

        # Tier 2 (Emotional) and Tier 3 (Distress) - show care pathway with context-aware textures
        if emotional_tier in ('emotional', 'distress'):
            # Detect which emotional state the user is in (ANGRY, LONELY, OVERWHELMED, GRIEF, LOW_HEAVY)
            care_state, state_keywords = detect_care_state(user_prompt)
            print(f"   🛡️ Care pathway: {emotional_tier} tier detected, state: {care_state}")
            print(f"      State keywords: {state_keywords}")

            # Get state-specific preamble and textures
            state_preamble = get_state_preamble(care_state)
            state_textures = get_state_textures(care_state)

            # For distress tier, use the state preamble; for emotional tier, may use a softer variant
            preamble = state_preamble if emotional_tier == 'distress' else state_preamble

            return jsonify({
                'responses': [],  # No venues yet - wait for texture choice
                'mood': None,
                'confidence': 0.0,
                'venue_count': 0,
                'filters': filters,
                'safety': {
                    'tier': emotional_tier,
                    'care_state': care_state,
                    'show_soft_footer': safety_config.get('show_soft_footer', False),
                    'show_support_box': False,  # Now using care pathway
                    'show_crisis_resources': False,
                    'show_care_pathway': True,
                    'use_texture_cards': True,  # New: use texture cards instead of buttons
                    'textures': state_textures,  # New: state-specific texture options
                    'resources_footer': safety_config.get('resources_footer'),
                    'lark_preamble': preamble
                },
                'debug': {
                    'reason': 'care_pathway',
                    'tier': emotional_tier,
                    'care_state': care_state,
                    'keywords': safety_keywords,
                    'state_keywords': state_keywords
                }
            })

        # Tier 4 (Crisis) - show resources first, then optionally gentle venues
        if emotional_tier == 'crisis':
            print(f"   🛡️ Crisis tier detected, showing resources first")

            # For crisis, we might still want to offer gentle venues
            gentle_venues = []
            try:
                all_venues = load_parsed_venues()
                gentle_arcana = [
                    'Contemplative & Meditative',
                    'Folk & Intimate',
                    'Grief & Grace',
                    'Spiritual / Sacred / Mystical'
                ]
                gentle_venues = [v for v in all_venues if v.get('arcana') in gentle_arcana]
                random.shuffle(gentle_venues)
                gentle_venues = gentle_venues[:1]  # Just one gentle option for crisis
            except Exception as e:
                print(f"   Could not load gentle venues: {e}")

            # Build response with optional gentle venue
            responses = []
            if gentle_venues:
                venue = gentle_venues[0]
                response_text = generate_response(venue, {'mood': venue.get('arcana')})
                responses.append({
                    'text': response_text,
                    'venue_name': venue.get('name', venue.get('display_name', '')),
                    'area': venue.get('area', venue.get('location', '')),
                    'website': venue.get('website', venue.get('url', ''))
                })

            return jsonify({
                'responses': responses,
                'mood': None,
                'confidence': 0.0,
                'venue_count': len(responses),
                'filters': filters,
                'safety': {
                    'tier': emotional_tier,
                    'show_soft_footer': False,
                    'show_support_box': False,
                    'show_crisis_resources': True,
                    'show_care_pathway': False,
                    'care_choices': None,
                    'resources_footer': None,
                    'lark_preamble': safety_config.get('lark_preamble')
                },
                'debug': {
                    'reason': 'crisis_tier',
                    'tier': emotional_tier,
                    'keywords': safety_keywords
                }
            })

        # =====================================================================
        # CONFIDENCE THRESHOLD CHECKS (only reached if no safety override)
        # =====================================================================
        
        # If no mood detected at all (None with 0.0 confidence), show conversational fallback
        if filters.get("mood") is None and mood_confidence == 0.0:
            print(f"   ❌ No recognizable mood keywords found - asking for clarification")

            # Try text search first - maybe they're looking for a specific venue by name
            from venue_matcher import search_venue_text
            from parse_venues import load_parsed_venues
            all_venues = load_parsed_venues()
            name_matches, text_matches = search_venue_text(user_prompt, all_venues, filters.get("location"))

            # If we found text matches, return those instead of null state
            if name_matches or text_matches:
                print(f"   ✨ Found text matches despite no mood - using them")
                matches = name_matches[:3] if name_matches else text_matches[:3]
                from venue_matcher import normalize_venue
                normalized = [normalize_venue(v) for v in matches]

                responses = []
                for venue in normalized:
                    response = generate_response(venue, filters)
                    raw_data = venue.get('raw_data', {})
                    venue_arcana = raw_data.get('arcana', 'Unknown')
                    responses.append({
                        'text': response,
                        'venue_name': venue.get('name', ''),
                        'area': venue.get('area', ''),
                        'website': venue.get('website', ''),
                        'whisper': venue.get('whisper', ''),
                        'arcana': venue_arcana,
                        'is_adjacent': False
                    })

                return jsonify({
                    'responses': responses,
                    'mood': None,
                    'confidence': 0.5,  # Medium confidence for text match
                    'venue_count': len(responses),
                    'filters': filters,
                    'safety': {
                        'tier': emotional_tier,
                        'show_soft_footer': safety_config.get('show_soft_footer', False),
                        'show_support_box': safety_config.get('show_support_box', False),
                        'show_crisis_resources': safety_config.get('show_crisis_resources', False),
                        'lark_preamble': None
                    },
                    'debug': {
                        'reason': 'text_search_match',
                        'name_matches': len(name_matches),
                        'text_matches': len(text_matches)
                    }
                })

            # No text matches either - offer conversational help
            # Lark-voiced fallback messages
            fallback_messages = [
                "I'm not sure I found that door. Tell me more — or shall I draw for you?",
                "That word is new to me. Shall I draw a card instead, or tell me what you're seeking?",
                "I couldn't quite catch that. What kind of evening calls to you?",
                "Hmm, I'm not finding a thread there. Could you say more about what you're after?"
            ]
            import random
            chosen_message = random.choice(fallback_messages)

            null_config = get_null_state_config()
            return jsonify({
                'responses': [{
                    'text': chosen_message,
                    'venue_name': None,
                    'area': None,
                    'website': None
                }],
                'mood': None,
                'confidence': 0.0,
                'venue_count': 0,
                'filters': filters,
                'null_state': {
                    'is_null': True,
                    'preamble': null_config['preamble'],
                    'choices': null_config['choices']
                },
                'needs_clarification': True,
                'clarification_type': 'no_match',
                'safety': {
                    'tier': emotional_tier,
                    'show_soft_footer': safety_config.get('show_soft_footer', False),
                    'show_support_box': safety_config.get('show_support_box', False),
                    'show_crisis_resources': safety_config.get('show_crisis_resources', False),
                    'show_care_pathway': False,
                    'care_choices': None,
                    'resources_footer': None,
                    'lark_preamble': None
                },
                'debug': {
                    'reason': 'null_state_with_clarification',
                    'keywords_checked': user_prompt.lower().split()
                }
            })

        # If confidence is very low (< 0.3), try text search first, then ask for clarification
        if mood_confidence < 0.3:
            print(f"   ⚠️ Very low confidence ({mood_confidence}), trying text search before asking")

            # Try text search as fallback
            from venue_matcher import search_venue_text
            from parse_venues import load_parsed_venues
            all_venues = load_parsed_venues()
            name_matches, text_matches = search_venue_text(user_prompt, all_venues, filters.get("location"))

            if name_matches or text_matches:
                print(f"   ✨ Found text matches despite low confidence - using them")
                matches = name_matches[:3] if name_matches else text_matches[:3]
                from venue_matcher import normalize_venue
                normalized = [normalize_venue(v) for v in matches]

                responses = []
                for venue in normalized:
                    response = generate_response(venue, filters)
                    raw_data = venue.get('raw_data', {})
                    venue_arcana = raw_data.get('arcana', 'Unknown')
                    responses.append({
                        'text': response,
                        'venue_name': venue.get('name', ''),
                        'area': venue.get('area', ''),
                        'website': venue.get('website', ''),
                        'whisper': venue.get('whisper', ''),
                        'arcana': venue_arcana,
                        'is_adjacent': False
                    })

                return jsonify({
                    'responses': responses,
                    'mood': filters.get('mood'),
                    'confidence': 0.5,  # Bump confidence for text match
                    'venue_count': len(responses),
                    'filters': filters,
                    'safety': {
                        'tier': emotional_tier,
                        'show_soft_footer': safety_config['show_soft_footer'],
                        'show_support_box': safety_config['show_support_box'],
                        'show_crisis_resources': safety_config['show_crisis_resources'],
                        'lark_preamble': safety_config['lark_preamble']
                    },
                    'debug': {
                        'reason': 'text_search_fallback',
                        'original_confidence': mood_confidence
                    }
                })

            # No text matches - ask for clarification in Lark's voice
            mood_detected = filters.get('mood', 'something')
            clarification_messages = [
                f"I hear a whisper of '{mood_detected}' in your words, but I'm not certain. What kind of night are you dreaming of?",
                f"I sense something in '{mood_detected}'... but tell me more. What feeling are you chasing?",
                f"'{mood_detected}' echoes faintly. Help me understand — what draws you tonight?"
            ]
            import random
            chosen_message = random.choice(clarification_messages)

            return jsonify({
                'responses': [{
                    'text': chosen_message,
                    'venue_name': None,
                    'area': None,
                    'website': None
                }],
                'mood': filters.get('mood'),
                'confidence': mood_confidence,
                'venue_count': 0,
                'filters': filters,
                'needs_clarification': True,
                'clarification_type': 'low_confidence',
                'safety': {
                    'tier': emotional_tier,
                    'show_soft_footer': safety_config['show_soft_footer'],
                    'show_support_box': safety_config['show_support_box'],
                    'show_crisis_resources': safety_config['show_crisis_resources'],
                    'lark_preamble': safety_config['lark_preamble']
                },
                'debug': {
                    'reason': 'low_confidence',
                    'threshold': 0.3
                }
            })

        # If confidence is moderate (0.3-0.5), warn but proceed cautiously
        if mood_confidence < 0.5:
            print(f"   ⚠️ Moderate confidence ({mood_confidence}), proceeding with caution")

        # Get voice profile for the mood
        voice_profile_name = get_profile_name(filters.get("mood"))
        voice_profile_info = get_current_voice_profile(filters.get("mood"))
        print(f"   🎭 Voice profile: {voice_profile_name}")

        # Match venues with adjacency-based drawing (2 primary + 1 adjacent)
        matches = match_venues_with_adjacency(filters)
        print(f"   Matched {len(matches)} venues (with adjacency)")

        # Log metrics
        metrics = get_metrics()
        metrics.log_query(filters, mood_confidence, len(matches))

        # Generate opening line (the Lark's preamble)
        opening_line = None
        if HAS_VOICE_PROFILES and filters.get("mood"):
            opening_line = get_opening(filters.get("mood"))

        # Generate responses
        responses = []
        if matches:
            # Return up to 3 matches
            for venue in matches[:3]:
                response = generate_response(venue, filters)
                # Get the venue's actual arcana (may differ from searched mood for adjacent draws)
                raw_data = venue.get('raw_data', {})
                venue_arcana = raw_data.get('arcana', filters.get('mood'))
                responses.append({
                    'text': response,
                    'venue_name': venue.get('name', ''),
                    'area': venue.get('area', ''),
                    'website': venue.get('website', ''),
                    'whisper': venue.get('whisper', ''),
                    'arcana': venue_arcana,
                    'is_adjacent': venue.get('is_adjacent', False)
                })
        else:
            # No matches
            response = generate_response(None, filters)
            responses.append({
                'text': response,
                'venue_name': None,
                'area': None,
                'website': None
            })

        # Log successful interaction
        response_time_ms = (time.time() - start_time) * 1000
        first_response = responses[0].get('text', '') if responses else ''
        log_ask_interaction(
            session_id=session_id,
            user_query=user_prompt,
            lark_response=first_response,
            response_time_ms=response_time_ms,
            safety_tier=emotional_tier,
            mood_detected=filters.get('mood'),
            confidence=mood_confidence,
            ip_hash=ip_hash
        )

        return jsonify({
            'responses': responses,
            'mood': filters.get('mood'),
            'confidence': mood_confidence,
            'venue_count': len(matches),
            'filters': filters,
            'voice_profile': voice_profile_info,
            'opening_line': opening_line,
            'session_id': session_id,
            'safety': {
                'tier': emotional_tier,
                'show_soft_footer': safety_config['show_soft_footer'],
                'show_support_box': safety_config['show_support_box'],
                'show_crisis_resources': safety_config['show_crisis_resources'],
                'lark_preamble': safety_config['lark_preamble']
            },
            'debug': {
                'mood_detected': filters.get('mood'),
                'confidence': mood_confidence,
                'matches_found': len(matches),
                'voice_profile': voice_profile_name
            }
        })

    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        error_msg = f"I stumbled: {str(e)}"

        # Log error
        log_ask_interaction(
            session_id=session_id,
            user_query=user_prompt if 'user_prompt' in dir() else '',
            lark_response='',
            response_time_ms=response_time_ms,
            error=error_msg,
            ip_hash=ip_hash
        )

        return jsonify({
            'error': error_msg,
            'responses': [],
            'session_id': session_id
        }), 500


@app.route('/care-pathway', methods=['POST'])
@rate_limited
def care_pathway():
    """
    Handle care pathway choice selection.
    Returns 3 venues from specified arcana(s), texture selection, or therapeutic spread.

    Supports both:
    - Legacy: arcana list directly
    - New: texture_key that maps to arcana pool

    For "therapeutic_random" / "therapeutic_spread" / "let_me_draw_for_you":
    - Draws from 3 different need clusters (not 3 from same arcana)
    - Three different medicines, not "here's more sadness"
    """
    try:
        data = request.json or {}
        arcana_list = data.get('arcana', [])
        texture_key = data.get('texture_key')  # New: texture card selection
        tier = data.get('tier', 'emotional')
        use_spread = data.get('use_therapeutic_spread', False)

        all_venues = load_parsed_venues()

        # NEW: Handle texture_key selection (from texture cards)
        if texture_key:
            print(f"   🌸 Texture selection: '{texture_key}' for tier: {tier}")

            # Get the texture configuration
            texture_config = TEXTURE_ARCANA_MAPPING.get(texture_key)
            if not texture_config:
                return jsonify({
                    'error': f"Unknown texture: {texture_key}",
                    'responses': []
                }), 400

            arcana_pool = texture_config.get('arcana_pool', [])
            texture_name = texture_config.get('texture', texture_key)

            # Handle "let me draw for you" (therapeutic_spread)
            if arcana_pool == 'therapeutic_spread':
                print(f"      Using therapeutic spread for '{texture_key}'")
                spread_config = get_care_pathway_arcana_spread(tier)
                arcana_pool = spread_config['arcana_spread']

                # Draw one venue from each arcana in the spread
                selected_venues = []
                seen_names = set()

                for arcana in arcana_pool:
                    candidates = [
                        v for v in all_venues
                        if v.get('arcana') == arcana
                        and v.get('name', '').lower().strip() not in seen_names
                    ]
                    if candidates:
                        random.shuffle(candidates)
                        venue = candidates[0]
                        selected_venues.append(venue)
                        seen_names.add(venue.get('name', '').lower().strip())
                        print(f"      ✓ From '{arcana}': {venue.get('name')}")

                # Build responses
                responses = []
                for i, venue in enumerate(selected_venues):
                    response_text = generate_response(venue, {'mood': venue.get('arcana')})
                    responses.append({
                        'text': response_text,
                        'venue_name': venue.get('name', venue.get('display_name', '')),
                        'area': venue.get('area', venue.get('location', '')),
                        'website': venue.get('website', venue.get('url', '')),
                        'arcana': venue.get('arcana'),
                        'whisper': venue.get('whisper', ''),
                        'need_cluster': spread_config['needs_used'][i] if i < len(spread_config['needs_used']) else None
                    })

                safety_config = get_tier_response_config(tier)

                return jsonify({
                    'responses': responses,
                    'mood': 'therapeutic_spread',
                    'venue_count': len(responses),
                    'texture': texture_name,
                    'spread_description': spread_config['description'],
                    'safety': {
                        'tier': tier,
                        'show_soft_footer': safety_config.get('show_soft_footer', False),
                        'resources_footer': safety_config.get('resources_footer')
                    },
                    'debug': {
                        'texture_key': texture_key,
                        'needs_used': spread_config['needs_used'],
                        'arcana_spread': arcana_pool
                    }
                })

            # Handle texture with specific arcana pool (draw one from each arcana, 2+1 if pool has 3)
            print(f"      Arcana pool: {arcana_pool}")
            selected_venues = []
            seen_names = set()

            # Draw one venue from each arcana in the pool (up to 3)
            for arcana in arcana_pool[:3]:
                candidates = [
                    v for v in all_venues
                    if v.get('arcana') == arcana
                    and v.get('name', '').lower().strip() not in seen_names
                ]
                if candidates:
                    random.shuffle(candidates)
                    venue = candidates[0]
                    selected_venues.append(venue)
                    seen_names.add(venue.get('name', '').lower().strip())
                    print(f"      ✓ From '{arcana}': {venue.get('name')}")

            # Build responses
            responses = []
            for venue in selected_venues:
                response_text = generate_response(venue, {'mood': venue.get('arcana')})
                responses.append({
                    'text': response_text,
                    'venue_name': venue.get('name', venue.get('display_name', '')),
                    'area': venue.get('area', venue.get('location', '')),
                    'website': venue.get('website', venue.get('url', '')),
                    'arcana': venue.get('arcana'),
                    'whisper': venue.get('whisper', '')
                })

            safety_config = get_tier_response_config(tier)

            return jsonify({
                'responses': responses,
                'mood': arcana_pool[0] if arcana_pool else None,
                'venue_count': len(responses),
                'texture': texture_name,
                'safety': {
                    'tier': tier,
                    'show_soft_footer': safety_config.get('show_soft_footer', False),
                    'resources_footer': safety_config.get('resources_footer')
                },
                'debug': {
                    'texture_key': texture_key,
                    'arcana_pool': arcana_pool
                }
            })

        # Handle therapeutic spread drawing (from need clusters)
        if use_spread or arcana_list == "therapeutic_spread" or "therapeutic_spread" in arcana_list:
            print(f"   🌿 Therapeutic spread requested for tier: {tier}")
            spread_config = get_care_pathway_arcana_spread(tier)
            arcana_spread = spread_config['arcana_spread']

            # Draw one venue from each arcana in the spread
            selected_venues = []
            seen_names = set()

            for arcana in arcana_spread:
                candidates = [
                    v for v in all_venues
                    if v.get('arcana') == arcana
                    and v.get('name', '').lower().strip() not in seen_names
                ]
                if candidates:
                    random.shuffle(candidates)
                    venue = candidates[0]
                    selected_venues.append(venue)
                    seen_names.add(venue.get('name', '').lower().strip())
                    print(f"      ✓ From '{arcana}': {venue.get('name')}")

            # Build responses
            responses = []
            for venue in selected_venues:
                response_text = generate_response(venue, {'mood': venue.get('arcana')})
                responses.append({
                    'text': response_text,
                    'venue_name': venue.get('name', venue.get('display_name', '')),
                    'area': venue.get('area', venue.get('location', '')),
                    'website': venue.get('website', venue.get('url', '')),
                    'arcana': venue.get('arcana'),
                    'whisper': venue.get('whisper', ''),
                    'need_cluster': spread_config['needs_used'][selected_venues.index(venue)] if selected_venues.index(venue) < len(spread_config['needs_used']) else None
                })

            safety_config = get_tier_response_config(tier)

            return jsonify({
                'responses': responses,
                'mood': 'therapeutic_spread',
                'venue_count': len(responses),
                'spread_description': spread_config['description'],
                'safety': {
                    'tier': tier,
                    'show_soft_footer': safety_config.get('show_soft_footer', False),
                    'resources_footer': safety_config.get('resources_footer')
                },
                'debug': {
                    'needs_used': spread_config['needs_used'],
                    'arcana_spread': arcana_spread
                }
            })

        # Handle "therapeutic_random" - pick random from therapeutic arcana (legacy)
        if arcana_list == "therapeutic_random" or "therapeutic_random" in arcana_list:
            # Use the new spread-based drawing instead
            spread_config = get_care_pathway_arcana_spread(tier)
            arcana_list = spread_config['arcana_spread']

        if not arcana_list:
            return jsonify({
                'error': "No arcana specified",
                'responses': []
            }), 400

        # Load venues from the specified arcana (original behavior for specific choices)
        matching_venues = [
            v for v in all_venues
            if v.get('arcana') in arcana_list
        ]

        if not matching_venues:
            # Fallback to therapeutic spread if no matches
            spread_config = get_care_pathway_arcana_spread(tier)
            fallback_arcana = spread_config['arcana_spread']
            matching_venues = [
                v for v in all_venues
                if v.get('arcana') in fallback_arcana
            ]

        # Shuffle and take up to 3
        random.shuffle(matching_venues)
        selected_venues = matching_venues[:3]

        # Build responses
        responses = []
        for venue in selected_venues:
            response_text = generate_response(venue, {'mood': venue.get('arcana')})
            responses.append({
                'text': response_text,
                'venue_name': venue.get('name', venue.get('display_name', '')),
                'area': venue.get('area', venue.get('location', '')),
                'website': venue.get('website', venue.get('url', '')),
                'arcana': venue.get('arcana'),
                'whisper': venue.get('whisper', '')
            })

        # Get safety config for footer handling
        safety_config = get_tier_response_config(tier)

        return jsonify({
            'responses': responses,
            'mood': arcana_list[0] if arcana_list else None,
            'venue_count': len(responses),
            'safety': {
                'tier': tier,
                'show_soft_footer': safety_config.get('show_soft_footer', False),
                'resources_footer': safety_config.get('resources_footer')
            }
        })

    except Exception as e:
        return jsonify({
            'error': f"Something went awry: {str(e)}",
            'responses': []
        }), 500


# =============================================================================
# LARK MIND - Conversational AI (Prototype)
# =============================================================================

@app.route('/lark-mind-test')
def lark_mind_test():
    """Serve the Lark Mind test page (hidden prototype)"""
    greeting = get_lark_mind_greeting()
    return render_template('lark_mind_test.html', greeting=greeting)


@app.route('/chat', methods=['POST'])
@rate_limited
@budget_protected
@validate_input_length
def chat():
    """
    Lark Mind chat endpoint.

    Expects JSON: { "messages": [{"role": "user", "content": "..."}, ...] }
    Returns JSON: { "response": "...", "usage": {...}, "error": null }

    Protected by:
    - Rate limiting (per IP)
    - Daily budget cap
    - Input length validation
    - Conversation length limits
    """
    start_time = time.time()
    session_id = request.json.get('session_id') or generate_session_id()
    ip = get_client_ip()
    ip_hash = hash_ip(ip)

    try:
        data = request.json or {}
        messages = data.get('messages', [])

        if not messages:
            return jsonify({
                'error': 'No messages provided',
                'response': None,
                'session_id': session_id
            }), 400

        # Get the user's latest message for logging
        user_query = messages[-1].get('content', '') if messages else ''

        # Check for prompt injection/abuse (flag, don't block)
        content_check = check_and_flag_content(user_query, session_id, ip_hash)
        if content_check['flags']:
            print(f"   Flags detected: {content_check['flags']}")

        # Call Lark Mind
        result = chat_with_lark(messages)

        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000

        # Extract response and usage
        lark_response = result.get('response', '')
        usage = result.get('usage', {})
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        error = result.get('error')

        # Parse response for venue cards and draws
        parsed = parse_card_response(lark_response) if lark_response else {
            'segments': [],
            'raw_text': '',
            'has_cards': False,
            'has_draws': False
        }

        # Log the interaction
        log_chat_interaction(
            session_id=session_id,
            user_query=user_query,
            lark_response=lark_response or '',
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            response_time_ms=response_time_ms,
            error=error,
            ip_hash=ip_hash
        )

        if error:
            return jsonify({**result, 'session_id': session_id}), 500

        # Return enriched response with card/draw segments
        return jsonify({
            'response': parsed['raw_text'],  # Clean text without markers
            'segments': parsed['segments'],   # Structured segments for rendering
            'has_cards': parsed['has_cards'],
            'has_draws': parsed['has_draws'],
            'usage': usage,
            'error': None,
            'session_id': session_id
        })

    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        error_msg = f"Something went awry: {str(e)}"

        # Log the error
        log_chat_interaction(
            session_id=session_id,
            user_query=request.json.get('messages', [{}])[-1].get('content', '') if request.json else '',
            lark_response='',
            input_tokens=0,
            output_tokens=0,
            response_time_ms=response_time_ms,
            error=error_msg,
            ip_hash=ip_hash
        )

        return jsonify({
            'error': error_msg,
            'response': None,
            'session_id': session_id
        }), 500


# =============================================================================
# FEEDBACK ENDPOINTS - Testimonies & Flags
# =============================================================================

@app.route('/feedback/testimony', methods=['POST'])
def submit_testimony():
    """
    Log a positive testimony about a venue.
    Called when users click the ✧ love icon and share their experience.
    """
    try:
        data = request.get_json() or {}
        venue = data.get('venue', '')
        text = data.get('text', '')
        email = data.get('email', '')

        if not venue:
            return jsonify({'error': 'Venue required'}), 400

        # Get IP hash for basic tracking
        ip_hash = hash_ip(get_client_ip(request))

        # Log the testimony
        feedback_logger = get_feedback_logger()
        feedback_logger.log_testimony(
            venue=venue,
            text=text,
            email=email if email else None,
            ip_hash=ip_hash
        )

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/feedback/flag', methods=['POST'])
def submit_flag():
    """
    Log a flag/issue report about a venue.
    Called when users click the 🜃 flag icon to report problems.
    """
    try:
        data = request.get_json() or {}
        venue = data.get('venue', '')
        reason = data.get('reason', 'other')
        details = data.get('details', '')

        if not venue:
            return jsonify({'error': 'Venue required'}), 400

        # Get IP hash for basic tracking
        ip_hash = hash_ip(get_client_ip(request))

        # Log the flag
        feedback_logger = get_feedback_logger()
        feedback_logger.log_flag(
            venue=venue,
            reason=reason,
            details=details if details else None,
            ip_hash=ip_hash
        )

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# ADMIN ENDPOINTS - Usage Visibility
# =============================================================================

@app.route('/admin/usage', methods=['GET'])
def usage_summary():
    """
    Returns usage statistics for monitoring and budgeting.

    This is a simple admin endpoint - no authentication for now.
    In production, you might want to add a simple token check.

    Returns:
    - Today's stats (conversations, tokens, cost)
    - Last 7 days summary
    - Lifetime totals
    """
    try:
        tracker = get_usage_tracker()
        summary = tracker.get_summary_report()

        return jsonify({
            'status': 'ok',
            'usage': summary
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/admin/budget', methods=['GET'])
def budget_status():
    """
    Returns current budget status.

    Returns:
    - Daily limit
    - Current spend
    - Remaining budget
    - Is within budget
    """
    try:
        from lark_protection import get_budget_guard, DAILY_BUDGET_CAP_USD

        guard = get_budget_guard()
        is_within_budget, current_spend = guard.check_budget()

        return jsonify({
            'status': 'ok',
            'budget': {
                'daily_limit_usd': DAILY_BUDGET_CAP_USD,
                'current_spend_usd': round(current_spend, 4),
                'remaining_usd': round(guard.get_remaining_budget(), 4),
                'is_within_budget': is_within_budget,
                'percentage_used': round((current_spend / DAILY_BUDGET_CAP_USD) * 100, 1) if DAILY_BUDGET_CAP_USD > 0 else 0
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/admin/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint for monitoring.

    Returns current status and basic metrics.
    """
    try:
        tracker = get_usage_tracker()
        today_stats = tracker.get_today_stats()

        return jsonify({
            'status': 'healthy',
            'service': 'the-london-lark',
            'today': {
                'conversations': today_stats['conversations'],
                'errors': today_stats['errors']
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'degraded',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🕊️  THE LONDON LARK")
    print("  Opening her wings...")
    print("="*60)
    print("\n  Open your browser to: http://localhost:5000")
    print("\n  Press Ctrl+C to close when done.\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
