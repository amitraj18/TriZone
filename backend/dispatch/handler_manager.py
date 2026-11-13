"""
Handler Manager
Authority Staff Selection, Capacity Management & Workload Balancing
-------------------------------------------------------------------
Implements deterministic handler selection based on statutory role matching,
real-time capacity verification, lowest-workload balancing, and backup escalation.
"""

from typing import Dict, Any, List, Optional
import sqlite3
from database.connection import db_session

class HandlerManager:
    @staticmethod
    def get_all_handlers(conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
        """Returns all handlers with capacity and workload stats."""
        query = """
            SELECT id, handler_uid, name, role, department, capacity, current_load, is_available, contact
            FROM handlers
            ORDER BY role ASC, current_load ASC, handler_uid ASC
        """
        if conn:
            cur = conn.execute(query)
            return [dict(r) for r in cur.fetchall()]
        with db_session() as session_conn:
            cur = session_conn.execute(query)
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def find_eligible_handler(
        target_authority: str,
        escalation_authority: Optional[str] = None,
        conn: Optional[sqlite3.Connection] = None
    ) -> Dict[str, Any]:
        """
        Deterministic handler selection algorithm:
        1. Find handlers matching target_authority where is_available = 1 and current_load < capacity.
        2. Sort by lowest current workload (current_load ASC), then stable handler_uid ASC.
        3. If primary handlers are all at capacity / offline, attempt escalation_authority backup.
        4. If no handler is available, return None with reason to trigger queueing.
        """
        def _execute_search(c: sqlite3.Connection):
            # Step 1: Search Primary Authority handlers
            cur = c.execute("""
                SELECT id, handler_uid, name, role, department, capacity, current_load, is_available, contact
                FROM handlers
                WHERE role = ? AND is_available = 1 AND current_load < capacity
                ORDER BY current_load ASC, handler_uid ASC
                LIMIT 1
            """, (target_authority,))
            primary = cur.fetchone()
            if primary:
                return {
                    "found": True,
                    "handler": dict(primary),
                    "assignment_type": "PRIMARY",
                    "reason": f"Assigned to primary authority handler {primary['name']} ({primary['current_load']}/{primary['capacity']} active)."
                }

            # Step 2: Search Backup / Escalation Authority handlers if specified
            if escalation_authority and escalation_authority != target_authority:
                cur_backup = c.execute("""
                    SELECT id, handler_uid, name, role, department, capacity, current_load, is_available, contact
                    FROM handlers
                    WHERE role = ? AND is_available = 1 AND current_load < capacity
                    ORDER BY current_load ASC, handler_uid ASC
                    LIMIT 1
                """, (escalation_authority,))
                backup = cur_backup.fetchone()
                if backup:
                    return {
                        "found": True,
                        "handler": dict(backup),
                        "assignment_type": "BACKUP",
                        "reason": (
                            f"Primary authority '{target_authority}' at full capacity. "
                            f"Escalated to backup authority handler {backup['name']} ({escalation_authority})."
                        )
                    }

            # Step 3: No eligible handlers found
            return {
                "found": False,
                "handler": None,
                "assignment_type": "NONE",
                "reason": f"All handlers for authority '{target_authority}' are at maximum capacity or offline."
            }

        if conn:
            return _execute_search(conn)
        with db_session() as session_conn:
            return _execute_search(session_conn)

    @staticmethod
    def increment_workload(handler_id: int, conn: sqlite3.Connection) -> bool:
        """Atomically increments handler current_load if capacity allows."""
        cur = conn.execute("""
            UPDATE handlers 
            SET current_load = current_load + 1
            WHERE id = ? AND current_load < capacity
        """, (handler_id,))
        return cur.rowcount > 0

    @staticmethod
    def decrement_workload(handler_id: int, conn: sqlite3.Connection) -> bool:
        """Atomically decrements handler current_load upon incident resolution (floor at 0)."""
        cur = conn.execute("""
            UPDATE handlers 
            SET current_load = MAX(0, current_load - 1)
            WHERE id = ?
        """, (handler_id,))
        return cur.rowcount > 0

    @staticmethod
    def set_availability(handler_id: int, is_available: bool) -> bool:
        """Updates handler online/offline availability."""
        with db_session() as conn:
            cur = conn.execute("""
                UPDATE handlers 
                SET is_available = ?
                WHERE id = ?
            """, (1 if is_available else 0, handler_id))
            return cur.rowcount > 0

    @staticmethod
    def update_capacity(handler_id: int, new_capacity: int) -> bool:
        """Updates handler maximum concurrent incident capacity."""
        if new_capacity < 1:
            raise ValueError("Capacity must be at least 1 incident.")
        with db_session() as conn:
            cur = conn.execute("""
                UPDATE handlers 
                SET capacity = ?
                WHERE id = ?
            """, (new_capacity, handler_id))
            return cur.rowcount > 0

