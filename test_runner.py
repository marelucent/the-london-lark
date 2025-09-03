# 🚦 test_runner.py

"""
The London Lark — Test Runner

Simulates a full run from natural prompt → poetic recommendation.
Imports all modules: interpreter → mood resolver → venue matcher → response generator
"""

from prompt_interpreter import interpret_prompt
from mood_resolver import resolve_from_keywords
from venue_matcher import match_venues
from response_generator import generate_response

# Sample test prompt
user_prompt = "I'm in the mood for something quiet and thoughtful near Camden this Friday. Nothing too expensive, just for me."

# Step 1: Interpret filters
filters = interpret_prompt(user_prompt)
print("\n🎯 Filters:", filters)

# Step 2: Confirm or refine mood
if not filters.get("mood"):
    keywords = user_prompt.lower().split()
    mood = resolve_from_keywords(keywords)
    filters["mood"] = mood

print("🔮 Resolved Mood:", filters["mood"])

# Step 3: Match venues
matches = match_venues(filters)
print(f"🏛️ Found {len(matches)} venue(s).")

# Step 4: Generate poetic output
if matches:
    # For now, use first match only
    response = generate_response(matches[0], filters)
else:
    response = generate_response(None, filters)

print("\n🎭 Poetic Recommendation:\n")
print(response)
