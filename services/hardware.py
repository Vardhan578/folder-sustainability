"""
ECO-PULSE Hardware Adapter & ESP32 Water-Flow Sensor Integration
Provides a decoupled hardware gateway interface for YF-S201 / Hall-effect flow sensors
connected to ESP32 microcontrollers over HTTP/REST or MQTT.
Maintains strict separation between REAL hardware readings and SIMULATED test bench readings.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import random

class HardwareAdapter:
    """
    Hardware bridge interface for real ESP32 devices and local mock simulator.
    """

    CRITICAL_FLOW_THRESHOLD_LPM = 3.0 # Flow rate above 3.0 L/min flagged as potential leak
    
    @staticmethod
    def process_incoming_reading(payload: Dict[str, Any], is_simulated: bool = False) -> Dict[str, Any]:
        """
        Validates and parses payload from ESP32.
        Expected JSON schema:
        {
            "device_id": "esp32-flow-node-01",
            "flow_rate_lpm": 2.45,
            "total_liters": 158.2,
            "timestamp": "2026-10-13T09:30:00Z",
            "api_key": "..."
        }
        """
        device_id = payload.get("device_id", "unknown-device").strip()
        if not device_id:
            raise ValueError("Device ID is required in hardware payload.")

        try:
            flow_rate_lpm = float(payload.get("flow_rate_lpm", 0.0))
            total_liters = float(payload.get("total_liters", 0.0))
        except (ValueError, TypeError):
            raise ValueError("flow_rate_lpm and total_liters must be valid floating point numbers.")

        if flow_rate_lpm < 0 or total_liters < 0:
            raise ValueError("Flow readings cannot be negative.")

        timestamp = payload.get("timestamp") or datetime.now(timezone.utc).isoformat()
        
        # Anomaly / leak trigger check
        is_abnormal = flow_rate_lpm >= HardwareAdapter.CRITICAL_FLOW_THRESHOLD_LPM
        status = "abnormal_leak" if is_abnormal else "normal"

        return {
            "device_id": device_id,
            "flow_rate_lpm": round(flow_rate_lpm, 2),
            "total_liters": round(total_liters, 2),
            "status": status,
            "is_simulated": 1 if is_simulated else 0,
            "timestamp": timestamp,
            "is_abnormal": is_abnormal,
            "warning": f"Abnormal flow detected: {flow_rate_lpm:.2f} L/min exceeds threshold of {HardwareAdapter.CRITICAL_FLOW_THRESHOLD_LPM} L/min." if is_abnormal else None
        }

    @staticmethod
    def generate_simulated_reading(scenario: str = "leak") -> Dict[str, Any]:
        """
        Produces an explicitly labeled SIMULATED reading for hackathon demonstration.
        Never disguised as real hardware.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        if scenario == "leak":
            # Flowing leak between 3.2 and 4.8 L/min
            flow = round(random.uniform(3.2, 4.8), 2)
            total = round(random.uniform(120.0, 240.0), 1)
        elif scenario == "normal_trickle":
            flow = round(random.uniform(0.1, 0.4), 2)
            total = round(random.uniform(20.0, 45.0), 1)
        else: # resolved / zero flow
            flow = 0.00
            total = 180.5

        parsed = HardwareAdapter.process_incoming_reading({
            "device_id": "esp32-sim-bench-01",
            "flow_rate_lpm": flow,
            "total_liters": total,
            "timestamp": now_iso
        }, is_simulated=True)

        parsed["source_label"] = "SIMULATED TEST BENCH"
        return parsed
