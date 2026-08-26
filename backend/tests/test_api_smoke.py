import os
import tempfile

os.environ.setdefault("MOCK_LLM", "1")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.gettempdir()}/specresearch-test.db")

from app.main import app


def test_health_endpoint_reports_ok():
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_read_session():
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        created = client.post("/api/v1/sessions")

        assert created.status_code == 200
        session_id = created.json()["session_id"]

        fetched = client.get(f"/api/v1/sessions/{session_id}")

    assert fetched.status_code == 200
    body = fetched.json()
    assert body["session_id"] == session_id
    assert body["fsm_state"] == "IDEA"


def test_seed_knowledge_and_chat_history_endpoints():
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        created = client.post("/api/v1/sessions")
        session_id = created.json()["session_id"]

        knowledge = client.get("/api/v1/knowledge")
        sessions = client.get("/api/v1/sessions?limit=5&offset=0")
        chat = client.post(
            f"/api/v1/sessions/{session_id}/chat",
            json={"content": "Ghi chú demo", "step": "Idea"},
        )
        history = client.get(f"/api/v1/sessions/{session_id}/chat")

    assert knowledge.status_code == 200
    assert len(knowledge.json()["items"]) >= 4
    assert sessions.status_code == 200
    assert sessions.json()["total"] >= 1
    assert chat.status_code == 200
    assert history.status_code == 200
    assert history.json()["items"][0]["content"] == "Ghi chú demo"
