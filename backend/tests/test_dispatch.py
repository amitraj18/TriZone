import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dispatch.priority_manager import PriorityManager
from dispatch.handler_manager import HandlerManager
from dispatch.queue_manager import QueueManager
from dispatch.dispatch_engine import DispatchEngine
from database.connection import db_session
from database.seed_data import init_db

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    test_db = str(tmp_path / "test_disp.db")
    os.environ["DATABASE"] = test_db
    init_db(db_path=test_db, force=True)

class TestPriorityManager:
    def test_default_priorities(self):
        p1 = PriorityManager.determine_priority("IR01")
        assert p1["default_priority"] == "HIGH"
        assert p1["effective_priority"] == "HIGH"
        assert p1["is_overridden"] is False

        p3 = PriorityManager.determine_priority("IR03")
        assert p3["default_priority"] == "CRITICAL"
        assert p3["effective_priority"] == "CRITICAL"

    def test_emergency_override(self):
        # IR02 default is MEDIUM. Emergency overrides to CRITICAL.
        p2 = PriorityManager.determine_priority("IR02", is_emergency=True, override_reason="Candidate violence in hall")
        assert p2["default_priority"] == "MEDIUM"
        assert p2["effective_priority"] == "CRITICAL"
        assert p2["is_overridden"] is True
        assert "Candidate violence" in p2["override_reason"]
        assert p2["override_timestamp"] is not None


class TestHandlerSelectionAndCapacity:
    def test_handler_selection_lowest_workload(self):
        # Chief Superintendent has Robert Davis (load 2, cap 5) and Elizabeth Blackwell (load 0, cap 5)
        # Should deterministically select Elizabeth Blackwell because load 0 < load 2!
        with db_session() as conn:
            res = HandlerManager.find_eligible_handler("Chief Superintendent", conn=conn)
            assert res["found"] is True
            assert res["handler"]["name"] == "Dr. Elizabeth Blackwell"
            assert res["handler"]["current_load"] == 0

    def test_handler_capacity_overflow_escalation(self):
        # Set all Chief Superintendent handlers to full capacity
        with db_session() as conn:
            conn.execute("UPDATE handlers SET current_load = capacity WHERE role = 'Chief Superintendent'")
            # Now search with escalation to 'Controller of Examinations'
            res = HandlerManager.find_eligible_handler("Chief Superintendent", escalation_authority="Controller of Examinations", conn=conn)
            assert res["found"] is True
            assert res["assignment_type"] == "BACKUP"
            assert res["handler"]["role"] == "Controller of Examinations"

    def test_handler_capacity_overflow_queueing(self):
        # Set ALL handlers in database to capacity
        with db_session() as conn:
            conn.execute("UPDATE handlers SET current_load = capacity")
            res = HandlerManager.find_eligible_handler("Chief Superintendent", escalation_authority="Controller of Examinations", conn=conn)
            assert res["found"] is False
            assert res["handler"] is None


class TestDispatchEnginePipeline:
    def _create_dummy_report(self, code="IR01", severity="HIGH", authority="Chief Superintendent"):
        with db_session() as conn:
            cur = conn.execute("""
                INSERT INTO reports (report_uid, invigilator_id, irregularity_code, hall_id, description, severity, target_authority, status)
                VALUES ('TEST-REP-1', 'INVCSE0001', ?, 'HALL-401', 'Test incident', ?, ?, 'VALIDATED')
            """, (code, severity, authority))
            return cur.lastrowid

    def test_successful_dispatch_and_resolution_cycle(self):
        report_id = self._create_dummy_report(code="IR01")
        
        # Dispatch report
        res = DispatchEngine.dispatch_report(report_id, irregularity_code="IR01")
        assert res["success"] is True
        assert res["dispatch_status"] == "ASSIGNED"
        assert res["target_authority"] == "Chief Superintendent"
        assigned_handler_id = res["assigned_handler"]["id"]

        # Verify database assignment and workload
        with db_session() as conn:
            h = conn.execute("SELECT current_load FROM handlers WHERE id = ?", (assigned_handler_id,)).fetchone()
            load_after_assign = h["current_load"]

        # Now resolve the report
        update_res = DispatchEngine.update_report_status(report_id, "RESOLVED", comment="Incident resolved peacefully.")
        assert update_res["new_status"] == "RESOLVED"

        # Verify workload was decremented
        with db_session() as conn:
            h_resolved = conn.execute("SELECT current_load FROM handlers WHERE id = ?", (assigned_handler_id,)).fetchone()
            assert h_resolved["current_load"] == load_after_assign - 1

    def test_deterministic_priority_queue_ordering(self):
        # Fill all Centre Superintendent handlers
        with db_session() as conn:
            conn.execute("UPDATE handlers SET current_load = capacity WHERE role = 'Centre Superintendent'")
            
            # Insert 3 queued reports: 1 MEDIUM, 1 CRITICAL, 1 HIGH
            conn.execute("INSERT INTO reports (report_uid, invigilator_id, irregularity_code, hall_id, description, severity, target_authority, status, created_at) VALUES ('Q-MED', 'INVCSE0001', 'IR02', 'HALL-401', 'd', 'MEDIUM', 'Centre Superintendent', 'QUEUED', '2026-11-13 10:00:00')")
            conn.execute("INSERT INTO reports (report_uid, invigilator_id, irregularity_code, hall_id, description, severity, target_authority, status, created_at) VALUES ('Q-CRIT', 'INVCSE0001', 'IR02', 'HALL-401', 'd', 'CRITICAL', 'Centre Superintendent', 'QUEUED', '2026-11-13 10:05:00')")
            conn.execute("INSERT INTO reports (report_uid, invigilator_id, irregularity_code, hall_id, description, severity, target_authority, status, created_at) VALUES ('Q-HIGH', 'INVCSE0001', 'IR02', 'HALL-401', 'd', 'HIGH', 'Centre Superintendent', 'QUEUED', '2026-11-13 09:55:00')")

        queued = QueueManager.get_queued_reports()
        # Expect order: CRITICAL (Q-CRIT) -> HIGH (Q-HIGH) -> MEDIUM (Q-MED)
        uids = [q["report_uid"] for q in queued if q["report_uid"].startswith("Q-")]
        assert uids == ["Q-CRIT", "Q-HIGH", "Q-MED"]

