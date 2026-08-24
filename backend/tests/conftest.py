from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["MOCK_LLM"] = "1"
os.environ["DATABASE_URL"] = "sqlite://"

from app.db import models


@pytest.fixture(autouse=True)
def isolated_database(monkeypatch: pytest.MonkeyPatch):
    """Run every test against a fresh database through the production dependency."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )
    models.Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(models, "SessionLocal", testing_session_local)

    yield

    models.Base.metadata.drop_all(bind=engine)
    engine.dispose()
