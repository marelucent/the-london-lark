# 🕊️ The London Lark — Prompt Parser

import re
from datetime import datetime, timedelta

# Mood keyword map (can be expanded or externalised later)
MOOD_KEYWORDS = {
    "dreamlike": "Dreamlike & Hypnagogic",
    "strange": "Playful & Weird",
    "folk": "Folk & Intimate",
    "poetic": "Poetic",
    "protest": "Punchy / Protest",
    "queer": "Queer Revelry",
    "sacred": "Spiritual / Sacred / Mystical",
    "grief": "Grief & Grace",
    "joy": "Group Energy",
    "weird": "Playful & Weird",
    "intimate": "Folk & Intimate",
    "candlelit": "Romanticised London",
    # Add more as needed
}

# Main parsing function
def parse_prompt(prompt):
    filters = {
        'moods': [],
        'budget': None,
        'date': None,
        'location': None,
        'category': None  # optional
    }

    prompt_lower = prompt.lower()

    # Budget
    budget_match = re.search(r'under \£?(\d+)', prompt_lower)
    if budget_match:
        filters['budget'] = int(budget_match.group(1))

    # Date handling
    if 'this friday' in prompt_lower:
        today = datetime.today()
        days_ahead = (4 - today.weekday()) % 7  # 4 = Friday
        target_date = today + timedelta(days=days_ahead)
        filters['date'] = target_date.strftime('%Y-%m-%d')
    elif 'this weekend' in prompt_lower:
        today = datetime.today()
        saturday = today + timedelta((5 - today.weekday()) % 7)
        sunday = saturday + timedelta(days=1)
        filters['date'] = [saturday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d')]

    # Mood tags
    for keyword, mood in MOOD_KEYWORDS.items():
        if keyword in prompt_lower:
            filters['moods'].append(mood)

    # Location (basic check)
    for loc in ["south london", "east london", "north london", "west london", "central london"]:
        if loc in prompt_lower:
            filters['location'] = loc.title()

    return filters


# Example usage
if __name__ == "__main__":
    test_prompt = "Take me somewhere dreamlike and strange under £15 this Friday"
    print(parse_prompt(test_prompt))
