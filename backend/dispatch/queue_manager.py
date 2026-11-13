"""
Queue Manager
Deterministic Priority Queue for Incident Intake
-------------------------------------------------
Maintains a strict priority-ordered queue in SQLite:
1. Priority descending (CRITICAL > HIGH > MEDIUM > LOW)
2. Submission timestamp ascending (FIFO within priority tier)
3. Report ID ascending (deterministic tie-breaker)
"""

from typing import Dict, Any, List, Optional
import sqlite3
from database.connection import db_session

class QueueManager:
    @staticmethod
    def get_queued_reports(conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
        """
        Retrieves all active queued reports ordered by deterministic priority:
        CRITICAL (4) -> HIGH (3) -> MEDIUM (2) -> LOW (1), then created_at ASC, id ASC.
        """
        query = """
            SELECT r.*, c.name as category_name, i.name as invigilator_name,
                   CASE r.severity
                       WHEN 'CRITICAL' THEN 4
                       WHEN 'HIGH' THEN 3
                       WHEN 'MEDIUM' THEN 2
                       WHEN 'LOW' THEN 1
                       ELSE 1
                   END as priority_weight
            FROM reports r
            LEFT JOIN categories c ON r.irregularity_code = c.code
            LEFT JOIN invigilators i ON r.invigilator_id = i.invigilator_id
            WHERE r.status = 'QUEUED'
            ORDER BY priority_weight DESC, r.created_at ASC, r.id ASC
        """
        if conn:
            cur = conn.execute(query)
            rows = [dict(r) for r in cur.fetchall()]
        else:
            with db_session() as session_conn:
                cur = session_conn.execute(query)
                rows = [dict(r) for r in cur.fetchall()]

        # Assign 1-indexed queue position
        for idx, row in enumerate(rows, start=1):
            row["queue_position"] = idx
        return rows

    @staticmethod
    def process_queue_for_authority(target_authority: str, conn: sqlite3.Connection) -> Optional[Dict[str, Any]]:
        """
        Attempts to assign the highest-priority queued report matching target_authority
        to an available handler.
        Called when a handler becomes available or finishes an incident.
        """
        # Look for eligible handler
        cur_handler = conn.execute("""
            SELECT id, handler_uid, name, role, department, capacity, current_load, is_available
            FROM handlers
            WHERE role = ? AND is_available = 1 AND current_load < capacity
            ORDER BY current_load ASC, handler_uid ASC
            LIMIT 1
        """, (target_authority,))
        handler = cur_handler.fetchone()
        if not handler:
            return None

        # Look for highest-priority report in queue for this authority
        cur_report = conn.execute("""
            SELECT r.id, r.report_uid, r.target_authority, r.severity
            FROM reports r
            WHERE r.status = 'QUEUED' AND r.target_authority = ?
            ORDER BY 
                CASE r.severity
                    WHEN 'CRITICAL' THEN 4
                    WHEN 'HIGH' THEN 3
                    WHEN 'MEDIUM' THEN 2
                    WHEN 'LOW' THEN 1
                    ELSE 1
                END DESC,
                r.created_at ASC,
                r.id ASC
            LIMIT 1
        """, (target_authority,))
        report = cur_report.fetchone()
        if not report:
            return None

        report_id = report["id"]
        handler_id = handler["id"]

        # Increment handler load
        conn.execute("""
            UPDATE handlers SET current_load = current_load + 1 WHERE id = ?
        """, (handler_id,))

        # Update report status to ASSIGNED
        conn.execute("""
            UPDATE reports SET status = 'ASSIGNED', updated_at = CURRENT_TIMESTAMP WHERE id = ?
        """, (report_id,))

        # Create assignment
        conn.execute("""
            INSERT INTO assignments (report_id, handler_id, assigned_role, assignment_type, status, notes)
            VALUES (?, ?, ?, 'PRIMARY', 'ASSIGNED', 'Dequeued from priority queue upon handler capacity release.')
        """, (report_id, handler_id, handler["role"]))

        # Record status history
        conn.execute("""
            INSERT INTO status_history (report_id, old_status, new_status, updated_by, comment)
            VALUES (?, 'QUEUED', 'ASSIGNED', 'SYSTEM_DISPATCH', ?)
        """, (report_id, f"Dequeued and assigned to {handler['name']} ({handler['role']})."))

        # Log dispatch
        conn.execute("""
            INSERT INTO dispatch_logs (report_id, handler_id, action, reason, success)
            VALUES (?, ?, 'ASSIGNED', 'Automatic queue dispatch', 1)
        """, (report_id, handler_id))

        return {
            "report_id": report_id,
            "report_uid": report["report_uid"],
            "handler_id": handler_id,
            "handler_name": handler["name"],
            "authority": handler["role"]
        }

