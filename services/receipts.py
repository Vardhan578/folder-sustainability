"""
ECO-PULSE Environmental Receipt Generator & Black Box Ledger
Produces tamper-evident, auditable environmental receipts with transparent
provenance, cryptographic digest signatures, and strict confidence classifications.
"""

from typing import Dict, Any, Optional
import hashlib
import uuid
from datetime import datetime, timezone
from services.calculations import EnvironmentalCalculationEngine

class ReceiptService:
    """
    Core differentiator: The Environmental Receipt.
    Turns an informal intervention into an irrefutable audit document.
    """

    @staticmethod
    def generate_receipt(
        incident: Dict[str, Any],
        followup_value: float,
        followup_unit: str,
        observation_hours: float = 24.0,
        observation_days: float = 1.0,
        action_id: Optional[str] = None,
        emission_factor: Optional[float] = None,
        emission_source: Optional[str] = None,
        verifier_identity: str = "ECO-PULSE Audit BlackBox",
        is_simulated_override: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Creates an Environmental Receipt from an incident and follow-up data.
        Determines confidence level: VERIFIED | ESTIMATED | SIMULATED.
        """
        incident_id = incident.get("id")
        location = incident.get("location", "Unknown Location")
        category = incident.get("category", "other").lower()
        baseline_val = incident.get("baseline_value")
        baseline_unit = incident.get("baseline_unit", "")
        is_simulated_flag = bool(incident.get("is_simulated", 0))
        if is_simulated_override is not None:
            is_simulated_flag = is_simulated_override

        # Determine confidence classification
        if is_simulated_flag:
            confidence = "SIMULATED"
        elif baseline_val is None or followup_value is None:
            confidence = "ESTIMATED"
        elif baseline_unit.strip().lower() != followup_unit.strip().lower():
            # Incompatible units cannot be directly verified
            confidence = "ESTIMATED"
        else:
            confidence = "VERIFIED"

        # Calculate savings via calculation engine
        if category == "water":
            res = EnvironmentalCalculationEngine.calculate_water_savings(
                baseline_flow_lpm=baseline_val or 0.0,
                followup_flow_lpm=followup_value,
                observation_hours_per_day=observation_hours,
                observation_days=observation_days,
                baseline_unit=baseline_unit,
                followup_unit=followup_unit,
                is_simulated=is_simulated_flag
            )
            savings_amount = res["savings_amount"]
            savings_unit = res["savings_unit"]
            calc_formula = res["formula"]
            assumptions = res["assumptions"]

        elif category == "electricity":
            res = EnvironmentalCalculationEngine.calculate_electricity_savings(
                baseline_kwh=baseline_val or 0.0,
                followup_kwh=followup_value,
                observation_days=observation_days,
                baseline_unit=baseline_unit,
                followup_unit=followup_unit,
                is_simulated=is_simulated_flag
            )
            savings_amount = res["savings_amount"]
            savings_unit = res["savings_unit"]
            calc_formula = res["formula"]
            assumptions = res["assumptions"]

        elif category == "waste":
            # For waste, the followup represents the segregated/diverted weight
            res = EnvironmentalCalculationEngine.calculate_waste_diversion(
                diverted_kg=followup_value,
                unit=followup_unit,
                is_simulated=is_simulated_flag
            )
            savings_amount = res["savings_amount"]
            savings_unit = res["savings_unit"]
            calc_formula = res["formula"]
            assumptions = res["assumptions"]

        else:
            # Generic category
            delta = max(0.0, float(baseline_val or 0.0) - float(followup_value))
            savings_amount = round(delta, 2)
            savings_unit = followup_unit or "units"
            calc_formula = f"Baseline ({baseline_val}) - Followup ({followup_value}) = {savings_amount} {savings_unit}"
            assumptions = "Direct before-and-after variance recorded."

        # Compute carbon avoidance if emission factor provided
        carbon_res = EnvironmentalCalculationEngine.calculate_carbon_avoidance(
            category=category,
            savings_amount=savings_amount,
            emission_factor=emission_factor,
            source_citation=emission_source
        )
        carbon_kg = carbon_res["carbon_kg_co2e"]
        carbon_source = carbon_res["source"]
        carbon_factor_used = carbon_res["emission_factor_used"]

        receipt_id = f"RCP-2026-{uuid.uuid4().hex[:6].upper()}"
        verified_at = datetime.now(timezone.utc).isoformat()
        is_repeat = 1 if (incident.get("repeat_count") or 0) > 0 else 0

        # Cryptographic Black Box Hash Signature (SHA-256)
        raw_payload = f"{receipt_id}|{incident_id}|{location}|{baseline_val}|{followup_value}|{savings_amount}|{verified_at}"
        hash_signature = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

        evidence_src = "Calibrated Sensor Log" if not is_simulated_flag else "Simulated Hackathon Test Bench"
        if incident.get("evidence_image"):
            evidence_src += f" + Photo Proof: {incident.get('evidence_image')}"

        receipt = {
            "id": receipt_id,
            "incident_id": incident_id,
            "action_id": action_id,
            "location": location,
            "category": category,
            "baseline_measurement": float(baseline_val or 0.0),
            "baseline_unit": baseline_unit,
            "followup_measurement": float(followup_value),
            "followup_unit": followup_unit,
            "observation_interval_hours": float(observation_hours),
            "savings_amount": float(savings_amount),
            "savings_unit": savings_unit,
            "carbon_kg_co2e": carbon_kg,
            "emission_factor_used": carbon_factor_used,
            "emission_factor_source": carbon_source,
            "calculation_formula": calc_formula,
            "assumptions": assumptions,
            "confidence_level": confidence,
            "evidence_source": evidence_src,
            "is_repeat_incident": is_repeat,
            "verified_at": verified_at,
            "verifier_identity": verifier_identity,
            "hash_signature": hash_signature
        }

        return receipt

    @staticmethod
    def generate_csv_for_receipts(receipts_list: list) -> str:
        """Exports receipts to standard CSV text."""
        import io
        import csv

        output = io.StringIO()
        fieldnames = [
            "Receipt_ID", "Incident_ID", "Location", "Category",
            "Baseline_Measurement", "Baseline_Unit",
            "Followup_Measurement", "Followup_Unit",
            "Observation_Hours", "Savings_Amount", "Savings_Unit",
            "Carbon_Avoided_kg_CO2e", "Confidence_Level",
            "Verified_At", "Hash_Signature"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for r in receipts_list:
            writer.writerow({
                "Receipt_ID": r.get("id"),
                "Incident_ID": r.get("incident_id"),
                "Location": r.get("location"),
                "Category": r.get("category"),
                "Baseline_Measurement": r.get("baseline_measurement"),
                "Baseline_Unit": r.get("baseline_unit"),
                "Followup_Measurement": r.get("followup_measurement"),
                "Followup_Unit": r.get("followup_unit"),
                "Observation_Hours": r.get("observation_interval_hours"),
                "Savings_Amount": r.get("savings_amount"),
                "Savings_Unit": r.get("savings_unit"),
                "Carbon_Avoided_kg_CO2e": r.get("carbon_kg_co2e") or "Unavailable",
                "Confidence_Level": r.get("confidence_level"),
                "Verified_At": r.get("verified_at"),
                "Hash_Signature": r.get("hash_signature")
            })

        return output.getvalue()
