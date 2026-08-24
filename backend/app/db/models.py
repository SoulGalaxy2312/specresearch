from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.config import get_settings

class Base(DeclarativeBase):
    pass

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

class SessionRow(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    fsm_state: Mapped[str] = mapped_column(String(64), default="IDEA")
    raw_idea: Mapped[str] = mapped_column(Text, default="")
    confirmed_interpretation: Mapped[str] = mapped_column(Text, default="")
    revise_count: Mapped[int] = mapped_column(Integer, default=0)
    working_ast_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

class SpecVersionRow(Base):
    __tablename__ = "spec_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    version_no: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(64), default="draft")
    ast_json: Mapped[str] = mapped_column(Text, default="{}")
    markdown: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

class DecisionRow(Base):
    __tablename__ = "decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    step: Mapped[str] = mapped_column(String(64))
    options_json: Mapped[str] = mapped_column(Text, default="[]")
    choice_key: Mapped[str] = mapped_column(String(64), default="")
    choice_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

class JudgeRunRow(Base):
    __tablename__ = "judge_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    version_id: Mapped[str] = mapped_column(String(36), index=True)
    round_no: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="in_progress")
    aggregate_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

class JudgeFindingRow(Base):
    __tablename__ = "judge_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(36), index=True)
    judge_type: Mapped[str] = mapped_column(String(32))
    severity: Mapped[str] = mapped_column(String(16), default="MINOR")
    target: Mapped[str] = mapped_column(String(64), default="overall")
    target_id: Mapped[str] = mapped_column(String(64), default="")
    issue: Mapped[str] = mapped_column(Text, default="")
    reason: Mapped[str] = mapped_column(Text, default="")
    suggestion: Mapped[str] = mapped_column(Text, default="")
    raw_json: Mapped[str] = mapped_column(Text, default="")

class SourceRow(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    openalex_id: Mapped[str] = mapped_column(String(128), default="")
    title: Mapped[str] = mapped_column(Text, default="")
    year: Mapped[int] = mapped_column(Integer, default=0)
    authors_json: Mapped[str] = mapped_column(Text, default="[]")
    abstract: Mapped[str] = mapped_column(Text, default="")
    doi_url: Mapped[str] = mapped_column(Text, default="")
    cited_by_count: Mapped[int] = mapped_column(Integer, default=0)

_settings = get_settings()
engine = create_engine(
    _settings.database_url,
    connect_args={"check_same_thread": False} if _settings.database_url.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

