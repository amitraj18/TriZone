"""
Tests for Master Phase authentication, persistent in-app notifications,
RFC 4180 CSV report export, CIDR subnet calculation, admin routing rule modifications,
and demo database state resetter.
"""
import pytest
import csv
import io
from app import create_app
from database.seed_data import init_db
from auth.auth_service import authenticate_user, verify_auth_token, hash_password
from notifications.notification_service import NotificationService
from export.csv_exporter import export_reports_to_csv


@pytest.fixture
def app_instance(tmp_path, monkeypatch):
    db_file = tmp_path / "test_auth_features.db"
    monkeypatch.setenv("DATABASE", str(db_file))
    init_db(str(db_file))
    app = create_app({"TESTING": True, "DATABASE": str(db_file)})
    return app


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


# ---------------------------------------------------------------------------
# Authentication & RBAC Tests
# ---------------------------------------------------------------------------
def test_password_hashing_and_auth():
    """Verify werkzeug secure password hashing and verification."""
    pwd = "securepassword123"
    h = hash_password(pwd)
    assert h != pwd
    assert h.startswith("pbkdf2:sha256:") or h.startswith("scrypt:")


def test_auth_success(client):
    """Test successful user login with valid credentials."""
    resp = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "token" in data["data"]
    assert data["data"]["role"] == "ADMIN"
    assert data["data"]["username"] == "admin"

    # Verify token
    user_payload = verify_auth_token(data["data"]["token"])
    assert user_payload is not None
    assert user_payload["usr"] == "admin"
    assert user_payload["rol"] == "ADMIN"


def test_auth_invalid_credentials(client):
    """Test login failure with bad password or unknown user."""
    resp = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    assert resp.status_code == 401
    data = resp.get_json()
    assert data["success"] is False

    resp2 = client.post("/api/auth/login", json={
        "username": "nonexistent_user",
        "password": "password"
    })
    assert resp2.status_code == 401


def test_auth_me_endpoint(client):
    """Test /api/auth/me token inspection endpoint."""
    # Login first with valid seeded credentials
    login_resp = client.post("/api/auth/login", json={
        "username": "handler_cs",
        "password": "exam123"
    })
    assert login_resp.status_code == 200
    token = login_resp.get_json()["data"]["token"]

    # Call /api/auth/me with Bearer token
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.get_json()["data"]["role"] == "HANDLER"
    assert resp.get_json()["data"]["username"] == "handler_cs"

    # Call with invalid token
    bad_resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.str"})
    assert bad_resp.status_code == 401


# ---------------------------------------------------------------------------
# Persistent In-App Notification Tests
# ---------------------------------------------------------------------------
def test_notification_lifecycle(client):
    """Test creating, reading, and marking notifications as read."""
    # Create notification
    notif_id = NotificationService.create_notification(
        title="Emergency Incident",
        message="Medical emergency in Hall B",
        n_type="URGENT",
        target_role="HANDLER",
        report_id=1
    )
    assert notif_id is not None

    # Fetch notifications for HANDLER
    resp = client.get("/api/notifications?role=HANDLER")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["unread_count"] >= 1
    found = any(n["id"] == notif_id for n in data["data"])
    assert found is True

    # Mark as read
    patch_resp = client.patch(f"/api/notifications/{notif_id}/read")
    assert patch_resp.status_code == 200
    assert patch_resp.get_json()["data"]["is_read"] == 1

    # Mark all read
    all_read_resp = client.post("/api/notifications/mark-all-read")
    assert all_read_resp.status_code == 200

    # Unread count should now be 0 for ALL
    resp_after = client.get("/api/notifications?role=ALL")
    assert resp_after.get_json()["unread_count"] == 0


# ---------------------------------------------------------------------------
# RFC 4180 CSV Report Export Tests
# ---------------------------------------------------------------------------
def test_csv_export(client):
    """Test CSV export endpoint for RFC 4180 compliance and contents."""
    resp = client.get("/api/reports/export/csv")
    assert resp.status_code == 200
    assert resp.content_type.startswith("text/csv")
    assert "attachment; filename=" in resp.headers.get("Content-Disposition", "")

    csv_text = resp.data.decode("utf-8")
    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)

    # Validate header row
    header = rows[0]
    expected_headers = [
        "Report UID", "Invigilator ID", "Department", "Category Code",
        "Severity", "Target Authority", "Status", "Source IP"
    ]
    for eh in expected_headers:
        assert eh in header

    # Ensure at least one data row exists from seed
    assert len(rows) > 1


# ---------------------------------------------------------------------------
# CIDR Subnet Calculation Tests
# ---------------------------------------------------------------------------
def test_subnet_calculator_endpoint(client):
    """Test /api/network-routes/calculate-subnet endpoint."""
    resp = client.post("/api/network-routes/calculate-subnet", json={
        "cidr": "192.168.10.0/24"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["network_address"] == "192.168.10.0"
    assert data["netmask"] == "255.255.255.0"
    assert data["wildcard_mask"] == "0.0.0.255"
    assert data["broadcast_address"] == "192.168.10.255"
    assert data["prefix_length"] == 24
    assert data["total_hosts"] == 256
    assert data["usable_hosts"] == 254
    assert data["first_usable_host"] == "192.168.10.1"
    assert data["last_usable_host"] == "192.168.10.254"

    # Test invalid CIDR
    bad_resp = client.post("/api/network-routes/calculate-subnet", json={
        "cidr": "invalid-ip/99"
    })
    assert bad_resp.status_code == 400


# ---------------------------------------------------------------------------
# Admin Routing Rule Modification & Audit Trail Tests
# ---------------------------------------------------------------------------
def test_admin_routing_rule_modification(client):
    """Test modifying a routing rule and verifying historical audit log."""
    # Fetch existing rules
    rules_resp = client.get("/api/routing-rules")
    rules = rules_resp.get_json()["data"]
    assert len(rules) > 0
    rule_id = rules[0]["id"]

    # Update rule
    update_resp = client.put(f"/api/routing-rules/{rule_id}", json={
        "target_authority": "Chief Superintendent",
        "escalation_authority": "Controller of Examinations",
        "priority": "CRITICAL",
        "reason": "Updated by Automated Pytest for hackathon audit test",
        "modified_by": "DR_LISKOV"
    })
    assert update_resp.status_code == 200
    assert update_resp.get_json()["success"] is True

    # Verify audit history is logged
    hist_resp = client.get("/api/routing-rules/history")
    assert hist_resp.status_code == 200
    hist_data = hist_resp.get_json()["data"]
    assert len(hist_data) >= 1
    assert any(h["rule_id"] == rule_id for h in hist_data)


# ---------------------------------------------------------------------------
# Demo Database Reset Tests
# ---------------------------------------------------------------------------
def test_demo_reset_endpoint(client):
    """Test /api/demo/reset creates an active showcase state for demonstration."""
    resp = client.post("/api/demo/reset")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True

    # Check stats
    stats_resp = client.get("/api/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.get_json()["data"]
    assert stats["total_reports"] >= 5
    assert stats["active_incidents"] >= 1
    assert stats["queued_incidents"] >= 0
