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
from response_generator import generate_response
from lark_metrics import get_metrics

app = Flask(__name__)

@app.route('/')
def home():
    """Serve the main page"""
    return render_template('index.html')

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

        # Resolve mood if not found
        mood_confidence = 1.0
        if not filters.get("mood"):
            keywords = user_prompt.lower().split()
            mood, confidence = resolve_from_keywords(keywords)
            filters["mood"] = mood
            mood_confidence = confidence

        # Match venues
        matches = match_venues(filters)

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
                'area': None
            })

        return jsonify({
            'responses': responses,
            'mood': filters.get('mood'),
            'confidence': mood_confidence,
            'venue_count': len(matches),
            'filters': filters
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
