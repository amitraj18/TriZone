"""
Dispatch Engine Orchestrator
Operational Authority Routing, Handler Allocation & Lifecycle Management
------------------------------------------------------------------------
Coordinates examination authority lookup from SQLite, priority determination,
deterministic handler allocation, backup escalation, priority queueing,
and full transactional status transitions.
"""

from typing import Dict, Any, Optional
import sqlite3
from database.connection import db_session
from dispatch.priority_manager import PriorityManager
from dispatch.handler_manager import HandlerManager
from dispatch.queue_manager import QueueManager

class DispatchEngine:
    @staticmethod
    def get_authority_routing_rule(irregularity_code: str, conn: sqlite3.Connection) -> Dict[str, Any]:
        """
        Reads explicit authority routing rule from SQLite routing_rules table.
        Does NOT hardcode mapping in function.
        """
        cur = conn.execute("""
            SELECT rr.irregularity_code, rr.target_authority, rr.escalation_authority, 
                   rr.priority, c.name as category_name
            FROM routing_rules rr
            JOIN categories c ON rr.irregularity_code = c.code
            WHERE rr.irregularity_code = ? AND rr.is_active = 1
        """, (irregularity_code,))
        rule = cur.fetchone()
        if not rule:
            raise ValueError(f"No active routing rule configured for irregularity code '{irregularity_code}'.")
        return dict(rule)

    @staticmethod
    def dispatch_report(
        report_id: int,
        irregularity_code: str,
        is_emergency: bool = False,
        override_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end dispatch decision in a single atomic transaction:
        1. Queries explicit authority routing rule from SQLite.
        2. Evaluates priority with emergency override.
        3. Identifies eligible handler (Primary -> Backup).
        4. If handler found: increments workload, records assignment, marks ASSIGNED.
        5. If no handler found: records QUEUED status, enters deterministic priority queue.
        6. Logs all decisions to status_history and dispatch_logs.
        """
        with db_session() as conn:
            # Step 1: Query authority routing rule from SQLite
            rule = DispatchEngine.get_authority_routing_rule(irregularity_code, conn)
            target_authority = rule["target_authority"]
            escalation_authority = rule.get("escalation_authority")

            # Step 2: Determine priority (with emergency override check)
            prio_decision = PriorityManager.determine_priority(
                irregularity_code=irregularity_code,
                is_emergency=is_emergency,
                override_reason=override_reason
            )
            effective_priority = prio_decision["effective_priority"]

            # Update report severity and target authority in SQLite
            conn.execute("""
                UPDATE reports 
                SET severity = ?, target_authority = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (effective_priority, target_authority, report_id))

            # Step 3: Find eligible handler
            handler_search = HandlerManager.find_eligible_handler(
                target_authority=target_authority,
                escalation_authority=escalation_authority,
                conn=conn
            )

            if handler_search["found"]:
                handler = handler_search["handler"]
                assignment_type = handler_search["assignment_type"]
                handler_id = handler["id"]

                # Increment handler load
                conn.execute("""
                    UPDATE handlers SET current_load = current_load + 1 WHERE id = ?
                """, (handler_id,))

                # Set report status
                new_status = "ASSIGNED" if assignment_type == "PRIMARY" else "ESCALATED"
                conn.execute("""
                    UPDATE reports SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
                """, (new_status, report_id))

                # Create assignment record
                conn.execute("""
                    INSERT INTO assignments (report_id, handler_id, assigned_role, assignment_type, status, notes)
                    VALUES (?, ?, ?, ?, 'ASSIGNED', ?)
                """, (report_id, handler_id, handler["role"], assignment_type, handler_search["reason"]))

                # Status history log
                conn.execute("""
                    INSERT INTO status_history (report_id, old_status, new_status, updated_by, comment)
                    VALUES (?, 'VALIDATED', ?, 'SYSTEM_DISPATCH', ?)
                """, (report_id, new_status, handler_search["reason"]))

                # Dispatch log
                conn.execute("""
                    INSERT INTO dispatch_logs (report_id, handler_id, action, reason, success)
                    VALUES (?, ?, ?, ?, 1)
                """, (report_id, handler_id, new_status, handler_search["reason"]))

                return {
                    "success": True,
                    "report_id": report_id,
                    "target_authority": target_authority,
                    "category": rule["category_name"],
                    "priority": prio_decision,
                    "dispatch_status": new_status,
                    "assigned_handler": {
                        "id": handler["id"],
                        "uid": handler["handler_uid"],
                        "name": handler["name"],
                        "role": handler["role"],
                        "department": handler["department"],
                        "assignment_type": assignment_type,
                        "current_load": handler["current_load"] + 1,
                        "capacity": handler["capacity"]
                    },
                    "reason": handler_search["reason"]
                }
            else:
                # No handler available -> Enqueue report
                new_status = "QUEUED"
                conn.execute("""
                    UPDATE reports SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
                """, (new_status, report_id))

                queue_reason = (
                    f"No available handler for {target_authority}. "
                    f"Report placed in deterministic priority queue (Weight: {prio_decision['priority_weight']})."
                )

                conn.execute("""
                    INSERT INTO status_history (report_id, old_status, new_status, updated_by, comment)
                    VALUES (?, 'VALIDATED', 'QUEUED', 'SYSTEM_DISPATCH', ?)
                """, (report_id, queue_reason))

                conn.execute("""
                    INSERT INTO dispatch_logs (report_id, handler_id, action, reason, success)
                    VALUES (?, NULL, 'QUEUED', ?, 1)
                """, (report_id, queue_reason))

                return {
                    "success": True,
                    "report_id": report_id,
                    "target_authority": target_authority,
                    "category": rule["category_name"],
                    "priority": prio_decision,
                    "dispatch_status": "QUEUED",
                    "assigned_handler": None,
                    "reason": queue_reason
                }

    @staticmethod
    def update_report_status(
        report_id: int, 
        new_status: str, 
        updated_by: str = "EXAMINATION_CELL", 
        comment: str = ""
    ) -> Dict[str, Any]:
        """
        Transitions report status with transaction integrity:
        - If new_status in ('RESOLVED', 'REJECTED'):
          * Decrements handler workload
          * Sets assignment status to RESOLVED
          * Automatically checks priority queue and assigns next waiting incident
        - Records immutable status_history entry.
        """
        valid_statuses = {"SUBMITTED", "VALIDATED", "ASSIGNED", "ESCALATED", "QUEUED", "IN_PROGRESS", "RESOLVED", "REJECTED"}
        norm_status = new_status.upper().strip()
        if norm_status not in valid_statuses:
            raise ValueError(f"Invalid status '{new_status}'. Allowed: {sorted(list(valid_statuses))}")

        with db_session() as conn:
            # Fetch current report
            cur = conn.execute("SELECT id, status, target_authority FROM reports WHERE id = ?", (report_id,))
            report = cur.fetchone()
            if not report:
                raise ValueError(f"Report ID {report_id} not found.")

            old_status = report["status"]
            target_authority = report["target_authority"]

            # Update report status
            conn.execute("""
                UPDATE reports SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """, (norm_status, report_id))

            # Status history
            conn.execute("""
                INSERT INTO status_history (report_id, old_status, new_status, updated_by, comment)
                VALUES (?, ?, ?, ?, ?)
            """, (report_id, old_status, norm_status, updated_by, comment or f"Status updated to {norm_status}."))

            # If resolving or closing: free up handler load
            dequeued_item = None
            if norm_status in ("RESOLVED", "REJECTED"):
                # Find active assignment
                cur_assign = conn.execute("""
                    SELECT id, handler_id FROM assignments 
                    WHERE report_id = ? AND status = 'ASSIGNED'
                    LIMIT 1
                """, (report_id,))
                assign = cur_assign.fetchone()
                if assign:
                    handler_id = assign["handler_id"]
                    # Mark assignment resolved
                    conn.execute("""
                        UPDATE assignments 
                        SET status = 'RESOLVED', resolved_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (assign["id"],))

                    # Decrement handler workload safely
                    HandlerManager.decrement_workload(handler_id, conn)

                    # Trigger queue processor for this authority
                    if target_authority:
                        dequeued_item = QueueManager.process_queue_for_authority(target_authority, conn)

            return {
                "report_id": report_id,
                "old_status": old_status,
                "new_status": norm_status,
                "dequeued_next_report": dequeued_item
            }

