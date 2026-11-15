import os
os.environ["DATABASE_URL"] = "sqlite:///./test_agrispace.db"
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    # Context management executes the FastAPI lifespan, including schema setup.
    with TestClient(app) as test_client:
        yield test_client

def test_health_has_demo_disclosure(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert "demo_mode" in response.json()
    assert response.headers["x-content-type-options"] == "nosniff"

def test_user_farm_isolation_and_area(client):
    first = client.post("/api/v1/auth/register", json={"name":"Asha Farmer","email":"asha@example.com","password":"SafePassword123"}).json()
    headers = {"Authorization": f"Bearer {first['access_token']}"}
    boundary = {"type":"Polygon","coordinates":[[[77.0,28.0],[77.001,28.0],[77.001,28.001],[77.0,28.0]]]}
    farm = client.post("/api/v1/farms", headers=headers, json={"name":"North Field","latitude":28,"longitude":77,"boundary":boundary})
    assert farm.status_code == 201
    assert farm.json()["area_hectares"] > 0
    second = client.post("/api/v1/auth/register", json={"name":"Ravi Farmer","email":"ravi@example.com","password":"SafePassword123"}).json()
    denied = client.get(f"/api/v1/farms/{farm.json()['id']}", headers={"Authorization":f"Bearer {second['access_token']}"})
    assert denied.status_code == 403

def test_field_belongs_to_its_farm(client):
    token = client.post("/api/v1/auth/register", json={"name":"Field Owner","email":"fields@example.com","password":"SafePassword123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    farm = client.post("/api/v1/farms", headers=headers, json={"name":"Field Farm","latitude":28,"longitude":77}).json()
    field = client.post(f"/api/v1/farms/{farm['id']}/fields", headers=headers, json={"name":"West Plot","current_crop":"Chickpea"})
    assert field.status_code == 201
    assert client.get(f"/api/v1/farms/{farm['id']}/fields", headers=headers).json()[0]["name"] == "West Plot"

def test_refresh_rotation_logout_revocation_and_export(client):
    registration = client.post("/api/v1/auth/register", json={"name":"Session Owner","email":"session@example.com","password":"SafePassword123"})
    assert registration.status_code == 201
    access_token = registration.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    exported = client.get("/api/v1/users/me/export", headers=headers)
    assert exported.status_code == 200
    assert exported.headers["cache-control"] == "no-store"
    assert exported.json()["user"]["email"] == "session@example.com"
    refreshed = client.post("/api/v1/auth/refresh")
    assert refreshed.status_code == 200
    logged_out = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {refreshed.json()['access_token']}"})
    assert logged_out.status_code == 204
    assert client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {refreshed.json()['access_token']}"}).status_code == 401

def test_llm_context_is_source_labelled_and_not_training_ready(client):
    token = client.post("/api/v1/auth/register", json={"name":"Context Owner","email":"context@example.com","password":"SafePassword123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    farm = client.post("/api/v1/farms", headers=headers, json={"name":"Context Farm","latitude":28,"longitude":77}).json()
    response = client.get(f"/api/v1/farms/{farm['id']}/llm-context", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["environmental_observations"]["simulated"] is True
    assert body["ml_readiness"]["eligible_as_training_labels"] is False
