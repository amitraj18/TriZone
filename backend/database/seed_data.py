import os
import sys
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import DATABASE_PATH
from database.connection import resolve_db_path

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def init_db(db_path=None, force: bool = False):
    """Initializes the SQLite database with tables and seed data."""
    target_path = resolve_db_path(db_path)

    if force and os.path.exists(target_path):
        try:
            os.remove(target_path)
        except PermissionError:
            # If open by another connection, truncate or continue with CREATE IF NOT EXISTS
            pass

    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)

    # Seed Categories
    categories = [
        ("IR01", "Malpractice", "Unauthorized materials, communication, or copying detected during exam", "HIGH", "Chief Superintendent"),
        ("IR02", "Disturbance", "Noise, disruptive conduct, or unauthorized movement in examination hall", "MEDIUM", "Centre Superintendent"),
        ("IR03", "Medical", "Student medical distress, sudden illness, or physical emergency", "CRITICAL", "Chief Superintendent"),
        ("IR04", "Technical", "CCTV blindspot, power flicker, biometric or network hardware failure", "MEDIUM", "Centre Superintendent"),
        ("IR05", "Missing-Script", "Unaccounted answer booklet, missing barcode slip, or inventory mismatch", "CRITICAL", "Controller of Examinations")
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO categories (code, name, description, default_priority, authority_role)
        VALUES (?, ?, ?, ?, ?)
    """, categories)

    # Seed Routing Rules (Explicit lookup table per requirements)
    routing_rules = [
        ("IR01", "Chief Superintendent", "Controller of Examinations", "HIGH"),
        ("IR02", "Centre Superintendent", "Chief Superintendent", "MEDIUM"),
        ("IR03", "Chief Superintendent", "Campus Medical Officer", "CRITICAL"),
        ("IR04", "Centre Superintendent", "Technical Support Lead", "MEDIUM"),
        ("IR05", "Controller of Examinations", "Chief Superintendent", "CRITICAL")
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO routing_rules (irregularity_code, target_authority, escalation_authority, priority)
        VALUES (?, ?, ?, ?)
    """, routing_rules)

    # Seed Invigilators
    invigilators = [
        ("INVCSE0001", "Dr. Alan Turing", "CSE", "a.turing@exam.institution.edu", "+91 98765 43210"),
        ("INVCSE0002", "Prof. Grace Hopper", "CSE", "g.hopper@exam.institution.edu", "+91 98765 43211"),
        ("INVECE0001", "Dr. Claude Shannon", "ECE", "c.shannon@exam.institution.edu", "+91 98765 43212"),
        ("INVEEE0001", "Dr. Nikola Tesla", "EEE", "n.tesla@exam.institution.edu", "+91 98765 43213"),
        ("INVMECH001", "Dr. James Watt", "MECH", "j.watt@exam.institution.edu", "+91 98765 43214")
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO invigilators (invigilator_id, name, department, email, phone)
        VALUES (?, ?, ?, ?, ?)
    """, invigilators)

    # Seed Handlers
    handlers = [
        ("HND-001", "Dr. Robert Davis", "Chief Superintendent", "Administration", 5, 2, 1, "ext. 401"),
        ("HND-002", "Prof. Margaret Hamilton", "Centre Superintendent", "Administration", 6, 3, 1, "ext. 402"),
        ("HND-003", "Dr. Barbara Liskov", "Controller of Examinations", "Evaluation Branch", 4, 1, 1, "ext. 400"),
        ("HND-004", "Eng. Dennis Ritchie", "Centre Superintendent", "IT & Infrastructure", 8, 2, 1, "ext. 408"),
        ("HND-005", "Dr. Elizabeth Blackwell", "Chief Superintendent", "Campus Health Care", 5, 0, 1, "ext. 108")
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO handlers (handler_uid, name, role, department, capacity, current_load, is_available, contact)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, handlers)

    # Seed Network Routes (Initial example networks per requirement 7)
    routes = [
        ("CSE", "192.168.10.0/24", "255.255.255.0", 24, "192.168.10.1", "eth0", 10),
        ("ECE", "192.168.20.0/24", "255.255.255.0", 24, "192.168.20.1", "eth1", 10),
        ("EEE", "192.168.30.0/24", "255.255.255.0", 24, "192.168.30.1", "eth2", 10),
        ("Administration", "192.168.40.0/24", "255.255.255.0", 24, "192.168.40.1", "vlan40", 5),
        ("CSE Specialized Lab Subnet", "192.168.10.128/25", "255.255.255.128", 25, "192.168.10.254", "eth0.100", 5),
        ("Campus Backbone Default", "0.0.0.0/0", "0.0.0.0", 0, "192.168.1.1", "wan0", 100)
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO network_routes (department, destination_network, subnet_mask, prefix_length, next_hop, interface, metric)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, routes)

    # Seed Initial Seed Reports for realistic Phase 1 testing
    sample_reports = [
        ("REP-2026-001", "INVCSE0001", "IR01", "HALL-401", "21CS042", "Smartwatch detected under desk during Distributed Systems exam", "HIGH", "Chief Superintendent", "ASSIGNED", "192.168.10.45"),
        ("REP-2026-002", "INVECE0001", "IR03", "HALL-204", "21EC019", "Candidate experienced severe asthma symptoms requiring immediate medical aid", "CRITICAL", "Chief Superintendent", "IN_PROGRESS", "192.168.20.12"),
        ("REP-2026-003", "INVCSE0002", "IR04", "LAB-3", None, "Terminal 14 monitor flicker and intermittent keyboard disconnect", "MEDIUM", "Centre Superintendent", "RESOLVED", "192.168.10.134"),
        ("REP-2026-004", "INVEEE0001", "IR05", "HALL-102", "21EE088", "Discrepancy in collected main booklet serial counts vs attendance sheet", "CRITICAL", "Controller of Examinations", "SUBMITTED", "192.168.30.8")
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO reports (report_uid, invigilator_id, irregularity_code, hall_id, student_roll, description, severity, target_authority, status, source_ip)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_reports)

    # Seed Users for RBAC Authentication
    from werkzeug.security import generate_password_hash
    users = [
        ("admin", generate_password_hash("admin123"), "ADMIN", "Dr. Barbara Liskov", "b.liskov@exam.institution.edu", "Examination Cell", "HND-003"),
        ("inv_cse", generate_password_hash("exam123"), "INVIGILATOR", "Dr. Alan Turing", "a.turing@exam.institution.edu", "CSE", "INVCSE0001"),
        ("inv_ece", generate_password_hash("exam123"), "INVIGILATOR", "Dr. Claude Shannon", "c.shannon@exam.institution.edu", "ECE", "INVECE0001"),
        ("handler_cs", generate_password_hash("exam123"), "HANDLER", "Dr. Robert Davis", "r.davis@exam.institution.edu", "Administration", "HND-001"),
        ("handler_centre", generate_password_hash("exam123"), "HANDLER", "Prof. Margaret Hamilton", "m.hamilton@exam.institution.edu", "Administration", "HND-002")
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO users (username, password_hash, role, name, email, department, reference_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, users)

    # Seed Initial Notifications
    notifications = [
        (None, "ALL", "Examination Session Active", "IRIS incident monitoring and deterministic dispatch online.", "SUCCESS", None, 0),
        (None, "ADMIN", "Medical Emergency Logged", "Critical incident reported in Hall 204. Primary authority dispatched.", "CRITICAL", 2, 0),
        (None, "HANDLER", "Workload Notification", "Incident assigned to Chief Superintendent jurisdiction.", "INFO", 1, 0)
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO notifications (user_id, target_role, title, message, type, report_id, is_read)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, notifications)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db(force=True)
    print(f"Database initialized successfully at: {DATABASE_PATH}")
