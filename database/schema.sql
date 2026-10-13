-- ECO-PULSE SQLite Database Schema
-- Defines entities for incident tracking, measurements, actions, receipts, challenges, and hardware logs

CREATE TABLE IF NOT EXISTS incidents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL, -- 'water', 'electricity', 'waste', 'air_quality', 'other'
    location TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL, -- 'low', 'medium', 'high', 'critical'
    status TEXT NOT NULL DEFAULT 'open', -- 'open', 'in_progress', 'resolved', 'reopened'
    created_at TEXT NOT NULL,
    resolved_at TEXT,
    baseline_value REAL,
    baseline_unit TEXT,
    followup_value REAL,
    followup_unit TEXT,
    observation_hours REAL DEFAULT 24.0,
    evidence_image TEXT,
    reporter_name TEXT DEFAULT 'Anonymous',
    is_anonymous INTEGER DEFAULT 0,
    is_simulated INTEGER DEFAULT 0,
    anomaly_classification TEXT DEFAULT 'normal', -- 'normal', 'unusual', 'high_priority'
    anomaly_reason TEXT,
    repeat_incident_id TEXT,
    repeat_count INTEGER DEFAULT 0,
    latitude REAL,
    longitude REAL
);

CREATE TABLE IF NOT EXISTS actions (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    why_recommended TEXT,
    expected_benefit TEXT,
    estimated_cost TEXT,
    difficulty TEXT, -- 'easy', 'moderate', 'advanced'
    urgency TEXT, -- 'immediate', 'next_24h', 'scheduled'
    verification_method TEXT,
    limitations TEXT,
    status TEXT NOT NULL DEFAULT 'recommended', -- 'recommended', 'accepted', 'in_progress', 'completed', 'rejected'
    created_at TEXT NOT NULL,
    completed_at TEXT,
    FOREIGN KEY (incident_id) REFERENCES incidents (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS receipts (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    action_id TEXT,
    location TEXT NOT NULL,
    category TEXT NOT NULL,
    baseline_measurement REAL NOT NULL,
    baseline_unit TEXT NOT NULL,
    followup_measurement REAL NOT NULL,
    followup_unit TEXT NOT NULL,
    observation_interval_hours REAL NOT NULL,
    savings_amount REAL NOT NULL,
    savings_unit TEXT NOT NULL,
    carbon_kg_co2e REAL,
    emission_factor_used REAL,
    emission_factor_source TEXT,
    calculation_formula TEXT NOT NULL,
    assumptions TEXT,
    confidence_level TEXT NOT NULL, -- 'VERIFIED', 'ESTIMATED', 'SIMULATED'
    evidence_source TEXT,
    is_repeat_incident INTEGER DEFAULT 0,
    verified_at TEXT NOT NULL,
    verifier_identity TEXT DEFAULT 'ECO-PULSE BlackBox Engine',
    hash_signature TEXT NOT NULL,
    FOREIGN KEY (incident_id) REFERENCES incidents (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS challenges (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    target_interventions INTEGER NOT NULL,
    current_verified_count INTEGER DEFAULT 0,
    badge_name TEXT,
    icon TEXT,
    deadline TEXT
);

CREATE TABLE IF NOT EXISTS challenge_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id TEXT NOT NULL,
    participant_name TEXT NOT NULL,
    incident_id TEXT,
    joined_at TEXT NOT NULL,
    contributed_action INTEGER DEFAULT 0,
    FOREIGN KEY (challenge_id) REFERENCES challenges (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hardware_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    flow_rate_lpm REAL NOT NULL,
    total_liters REAL NOT NULL,
    status TEXT DEFAULT 'normal',
    is_simulated INTEGER DEFAULT 1,
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
