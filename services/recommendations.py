"""
ECO-PULSE Smart Action Recommendation Engine
Generates prioritized, actionable engineering and operational interventions
with transparent rationales, expected benefits, difficulty, and verification protocols.
"""

from typing import Dict, Any, List
import uuid
from datetime import datetime

class RecommendationEngine:
    """
    Expert rule engine providing concrete corrective steps for environmental anomalies.
    """

    @staticmethod
    def generate_recommendations(incident: Dict[str, Any], anomaly_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        category = incident.get("category", "other").lower()
        severity = incident.get("severity", "medium").lower()
        baseline_val = incident.get("baseline_value") or 0.0
        baseline_unit = incident.get("baseline_unit", "")
        reasons = anomaly_data.get("reasons", [])
        is_high_priority = anomaly_data.get("classification") == "high_priority"
        recurrence = anomaly_data.get("fingerprint", {}).get("recurrence_count", 0)

        actions = []
        now_iso = datetime.now().isoformat()

        if category == "water":
            if recurrence >= 2:
                # Chronic fixture failure
                actions.append({
                    "id": f"ACT-{uuid.uuid4().hex[:6].upper()}",
                    "incident_id": incident.get("id"),
                    "title": "Complete Ball Valve & Pressure Regulating Valve (PRV) Replacement",
                    "description": "Chronic leakage detected. Replace the worn brass internal valve seating and install an inline pressure regulating limiter set to 2.5 bar.",
                    "why_recommended": f"Facility has had {recurrence} repeat leak reports. Patching washers has failed; mechanical fatigue of the fixture requires root-cause replacement.",
                    "expected_benefit": f"Permanently eliminates {baseline_val} L/min continuous loss (~{baseline_val * 1440:,.0f} L/day).",
                    "estimated_cost": "$25 - $40 (Hardware + Labor)",
                    "difficulty": "moderate",
                    "urgency": "immediate" if is_high_priority else "next_24h",
                    "verification_method": "Perform 15-minute static pressure and flow log check after installation. Verify 0.0 L/min idle flow.",
                    "limitations": "Requires brief water supply shutoff to branch riser pipe for 45 minutes.",
                    "status": "recommended",
                    "created_at": now_iso
                })
            else:
                # Standard plumbing leak
                actions.append({
                    "id": f"ACT-{uuid.uuid4().hex[:6].upper()}",
                    "incident_id": incident.get("id"),
                    "title": "Fixture Cartridge & Washer Inspection and Seal Tightening",
                    "description": "Isolate fixture angle-stop, inspect internal ceramic disk/rubber washer for mineral fouling or tears, and re-torque or replace sealing o-ring.",
                    "why_recommended": "Rapid, cost-effective standard first-response for fixture dripping before replacing entire plumbing units.",
                    "expected_benefit": f"Stops drip rate of {baseline_val} {baseline_unit}, conserving estimated {baseline_val * 1440:,.0f} L daily.",
                    "estimated_cost": "$5 - $15 (Washers / Plumber tape)",
                    "difficulty": "easy",
                    "urgency": "next_24h",
                    "verification_method": "Place graduated catch cylinder under fixture for 10 minutes post-repair; measure zero accumulation.",
                    "limitations": "May be temporary if internal valve casting is corroded.",
                    "status": "recommended",
                    "created_at": now_iso
                })

            # Secondary acoustic or sub-meter audit if severe
            if baseline_val > 5.0 or severity in ["high", "critical"]:
                actions.append({
                    "id": f"ACT-{uuid.uuid4().hex[:6].upper()}",
                    "incident_id": incident.get("id"),
                    "title": "Ultrasonic Line Acoustic Audit & Sub-Meter Validation",
                    "description": "Deploy an ultrasonic clamp-on flow sensor or acoustic pipe microphone to verify concealed wall or underground pipe integrity.",
                    "why_recommended": "High flow rate indicates risk of concealed pipe fracture behind wall tiles or under floor slabs.",
                    "expected_benefit": "Detects subsurface line fractures before structural water damage occurs.",
                    "estimated_cost": "Cost unknown (In-house instrumentation or $80 contractor fee)",
                    "difficulty": "advanced",
                    "urgency": "immediate",
                    "verification_method": "Cross-compare main supply sub-meter with sum of terminal fixture readings.",
                    "limitations": "Requires acoustic silence window during late night hours.",
                    "status": "recommended",
                    "created_at": now_iso
                })

        elif category == "electricity":
            actions.append({
                "id": f"ACT-{uuid.uuid4().hex[:6].upper()}",
                "incident_id": incident.get("id"),
                "title": "Automated Programmable Timer & Smart Occupancy Relay Integration",
                "description": "Install DIN-rail weekly astronomical timer relay or dual-technology PIR/ultrasonic occupancy sensor on circuit breaker branch.",
                "why_recommended": "Addresses off-hours phantom loads and human forgetfulness without requiring manual nightly patrols.",
                "expected_benefit": f"Cuts idle nocturnal draw by estimated {baseline_val * 0.85:.1f} kWh nightly.",
                "estimated_cost": "$30 - $60 per circuit",
                "difficulty": "moderate",
                "urgency": "next_24h" if is_high_priority else "scheduled",
                "verification_method": "Compare sub-meter active power (kW) at 02:00 AM before and after timer installation over 3 consecutive weekdays.",
                "limitations": "Must provide manual emergency override switch for late-night maintenance staff.",
                "status": "recommended",
                "created_at": now_iso
            })
            actions.append({
                "id": f"ACT-{uuid.uuid4().hex[:6].upper()}",
                "incident_id": incident.get("id"),
                "title": "Appliance Energy Star Audit & Standby Power Strip Deployment",
                "description": "Inspect connected refrigeration, display monitors, and computing hardware. Install master-slave auto-cut power strips.",
                "why_recommended": "Peripheral equipment often consumes 10-15W continuously in quiescent standby mode.",
                "expected_benefit": "Saves 5-15% of branch load through automated idle isolation.",
                "estimated_cost": "$20 per smart power strip",
                "difficulty": "easy",
                "urgency": "scheduled",
                "verification_method": "Plug-in kill-a-watt power meter verification after 1 week.",
                "limitations": "User education required so critical network gear is not plugged into switched sockets.",
                "status": "recommended",
                "created_at": now_iso
            })

        elif category == "waste":
            actions.append({
                "id": f"ACT-{uuid.uuid4().hex[:6].upper()}",
                "incident_id": incident.get("id"),
                "title": "Dual-Stream Color-Coded Segregation Bins & Visual Nudge Signage",
                "description": "Replace single unsegregated bins with paired Green (Wet Organic / Compost) and Blue (Dry Recyclable) stations with pictographic lid apertures.",
                "why_recommended": "Contamination at point-of-disposal causes 80%+ of recyclable or compostable materials to be sent directly to landfills.",
                "expected_benefit": f"Diverts up to {baseline_val * 0.7:.1f} kg/week of clean organic and dry materials.",
                "estimated_cost": "$40 per dual-bin station",
                "difficulty": "easy",
                "urgency": "next_24h",
                "verification_method": "Conduct unannounced daily weigh-ins and contamination audits (<5% non-compliant waste) for 7 days.",
                "limitations": "Requires coordination with campus custodial crew to maintain separated collection bags.",
                "status": "recommended",
                "created_at": now_iso
            })

        elif category == "air_quality":
            actions.append({
                "id": f"ACT-{uuid.uuid4().hex[:6].upper()}",
                "incident_id": incident.get("id"),
                "title": "MERV-13 Filter Replacement & Outdoor Air Damper Rebalancing",
                "description": "Inspect air handling unit (AHU) intake filters, replace loaded media with MERV-13 rated pleats, and verify minimum outdoor air ventilation dampers.",
                "why_recommended": "High particulate or elevated CO2 concentrations indicate depleted filter lifespan and recirculating stagnant indoor air.",
                "expected_benefit": "Reduces indoor PM2.5 by 60-80% and brings CO2 below 800 ppm threshold.",
                "estimated_cost": "$45 - $90 per air handler",
                "difficulty": "moderate",
                "urgency": "immediate" if is_high_priority else "next_24h",
                "verification_method": "Continuous IAQ calibrated monitor reading for 48 hours under full occupancy conditions.",
                "limitations": "Higher MERV rating slightly increases fan static pressure and minor blower energy consumption.",
                "status": "recommended",
                "created_at": now_iso
            })

        else:
            # General environmental mitigation
            actions.append({
                "id": f"ACT-{uuid.uuid4().hex[:6].upper()}",
                "incident_id": incident.get("id"),
                "title": "Targeted Root-Cause Inspection & Metered Assessment",
                "description": "Perform physical walkthrough by facility officer and document calibrated baseline measurements.",
                "why_recommended": "Establish precise quantifiable baseline before allocating capital expenditure.",
                "expected_benefit": "Prevents redundant repairs and isolates underlying inefficiency.",
                "estimated_cost": "Low (Internal staff hours)",
                "difficulty": "easy",
                "urgency": "next_24h",
                "verification_method": "Logged comparison report with timestamped photographic proof.",
                "limitations": "Depends on availability of certified testing equipment.",
                "status": "recommended",
                "created_at": now_iso
            })

        return actions
