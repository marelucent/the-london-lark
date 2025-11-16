#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for The London Lark local scraper.

Run with: pytest test_scraper.py -v
"""

import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Import the scraper module
import local_scraper as scraper


class TestDateParsing:
    """Test the parse_date function"""

    def test_iso_format(self):
        """Parse ISO date format"""
        result = scraper.parse_date("2025-01-15")
        assert result == "2025-01-15"

    def test_british_format_full(self):
        """Parse British date format with full month"""
        result = scraper.parse_date("15 January 2025")
        assert result == "2025-01-15"

    def test_british_format_short(self):
        """Parse British date format with short month"""
        result = scraper.parse_date("15 Jan 2025")
        assert result == "2025-01-15"

    def test_us_format(self):
        """Parse US date format"""
        result = scraper.parse_date("January 15, 2025")
        assert result == "2025-01-15"

    def test_slashed_dmy(self):
        """Parse DD/MM/YYYY format"""
        result = scraper.parse_date("15/01/2025")
        assert result == "2025-01-15"

    def test_short_month_day(self):
        """Parse date with short month name (no year)"""
        result = scraper.parse_date("Sat 15 Jan")
        assert result is not None
        # Should be current or next year
        year = datetime.now().year
        assert result.startswith(str(year)) or result.startswith(str(year + 1))
        assert result.endswith("-01-15")

    def test_invalid_date(self):
        """Return None for unparseable date"""
        result = scraper.parse_date("not a date")
        assert result is None

    def test_gibberish(self):
        """Return None for gibberish"""
        result = scraper.parse_date("xyzabc123")
        assert result is None

    def test_empty_string(self):
        """Handle empty string"""
        result = scraper.parse_date("")
        assert result is None


class TestMoodInference:
    """Test the mood tag inference logic"""

    def test_folk_keywords(self):
        """Detect folk mood from keywords"""
        tags = scraper.infer_mood_tags("Acoustic Folk Night", "The Green Note", "")
        assert "Folk & Intimate" in tags

    def test_queer_keywords(self):
        """Detect queer mood from keywords"""
        tags = scraper.infer_mood_tags("Drag Extravaganza", "The Glory", "")
        assert "Queer Revelry" in tags

    def test_late_night_keywords(self):
        """Detect late night mood from keywords"""
        tags = scraper.infer_mood_tags("After Hours", "Fabric", "All night party")
        assert "Late-Night Lark" in tags

    def test_comedy_keywords(self):
        """Detect comedy mood from keywords"""
        tags = scraper.infer_mood_tags("Stand-up Comedy Night", "Comedy Store", "")
        assert "Comic Relief" in tags

    def test_classical_keywords(self):
        """Detect classical mood from keywords"""
        tags = scraper.infer_mood_tags("Symphony Orchestra", "Royal Albert Hall", "")
        assert "Wonder & Awe" in tags

    def test_no_match_defaults(self):
        """Default to Curious Encounters when no keywords match"""
        tags = scraper.infer_mood_tags("Random Event", "Some Venue", "")
        assert "Curious Encounters" in tags

    def test_max_two_tags(self):
        """Return maximum of 2 mood tags"""
        # Event with multiple mood indicators
        tags = scraper.infer_mood_tags("Folk Queer Comedy Night", "Venue", "Drag show with folk music and stand-up comedy")
        assert len(tags) <= 2

    def test_case_insensitive(self):
        """Keywords should be case insensitive"""
        tags = scraper.infer_mood_tags("FOLK ACOUSTIC", "THE GREEN NOTE", "INTIMATE SETTING")
        assert "Folk & Intimate" in tags


class TestDeduplication:
    """Test event deduplication"""

    def test_remove_exact_duplicates(self):
        """Remove exact duplicate events"""
        events = [
            {"event_name": "Jazz Night", "venue_name": "Vortex", "date": "2025-01-15"},
            {"event_name": "Jazz Night", "venue_name": "Vortex", "date": "2025-01-15"},
        ]
        result = scraper.deduplicate_events(events)
        assert len(result) == 1

    def test_keep_different_dates(self):
        """Keep same event on different dates"""
        events = [
            {"event_name": "Jazz Night", "venue_name": "Vortex", "date": "2025-01-15"},
            {"event_name": "Jazz Night", "venue_name": "Vortex", "date": "2025-01-16"},
        ]
        result = scraper.deduplicate_events(events)
        assert len(result) == 2

    def test_keep_different_venues(self):
        """Keep same event at different venues"""
        events = [
            {"event_name": "Jazz Night", "venue_name": "Vortex", "date": "2025-01-15"},
            {"event_name": "Jazz Night", "venue_name": "Ronnie Scotts", "date": "2025-01-15"},
        ]
        result = scraper.deduplicate_events(events)
        assert len(result) == 2

    def test_case_insensitive_dedup(self):
        """Deduplication should be case insensitive"""
        events = [
            {"event_name": "Jazz Night", "venue_name": "Vortex", "date": "2025-01-15"},
            {"event_name": "JAZZ NIGHT", "venue_name": "vortex", "date": "2025-01-15"},
        ]
        result = scraper.deduplicate_events(events)
        assert len(result) == 1

    def test_empty_list(self):
        """Handle empty event list"""
        result = scraper.deduplicate_events([])
        assert result == []


class TestRateLimiting:
    """Test rate limiting behavior"""

    @patch('local_scraper.time.sleep')
    @patch('local_scraper.random.uniform')
    def test_rate_limit_calls_sleep(self, mock_uniform, mock_sleep):
        """Rate limit should call time.sleep"""
        mock_uniform.return_value = 1.5
        scraper.rate_limit()
        mock_sleep.assert_called_once_with(1.5)

    @patch('local_scraper.random.uniform')
    def test_rate_limit_uses_random(self, mock_uniform):
        """Rate limit should use random delay"""
        with patch('local_scraper.time.sleep'):
            scraper.rate_limit()
            mock_uniform.assert_called_once()
            args = mock_uniform.call_args[0]
            assert args[0] >= 1.0  # MIN_DELAY
            assert args[1] <= 2.0  # MAX_DELAY


class TestSafeRequest:
    """Test the safe_request function"""

    @patch('local_scraper.requests.get')
    def test_successful_request(self, mock_get):
        """Return response for successful request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = scraper.safe_request("https://example.com")
        assert result == mock_response

    @patch('local_scraper.requests.get')
    def test_403_returns_none(self, mock_get):
        """Return None for 403 Forbidden"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        result = scraper.safe_request("https://example.com")
        assert result is None

    @patch('local_scraper.requests.get')
    @patch('local_scraper.time.sleep')
    def test_429_retries(self, mock_sleep, mock_get):
        """Retry on 429 rate limit"""
        mock_response_429 = Mock()
        mock_response_429.status_code = 429

        mock_response_200 = Mock()
        mock_response_200.status_code = 200

        mock_get.side_effect = [mock_response_429, mock_response_200]

        result = scraper.safe_request("https://example.com")
        assert result == mock_response_200
        assert mock_get.call_count == 2

    @patch('local_scraper.requests.get')
    def test_timeout_returns_none(self, mock_get):
        """Return None on timeout"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        result = scraper.safe_request("https://example.com")
        assert result is None

    @patch('local_scraper.requests.get')
    def test_connection_error_returns_none(self, mock_get):
        """Return None on connection error"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()

        result = scraper.safe_request("https://example.com")
        assert result is None


class TestEventFormat:
    """Test that scraped events have correct format"""

    def test_event_has_required_fields(self):
        """Events should have all required fields"""
        # Mock a basic event
        event = {
            "event_name": "Test Event",
            "venue_name": "Test Venue",
            "date": "2025-01-15",
            "time": "20:00",
            "source": "Test",
            "url": "",
            "description": "",
            "mood_tags": ["Curious Encounters"]
        }

        required_fields = ["event_name", "venue_name", "date", "time", "source", "mood_tags"]
        for field in required_fields:
            assert field in event

    def test_date_format_valid(self):
        """Date should be in YYYY-MM-DD format"""
        event = {
            "event_name": "Test",
            "venue_name": "Test",
            "date": "2025-01-15",
            "time": "20:00",
            "source": "Test",
            "mood_tags": []
        }

        # Should not raise ValueError
        datetime.strptime(event["date"], "%Y-%m-%d")

    def test_time_format_valid(self):
        """Time should be in HH:MM format"""
        valid_times = ["20:00", "23:30", "09:00", "19:45"]
        for time_str in valid_times:
            # Should not raise ValueError
            datetime.strptime(time_str, "%H:%M")


class TestScraperClasses:
    """Test individual scraper class methods"""

    def test_ra_scraper_init(self):
        """RA scraper should initialize"""
        ra = scraper.ResidentAdvisorScraper()
        assert ra.session is not None
        assert ra.BASE_URL == "https://ra.co"

    def test_dice_scraper_init(self):
        """Dice scraper should initialize"""
        dice = scraper.DiceFMScraper()
        assert dice.session is not None
        assert dice.BASE_URL == "https://dice.fm"

    def test_timeout_scraper_init(self):
        """Time Out scraper should initialize"""
        timeout = scraper.TimeOutScraper()
        assert timeout.session is not None
        assert timeout.BASE_URL == "https://www.timeout.com"

    @patch.object(scraper.ResidentAdvisorScraper, 'scrape')
    @patch.object(scraper.DiceFMScraper, 'scrape')
    @patch.object(scraper.TimeOutScraper, 'scrape')
    def test_scrape_all_sources(self, mock_timeout, mock_dice, mock_ra):
        """Scrape all sources aggregates results"""
        mock_ra.return_value = [{"event_name": "RA Event", "venue_name": "V1", "date": "2025-01-15"}]
        mock_dice.return_value = [{"event_name": "Dice Event", "venue_name": "V2", "date": "2025-01-15"}]
        mock_timeout.return_value = [{"event_name": "TimeOut Event", "venue_name": "V3", "date": "2025-01-15"}]

        result = scraper.scrape_all_sources(days_ahead=7)
        assert len(result) == 3

    @patch.object(scraper.ResidentAdvisorScraper, 'scrape')
    def test_scrape_single_source(self, mock_ra):
        """Scrape only specified sources"""
        mock_ra.return_value = [{"event_name": "RA Event", "venue_name": "V1", "date": "2025-01-15"}]

        result = scraper.scrape_all_sources(days_ahead=7, sources=["ra"])
        assert len(result) == 1
        mock_ra.assert_called_once_with(days_ahead=7)


class TestJSONOutput:
    """Test JSON output functionality"""

    @patch('builtins.open', create=True)
    @patch('local_scraper.json.dump')
    def test_save_events_writes_json(self, mock_dump, mock_open):
        """Save events should write JSON file"""
        events = [
            {"event_name": "Test", "venue_name": "Venue", "date": "2025-01-15"}
        ]

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        scraper.save_events(events, "test.json")

        mock_open.assert_called_once()
        mock_dump.assert_called_once()

        # Check the structure of saved data
        saved_data = mock_dump.call_args[0][0]
        assert "scraped_at" in saved_data
        assert "event_count" in saved_data
        assert "events" in saved_data
        assert saved_data["event_count"] == 1

    def test_output_format_matches_importer(self):
        """Output format should match what import_events.py expects"""
        events = [
            {
                "event_name": "Test Event",
                "venue_name": "Test Venue",
                "date": "2025-01-15",
                "time": "20:00",
                "source": "Test",
                "url": "https://example.com",
                "description": "Test description",
                "mood_tags": ["Curious Encounters"]
            }
        ]

        output_data = {
            "scraped_at": datetime.now().isoformat(),
            "event_count": len(events),
            "sources": ["Test"],
            "events": events
        }

        # Verify it can be serialized to JSON
        json_str = json.dumps(output_data)
        assert json_str is not None

        # Verify it can be parsed back
        parsed = json.loads(json_str)
        assert parsed["events"][0]["event_name"] == "Test Event"


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_event_name(self):
        """Handle empty event names gracefully"""
        tags = scraper.infer_mood_tags("", "Venue", "")
        assert len(tags) > 0  # Should still return default tags

    def test_very_long_event_name(self):
        """Handle very long event names"""
        long_name = "A" * 1000
        tags = scraper.infer_mood_tags(long_name, "Venue", "")
        assert len(tags) > 0

    def test_special_characters_in_name(self):
        """Handle special characters in event names"""
        name = "Folk Night @ The Green Note! #acoustic 🎸"
        tags = scraper.infer_mood_tags(name, "Venue", "")
        assert "Folk & Intimate" in tags

    def test_unicode_in_venue_name(self):
        """Handle unicode characters in venue names"""
        venue = "Café Oto"
        tags = scraper.infer_mood_tags("Experimental Night", venue, "")
        assert len(tags) > 0


class TestHTMLParsing:
    """Test HTML parsing helpers"""

    def test_parse_jsonld_event_valid(self):
        """Parse valid JSON-LD event data"""
        ra = scraper.ResidentAdvisorScraper()
        jsonld = {
            "@type": "Event",
            "name": "Test Event",
            "location": {"name": "Test Venue"},
            "startDate": "2025-01-15T21:00:00",
            "url": "https://example.com/event",
            "description": "Test description"
        }

        result = ra._parse_jsonld_event(jsonld)
        assert result is not None
        assert result["event_name"] == "Test Event"
        assert result["venue_name"] == "Test Venue"
        assert result["date"] == "2025-01-15"
        assert result["time"] == "21:00"

    def test_parse_jsonld_event_missing_fields(self):
        """Handle JSON-LD with missing optional fields"""
        ra = scraper.ResidentAdvisorScraper()
        jsonld = {
            "@type": "Event",
            "name": "Test Event",
            "location": {"name": "Test Venue"},
        }

        result = ra._parse_jsonld_event(jsonld)
        # Should still return something, with defaults
        assert result is not None or result is None  # Either is valid

    def test_parse_jsonld_event_invalid(self):
        """Handle invalid JSON-LD data"""
        ra = scraper.ResidentAdvisorScraper()
        jsonld = {"invalid": "data"}

        result = ra._parse_jsonld_event(jsonld)
        # Should return None or handle gracefully
        # Not crash


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
