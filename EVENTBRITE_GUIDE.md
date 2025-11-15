# Getting an Eventbrite API Token

## Quick Start

**1. Create Eventbrite Account**
- Go to https://www.eventbrite.com
- Sign up for free account (if you don't have one)

**2. Get OAuth Token**
- Visit: https://www.eventbrite.com/platform/api#/introduction/authentication
- Click "Create App" or go to https://www.eventbrite.com/account-settings/apps
- Fill in app details:
  - App Name: "London Lark Event Fetcher"
  - Description: "Fetches cultural events for mood-based recommendations"
  - App URL: `http://localhost:5000` (or any URL)

**3. Get Your Token**
- After creating the app, you'll see your **Private Token** (OAuth token)
- Copy this token
- Set it in `event_fetcher.py`:
  ```python
  EVENTBRITE_TOKEN = "YOUR_TOKEN_HERE"
  ```

**4. Test It**
```bash
python event_fetcher.py --real
```

## Rate Limits

- **Free tier:** 1000 requests/hour
- **Sufficient for:** Daily event refreshes
- **No cost** for non-commercial use

## API Documentation

Full docs: https://www.eventbrite.com/platform/api

Key endpoints we use:
- `/events/search/` - Search events by location/category/date

## Troubleshooting

**"401 Unauthorized"**
→ Check your token is set correctly

**"Too many requests"**
→ You've hit rate limit (wait an hour or reduce fetch frequency)

**No events returned**
→ Check your filters aren't too strict (see event_config.py)

## Security

- **Never commit your token to git**
- Token is in `.gitignore` by default
- For production, use environment variables:
  ```bash
  export EVENTBRITE_TOKEN="your_token"
  ```

That's it! Token setup takes ~5 minutes.
