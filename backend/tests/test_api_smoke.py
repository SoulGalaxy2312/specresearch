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
