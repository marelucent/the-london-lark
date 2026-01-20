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
    get_tier_response_config,
    get_null_state_config,
    get_therapeutic_arcana,
    THERAPEUTIC_ARCANA
)
from venue_matcher import match_venues
from response_generator import generate_response, get_current_voice_profile, generate_surprise_response
from parse_venues import load_parsed_venues
from lark_metrics import get_metrics
from datetime import datetime
from zoneinfo import ZoneInfo
import random
import json
import os

# Import voice profile system for debug info
try:
    from poetic_templates import get_profile_name
    HAS_VOICE_PROFILES = True
except ImportError:
    HAS_VOICE_PROFILES = False
    get_profile_name = lambda x: "GENERAL"

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
def ask_lark():
    """Process a query and return the Lark's response"""
    try:
        user_prompt = request.json.get('prompt', '').strip()

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
        # SAFETY TIER PRIORITY CHECK
        # If distress or crisis detected, handle that FIRST before mood checks
        # =====================================================================

        # Tier 2 (Emotional) and Tier 3 (Distress) - show care pathway with choices
        if emotional_tier in ('emotional', 'distress'):
            print(f"   🛡️ Care pathway: {emotional_tier} tier detected, showing choices")

            return jsonify({
                'responses': [],  # No venues yet - wait for choice
                'mood': None,
                'confidence': 0.0,
                'venue_count': 0,
                'filters': filters,
                'safety': {
                    'tier': emotional_tier,
                    'show_soft_footer': safety_config.get('show_soft_footer', False),
                    'show_support_box': False,  # Now using care pathway
                    'show_crisis_resources': False,
                    'show_care_pathway': safety_config.get('show_care_pathway', True),
                    'care_choices': safety_config.get('care_choices', []),
                    'resources_footer': safety_config.get('resources_footer'),
                    'lark_preamble': safety_config.get('lark_preamble')
                },
                'debug': {
                    'reason': 'care_pathway',
                    'tier': emotional_tier,
                    'keywords': safety_keywords
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
        
        # If no mood detected at all (None with 0.0 confidence), show null state with presence
        if filters.get("mood") is None and mood_confidence == 0.0:
            print(f"   ❌ No recognizable mood keywords found - showing null state with presence")
            null_config = get_null_state_config()
            return jsonify({
                'responses': [],  # No venues, but she stays present
                'mood': None,
                'confidence': 0.0,
                'venue_count': 0,
                'filters': filters,
                'null_state': {
                    'is_null': True,
                    'preamble': null_config['preamble'],
                    'choices': null_config['choices']
                },
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
                    'reason': 'null_state_with_presence',
                    'keywords_checked': user_prompt.lower().split()
                }
            })

        # If confidence is very low (< 0.3), ask for clarification
        if mood_confidence < 0.3:
            print(f"   ⚠️ Very low confidence ({mood_confidence}), asking for clarification")
            return jsonify({
                'responses': [{
                    'text': f"I sense a whisper of '{filters.get('mood', 'something')}' in your words, but I'm not certain. Could you tell me more about the evening you're dreaming of?",
                    'venue_name': None,
                    'area': None,
                    'website': None
                }],
                'mood': filters.get('mood'),
                'confidence': mood_confidence,
                'venue_count': 0,
                'filters': filters,
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

        # Match venues
        matches = match_venues(filters)
        print(f"   Matched {len(matches)} venues")

        # Log metrics
        metrics = get_metrics()
        metrics.log_query(filters, mood_confidence, len(matches))

        # Generate responses
        responses = []
        if matches:
            # Return up to 3 matches
            for venue in matches[:3]:
                response = generate_response(venue, filters)
                responses.append({
                    'text': response,
                    'venue_name': venue.get('name', ''),
                    'area': venue.get('area', ''),
                    'website': venue.get('website', '')
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

        return jsonify({
            'responses': responses,
            'mood': filters.get('mood'),
            'confidence': mood_confidence,
            'venue_count': len(matches),
            'filters': filters,
            'voice_profile': voice_profile_info,
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
        return jsonify({
            'error': f"I stumbled: {str(e)}",
            'responses': []
        }), 500


@app.route('/care-pathway', methods=['POST'])
def care_pathway():
    """
    Handle care pathway choice selection.
    Returns 3 venues from the specified arcana(s).
    """
    try:
        data = request.json or {}
        arcana_list = data.get('arcana', [])
        tier = data.get('tier', 'emotional')

        if not arcana_list:
            return jsonify({
                'error': "No arcana specified",
                'responses': []
            }), 400

        # Handle "therapeutic_random" - pick random from therapeutic arcana
        if arcana_list == "therapeutic_random" or "therapeutic_random" in arcana_list:
            arcana_list = [random.choice(THERAPEUTIC_ARCANA)]

        # Load venues from the specified arcana
        all_venues = load_parsed_venues()
        matching_venues = [
            v for v in all_venues
            if v.get('arcana') in arcana_list
        ]

        if not matching_venues:
            # Fallback to all therapeutic arcana if no matches
            matching_venues = [
                v for v in all_venues
                if v.get('arcana') in THERAPEUTIC_ARCANA
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


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🕊️  THE LONDON LARK")
    print("  Opening her wings...")
    print("="*60)
    print("\n  Open your browser to: http://localhost:5000")
    print("\n  Press Ctrl+C to close when done.\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
