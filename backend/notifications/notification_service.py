"""
In-App Notification Service
---------------------------
Maintains persistent alerts in SQLite for assignments, escalations,
critical emergency reports, queue intake, and case resolutions.
"""

from typing import Dict, Any, List, Optional
from database.connection import db_session

class NotificationService:
    @staticmethod
    def create_notification(
        title: str,
        message: str,
        n_type: str = "INFO",
        target_role: str = "ALL",
        report_id: Optional[int] = None,
        user_id: Optional[int] = None,
        notif_type: Optional[str] = None
    ) -> int:
        """Persists an in-app notification to SQLite."""
        chosen_type = (notif_type or n_type or "INFO").upper()
        with db_session() as conn:
            cur = conn.execute("""
                INSERT INTO notifications (user_id, target_role, title, message, type, report_id, is_read)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (user_id, target_role.upper(), title, message, chosen_type, report_id))
            return cur.lastrowid

    @staticmethod
    def get_notifications(
        target_role: str = "ALL",
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Retrieves notifications for a specific user role or broadcast 'ALL'."""
        with db_session() as conn:
            cur = conn.execute("""
                SELECT n.*, r.report_uid
                FROM notifications n
                LEFT JOIN reports r ON n.report_id = r.id
                WHERE n.target_role = 'ALL' OR n.target_role = ?
                ORDER BY n.created_at DESC
                LIMIT ?
            """, (target_role.upper(), limit))
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def mark_as_read(notification_id: int) -> bool:
        """Marks a notification as read."""
        with db_session() as conn:
            cur = conn.execute("""
                UPDATE notifications SET is_read = 1 WHERE id = ?
            """, (notification_id,))
            return cur.rowcount > 0

    @staticmethod
    def mark_all_as_read(target_role: str = "ALL") -> int:
        """Marks all unread notifications for a role as read."""
        with db_session() as conn:
            cur = conn.execute("""
                UPDATE notifications SET is_read = 1 
                WHERE is_read = 0 AND (target_role = 'ALL' OR target_role = ?)
            """, (target_role.upper(),))
            return cur.rowcount

