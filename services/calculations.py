"""
ECO-PULSE Environmental Calculation Engine
Pure, testable, and transparent mathematical functions for resource savings,
carbon estimation, confidence classification, and intervention success rates.
"""

from typing import Dict, Any, Optional, Tuple

class EnvironmentalCalculationEngine:
    """
    Standardized formulas adhering to strict scientific & engineering audit guidelines:
    - No fabricated savings
    - Transparent formulas and disclosed assumptions
    - Guard against division by zero and negative reductions
    """

    @staticmethod
    def calculate_water_savings(
        baseline_flow_lpm: float,
        followup_flow_lpm: float,
        observation_hours_per_day: float = 24.0,
        observation_days: float = 1.0,
        baseline_unit: str = "L/min",
        followup_unit: str = "L/min",
        is_simulated: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates net water savings in liters.
        Formula: max(0, baseline_flow - followup_flow) * (observation_hours_per_day * 60) * observation_days
        """
        # Validate inputs
        if baseline_flow_lpm is None or followup_flow_lpm is None:
            raise ValueError("Baseline and follow-up flow rates are required.")
        
        if baseline_flow_lpm < 0 or followup_flow_lpm < 0:
            raise ValueError("Flow rates cannot be negative.")
            
        if observation_hours_per_day <= 0 or observation_hours_per_day > 24:
            raise ValueError("Observation hours per day must be between 0 and 24.")

        if observation_days <= 0:
            raise ValueError("Observation days must be greater than zero.")

        # Unit verification
        clean_base_unit = baseline_unit.strip().lower()
        clean_follow_unit = followup_unit.strip().lower()
        if clean_base_unit != clean_follow_unit:
            raise ValueError(f"Incompatible measurement units: '{baseline_unit}' vs '{followup_unit}'. Normalize units before calculating savings.")

        # Flow reduction
        net_flow_reduction_lpm = max(0.0, float(baseline_flow_lpm) - float(followup_flow_lpm))
        leak_minutes_per_day = float(observation_hours_per_day) * 60.0
        daily_savings_liters = net_flow_reduction_lpm * leak_minutes_per_day
        total_savings_liters = round(daily_savings_liters * float(observation_days), 2)

        # Baseline potential waste if not addressed
        baseline_daily_loss = round(float(baseline_flow_lpm) * leak_minutes_per_day, 2)

        confidence = "SIMULATED" if is_simulated else "VERIFIED"

        formula_str = (
            f"net_flow_reduction ({net_flow_reduction_lpm:.2f} L/min) × "
            f"({observation_hours_per_day:.1f} hrs/day × 60 min) × "
            f"{observation_days:.1f} days = {total_savings_liters:,.2f} Liters"
        )

        return {
            "savings_amount": total_savings_liters,
            "savings_unit": "Liters",
            "daily_savings": round(daily_savings_liters, 2),
            "baseline_daily_loss": baseline_daily_loss,
            "net_flow_reduction_lpm": round(net_flow_reduction_lpm, 2),
            "formula": formula_str,
            "confidence": confidence,
            "assumptions": f"Assumed active leak flow duration: {observation_hours_per_day:.1f} hrs/day across {observation_days:.1f} day(s)."
        }

    @staticmethod
    def calculate_electricity_savings(
        baseline_kwh: float,
        followup_kwh: float,
        observation_days: float = 1.0,
        baseline_unit: str = "kWh",
        followup_unit: str = "kWh",
        is_simulated: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates electricity savings in kilowatt-hours (kWh).
        Formula: max(0, baseline_kwh - followup_kwh) * observation_days
        """
        if baseline_kwh is None or followup_kwh is None:
            raise ValueError("Baseline and follow-up energy readings are required.")
        
        if baseline_kwh < 0 or followup_kwh < 0:
            raise ValueError("Energy readings cannot be negative.")

        if observation_days <= 0:
            raise ValueError("Observation days must be greater than zero.")

        if baseline_unit.strip().lower() != followup_unit.strip().lower():
            raise ValueError(f"Incompatible energy units: '{baseline_unit}' vs '{followup_unit}'.")

        net_kwh_per_day = max(0.0, float(baseline_kwh) - float(followup_kwh))
        total_kwh_saved = round(net_kwh_per_day * float(observation_days), 2)
        confidence = "SIMULATED" if is_simulated else "VERIFIED"

        formula_str = (
            f"max(0, baseline ({baseline_kwh:.2f}) - followup ({followup_kwh:.2f})) × "
            f"{observation_days:.1f} days = {total_kwh_saved:,.2f} kWh"
        )

        return {
            "savings_amount": total_kwh_saved,
            "savings_unit": "kWh",
            "daily_savings": round(net_kwh_per_day, 2),
            "formula": formula_str,
            "confidence": confidence,
            "assumptions": f"Compared equivalent operational schedules over {observation_days:.1f} representative day(s)."
        }

    @staticmethod
    def calculate_waste_diversion(
        diverted_kg: float,
        unit: str = "kg",
        is_simulated: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates waste diverted from landfill in kg.
        """
        if diverted_kg is None or diverted_kg < 0:
            raise ValueError("Diverted waste weight must be non-negative.")

        net_kg = round(float(diverted_kg), 2)
        confidence = "SIMULATED" if is_simulated else "VERIFIED"

        return {
            "savings_amount": net_kg,
            "savings_unit": "kg",
            "formula": f"Measured segregated weight = {net_kg} kg diverted from landfill",
            "confidence": confidence,
            "assumptions": "Only counted strictly segregated, contamination-free material sent to verified composting or recycling streams."
        }

    @staticmethod
    def calculate_carbon_avoidance(
        category: str,
        savings_amount: float,
        emission_factor: Optional[float] = None,
        source_citation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimates avoided CO2-equivalent emissions if a documented emission factor is provided.
        Returns None for carbon_kg if emission factor is not supplied.
        """
        if emission_factor is None or emission_factor <= 0 or savings_amount is None or savings_amount <= 0:
            return {
                "carbon_kg_co2e": None,
                "status_text": "Carbon estimate unavailable",
                "reason": "Missing or non-positive emission factor",
                "emission_factor_used": None,
                "source": None
            }

        carbon_kg = round(float(savings_amount) * float(emission_factor), 3)
        return {
            "carbon_kg_co2e": carbon_kg,
            "status_text": f"{carbon_kg:,.2f} kg CO₂e avoided",
            "emission_factor_used": emission_factor,
            "source": source_citation or "Configured Regional Baseline",
            "formula": f"{savings_amount} units × {emission_factor} kg CO₂e/unit = {carbon_kg} kg CO₂e"
        }

    @staticmethod
    def calculate_success_rate(
        verified_interventions: int,
        eligible_completed_interventions: int
    ) -> Dict[str, Any]:
        """
        Calculates environmental intervention success rate.
        Formula: (verified_interventions / eligible_completed_interventions) * 100
        """
        if eligible_completed_interventions < 0 or verified_interventions < 0:
            raise ValueError("Intervention counts cannot be negative.")

        if eligible_completed_interventions == 0:
            return {
                "rate_percentage": 0.0,
                "sample_size": 0,
                "verified_count": 0,
                "eligible_count": 0,
                "display_text": "0.0% (0/0 verified)",
                "eligibility_criteria": "Requires documented before-and-after measurements with verifiable net savings."
            }

        rate = min(100.0, (float(verified_interventions) / float(eligible_completed_interventions)) * 100.0)
        return {
            "rate_percentage": round(rate, 1),
            "sample_size": eligible_completed_interventions,
            "verified_count": verified_interventions,
            "eligible_count": eligible_completed_interventions,
            "display_text": f"{rate:.1f}% ({verified_interventions}/{eligible_completed_interventions})",
            "eligibility_criteria": "Completed interventions with verified before & after audit records and positive resource reduction."
        }
