# 📊 lark_metrics.py

"""
The London Lark — Metrics and Logging

Tracks usage stats to measure coverage and success rates:
- Mood resolution confidence distribution
- Venue match success rate
- Filter usage frequency
"""

import json
import os
from datetime import datetime
from pathlib import Path

METRICS_FILE = "lark_metrics.json"

class LarkMetrics:
    def __init__(self):
        self.metrics = self._load_metrics()

    def _load_metrics(self):
        """Load existing metrics from file or create new"""
        if os.path.exists(METRICS_FILE):
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        return {
            "total_queries": 0,
            "mood_found": 0,
            "mood_not_found": 0,
            "confidence_distribution": {
                "exact_match": 0,      # confidence = 1.0
                "high_confidence": 0,  # 0.9 <= confidence < 1.0
                "medium_confidence": 0, # 0.8 <= confidence < 0.9
                "low_confidence": 0    # 0.75 <= confidence < 0.8
            },
            "venue_matches": {
                "found_venues": 0,
                "no_venues": 0
            },
            "filter_usage": {
                "mood": 0,
                "location": 0,
                "time": 0,
                "budget": 0,
                "group": 0,
                "genre": 0
            },
            "session_history": []
        }

    def log_query(self, filters, mood_confidence, venue_count):
        """Log a single query with its results"""
        self.metrics["total_queries"] += 1

        # Track mood resolution
        if filters.get("mood"):
            self.metrics["mood_found"] += 1

            # Track confidence distribution
            if mood_confidence >= 1.0:
                self.metrics["confidence_distribution"]["exact_match"] += 1
            elif mood_confidence >= 0.9:
                self.metrics["confidence_distribution"]["high_confidence"] += 1
            elif mood_confidence >= 0.8:
                self.metrics["confidence_distribution"]["medium_confidence"] += 1
            elif mood_confidence >= 0.75:
                self.metrics["confidence_distribution"]["low_confidence"] += 1
        else:
            self.metrics["mood_not_found"] += 1

        # Track venue matches
        if venue_count > 0:
            self.metrics["venue_matches"]["found_venues"] += 1
        else:
            self.metrics["venue_matches"]["no_venues"] += 1

        # Track filter usage
        for filter_name in ["mood", "location", "time", "budget", "group", "genre"]:
            if filters.get(filter_name):
                self.metrics["filter_usage"][filter_name] += 1

        # Add to session history (keep last 10)
        self.metrics["session_history"].append({
            "timestamp": datetime.now().isoformat(),
            "filters": filters,
            "confidence": mood_confidence,
            "venue_count": venue_count
        })
        if len(self.metrics["session_history"]) > 10:
            self.metrics["session_history"].pop(0)

        # Save after each log
        self._save_metrics()

    def _save_metrics(self):
        """Save metrics to file"""
        with open(METRICS_FILE, 'w') as f:
            json.dump(self.metrics, f, indent=2)

    def get_coverage_stats(self):
        """Calculate and return coverage statistics"""
        total = self.metrics["total_queries"]
        if total == 0:
            return {
                "total_queries": 0,
                "mood_resolution_rate": 0,
                "venue_match_rate": 0,
                "exact_match_rate": 0
            }

        mood_found = self.metrics["mood_found"]
        venues_found = self.metrics["venue_matches"]["found_venues"]
        exact_matches = self.metrics["confidence_distribution"]["exact_match"]

        return {
            "total_queries": total,
            "mood_resolution_rate": (mood_found / total) * 100,
            "venue_match_rate": (venues_found / total) * 100,
            "exact_match_rate": (exact_matches / total) * 100 if total > 0 else 0,
            "avg_filters_per_query": sum(self.metrics["filter_usage"].values()) / total
        }

    def print_report(self):
        """Print a formatted metrics report"""
        stats = self.get_coverage_stats()
        total = self.metrics["total_queries"]

        print("\n" + "="*60)
        print("  THE LONDON LARK — METRICS REPORT")
        print("="*60)

        if total == 0:
            print("\nNo queries logged yet.")
            print("="*60 + "\n")
            return

        print(f"\n📊 Overall Stats:")
        print(f"   Total queries: {total}")
        print(f"   Mood resolution rate: {stats['mood_resolution_rate']:.1f}%")
        print(f"   Venue match rate: {stats['venue_match_rate']:.1f}%")
        print(f"   Exact match rate: {stats['exact_match_rate']:.1f}%")
        print(f"   Avg filters per query: {stats['avg_filters_per_query']:.1f}")

        print(f"\n🎯 Mood Confidence Distribution:")
        conf_dist = self.metrics["confidence_distribution"]
        total_with_mood = self.metrics["mood_found"]
        if total_with_mood > 0:
            print(f"   Exact matches (1.0):      {conf_dist['exact_match']} ({conf_dist['exact_match']/total_with_mood*100:.1f}%)")
            print(f"   High confidence (0.9+):   {conf_dist['high_confidence']} ({conf_dist['high_confidence']/total_with_mood*100:.1f}%)")
            print(f"   Medium confidence (0.8+): {conf_dist['medium_confidence']} ({conf_dist['medium_confidence']/total_with_mood*100:.1f}%)")
            print(f"   Low confidence (0.75+):   {conf_dist['low_confidence']} ({conf_dist['low_confidence']/total_with_mood*100:.1f}%)")
        else:
            print("   No moods resolved yet")

        print(f"\n🏛️ Venue Matching:")
        vm = self.metrics["venue_matches"]
        print(f"   Found venues:  {vm['found_venues']} ({vm['found_venues']/total*100:.1f}%)")
        print(f"   No venues:     {vm['no_venues']} ({vm['no_venues']/total*100:.1f}%)")

        print(f"\n🔍 Filter Usage:")
        fu = self.metrics["filter_usage"]
        for filter_name, count in sorted(fu.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"   {filter_name.capitalize()}: {count} ({count/total*100:.1f}%)")

        print("\n" + "="*60 + "\n")

    def reset_metrics(self):
        """Reset all metrics (useful for testing)"""
        self.metrics = {
            "total_queries": 0,
            "mood_found": 0,
            "mood_not_found": 0,
            "confidence_distribution": {
                "exact_match": 0,
                "high_confidence": 0,
                "medium_confidence": 0,
                "low_confidence": 0
            },
            "venue_matches": {
                "found_venues": 0,
                "no_venues": 0
            },
            "filter_usage": {
                "mood": 0,
                "location": 0,
                "time": 0,
                "budget": 0,
                "group": 0,
                "genre": 0
            },
            "session_history": []
        }
        self._save_metrics()

# Global metrics instance
_metrics_instance = None

def get_metrics():
    """Get or create the global metrics instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = LarkMetrics()
    return _metrics_instance

# Example usage
if __name__ == "__main__":
    metrics = LarkMetrics()
    metrics.print_report()
