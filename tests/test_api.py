import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

# Mock required environment variables
os.environ["GOOGLE_API_KEY"] = "dummy"
os.environ["TWILIO_ACCOUNT_SID"] = "dummy"
os.environ["TWILIO_API_KEY"] = "dummy"
os.environ["TWILIO_API_SECRET"] = "dummy"
os.environ["DEEPGRAM_API_KEY"] = "dummy"
os.environ["ELEVENLABS_API_KEY"] = "dummy"

client = TestClient(app)

def test_landing_page():
    response = client.get("/")
    assert response.status_code == 200

def test_new_routes():
    routes = [
        "/register", "/admin", "/call-logs", "/landing-ar",
        "/real-estate", "/knowledge-base", "/agent-editor",
        "/campaigns", "/campaign-builder", "/billing",
        "/api-portal", "/call-analysis", "/tenants", "/integrations"
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, f"Route {route} failed"

def test_api_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    assert "calls" in response.json()

def test_agent_config():
    response = client.post("/api/agent/config?dialect=test&instructions=test")
    assert response.status_code == 200
    assert response.json()["config"]["dialect"] == "test"
