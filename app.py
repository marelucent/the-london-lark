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

        # CONFIDENCE THRESHOLD CHECKS
        # If no mood detected at all (None with 0.0 confidence), reject
        if filters.get("mood") is None and mood_confidence == 0.0:
            print(f"   ❌ No recognizable mood keywords found")
            return jsonify({
                'responses': [{
                    'text': "I tilt my head... those words don't quite sing to me, petal. Could you describe the mood you're seeking? Perhaps something melancholic, intimate, queer, folk-like, or late-night?",
                    'venue_name': None,
                    'area': None,
                    'website': None
                }],
                'mood': None,
                'confidence': 0.0,
                'venue_count': 0,
                'filters': filters,
                'debug': {
                    'reason': 'no_mood_detected',
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

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🕊️  THE LONDON LARK")
    print("  Opening her wings...")
    print("="*60)
    print("\n  Open your browser to: http://localhost:5000")
    print("\n  Press Ctrl+C to close when done.\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
