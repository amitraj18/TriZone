"""
Demonstration Data Seeder & Reset Engine
----------------------------------------
Provides a deterministic demonstration state for hackathon evaluations,
seeding incidents in all five categories across multiple departments,
active priority queues, escalated handlers, and resolved historical records.
"""

from database.connection import db_session
from database.seed_data import init_db

def reset_demonstration_database():
    """Re-initializes SQLite schema and populates comprehensive demo incidents."""
    # Force re-initialize schema, categories, routes, invigilators, handlers
    init_db(force=True)

    with db_session() as conn:
        # Update handlers to realistic load states
        conn.execute("UPDATE handlers SET current_load = 2, is_available = 1 WHERE handler_uid = 'HND-001'") # Chief Super (cap 5)
        conn.execute("UPDATE handlers SET current_load = 3, is_available = 1 WHERE handler_uid = 'HND-002'") # Centre Super (cap 6)
        conn.execute("UPDATE handlers SET current_load = 1, is_available = 1 WHERE handler_uid = 'HND-003'") # COE (cap 4)
        conn.execute("UPDATE handlers SET current_load = 2, is_available = 1 WHERE handler_uid = 'HND-004'") # Tech Lead (cap 8)
        conn.execute("UPDATE handlers SET current_load = 0, is_available = 1 WHERE handler_uid = 'HND-005'") # Medical Officer (cap 5)

        # 1. Seed demo reports covering all 5 categories & statuses
        demo_reports = [
            # ID 1: IR01 Malpractice in Hall-401 (ASSIGNED to Chief Superintendent)
            ("REP-2026-101", "INVCSE0001", "IR01", "HALL-401", "21CS042", "Smartwatch detected under desk during Distributed Systems exam", "HIGH", "Chief Superintendent", "ASSIGNED", "192.168.10.45", "2026-11-13 09:30:00"),
            # ID 2: IR03 Medical Emergency in Hall-204 (IN_PROGRESS, Medical Officer)
            ("REP-2026-102", "INVECE0001", "IR03", "HALL-204", "21EC019", "Candidate experienced acute asthma symptoms; paramedic dispatched to room.", "CRITICAL", "Chief Superintendent", "IN_PROGRESS", "192.168.20.12", "2026-11-13 10:15:00"),
            # ID 3: IR04 Technical in Lab-3 (RESOLVED by Tech Lead, /25 Subnet LPM)
            ("REP-2026-103", "INVCSE0002", "IR04", "LAB-3", None, "Terminal 14 monitor flicker and intermittent keyboard disconnect resolved.", "MEDIUM", "Centre Superintendent", "RESOLVED", "192.168.10.134", "2026-11-13 08:45:00"),
            # ID 4: IR02 Disturbance in Hall-302 (ASSIGNED to Centre Superintendent)
            ("REP-2026-104", "INVCSE0001", "IR02", "HALL-302", "21CS088", "Loud continuous construction noise adjacent to hall; soundproofing blinds installed.", "MEDIUM", "Centre Superintendent", "ASSIGNED", "192.168.10.45", "2026-11-13 11:00:00"),
            # ID 5: IR05 Missing-Script in Hall-102 (QUEUED in Deterministic Priority Queue)
            ("REP-2026-105", "INVEEE0001", "IR05", "HALL-102", "21EE088", "Barcode mismatch between optical attendance register and booklet packet.", "CRITICAL", "Controller of Examinations", "QUEUED", "192.168.30.8", "2026-11-13 11:20:00"),
            # ID 6: IR01 Malpractice (ESCALATED backup handler)
            ("REP-2026-106", "INVECE0001", "IR01", "HALL-204", "21EC055", "Unauthorized formula notes folded in geometric instrument box.", "HIGH", "Chief Superintendent", "ESCALATED", "192.168.20.12", "2026-11-13 11:45:00")
        ]

        for rep in demo_reports:
            conn.execute("""
                INSERT OR REPLACE INTO reports 
                (report_uid, invigilator_id, irregularity_code, hall_id, student_roll, description, severity, target_authority, status, source_ip, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rep)

        # 2. Seed corresponding assignments
        assignments = [
            (1, 1, "Chief Superintendent", "PRIMARY", "ASSIGNED", "Immediate examination cell review"),
            (2, 5, "Chief Superintendent", "PRIMARY", "IN_PROGRESS", "Paramedic stationed on site"),
            (3, 4, "Centre Superintendent", "PRIMARY", "RESOLVED", "Replaced display adapter"),
            (4, 2, "Centre Superintendent", "PRIMARY", "ASSIGNED", "Supervisor dispatched"),
            (6, 3, "Chief Superintendent", "BACKUP", "ASSIGNED", "Assigned to Controller of Examinations as backup due to primary load")
        ]
        conn.executemany("""
            INSERT OR REPLACE INTO assignments (report_id, handler_id, assigned_role, assignment_type, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, assignments)

        # 3. Seed validation logs with nanosecond measurements
        val_logs = [
            (1, "INVIGILATOR_ID", "INVCSE0001", 1, 1, 1, "", 28400, 19200, 1),
            (1, "IRREGULARITY_CODE", "IR01", 1, 1, 1, "", 12500, 8900, 1),
            (2, "INVIGILATOR_ID", "INVECE0001", 1, 1, 1, "", 31200, 21400, 1),
            (2, "IRREGULARITY_CODE", "IR03", 1, 1, 1, "", 14100, 9200, 1)
        ]
        conn.executemany("""
            INSERT OR REPLACE INTO validation_logs 
            (report_id, entity_type, input_value, dfa_result, regex_result, is_valid, failure_reason, dfa_time_ns, regex_time_ns, agreement)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, val_logs)

        # 4. Seed status transition audit trails
        status_hist = [
            (1, "SUBMITTED", "VALIDATED", "TOC_ENGINE", "Conforms to INV[DEPT][4-digit] and IR01"),
            (1, "VALIDATED", "ASSIGNED", "SYSTEM_DISPATCH", "Assigned to Dr. Robert Davis (Chief Superintendent)"),
            (2, "SUBMITTED", "VALIDATED", "TOC_ENGINE", "Medical emergency IR03 confirmed"),
            (2, "VALIDATED", "ASSIGNED", "SYSTEM_DISPATCH", "Emergency priority CRITICAL dispatched to Dr. Elizabeth Blackwell"),
            (2, "ASSIGNED", "IN_PROGRESS", "HANDLER", "Paramedic arrived in Hall 204"),
            (3, "SUBMITTED", "VALIDATED", "TOC_ENGINE", "Technical IR04 validated via /25 subnet"),
            (3, "VALIDATED", "ASSIGNED", "SYSTEM_DISPATCH", "Assigned to Eng. Dennis Ritchie"),
            (3, "ASSIGNED", "RESOLVED", "HANDLER", "Monitor cable replaced. Terminal operational."),
            (5, "SUBMITTED", "VALIDATED", "TOC_ENGINE", "Missing script IR05 validated"),
            (5, "VALIDATED", "QUEUED", "SYSTEM_DISPATCH", "Controller of Examinations queue: Position #1")
        ]
        conn.executemany("""
            INSERT INTO status_history (report_id, old_status, new_status, updated_by, comment)
            VALUES (?, ?, ?, ?, ?)
        """, status_hist)

        # 5. Seed Dispatch logs
        disp_logs = [
            (1, 1, "ASSIGNED", "Primary authority matched with load 2/5", 1),
            (2, 5, "ASSIGNED", "Emergency medical dispatch", 1),
            (3, 4, "ASSIGNED", "Technical hardware allocation", 1),
            (3, 4, "RESOLVED", "Incident closed", 1),
            (5, None, "QUEUED", "No handler with capacity; placed in deterministic priority queue", 1)
        ]
        conn.executemany("""
            INSERT INTO dispatch_logs (report_id, handler_id, action, reason, success)
            VALUES (?, ?, ?, ?, ?)
        """, disp_logs)

    return {"success": True, "message": "Demonstration database successfully reset to clean evaluation state."}

