from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "chennai-digital-twin-backend"

def test_vehicles_stub():
    response = client.get("/api/v1/vehicles")
    assert response.status_code == 200
    assert response.json()["status"] == "not_implemented"
    assert response.json()["phase"] == "2"

def test_cameras_stub():
    response = client.get("/api/v1/cameras")
    assert response.status_code == 200
    assert response.json()["status"] == "not_implemented"
    assert response.json()["phase"] == "2"
