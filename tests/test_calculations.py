"""
Unit Tests for Environmental Calculation Engine & Receipts
Validates mathematical formulas, boundary conditions, edge cases, unit mismatches, and confidence levels.
"""

import unittest
from services.calculations import EnvironmentalCalculationEngine
from services.receipts import ReceiptService

class TestEnvironmentalCalculationEngine(unittest.TestCase):

    def test_water_savings_standard(self):
        # 2 L/min leak reduced to 0 L/min for 8 hours/day over 1 day: 2 * 60 * 8 = 960 L
        res = EnvironmentalCalculationEngine.calculate_water_savings(
            baseline_flow_lpm=2.0,
            followup_flow_lpm=0.0,
            observation_hours_per_day=8.0,
            observation_days=1.0,
            baseline_unit="L/min",
            followup_unit="L/min"
        )
        self.assertEqual(res["savings_amount"], 960.0)
        self.assertEqual(res["confidence"], "VERIFIED")
        self.assertEqual(res["savings_unit"], "Liters")

    def test_water_savings_partial_fix(self):
        # 4.5 L/min reduced to 1.5 L/min for 24 hours over 2 days
        # Delta = 3.0 L/min * 1440 min/day * 2 days = 8,640 Liters
        res = EnvironmentalCalculationEngine.calculate_water_savings(
            baseline_flow_lpm=4.5,
            followup_flow_lpm=1.5,
            observation_hours_per_day=24.0,
            observation_days=2.0
        )
        self.assertEqual(res["savings_amount"], 8640.0)
        self.assertEqual(res["net_flow_reduction_lpm"], 3.0)

    def test_water_savings_no_reduction_or_increase(self):
        # Follow-up flow is higher than baseline -> should clamp savings to 0, not negative
        res = EnvironmentalCalculationEngine.calculate_water_savings(
            baseline_flow_lpm=1.0,
            followup_flow_lpm=2.5,
            observation_hours_per_day=24.0,
            observation_days=1.0
        )
        self.assertEqual(res["savings_amount"], 0.0)
        self.assertEqual(res["net_flow_reduction_lpm"], 0.0)

    def test_unit_mismatch_raises_error(self):
        with self.assertRaises(ValueError):
            EnvironmentalCalculationEngine.calculate_water_savings(
                baseline_flow_lpm=2.0,
                followup_flow_lpm=0.5,
                baseline_unit="L/min",
                followup_unit="gallons/min"
            )

    def test_negative_input_raises_error(self):
        with self.assertRaises(ValueError):
            EnvironmentalCalculationEngine.calculate_water_savings(
                baseline_flow_lpm=-1.5,
                followup_flow_lpm=0.0
            )

    def test_electricity_savings_standard(self):
        # Baseline 120 kWh, followup 40 kWh over 5 days = (120 - 40) * 5 = 400 kWh
        res = EnvironmentalCalculationEngine.calculate_electricity_savings(
            baseline_kwh=120.0,
            followup_kwh=40.0,
            observation_days=5.0
        )
        self.assertEqual(res["savings_amount"], 400.0)
        self.assertEqual(res["savings_unit"], "kWh")
        self.assertEqual(res["confidence"], "VERIFIED")

    def test_waste_diversion(self):
        res = EnvironmentalCalculationEngine.calculate_waste_diversion(85.5)
        self.assertEqual(res["savings_amount"], 85.5)
        self.assertEqual(res["savings_unit"], "kg")

    def test_carbon_avoidance_with_factor(self):
        # 1,000 kWh saved with CEA grid factor 0.716 kg CO2e / kWh
        res = EnvironmentalCalculationEngine.calculate_carbon_avoidance(
            category="electricity",
            savings_amount=1000.0,
            emission_factor=0.716,
            source_citation="CEA Indian Power Sector Grid Factor"
        )
        self.assertEqual(res["carbon_kg_co2e"], 716.0)
        self.assertIn("716.00 kg CO₂e avoided", res["status_text"])

    def test_carbon_avoidance_without_factor(self):
        res = EnvironmentalCalculationEngine.calculate_carbon_avoidance(
            category="electricity",
            savings_amount=500.0,
            emission_factor=None
        )
        self.assertIsNone(res["carbon_kg_co2e"])
        self.assertEqual(res["status_text"], "Carbon estimate unavailable")

    def test_success_rate_calculation(self):
        # 8 verified out of 10 completed = 80.0%
        res = EnvironmentalCalculationEngine.calculate_success_rate(8, 10)
        self.assertEqual(res["rate_percentage"], 80.0)
        self.assertEqual(res["sample_size"], 10)

        # Zero sample size guard
        zero_res = EnvironmentalCalculationEngine.calculate_success_rate(0, 0)
        self.assertEqual(zero_res["rate_percentage"], 0.0)
        self.assertEqual(zero_res["sample_size"], 0)

    def test_receipt_confidence_classification(self):
        # Simulated flag produces SIMULATED
        incident_sim = {
            "id": "INC-SIM-01",
            "category": "water",
            "location": "Hostel B",
            "baseline_value": 3.0,
            "baseline_unit": "L/min",
            "is_simulated": 1
        }
        receipt_sim = ReceiptService.generate_receipt(
            incident=incident_sim,
            followup_value=0.0,
            followup_unit="L/min"
        )
        self.assertEqual(receipt_sim["confidence_level"], "SIMULATED")
        self.assertIsNotNone(receipt_sim["hash_signature"])

        # Genuine incident produces VERIFIED
        incident_real = {
            "id": "INC-REAL-01",
            "category": "water",
            "location": "Science Wing",
            "baseline_value": 2.5,
            "baseline_unit": "L/min",
            "is_simulated": 0
        }
        receipt_real = ReceiptService.generate_receipt(
            incident=incident_real,
            followup_value=0.0,
            followup_unit="L/min"
        )
        self.assertEqual(receipt_real["confidence_level"], "VERIFIED")

if __name__ == "__main__":
    unittest.main()
