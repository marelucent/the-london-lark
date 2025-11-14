#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# The London Lark - Main Entry Point

"""
The London Lark: A poetic, mood-driven cultural companion for London.

Usage:
    python lark_poet.py
    python lark_poet.py "Take me somewhere dreamlike and strange this Friday"
"""

import sys
from prompt_interpreter import interpret_prompt
from mood_resolver import resolve_from_keywords
from venue_matcher import match_venues
from response_generator import generate_response


def lark_header():
    """Print the Lark's greeting"""
    print("\n" + "="*60)
    print("  THE LONDON LARK")
    print("    A poetic companion for London's cultural undercurrent")
    print("="*60 + "\n")


def lark_prompt():
    """Interactive prompt mode"""
    lark_header()
    print("Tell me what kind of evening you're dreaming of...")
    print("(e.g., 'Something quiet and folk-y in Camden tonight')")
    print("(or type 'quit' to exit)\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nThe Lark bids you goodnight. Go gently into the city.\n")
            break

        process_query(user_input)
        print("\n" + "-"*60 + "\n")


def process_query(user_prompt):
    """Process a single user query through the full pipeline"""

    # Step 1: Interpret the prompt
    filters = interpret_prompt(user_prompt)

    # Step 2: Resolve mood if not found
    if not filters.get("mood"):
        keywords = user_prompt.lower().split()
        mood, confidence = resolve_from_keywords(keywords)
        filters["mood"] = mood

        # Debug output showing confidence for fuzzy matches
        if mood and confidence < 1.0:
            print(f"\nThe Lark senses: {mood} (confidence: {confidence:.0%})")
        elif mood:
            print(f"\nThe Lark senses: {mood}")
    else:
        # Mood already found by prompt_interpreter
        print(f"\nThe Lark senses: {filters['mood']}")

    # Step 3: Match venues
    matches = match_venues(filters)

    # Step 4: Generate poetic responses
    if not matches:
        print("\n" + generate_response(None, filters))

        # Provide helpful suggestions based on what filters were used
        suggestions = []
        if filters.get("mood"):
            suggestions.append(f"✨ Try a different mood (you searched for: {filters['mood']})")
        if filters.get("location"):
            suggestions.append(f"📍 Try a different area (you searched for: {filters['location']})")
        if filters.get("genre"):
            suggestions.append(f"🎭 Try a different genre (you searched for: {filters['genre']})")
        if filters.get("budget"):
            suggestions.append(f"💷 Try adjusting your budget")
        if filters.get("group"):
            suggestions.append(f"👥 Try removing the {filters['group']} filter")

        if suggestions:
            print("\n💡 Suggestions:")
            for suggestion in suggestions:
                print(f"   {suggestion}")
        else:
            print("\n💡 Try adding more details - like a mood, location, or what kind of event you're after")
        return

    print(f"\nThe Lark found {len(matches)} place(s) that might resonate...\n")

    for i, venue in enumerate(matches, 1):
        if i > 1:
            print("\n" + "~"*50 + "\n")

        # Generate poetic response
        response_type = "MoodMirror" if filters.get("mood") else "Matchmaker"
        response = generate_response(venue, filters, response_type)

        print(response)
        print(f"\n  {venue['name']} in {venue['area']}")

        if venue.get('typical_start_time'):
            print(f"  Doors around {venue['typical_start_time']}")
        if venue.get('price') and venue['price'] != 'TBC':
            print(f"  Price: {venue['price']}")


def main():
    """Main entry point"""

    # If argument provided, process it directly
    if len(sys.argv) > 1:
        lark_header()
        user_prompt = " ".join(sys.argv[1:])
        print(f"You asked: \"{user_prompt}\"\n")
        process_query(user_prompt)
        print()
    else:
        # Interactive mode
        lark_prompt()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nThe Lark bids you goodnight. Go gently into the city.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        print("Please check your input and try again.\n")
        sys.exit(1)
