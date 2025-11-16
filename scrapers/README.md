# 🕊️ The London Lark - Local Event Scraper

A standalone web scraping system to fetch real London cultural events from:
- **Resident Advisor** (RA) - Electronic music & club nights
- **Dice.fm** - Music, theatre, comedy events
- **Time Out London** - Music, theatre, nightlife

Run this on your **local Windows laptop** to collect events, then import them into the Lark.

---

## 📋 Prerequisites

- **Python 3.8+** installed on your Windows machine
- **pip** (Python package manager)
- Internet connection

To check your Python version:
```bash
python --version
```

If you don't have Python, download from: https://www.python.org/downloads/windows/

---

## 🚀 Quick Start

### Step 1: Install Dependencies

Open **Command Prompt** or **PowerShell** and navigate to the scrapers folder:

```bash
cd path\to\the-london-lark\scrapers
pip install -r requirements.txt
```

Or install individually:
```bash
pip install requests beautifulsoup4 lxml
```

### Step 2: Run the Scraper

```bash
python local_scraper.py
```

This will:
1. Scrape events from all 3 sources (next 7 days)
2. Deduplicate results
3. Save to `scraped_events.json`

### Step 3: Check Output

Open `scraped_events.json` to see your scraped events. Example output:

```json
{
  "scraped_at": "2025-01-15T14:30:00.123456",
  "event_count": 45,
  "sources": ["Resident Advisor", "Dice.fm", "Time Out London"],
  "events": [
    {
      "event_name": "Four Tet All Night Long",
      "venue_name": "Fabric",
      "date": "2025-01-18",
      "time": "23:00",
      "source": "Resident Advisor",
      "url": "https://ra.co/events/1234567",
      "description": "Electronic music pioneer...",
      "mood_tags": ["Late-Night Lark", "Big Night Out"]
    },
    ...
  ]
}
```

### Step 4: Import into the Lark

Copy your `scraped_events.json` to the project root and run:

```bash
cd ..
python scrapers/import_events.py scraped_events.json
```

This will match events to your curated venues and import them.

---

## 🎛️ Command Line Options

### Scrape Specific Sources

```bash
# Only Resident Advisor
python local_scraper.py --source ra

# Only Dice.fm
python local_scraper.py --source dice

# Only Time Out
python local_scraper.py --source timeout

# Multiple sources
python local_scraper.py --source ra dice
```

### Adjust Time Range

```bash
# Next 14 days
python local_scraper.py --days 14

# Next 30 days
python local_scraper.py --days 30

# Just today and tomorrow
python local_scraper.py --days 2
```

### Custom Output File

```bash
python local_scraper.py --output my_events.json
```

### Debug Mode

```bash
# Verbose logging for debugging
python local_scraper.py --verbose
```

### Skip Deduplication

```bash
python local_scraper.py --no-dedup
```

### Combined Example

```bash
python local_scraper.py --source ra dice --days 14 --output ra_dice_events.json --verbose
```

---

## 📊 Expected Output

When you run the scraper, you'll see:

```
============================================================
  🕊️  THE LONDON LARK - Event Scraper
  Fetching real events from London's cultural underground...
============================================================

14:30:00 [INFO] Starting scrape for next 7 days...
14:30:00 [INFO] 🎧 Scraping Resident Advisor (next 7 days)...
14:30:02 [INFO] ✅ Found 12 events from Resident Advisor

14:30:04 [INFO] 🎲 Scraping Dice.fm (next 7 days)...
14:30:06 [INFO] ✅ Found 18 events from Dice.fm

14:30:08 [INFO] ⏰ Scraping Time Out London (next 7 days)...
14:30:12 [INFO] ✅ Found 25 events from Time Out London

14:30:12 [INFO] Deduplicated: 55 → 45 events
14:30:12 [INFO] 💾 Saved 45 events to scraped_events.json

============================================================
  ✅ SCRAPING COMPLETE
============================================================
  Total events: 45
  • Resident Advisor: 12 events
  • Dice.fm: 18 events
  • Time Out London: 15 events

  Output file: scraped_events.json

  Next step: Copy scraped_events.json to your Lark project and run:
    python scrapers/import_events.py scraped_events.json
============================================================
```

---

## ⚠️ Common Issues & Solutions

### 1. "403 Forbidden" or "Access Denied"

**Problem**: Website is blocking your requests (bot protection).

**Solutions**:
- Wait 10-15 minutes and try again
- Use a VPN to change your IP address
- Try scraping just one source at a time
- Run at different times of day

### 2. "ModuleNotFoundError: No module named 'requests'"

**Problem**: Dependencies not installed.

**Solution**:
```bash
pip install -r requirements.txt
```

### 3. "0 events found"

**Problem**: Websites may have changed their HTML structure.

**Solutions**:
- Try `--verbose` flag to see what's happening
- Check if the website is accessible in your browser
- Some events may be loaded via JavaScript (not scrapable)

### 4. SSL/Certificate Errors

**Problem**: Network security issues.

**Solution**:
```bash
pip install --upgrade certifi
```

### 5. Rate Limiting (429 Error)

**Problem**: Too many requests sent too quickly.

**Solution**: The scraper has built-in rate limiting. If you still get 429s, wait 30 minutes before retrying.

---

## 🔧 Troubleshooting

### Enable Debug Logging

```bash
python local_scraper.py --verbose
```

This shows:
- Each HTTP request being made
- What content is being parsed
- Why certain events failed to parse

### Test Your Connection

```python
# test_connection.py
import requests
response = requests.get("https://www.timeout.com/london", timeout=10)
print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)}")
```

### Manual Fallback

If automated scraping fails, you can manually create events:

1. Create a file called `manual_events.json`
2. Add events in this format:

```json
{
  "events": [
    {
      "event_name": "Jazz Night at Vortex",
      "venue_name": "Vortex Jazz Club",
      "date": "2025-01-20",
      "time": "20:00"
    },
    {
      "event_name": "Folk Session",
      "venue_name": "The Green Note",
      "date": "2025-01-21",
      "time": "19:30"
    }
  ]
}
```

3. Import with:
```bash
python scrapers/import_events.py manual_events.json
```

---

## 📁 File Structure

```
scrapers/
├── local_scraper.py      # Main scraping script
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── test_scraper.py      # Unit tests
└── import_events.py     # Import scraped events to Lark
```

---

## 🧪 Running Tests

To verify the scraper code works correctly:

```bash
# Install test dependencies
pip install pytest pytest-mock responses

# Run all tests
pytest test_scraper.py -v

# Run specific test
pytest test_scraper.py::test_parse_date -v
```

---

## 🔄 Workflow Summary

1. **Scrape events locally**:
   ```bash
   python local_scraper.py --days 7
   ```

2. **Review the JSON output** (check for quality)

3. **Import to the Lark**:
   ```bash
   python scrapers/import_events.py scraped_events.json
   ```

4. **Verify in the UI** - Start the Lark and test queries

5. **Repeat weekly** to keep events fresh

---

## 🎭 Event Format Reference

Each event in the JSON has these fields:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `event_name` | string | Name of the event | ✅ Yes |
| `venue_name` | string | Name of the venue | ✅ Yes |
| `date` | string | Date in YYYY-MM-DD format | ✅ Yes |
| `time` | string | Start time in HH:MM format | ❌ No (default: 20:00) |
| `source` | string | Where the event came from | ❌ No |
| `url` | string | Link to event page | ❌ No |
| `description` | string | Event description | ❌ No |
| `mood_tags` | array | Inferred mood tags | ❌ No (auto-generated) |

---

## 🌟 Tips for Best Results

1. **Run during off-peak hours** - Less likely to be rate-limited
2. **Start with one source** - Test that it works before scraping all
3. **Check JSON for quality** - Remove any malformed events before importing
4. **Keep it legal** - Only scrape publicly available data, respect robots.txt
5. **Don't overdo it** - Scrape once per week, not multiple times per day

---

## 📜 Legal & Ethical Notes

- This scraper accesses publicly available event listings
- It uses rate limiting to be respectful to servers
- Do not use for commercial purposes without permission
- Respect each website's Terms of Service
- If a website blocks you, respect that decision

---

## 🆘 Need Help?

If the scraper isn't working:

1. Check the [Common Issues](#️-common-issues--solutions) section
2. Run with `--verbose` flag for debugging
3. Try the manual fallback method
4. Use the Lark's mock event system as a backup

Happy scraping! 🕊️
