"""
Unit Tests for Waste Fingerprint Anomaly Detector and Recommendation Engine
"""

import unittest
from services.anomaly_detection import AnomalyDetectionEngine
from services.recommendations import RecommendationEngine

class TestAnomalyAndRecommendations(unittest.TestCase):

    def test_off_hours_high_priority_leak(self):
        incident = {
            "id": "INC-TEST-01",
            "category": "water",
            "location": "Hostel Block B",
            "severity": "critical",
            "baseline_value": 4.5,
            "baseline_unit": "L/min",
            "created_at": "2026-10-13T02:30:00Z"
        }
        # Simulate 2 prior incidents at same location
        history = [
            {"id": "INC-OLD-1", "location": "Hostel Block B"},
            {"id": "INC-OLD-2", "location": "Hostel Block B"},
            {"id": "INC-OTHER", "location": "Library"}
        ]

        analysis = AnomalyDetectionEngine.analyze_fingerprint(incident, history)
        self.assertEqual(analysis["classification"], "high_priority")
        self.assertGreaterEqual(analysis["score"], 50)
        self.assertTrue(any("Off-Hours" in r for r in analysis["reasons"]))
        self.assertTrue(any("Recurring" in r for r in analysis["reasons"]))

        # Recommendation should advise chronic replacement
        recs = RecommendationEngine.generate_recommendations(incident, analysis)
        self.assertTrue(len(recs) > 0)
        self.assertIn("Valve", recs[0]["title"])
        self.assertIn("verification_method", recs[0])
        self.assertEqual(recs[0]["status"], "recommended")

    def test_normal_daytime_incident(self):
        incident = {
            "id": "INC-TEST-02",
            "category": "waste",
            "location": "Cafeteria Patio",
            "severity": "low",
            "baseline_value": 15.0,
            "baseline_unit": "kg",
            "created_at": "2026-10-13T14:00:00Z"
        }
        history = []
        analysis = AnomalyDetectionEngine.analyze_fingerprint(incident, history)
        self.assertEqual(analysis["classification"], "normal")
        self.assertLess(analysis["score"], 25)

if __name__ == "__main__":
    unittest.main()
