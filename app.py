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
from response_generator import generate_response, get_current_voice_profile
from lark_metrics import get_metrics
from datetime import datetime
from zoneinfo import ZoneInfo

# Import voice profile system for debug info
try:
    from poetic_templates import get_profile_name
    HAS_VOICE_PROFILES = True
except ImportError:
    HAS_VOICE_PROFILES = False
    get_profile_name = lambda x: "GENERAL"

app = Flask(__name__)

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

@app.route('/')
def home():
    """Serve the main page"""
    greeting = get_time_aware_greeting()
    return render_template('index.html', greeting=greeting)

@app.route('/ask', methods=['POST'])
def ask_lark():
    """Process a query and return the Lark's response"""
    try:
        user_prompt = request.json.get('prompt', '').strip()

        if not user_prompt:
            return jsonify({
                'response': "The Lark listens... but heard only silence. Speak, petal.",
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
                    'text': "The Lark tilts her head... those words don't quite sing to me, petal. Could you describe the mood you're seeking? Perhaps something melancholic, intimate, queer, folk-like, or late-night?",
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
                    'text': f"The Lark senses a whisper of '{filters.get('mood', 'something')}' in your words, but she's not certain. Could you tell me more about the evening you're dreaming of?",
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
            'error': f"The Lark stumbled: {str(e)}",
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
