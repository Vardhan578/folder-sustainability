"""
ECO-PULSE SQLite Database Access Layer
Provides parameterized queries, connection management, schema initialization, and transactional safety.
"""

import sqlite3
import os
import json
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eco_pulse.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")

def get_db_connection():
    """Returns a SQLite connection with row_factory enabled for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initializes the database using schema.sql if tables do not exist."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    with get_db_connection() as conn:
        conn.executescript(schema_sql)
        _init_default_settings(conn)
        _init_default_challenges(conn)

def _init_default_settings(conn):
    """Sets up default configuration if not already set."""
    defaults = {
        "org_name": "EcoCampus Polytechnic & Research Park",
        "theme": "dark",
        "unit_system": "metric",
        "grid_emission_factor": "0.716", # kg CO2e / kWh (CEA India Grid)
        "grid_emission_source": "Central Electricity Authority (CEA) v19 Baseline Database",
        "water_emission_factor": "0.000298", # kg CO2e / Liter
        "water_emission_source": "EPA WARM Water-Energy Supply Nexus Factor",
        "waste_emission_factor": "0.520", # kg CO2e / kg diverted
        "waste_emission_source": "IPCC Solid Waste Composting Methane Avoidance Model",
        "demo_mode": "true",
        "hardware_simulation": "true",
        "api_key": "eco_pulse_hackathon_demo_key_2026"
    }
    for k, v in defaults.items():
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
    conn.commit()

def _init_default_challenges(conn):
    """Initializes baseline campus sustainability challenges."""
    cursor = conn.execute("SELECT COUNT(*) as cnt FROM challenges")
    if cursor.fetchone()["cnt"] == 0:
        challenges = [
            ("CHL-001", "Zero Drip Hostel Drive", "Identify and fix 10 recurring bathroom and kitchen plumbing leaks across all hostel blocks.", "water", 10, 0, "Aquifer Defender", "droplet", "2026-11-30"),
            ("CHL-002", "Vampire Power Hunt", "Audit computer labs and lecture halls after 9:00 PM to eliminate standby phantom power loads.", "electricity", 15, 0, "Kilowatt Guardian", "zap", "2026-12-15"),
            ("CHL-003", "Clean Stream Dining Hall", "Achieve 90%+ organic waste segregation in Central Mess to divert compost from landfill.", "waste", 8, 0, "Circular Champion", "recycle", "2026-11-20"),
            ("CHL-004", "Clean Air Corridor", "Monitor and rectify particulate and ventilation blockages in engineering workshop bays.", "air_quality", 5, 0, "Pure Breath Sentinel", "wind", "2026-12-31")
        ]
        conn.executemany("""
            INSERT INTO challenges (id, title, description, category, target_interventions, current_verified_count, badge_name, icon, deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, challenges)
        conn.commit()

def dict_from_row(row):
    """Converts a sqlite3.Row object to a standard Python dictionary."""
    if row is None:
        return None
    return dict(row)

def rows_to_dict_list(rows):
    """Converts a sequence of sqlite3.Row objects to a list of dicts."""
    return [dict(r) for r in rows]
