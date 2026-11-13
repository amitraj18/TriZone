import sqlite3
from typing import List, Dict, Any, Optional
from database.connection import get_db_connection, db_session

class DatabaseModel:
    @staticmethod
    def dict_from_row(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
        if row is None:
            return None
        return dict(row)

    @staticmethod
    def dict_list_from_rows(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
        return [dict(r) for r in rows]


class InvigilatorModel(DatabaseModel):
    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        with db_session() as conn:
            cur = conn.execute("SELECT * FROM invigilators ORDER BY invigilator_id ASC")
            return cls.dict_list_from_rows(cur.fetchall())

    @classmethod
    def get_by_id(cls, invigilator_id: str) -> Optional[Dict[str, Any]]:
        with db_session() as conn:
            cur = conn.execute("SELECT * FROM invigilators WHERE invigilator_id = ?", (invigilator_id,))
            return cls.dict_from_row(cur.fetchone())


class CategoryModel(DatabaseModel):
    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        with db_session() as conn:
            cur = conn.execute("SELECT * FROM categories ORDER BY code ASC")
            return cls.dict_list_from_rows(cur.fetchall())

    @classmethod
    def get_by_code(cls, code: str) -> Optional[Dict[str, Any]]:
        with db_session() as conn:
            cur = conn.execute("SELECT * FROM categories WHERE code = ?", (code,))
            return cls.dict_from_row(cur.fetchone())


class RoutingRuleModel(DatabaseModel):
    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        with db_session() as conn:
            cur = conn.execute("""
                SELECT rr.*, c.name as category_name 
                FROM routing_rules rr
                JOIN categories c ON rr.irregularity_code = c.code
                ORDER BY rr.irregularity_code ASC
            """)
            return cls.dict_list_from_rows(cur.fetchall())


class HandlerModel(DatabaseModel):
    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        with db_session() as conn:
            cur = conn.execute("SELECT * FROM handlers ORDER BY role, name")
            return cls.dict_list_from_rows(cur.fetchall())


class NetworkRouteModel(DatabaseModel):
    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        with db_session() as conn:
            cur = conn.execute("SELECT * FROM network_routes ORDER BY prefix_length DESC, metric ASC")
            return cls.dict_list_from_rows(cur.fetchall())


class ReportModel(DatabaseModel):
    @classmethod
    def get_all(cls, limit: int = 50) -> List[Dict[str, Any]]:
        with db_session() as conn:
            cur = conn.execute("""
                SELECT r.*, c.name as category_name, i.name as invigilator_name, i.department as invigilator_dept
                FROM reports r
                LEFT JOIN categories c ON r.irregularity_code = c.code
                LEFT JOIN invigilators i ON r.invigilator_id = i.invigilator_id
                ORDER BY r.created_at DESC
                LIMIT ?
            """, (limit,))
            return cls.dict_list_from_rows(cur.fetchall())

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        with db_session() as conn:
            total = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
            active = conn.execute("SELECT COUNT(*) FROM reports WHERE status NOT IN ('RESOLVED', 'REJECTED')").fetchone()[0]
            resolved = conn.execute("SELECT COUNT(*) FROM reports WHERE status = 'RESOLVED'").fetchone()[0]
            critical = conn.execute("SELECT COUNT(*) FROM reports WHERE severity = 'CRITICAL'").fetchone()[0]
            return {
                "total_reports": total,
                "active_incidents": active,
                "resolved_incidents": resolved,
                "critical_alerts": critical
            }

