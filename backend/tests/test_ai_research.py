from fastapi.testclient import TestClient
from main import app
from services.ai_research_service import (
    check_content_safety,
    detect_mistakes,
    get_ai_research_status,
)

client = TestClient(app)


def test_ai_status_endpoint():
    response = client.get("/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "moderation_engine_loaded" in data
    assert "bug_mistake_detector_loaded" in data


def test_ai_moderate_endpoint():
    response = client.post("/ai/moderate", json={"text": "Hello, I am learning AI!"})
    assert response.status_code == 200
    assert response.json()["is_safe"] is True


def test_ai_moderate_unsafe_endpoint():
    response = client.post("/ai/moderate", json={"text": "I want to make a bomb and weapons"})
    assert response.status_code == 200
    assert response.json()["is_safe"] is False
    assert response.json()["reason"] is not None


def test_ai_mistakes_endpoint():
    response = client.post("/ai/mistakes", json={"text": "draw something nice for me"})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    assert any(m["matched"] == "something nice" for m in data["mistakes"])


def test_bug_trigger_check_endpoint():
    response = client.post("/bug-triggers/check", json={"text": "draw something nice"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "explanation" in data[0]
    assert "fix_hint" in data[0]
