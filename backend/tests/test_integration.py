import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database.seed_data import init_db
from database.connection import db_session

@pytest.fixture
def client(tmp_path):
    test_db = str(tmp_path / "test_integ.db")
    os.environ["DATABASE"] = test_db
    init_db(db_path=test_db, force=True)

    app = create_app({
        "TESTING": True,
        "DATABASE": test_db
    })

    with app.test_client() as client:
        yield client

class TestEndToEndPipeline:
    def test_complete_valid_report_submission(self, client):
        payload = {
            "invigilator_id": "INVCSE0001",
            "irregularity_code": "IR01",
            "hall_id": "HALL-401",
            "student_roll": "21CS042",
            "description": "Candidate attempting unauthorized communication during session.",
            "severity": "HIGH",
            "source_ip": "192.168.10.45"
        }
        res = client.post("/api/reports", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert data["target_authority"] == "Chief Superintendent"
        assert data["status"] in ("ASSIGNED", "ESCALATED")
        assert data["assigned_handler"] is not None
        assert data["assigned_handler"]["role"] == "Chief Superintendent"
        
        # Verify network routing
        assert "network_routing" in data
        assert data["network_routing"]["next_hop"] is not None
        assert data["network_routing"]["interface"] == "vlan40"

    def test_invalid_invigilator_id_rejection(self, client):
        payload = {
            "invigilator_id": "INVBADID001",  # Invalid department
            "irregularity_code": "IR01",
            "hall_id": "HALL-401",
            "description": "Test failure",
            "source_ip": "192.168.10.45"
        }
        res = client.post("/api/reports", json=payload)
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert data["stage"] == "TOC_VALIDATION"
        assert data["status"] == "REJECTED"

    def test_unsupported_irregularity_code_rejection(self, client):
        payload = {
            "invigilator_id": "INVCSE0001",
            "irregularity_code": "IR99",  # Unsupported code
            "hall_id": "HALL-401",
            "description": "Test failure",
            "source_ip": "192.168.10.45"
        }
        res = client.post("/api/reports", json=payload)
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert data["stage"] == "TOC_VALIDATION"

    def test_source_ip_zone_mismatch_rejection(self, client):
        payload = {
            "invigilator_id": "INVCSE0001",
            "irregularity_code": "IR01",
            "hall_id": "LAB-3",                # LAB-3 requires 192.168.10.128/25
            "description": "Subnet mismatch test",
            "source_ip": "192.168.10.45"       # Inside /24, but NOT inside /25!
        }
        res = client.post("/api/reports", json=payload)
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert data["stage"] == "SOURCE_IP_VALIDATION"
        assert "does not belong" in data["error"]

    def test_emergency_override_elevation(self, client):
        payload = {
            "invigilator_id": "INVECE0001",
            "irregularity_code": "IR02",        # Default is MEDIUM
            "hall_id": "HALL-204",
            "description": "Physical brawl erupted in exam hall.",
            "source_ip": "192.168.20.12",
            "is_emergency": True,
            "override_reason": "Severe physical altercation"
        }
        res = client.post("/api/reports", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["priority"]["effective_priority"] == "CRITICAL"
        assert data["priority"]["is_overridden"] is True

    def test_queueing_when_handlers_at_capacity(self, client):
        # Set all Centre Superintendent handlers to capacity
        with db_session() as conn:
            conn.execute("UPDATE handlers SET current_load = capacity WHERE role = 'Centre Superintendent'")
            # Also set backup to capacity so it cannot escalate
            conn.execute("UPDATE handlers SET current_load = capacity WHERE role = 'Chief Superintendent'")

        payload = {
            "invigilator_id": "INVCSE0001",
            "irregularity_code": "IR04",        # Technical -> Centre Superintendent
            "hall_id": "HALL-401",
            "description": "Network switch failure in hall.",
            "source_ip": "192.168.10.45"
        }
        res = client.post("/api/reports", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["status"] == "QUEUED"
        assert data["assigned_handler"] is None

        # Verify report appears in dispatch queue endpoint
        queue_res = client.get("/api/dispatch/queue")
        assert queue_res.status_code == 200
        q_data = queue_res.get_json()
        assert q_data["count"] >= 1
        assert any(item["report_uid"] == data["report_uid"] for item in q_data["data"])

    def test_handler_status_resolution_and_queue_dequeue(self, client):
        # 1. Fill handler capacity for both Controller of Examinations and escalation backup Chief Superintendent
        with db_session() as conn:
            conn.execute("UPDATE handlers SET current_load = capacity WHERE role = 'Controller of Examinations'")
            conn.execute("UPDATE handlers SET current_load = capacity WHERE role = 'Chief Superintendent'")

        # 2. Submit report for IR05 -> should enter queue
        payload = {
            "invigilator_id": "INVEEE0001",
            "irregularity_code": "IR05",
            "hall_id": "HALL-102",
            "description": "Missing booklet",
            "source_ip": "192.168.30.8"
        }
        res1 = client.post("/api/reports", json=payload)
        assert res1.get_json()["status"] == "QUEUED"
        queued_uid = res1.get_json()["report_uid"]

        # 3. Find an active report assigned to Controller of Examinations and resolve it
        with db_session() as conn:
            # Create a dummy active assigned report
            cur = conn.execute("""
                INSERT INTO reports (report_uid, invigilator_id, irregularity_code, hall_id, description, target_authority, status, source_ip)
                VALUES ('DUMMY-ACT', 'INVEEE0001', 'IR05', 'HALL-102', 'desc', 'Controller of Examinations', 'ASSIGNED', '192.168.30.8')
            """)
            dummy_id = cur.lastrowid
            h_coe = conn.execute("SELECT id FROM handlers WHERE role = 'Controller of Examinations' LIMIT 1").fetchone()
            conn.execute("""
                INSERT INTO assignments (report_id, handler_id, assigned_role, assignment_type, status)
                VALUES (?, ?, 'Controller of Examinations', 'PRIMARY', 'ASSIGNED')
            """, (dummy_id, h_coe["id"]))

        # 4. Resolve the active report
        res_resolve = client.put(f"/api/reports/{dummy_id}/status", json={"status": "RESOLVED", "comment": "Audit completed."})
        assert res_resolve.status_code == 200

        # 5. Verify the queued report was automatically dequeued and assigned!
        details_res = client.get("/api/reports")
        reports = details_res.get_json()["data"]
        queued_report_now = next((r for r in reports if r["report_uid"] == queued_uid), None)
        assert queued_report_now is not None
        assert queued_report_now["status"] == "ASSIGNED"

    def test_lpm_lookup_endpoint(self, client):
        # Specialized lab /25 lookup
        res = client.post("/api/network-routes/lookup", json={"destination_ip": "192.168.10.134"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["prefix_length"] == 25
        assert data["interface"] == "eth0.100"

        # Invalid IP
        res_bad = client.post("/api/network-routes/lookup", json={"destination_ip": "999.999.999.999"})
        assert res_bad.status_code == 404
