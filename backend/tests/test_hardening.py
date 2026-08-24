import asyncio
import logging

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from app.db import models
from app.main import _RequestLogMiddleware, _redacted_database_url, app


def test_database_url_redacts_password():
    redacted = _redacted_database_url("postgresql://researcher:secret@db.example/spec")

    assert "secret" not in redacted
    assert "***" in redacted


def test_health_reports_degraded_when_database_is_unavailable(monkeypatch):
    class BrokenSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, statement):
            raise RuntimeError("database unavailable")

    monkeypatch.setattr(models, "SessionLocal", BrokenSession)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["db_connected"] is False
    assert response.json()["session_count"] is None


def test_request_middleware_logs_unhandled_errors(caplog):
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/boom",
            "headers": [],
            "query_string": b"",
            "scheme": "http",
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
        }
    )
    middleware = _RequestLogMiddleware(app)

    async def fail(_request):
        raise RuntimeError("boom")

    with caplog.at_level(logging.ERROR, logger="specresearch"):
        with pytest.raises(RuntimeError, match="boom"):
            asyncio.run(middleware.dispatch(request, fail))

    assert "GET /boom" in caplog.text
    assert "unhandled error" in caplog.text


@pytest.mark.parametrize(
    ("path", "expected_status"),
    [
        ("/api/v1/sessions/not-a-uuid/versions", 400),
        ("/api/v1/sessions/not-a-uuid/versions/version-id/diff", 400),
        ("/api/v1/sessions/00000000-0000-0000-0000-000000000000/versions", 404),
        (
            "/api/v1/sessions/00000000-0000-0000-0000-000000000000/versions/version-id/diff",
            404,
        ),
    ],
)
def test_version_routes_validate_session(path, expected_status):
    with TestClient(app) as client:
        response = client.get(path)

    assert response.status_code == expected_status
