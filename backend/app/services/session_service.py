from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models import (
    ChatMessageRow,
    DecisionRow,
    JudgeFindingRow,
    JudgeRunRow,
    KnowledgeItemRow,
    SessionRow,
    SourceRow,
    SpecVersionRow,
)
from app.domain.spec_ast import FsmState, SpecAST, can_transition


def now() -> datetime:
    return datetime.now(timezone.utc)


def create_session(db: Session) -> SessionRow:
    row = SessionRow(
        id=str(uuid4()),
        fsm_state=FsmState.IDEA.value,
        working_ast_json=SpecAST().model_dump_json(),
    )
    db.add(row)
    db.flush()
    db.refresh(row)
    return row


def get_session(db: Session, session_id: str) -> SessionRow:
    row = db.get(SessionRow, session_id)
    if not row:
        raise KeyError("Session not found")
    return row


def list_sessions(db: Session, limit: int = 10, offset: int = 0) -> tuple[list[SessionRow], int]:
    query = db.query(SessionRow).order_by(SessionRow.updated_at.desc())
    return query.offset(offset).limit(limit).all(), query.count()


def load_ast(row: SessionRow) -> SpecAST:
    data = json.loads(row.working_ast_json or "{}")
    return SpecAST.model_validate(data)


def save_ast(db: Session, row: SessionRow, ast: SpecAST) -> None:
    row.working_ast_json = ast.model_dump_json()
    row.updated_at = now()
    db.add(row)
    db.flush()
    db.refresh(row)


def set_state(db: Session, row: SessionRow, target: FsmState) -> None:
    current = FsmState(row.fsm_state)
    if current != target and not can_transition(current, target):
        # Allow same-state refresh and JUDGING <-> REVISION loops already in map
        if not (current == target):
            raise ValueError(f"Invalid transition {current.value} -> {target.value}")
    row.fsm_state = target.value
    row.updated_at = now()
    db.add(row)
    db.flush()
    db.refresh(row)


def force_state(db: Session, row: SessionRow, target: FsmState) -> None:
    row.fsm_state = target.value
    row.updated_at = now()
    db.add(row)
    db.flush()
    db.refresh(row)


def record_decision(
    db: Session,
    session_id: str,
    step: str,
    options: list[dict[str, Any]],
    choice_key: str,
    choice_text: str,
) -> DecisionRow:
    row = DecisionRow(
        id=str(uuid4()),
        session_id=session_id,
        step=step,
        options_json=json.dumps(options, ensure_ascii=False),
        choice_key=choice_key,
        choice_text=choice_text,
    )
    db.add(row)
    db.flush()
    db.refresh(row)
    return row


def snapshot_version(
    db: Session,
    session_id: str,
    ast: SpecAST,
    markdown: str,
    label: str,
) -> SpecVersionRow:
    existing = (
        db.query(SpecVersionRow)
        .filter(SpecVersionRow.session_id == session_id)
        .order_by(SpecVersionRow.version_no.desc())
        .first()
    )
    version_no = (existing.version_no + 1) if existing else 1
    row = SpecVersionRow(
        id=str(uuid4()),
        session_id=session_id,
        version_no=version_no,
        label=label,
        ast_json=ast.model_dump_json(),
        markdown=markdown,
    )
    db.add(row)
    db.flush()
    db.refresh(row)
    return row


def list_versions(db: Session, session_id: str) -> list[SpecVersionRow]:
    return (
        db.query(SpecVersionRow)
        .filter(SpecVersionRow.session_id == session_id)
        .order_by(SpecVersionRow.version_no.asc())
        .all()
    )


def get_version(db: Session, version_id: str) -> SpecVersionRow:
    row = db.get(SpecVersionRow, version_id)
    if not row:
        raise KeyError("Version not found")
    return row


def upsert_sources(db: Session, session_id: str, sources: list[dict[str, Any]]) -> None:
    for s in sources:
        existing = db.get(SourceRow, s["id"])
        if existing:
            continue
        db.add(
            SourceRow(
                id=s["id"],
                session_id=session_id,
                openalex_id=s.get("openalex_id") or "",
                title=s.get("title") or "",
                year=s.get("year") or 0,
                authors_json=json.dumps(s.get("authors") or [], ensure_ascii=False),
                abstract=s.get("abstract") or "",
                doi_url=s.get("doi_url") or "",
                cited_by_count=s.get("cited_by_count") or 0,
            )
        )
    db.flush()


def create_judge_run(db: Session, session_id: str, version_id: str, round_no: int) -> JudgeRunRow:
    row = JudgeRunRow(
        id=str(uuid4()),
        session_id=session_id,
        version_id=version_id,
        round_no=round_no,
        status="in_progress",
    )
    db.add(row)
    db.flush()
    db.refresh(row)
    return row


def add_judge_findings(
    db: Session,
    run_id: str,
    judge_type: str,
    findings: list[dict[str, Any]],
    raw: dict[str, Any],
) -> None:
    for f in findings:
        db.add(
            JudgeFindingRow(
                id=str(uuid4()),
                run_id=run_id,
                judge_type=judge_type,
                severity=f.get("severity", "MINOR"),
                target=f.get("target", "overall"),
                target_id=f.get("target_id") or "",
                issue=f.get("issue", ""),
                reason=f.get("reason", ""),
                suggestion=f.get("suggestion", ""),
                raw_json=json.dumps(raw, ensure_ascii=False),
            )
        )
    db.flush()


def get_latest_judge_run(db: Session, session_id: str) -> JudgeRunRow | None:
    return (
        db.query(JudgeRunRow)
        .filter(JudgeRunRow.session_id == session_id)
        .order_by(JudgeRunRow.created_at.desc())
        .first()
    )


def list_knowledge(db: Session, category: str | None = None) -> list[dict[str, Any]]:
    query = db.query(KnowledgeItemRow).order_by(KnowledgeItemRow.category, KnowledgeItemRow.title)
    if category:
        query = query.filter(KnowledgeItemRow.category == category)
    rows = query.all()
    return [
        {
            "id": row.id,
            "category": row.category,
            "title": row.title,
            "summary": row.summary,
            "source_url": row.source_url,
            "tags": json.loads(row.tags_json or "[]"),
            "payload": json.loads(row.payload_json or "{}"),
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


def add_chat_message(
    db: Session,
    session_id: str,
    role: str,
    content: str,
    step: str = "",
) -> ChatMessageRow:
    row = ChatMessageRow(
        id=str(uuid4()),
        session_id=session_id,
        role=role,
        content=content,
        step=step,
    )
    db.add(row)
    db.flush()
    db.refresh(row)
    return row


def list_chat_messages(db: Session, session_id: str) -> list[dict[str, Any]]:
    rows = (
        db.query(ChatMessageRow)
        .filter(ChatMessageRow.session_id == session_id)
        .order_by(ChatMessageRow.created_at.asc())
        .all()
    )
    return [
        {
            "id": row.id,
            "session_id": row.session_id,
            "role": row.role,
            "content": row.content,
            "step": row.step,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


def session_summary(db: Session, row: SessionRow) -> dict[str, Any]:
    ast = load_ast(row)
    versions = list_versions(db, row.id)
    decisions = db.query(DecisionRow).filter(DecisionRow.session_id == row.id).order_by(DecisionRow.created_at).all()
    chat_messages = list_chat_messages(db, row.id)
    return {
        "session_id": row.id,
        "fsm_state": row.fsm_state,
        "revise_count": row.revise_count,
        "raw_idea": row.raw_idea,
        "confirmed_interpretation": row.confirmed_interpretation,
        "ast": ast.model_dump(),
        "versions": [
            {"id": v.id, "version_no": v.version_no, "label": v.label, "created_at": v.created_at.isoformat()}
            for v in versions
        ],
        "decisions": [
            {
                "id": d.id,
                "step": d.step,
                "choice_key": d.choice_key,
                "choice_text": d.choice_text,
                "created_at": d.created_at.isoformat(),
            }
            for d in decisions
        ],
        "chat_messages": chat_messages,
    }
