"""
ECO-PULSE Waste Fingerprint & Transparent Anomaly Detection Service
Deterministic, rule-based engine that evaluates resource waste patterns,
recurrence rates, temporal signals, and volumetric deviations.
"""

from typing import Dict, Any, List
from datetime import datetime

class AnomalyDetectionEngine:
    """
    Transparent Rule-Based Anomaly Detector.
    Strictly avoids fake ML claims. Provides clear reasoning and audit score.
    """

    @staticmethod
    def analyze_fingerprint(
        incident_data: Dict[str, Any],
        historical_incidents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluates an incident against historical data at the same location.
        Returns:
            classification: 'normal' | 'unusual' | 'high_priority'
            reasons: list of explanatory strings
            fingerprint: dictionary of evaluated features
            score: 0 to 100 anomaly intensity index
        """
        category = incident_data.get("category", "other").lower()
        location = incident_data.get("location", "").strip().lower()
        severity = incident_data.get("severity", "medium").lower()
        baseline_val = incident_data.get("baseline_value") or 0.0
        baseline_unit = incident_data.get("baseline_unit", "")
        created_at_str = incident_data.get("created_at") or datetime.now().isoformat()

        # Parse timestamp for off-hours detection
        try:
            dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            hour = dt.hour
        except Exception:
            hour = 12

        # Filter prior incidents at exact location
        prior_at_location = [
            inc for inc in historical_incidents
            if inc.get("location", "").strip().lower() == location and inc.get("id") != incident_data.get("id")
        ]
        recurrence_count = len(prior_at_location)

        score = 0
        reasons = []

        # 1. Temporal Analysis (Off-hours waste: 11 PM to 5 AM)
        is_off_hours = (hour >= 23 or hour <= 5)
        if is_off_hours:
            score += 25
            reasons.append(f"Off-Hours Signal: Detected at {hour:02d}:00 during low-occupancy facility hours.")

        # 2. Recurrence / Chronic Failure Analysis
        if recurrence_count >= 3:
            score += 35
            reasons.append(f"Chronic Recurrence: {recurrence_count} previous incident(s) recorded at '{incident_data.get('location')}'. Indicates systemic fixture or pipe failure.")
        elif recurrence_count >= 1:
            score += 15
            reasons.append(f"Recurring Issue: Repeat event ({recurrence_count} previous occurrence at this facility).")

        # 3. Severity & Magnitude Deviation
        if severity == "critical":
            score += 30
            reasons.append("Critical Hazard: Tagged as critical severity requiring immediate intervention.")
        elif severity == "high":
            score += 20
            reasons.append("High Severity: Rapid loss rate with significant environmental impact.")

        # Specific resource thresholds
        if category == "water" and baseline_val >= 3.0: # >= 3 L/min leak
            score += 20
            daily_loss = baseline_val * 60 * 24
            reasons.append(f"Severe Flow Rate: {baseline_val} L/min equates to {daily_loss:,.0f} L/day continuous municipal loss.")
        elif category == "electricity" and baseline_val >= 50.0: # >= 50 kWh off-hours
            score += 20
            reasons.append(f"Significant Power Draw: {baseline_val} kWh load exceeds typical idle building threshold.")
        elif category == "waste" and baseline_val >= 100.0: # >= 100 kg
            score += 15
            reasons.append(f"Bulk Waste Accumulation: {baseline_val} kg unsegregated waste mass.")

        # 4. Final Classification
        if score >= 50:
            classification = "high_priority"
            badge_title = "High Priority Anomaly"
        elif score >= 25:
            classification = "unusual"
            badge_title = "Unusual Pattern"
        else:
            classification = "normal"
            badge_title = "Normal Operational Range"
            if not reasons:
                reasons.append("Isolated event within expected operational variance.")

        return {
            "classification": classification,
            "badge_title": badge_title,
            "score": min(score, 100),
            "reasons": reasons,
            "fingerprint": {
                "recurrence_count": recurrence_count,
                "is_off_hours": is_off_hours,
                "recorded_hour": hour,
                "severity": severity,
                "baseline_value": baseline_val,
                "baseline_unit": baseline_unit,
                "location": incident_data.get("location"),
                "prior_incident_ids": [p.get("id") for p in prior_at_location]
            }
        }
