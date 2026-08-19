"""End-to-end smoke test: idea → restate → decompose.

Runs with MOCK_LLM=1 so no external API calls are needed.
Verifies that the core wizard flow works without crashing and
returns the expected shapes at each step.
"""

import os
import tempfile

os.environ.setdefault("MOCK_LLM", "1")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.gettempdir()}/specresearch-e2e.db")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_IDEA = (
    "Tối ưu prompt LLM nhiều vòng bằng evidence-based feedback "
    "để giảm hallucination khi trích xuất thông tin."
)


def _create_session() -> str:
    res = client.post("/api/v1/sessions")
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    return data["session_id"]


def test_idea_to_restate_flow():
    """Walk through the first three steps of the wizard."""
    sid = _create_session()

    # Step 1: set idea
    res = client.post(f"/api/v1/sessions/{sid}/idea", json={"idea": SAMPLE_IDEA})
    assert res.status_code == 200
    assert res.json()["ok"] is True

    # Step 2: generate restatement
    res = client.post(f"/api/v1/sessions/{sid}/restate")
    assert res.status_code == 200
    interps = res.json().get("interpretations", [])
    assert len(interps) >= 1, "Expected at least one interpretation"
    chosen = interps[0]["text"]

    # Step 3: confirm restatement
    res = client.post(
        f"/api/v1/sessions/{sid}/restate/confirm",
        json={"action": "confirm", "text": chosen},
    )
    assert res.status_code == 200
    body = res.json()
    assert body.get("ok") is True
    assert body.get("fsm_state") == "RESTATED"


def test_full_decompose_flow():
    """Extend the flow to decomposition and verify cards are produced."""
    sid = _create_session()

    # Setup
    client.post(f"/api/v1/sessions/{sid}/idea", json={"idea": SAMPLE_IDEA})
    res = client.post(f"/api/v1/sessions/{sid}/restate")
    chosen = res.json()["interpretations"][0]["text"]
    client.post(
        f"/api/v1/sessions/{sid}/restate/confirm",
        json={"action": "confirm", "text": chosen},
    )

    # Decompose
    res = client.post(f"/api/v1/sessions/{sid}/decompose")
    assert res.status_code == 200
    data = res.json()
    assert len(data.get("cards", [])) >= 1, "Expected at least one spec card"
    assert data.get("fsm_state") == "DECOMPOSED"


def test_invalid_session_returns_400():
    """Malformed session IDs should get a 400, not a 500."""
    res = client.get("/api/v1/sessions/not-a-uuid")
    assert res.status_code == 400


def test_missing_session_returns_404():
    """A well-formed but non-existent UUID should get 404."""
    res = client.get("/api/v1/sessions/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404
