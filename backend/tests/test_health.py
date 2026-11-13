import pytest
import os
import sys

# Ensure backend root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database.seed_data import init_db

@pytest.fixture
def client(tmp_path):
    test_db = str(tmp_path / "test_exam.db")
    # Initialize DB specifically for this test file
    init_db(db_path=test_db, force=True)

    app = create_app({
        "TESTING": True,
        "DATABASE": test_db
    })

    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data

def test_get_categories(client):
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    # Verify the 5 required irregularity codes
    codes = [item["code"] for item in data["data"]]
    assert set(codes) == {"IR01", "IR02", "IR03", "IR04", "IR05"}

def test_get_routing_rules(client):
    response = client.get("/api/routing-rules")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert len(data["data"]) == 5

def test_get_stats(client):
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "total_reports" in data["data"]
    assert "active_incidents" in data["data"]

def test_get_network_routes(client):
    response = client.get("/api/network-routes")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert len(data["data"]) >= 4
