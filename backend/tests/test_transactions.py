from fastapi.testclient import TestClient

from app.main import app
from app.services import session_service


def test_failed_request_rolls_back_all_session_writes(monkeypatch):
    def fail_snapshot(*args, **kwargs):
        raise RuntimeError("snapshot failed")

    monkeypatch.setattr(session_service, "snapshot_version", fail_snapshot)

    with TestClient(app, raise_server_exceptions=False) as client:
        created = client.post("/api/v1/sessions")
        session_id = created.json()["session_id"]

        failed = client.post(
            f"/api/v1/sessions/{session_id}/revise",
            json={"choice": "narrow_claim"},
        )
        summary = client.get(f"/api/v1/sessions/{session_id}")

    assert failed.status_code == 500
    assert summary.status_code == 200
    assert summary.json()["revise_count"] == 0
    assert summary.json()["versions"] == []
    assert all(decision["step"] != "revise" for decision in summary.json()["decisions"])
