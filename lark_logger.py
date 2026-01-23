#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The London Lark - Logging System

Comprehensive logging for visibility, debugging, and usage tracking.
Logs all requests/responses with:
- Timestamp
- Session ID
- User query
- Lark response
- Tokens used
- Response time
- Errors

Privacy note: Logs are not tied to any identity - we don't have accounts.
Conversations may be logged for improving the service.
"""

import json
import logging
import os
import uuid
from datetime import datetime, date
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any
from zoneinfo import ZoneInfo

# =============================================================================
# CONFIGURATION
# =============================================================================

LOGS_DIR = Path("logs")
CONVERSATION_LOG_FILE = LOGS_DIR / "conversations.jsonl"
ERROR_LOG_FILE = LOGS_DIR / "errors.log"
USAGE_LOG_FILE = LOGS_DIR / "usage.jsonl"
ABUSE_LOG_FILE = LOGS_DIR / "abuse_flags.jsonl"
FEEDBACK_LOG_FILE = LOGS_DIR / "feedback.jsonl"

# Maximum log file size before rotation (10MB)
MAX_LOG_SIZE = 10 * 1024 * 1024
# Keep 5 backup files
BACKUP_COUNT = 5

# Cost estimates (as of 2024, Sonnet pricing)
# Input: $3 per million tokens, Output: $15 per million tokens
COST_PER_INPUT_TOKEN = 3.0 / 1_000_000
COST_PER_OUTPUT_TOKEN = 15.0 / 1_000_000


# =============================================================================
# LOGGER SETUP
# =============================================================================

def setup_logging():
    """Initialize the logging infrastructure"""
    # Create logs directory
    LOGS_DIR.mkdir(exist_ok=True)

    # Setup error logger (traditional text logging)
    error_logger = logging.getLogger('lark.errors')
    error_logger.setLevel(logging.ERROR)

    if not error_logger.handlers:
        handler = RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        error_logger.addHandler(handler)

    return error_logger


# Global error logger
_error_logger = None


def get_error_logger():
    """Get the error logger instance"""
    global _error_logger
    if _error_logger is None:
        _error_logger = setup_logging()
    return _error_logger


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

def generate_session_id() -> str:
    """Generate a unique session ID for grouping conversation turns"""
    return str(uuid.uuid4())[:8]


# =============================================================================
# CONVERSATION LOGGING
# =============================================================================

class ConversationLogger:
    """
    Logs conversations in JSON Lines format for easy analysis.
    Each line is a complete JSON object representing one interaction.
    """

    def __init__(self):
        LOGS_DIR.mkdir(exist_ok=True)
        self._ensure_log_rotation()

    def _ensure_log_rotation(self):
        """Check if we need to rotate to a new daily log"""
        # We use a single file with rotation by size
        # Daily logs are handled by including date in each entry
        pass

    def _get_log_file(self) -> Path:
        """Get the appropriate log file for today"""
        return CONVERSATION_LOG_FILE

    def log_interaction(
        self,
        endpoint: str,
        session_id: str,
        user_query: str,
        lark_response: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        response_time_ms: float = 0,
        error: Optional[str] = None,
        ip_hash: Optional[str] = None,
        safety_tier: Optional[str] = None,
        mood_detected: Optional[str] = None,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a single interaction to the conversation log.

        All sensitive data (IP) is hashed. User queries are stored but not
        tied to any identity.
        """
        london_tz = ZoneInfo('Europe/London')
        now = datetime.now(london_tz)

        # Calculate estimated cost
        estimated_cost = (
            (input_tokens * COST_PER_INPUT_TOKEN) +
            (output_tokens * COST_PER_OUTPUT_TOKEN)
        )

        log_entry = {
            "timestamp": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "session_id": session_id,
            "endpoint": endpoint,
            "user_query": user_query[:1000] if user_query else None,  # Truncate very long queries
            "lark_response": lark_response[:2000] if lark_response else None,  # Truncate long responses
            "tokens": {
                "input": input_tokens,
                "output": output_tokens,
                "total": input_tokens + output_tokens
            },
            "estimated_cost_usd": round(estimated_cost, 6),
            "response_time_ms": round(response_time_ms, 2),
            "error": error,
            "ip_hash": ip_hash,
            "safety_tier": safety_tier,
            "mood_detected": mood_detected,
            "confidence": confidence,
            "metadata": metadata
        }

        try:
            with open(self._get_log_file(), 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            get_error_logger().error(f"Failed to write conversation log: {e}")

    def log_error(self, error_msg: str, endpoint: str, session_id: str,
                  user_query: Optional[str] = None, traceback: Optional[str] = None):
        """Log an error with context"""
        get_error_logger().error(
            f"Session: {session_id} | Endpoint: {endpoint} | "
            f"Query: {user_query[:100] if user_query else 'None'} | "
            f"Error: {error_msg}"
        )
        if traceback:
            get_error_logger().error(f"Traceback: {traceback}")


# =============================================================================
# USAGE TRACKING
# =============================================================================

class UsageTracker:
    """
    Tracks daily usage for budget management and reporting.
    Persists to a JSON file that's updated after each interaction.
    """

    USAGE_FILE = LOGS_DIR / "daily_usage.json"

    def __init__(self):
        LOGS_DIR.mkdir(exist_ok=True)
        self.usage = self._load_usage()

    def _load_usage(self) -> Dict[str, Any]:
        """Load or initialize usage tracking"""
        if self.USAGE_FILE.exists():
            try:
                with open(self.USAGE_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self._create_empty_usage()

    def _create_empty_usage(self) -> Dict[str, Any]:
        """Create empty usage structure"""
        today = date.today().isoformat()
        return {
            "current_date": today,
            "daily": {
                today: self._empty_day_stats()
            },
            "lifetime": {
                "total_conversations": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0
            }
        }

    def _empty_day_stats(self) -> Dict[str, Any]:
        """Create empty stats for a day"""
        return {
            "conversations": 0,
            "chat_requests": 0,
            "ask_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "estimated_cost_usd": 0.0,
            "errors": 0,
            "abuse_flags": 0,
            "unique_sessions": [],
            "first_request": None,
            "last_request": None
        }

    def _save_usage(self):
        """Persist usage data to file"""
        try:
            with open(self.USAGE_FILE, 'w') as f:
                json.dump(self.usage, f, indent=2)
        except IOError as e:
            get_error_logger().error(f"Failed to save usage data: {e}")

    def _ensure_today(self):
        """Ensure we have stats for today, rolling over if needed"""
        today = date.today().isoformat()

        if self.usage.get("current_date") != today:
            # New day - keep historical data but start fresh for today
            self.usage["current_date"] = today
            if "daily" not in self.usage:
                self.usage["daily"] = {}
            self.usage["daily"][today] = self._empty_day_stats()

            # Clean up old daily entries (keep last 30 days)
            dates = sorted(self.usage["daily"].keys())
            while len(dates) > 30:
                oldest = dates.pop(0)
                del self.usage["daily"][oldest]

    def record_request(
        self,
        endpoint: str,
        session_id: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        is_error: bool = False,
        is_abuse_flag: bool = False
    ):
        """Record a request for usage tracking"""
        self._ensure_today()
        today = date.today().isoformat()
        day_stats = self.usage["daily"][today]

        # Update request counts
        day_stats["conversations"] += 1
        if endpoint == "/chat":
            day_stats["chat_requests"] += 1
        elif endpoint == "/ask":
            day_stats["ask_requests"] += 1

        # Update token counts
        day_stats["total_input_tokens"] += input_tokens
        day_stats["total_output_tokens"] += output_tokens

        # Calculate cost
        cost = (
            (input_tokens * COST_PER_INPUT_TOKEN) +
            (output_tokens * COST_PER_OUTPUT_TOKEN)
        )
        day_stats["estimated_cost_usd"] += cost

        # Track errors and abuse
        if is_error:
            day_stats["errors"] += 1
        if is_abuse_flag:
            day_stats["abuse_flags"] += 1

        # Track unique sessions
        if session_id and session_id not in day_stats["unique_sessions"]:
            day_stats["unique_sessions"].append(session_id)

        # Update timestamps
        now = datetime.now(ZoneInfo('Europe/London')).isoformat()
        if day_stats["first_request"] is None:
            day_stats["first_request"] = now
        day_stats["last_request"] = now

        # Update lifetime stats
        self.usage["lifetime"]["total_conversations"] += 1
        self.usage["lifetime"]["total_tokens"] += input_tokens + output_tokens
        self.usage["lifetime"]["total_cost_usd"] += cost

        self._save_usage()

    def get_today_stats(self) -> Dict[str, Any]:
        """Get today's usage statistics"""
        self._ensure_today()
        today = date.today().isoformat()
        stats = self.usage["daily"].get(today, self._empty_day_stats())

        return {
            "date": today,
            "conversations": stats["conversations"],
            "chat_requests": stats["chat_requests"],
            "ask_requests": stats["ask_requests"],
            "tokens": {
                "input": stats["total_input_tokens"],
                "output": stats["total_output_tokens"],
                "total": stats["total_input_tokens"] + stats["total_output_tokens"]
            },
            "estimated_cost_usd": round(stats["estimated_cost_usd"], 4),
            "estimated_cost_gbp": round(stats["estimated_cost_usd"] * 0.79, 4),  # Approximate conversion
            "unique_sessions": len(stats["unique_sessions"]),
            "errors": stats["errors"],
            "abuse_flags": stats["abuse_flags"]
        }

    def get_daily_cost_usd(self) -> float:
        """Get today's estimated cost in USD"""
        self._ensure_today()
        today = date.today().isoformat()
        return self.usage["daily"].get(today, {}).get("estimated_cost_usd", 0.0)

    def get_summary_report(self) -> Dict[str, Any]:
        """Get a summary report for the dashboard"""
        self._ensure_today()
        today_stats = self.get_today_stats()

        return {
            "today": today_stats,
            "lifetime": {
                "total_conversations": self.usage["lifetime"]["total_conversations"],
                "total_tokens": self.usage["lifetime"]["total_tokens"],
                "total_cost_usd": round(self.usage["lifetime"]["total_cost_usd"], 2),
                "total_cost_gbp": round(self.usage["lifetime"]["total_cost_usd"] * 0.79, 2)
            },
            "last_7_days": self._get_last_n_days(7)
        }

    def _get_last_n_days(self, n: int) -> list:
        """Get stats for the last N days"""
        from datetime import timedelta

        result = []
        for i in range(n):
            day = (date.today() - timedelta(days=i)).isoformat()
            if day in self.usage.get("daily", {}):
                day_data = self.usage["daily"][day]
                result.append({
                    "date": day,
                    "conversations": day_data["conversations"],
                    "cost_usd": round(day_data["estimated_cost_usd"], 4)
                })
            else:
                result.append({
                    "date": day,
                    "conversations": 0,
                    "cost_usd": 0.0
                })
        return result


# =============================================================================
# ABUSE FLAGGING
# =============================================================================

class AbuseLogger:
    """
    Logs potentially abusive interactions for review.
    Does not block immediately - flags for human review.
    """

    def __init__(self):
        LOGS_DIR.mkdir(exist_ok=True)

    def flag_interaction(
        self,
        session_id: str,
        ip_hash: str,
        flag_type: str,
        user_query: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Flag an interaction for review.

        Flag types:
        - prompt_injection: Attempted prompt manipulation
        - abuse: Aggressive or abusive language
        - spam: Repeated identical requests
        - harmful_content: Attempts to get harmful content
        """
        london_tz = ZoneInfo('Europe/London')
        now = datetime.now(london_tz)

        flag_entry = {
            "timestamp": now.isoformat(),
            "session_id": session_id,
            "ip_hash": ip_hash,
            "flag_type": flag_type,
            "user_query": user_query[:500],  # Truncate
            "details": details
        }

        try:
            with open(ABUSE_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(flag_entry) + '\n')
        except Exception as e:
            get_error_logger().error(f"Failed to write abuse flag: {e}")


# =============================================================================
# FEEDBACK LOGGING (Testimonies & Flags)
# =============================================================================

class FeedbackLogger:
    """
    Logs user feedback about venues: testimonies (love) and flags (issues).
    """

    def __init__(self):
        LOGS_DIR.mkdir(exist_ok=True)

    def log_testimony(
        self,
        venue: str,
        text: str,
        email: Optional[str] = None,
        ip_hash: Optional[str] = None
    ):
        """Log a positive testimony about a venue."""
        london_tz = ZoneInfo('Europe/London')
        now = datetime.now(london_tz)

        entry = {
            "timestamp": now.isoformat(),
            "type": "testimony",
            "venue": venue,
            "text": text[:2000] if text else None,
            "email": email,
            "ip_hash": ip_hash
        }

        try:
            with open(FEEDBACK_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            get_error_logger().error(f"Failed to write testimony: {e}")

    def log_flag(
        self,
        venue: str,
        reason: str,
        details: Optional[str] = None,
        ip_hash: Optional[str] = None
    ):
        """Log a flag/issue report about a venue."""
        london_tz = ZoneInfo('Europe/London')
        now = datetime.now(london_tz)

        entry = {
            "timestamp": now.isoformat(),
            "type": "flag",
            "venue": venue,
            "reason": reason,
            "details": details[:1000] if details else None,
            "ip_hash": ip_hash
        }

        try:
            with open(FEEDBACK_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            get_error_logger().error(f"Failed to write flag: {e}")


# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

_conversation_logger = None
_usage_tracker = None
_abuse_logger = None
_feedback_logger = None


def get_conversation_logger() -> ConversationLogger:
    """Get the conversation logger instance"""
    global _conversation_logger
    if _conversation_logger is None:
        _conversation_logger = ConversationLogger()
    return _conversation_logger


def get_usage_tracker() -> UsageTracker:
    """Get the usage tracker instance"""
    global _usage_tracker
    if _usage_tracker is None:
        _usage_tracker = UsageTracker()
    return _usage_tracker


def get_abuse_logger() -> AbuseLogger:
    """Get the abuse logger instance"""
    global _abuse_logger
    if _abuse_logger is None:
        _abuse_logger = AbuseLogger()
    return _abuse_logger


def get_feedback_logger() -> FeedbackLogger:
    """Get the feedback logger instance"""
    global _feedback_logger
    if _feedback_logger is None:
        _feedback_logger = FeedbackLogger()
    return _feedback_logger


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def log_chat_interaction(
    session_id: str,
    user_query: str,
    lark_response: str,
    input_tokens: int,
    output_tokens: int,
    response_time_ms: float,
    error: Optional[str] = None,
    ip_hash: Optional[str] = None
):
    """Convenience function to log a /chat interaction"""
    logger = get_conversation_logger()
    tracker = get_usage_tracker()

    logger.log_interaction(
        endpoint="/chat",
        session_id=session_id,
        user_query=user_query,
        lark_response=lark_response,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        response_time_ms=response_time_ms,
        error=error,
        ip_hash=ip_hash
    )

    tracker.record_request(
        endpoint="/chat",
        session_id=session_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        is_error=error is not None
    )


def log_ask_interaction(
    session_id: str,
    user_query: str,
    lark_response: str,
    response_time_ms: float,
    safety_tier: Optional[str] = None,
    mood_detected: Optional[str] = None,
    confidence: Optional[float] = None,
    error: Optional[str] = None,
    ip_hash: Optional[str] = None
):
    """Convenience function to log an /ask interaction"""
    logger = get_conversation_logger()
    tracker = get_usage_tracker()

    logger.log_interaction(
        endpoint="/ask",
        session_id=session_id,
        user_query=user_query,
        lark_response=lark_response,
        input_tokens=0,  # /ask doesn't use Claude API
        output_tokens=0,
        response_time_ms=response_time_ms,
        error=error,
        ip_hash=ip_hash,
        safety_tier=safety_tier,
        mood_detected=mood_detected,
        confidence=confidence
    )

    tracker.record_request(
        endpoint="/ask",
        session_id=session_id,
        input_tokens=0,
        output_tokens=0,
        is_error=error is not None
    )


# =============================================================================
# CLI TEST
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  Lark Logger - Test")
    print("="*60)

    # Test logging
    session_id = generate_session_id()
    print(f"\n  Generated session ID: {session_id}")

    # Test conversation logging
    logger = get_conversation_logger()
    logger.log_interaction(
        endpoint="/chat",
        session_id=session_id,
        user_query="I need somewhere witchy tonight",
        lark_response="The veil is thin tonight. Treadwell's Bookshop in Bloomsbury...",
        input_tokens=5000,
        output_tokens=150,
        response_time_ms=1234.56,
        mood_detected="Witchy & Wild"
    )
    print("  Logged test conversation")

    # Test usage tracking
    tracker = get_usage_tracker()
    tracker.record_request("/chat", session_id, 5000, 150)

    # Print summary
    summary = tracker.get_summary_report()
    print(f"\n  Today's stats:")
    print(f"    Conversations: {summary['today']['conversations']}")
    print(f"    Cost: ${summary['today']['estimated_cost_usd']:.4f}")

    print("\n" + "="*60)
