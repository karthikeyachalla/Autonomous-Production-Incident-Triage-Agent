"""
SQLite Incident Memory Storage for Triage Agent
Saves all triaged incident reports to a local database for historical search & lookup.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any

DB_PATH = "incidents_history.db"

def init_db():
    """Initializes SQLite table for storing triaged incident records."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            severity TEXT,
            error_type TEXT,
            raw_log TEXT,
            diagnosis TEXT,
            status TEXT,
            rca_report TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_incident(result_state: Dict[str, Any]) -> int:
    """Saves a triaged incident result state into SQLite database."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta = result_state.get("parsed_metadata", {})
    severity = result_state.get("severity", "P2")
    error_type = meta.get("error_type", "Unknown")
    raw_log = result_state.get("raw_log", "")
    diagnosis = result_state.get("diagnosis", "")
    status = result_state.get("status", "TRIAGE_COMPLETE")
    rca_report = result_state.get("rca_report", "")
    
    cursor.execute("""
        INSERT INTO incidents (timestamp, severity, error_type, raw_log, diagnosis, status, rca_report)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, severity, error_type, raw_log, diagnosis, status, rca_report))
    
    incident_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return incident_id

def get_recent_incidents(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieves recent triaged incidents from database."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
