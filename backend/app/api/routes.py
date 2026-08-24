from __future__ import annotations

import json
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.domain.spec_ast import CardStatus, FsmState
from app.services import session_service as ss
from app.services.aggregate_service import aggregate_findings
from app.services.claim_service import build_claims
from app.services.decompose_service import decompose_idea
from app.services.experiment_service import plan_experiments
from app.services.feasibility_service import apply_scale_down, estimate_feasibility
from app.services.gap_service import propose_gap
from app.services.judge_service import JUDGE_TYPES, apply_readiness, findings_to_models, run_judge
from app.services.related_work_service import add_manual_paper, run_related_work
from app.services.restate_service import generate_restatement
from app.services.revision_service import apply_revision
from app.services.spec_assemble_service import assemble_markdown

router = APIRouter(prefix="/api/v1")


class IdeaBody(BaseModel):
    idea: str


class RestateConfirmBody(BaseModel):
    action: str
    text: Optional[str] = None


class ResolveBody(BaseModel):
    choice_key: str
    choice_text: str = ""
    options: list[dict[str, Any]] = Field(default_factory=list)
    card_updates: list[dict[str, Any]] = Field(default_factory=list)


class ManualPaperBody(BaseModel):
    title: str
    url: str = ""
    abstract: Optional[str] = None


class ChooseBody(BaseModel):
    choice: str
    other_text: Optional[str] = None


class ClaimsConfirmBody(BaseModel):
    contributions: Optional[list[str]] = None
    claim_cards: Optional[list[dict[str, Any]]] = None


class FeasibilityChooseBody(BaseModel):
    choice: str


class ReviseBody(BaseModel):
    choice: str
    other_text: Optional[str] = None


@router.post("/sessions")
def create_session(db: Session = Depends(get_db)):
    row = ss.create_session(db)
    return {"session_id": row.id, "fsm_state": row.fsm_state}


@router.get("/sessions/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    return ss.session_summary(db, row)


@router.post("/sessions/{session_id}/idea")
def set_idea(session_id: str, body: IdeaBody, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    row.raw_idea = body.idea
    ast = ss.load_ast(row)
    ast.raw_idea = body.idea
    ss.save_ast(db, row, ast)
    return {"ok": True, "raw_idea": body.idea}


@router.post("/sessions/{session_id}/restate")
def restate(session_id: str, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    if not row.raw_idea:
        raise HTTPException(400, "Chưa có ý tưởng")
    try:
        data = generate_restatement(row.raw_idea)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"LLM lỗi: {exc}") from exc
    return data


@router.post("/sessions/{session_id}/restate/confirm")
def restate_confirm(session_id: str, body: RestateConfirmBody, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    text = body.text or ""
    if body.action == "confirm" and not text:
        raise HTTPException(400, "Cần text diễn giải khi confirm")
    if body.action == "alternative":
        data = generate_restatement(row.raw_idea + "\n(Yêu cầu phiên bản diễn giải khác)")
        return {"action": "alternative", **data}
    if body.action in {"edit", "other", "confirm"}:
        if not text:
            raise HTTPException(400, "Thiếu text")
        row.confirmed_interpretation = text
        ast = ss.load_ast(row)
        ast.interpretation = text
        ast.decision_history.append(
            {"step": "restate", "choice_key": body.action, "choice_text": text}
        )
        ss.save_ast(db, row, ast)
        ss.record_decision(db, session_id, "restate", [], body.action, text)
        try:
            ss.set_state(db, row, FsmState.RESTATED)
        except ValueError:
            ss.force_state(db, row, FsmState.RESTATED)
        return {"ok": True, "interpretation": text, "fsm_state": row.fsm_state}
    raise HTTPException(400, "action không hợp lệ")


@router.post("/sessions/{session_id}/decompose")
def decompose(session_id: str, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    if not row.confirmed_interpretation:
        raise HTTPException(400, "Chưa confirm diễn giải")
    try:
        partial_ast, issues = decompose_idea(row.confirmed_interpretation)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"LLM lỗi: {exc}") from exc
    ast = ss.load_ast(row)
    ast.interpretation = row.confirmed_interpretation
    ast.cards = partial_ast.cards
    ss.save_ast(db, row, ast)
    try:
        ss.set_state(db, row, FsmState.DECOMPOSED)
    except ValueError:
        ss.force_state(db, row, FsmState.DECOMPOSED)
    return {"cards": [c.model_dump() for c in ast.cards], "issues": issues, "fsm_state": row.fsm_state}


@router.post("/sessions/{session_id}/decompose/resolve")
def decompose_resolve(session_id: str, body: ResolveBody, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    ss.record_decision(db, session_id, "decompose", body.options, body.choice_key, body.choice_text)
    ast.decision_history.append(
        {"step": "decompose", "choice_key": body.choice_key, "choice_text": body.choice_text}
    )
    for upd in body.card_updates:
        for card in ast.cards:
            if card.id == upd.get("id"):
                if upd.get("content"):
                    card.content = upd["content"]
                if upd.get("status"):
                    try:
                        card.status = CardStatus(upd["status"])
                    except Exception:  # noqa: BLE001
                        pass
                # confirming open question via choice
                if body.choice_key and card.status in {CardStatus.AMBIGUOUS, CardStatus.MISSING}:
                    card.status = CardStatus.CONFIRMED
                    if body.choice_text:
                        card.meta["resolution"] = body.choice_text
    # mark ambiguous as confirmed if resolved
    for card in ast.cards:
        if card.status == CardStatus.AMBIGUOUS and body.choice_text:
            card.status = CardStatus.CONFIRMED
            card.meta["resolution"] = body.choice_text
            break
    ss.save_ast(db, row, ast)
    return {"ok": True, "cards": [c.model_dump() for c in ast.cards]}


@router.post("/sessions/{session_id}/related-work")
def related_work(session_id: str, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    settings = get_settings()
    ast = ss.load_ast(row)
    try:
        ast = run_related_work(ast, limit=settings.related_work_limit)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"Related work lỗi: {exc}") from exc
    ss.upsert_sources(db, session_id, [s.model_dump() for s in ast.sources])
    ss.save_ast(db, row, ast)
    ss.force_state(db, row, FsmState.RELATED_WORK)
    return {
        "status": ast.related_work_status,
        "sources": [s.model_dump() for s in ast.sources],
        "related_work": [e.model_dump() for e in ast.related_work],
        "fsm_state": row.fsm_state,
    }


@router.post("/sessions/{session_id}/related-work/manual")
def related_work_manual(session_id: str, body: ManualPaperBody, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    ast = add_manual_paper(ast, body.title, body.url, body.abstract)
    ss.upsert_sources(db, session_id, [s.model_dump() for s in ast.sources])
    ss.save_ast(db, row, ast)
    return {"sources": [s.model_dump() for s in ast.sources], "related_work": [e.model_dump() for e in ast.related_work]}


@router.post("/sessions/{session_id}/gap")
def gap(session_id: str, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    try:
        proposal = propose_gap(ast)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"LLM lỗi: {exc}") from exc
    ast.gap = proposal
    ss.save_ast(db, row, ast)
    return proposal.model_dump()


@router.post("/sessions/{session_id}/gap/choose")
def gap_choose(session_id: str, body: ChooseBody, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    label = body.other_text or body.choice
    if ast.gap:
        for opt in ast.gap.options:
            if opt.key == body.choice:
                label = body.other_text or f"{opt.label}: {opt.explanation}"
                break
    ast.chosen_gap_key = body.choice
    ast.chosen_gap_text = label
    ast.decision_history.append({"step": "gap", "choice_key": body.choice, "choice_text": label})
    ss.record_decision(db, session_id, "gap", [o.model_dump() for o in (ast.gap.options if ast.gap else [])], body.choice, label)
    ss.save_ast(db, row, ast)
    ss.force_state(db, row, FsmState.GAP_CHOSEN)
    return {"ok": True, "chosen_gap_text": label, "fsm_state": row.fsm_state}


@router.post("/sessions/{session_id}/claims")
def claims(session_id: str, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    try:
        ast = build_claims(ast)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"LLM lỗi: {exc}") from exc
    ss.save_ast(db, row, ast)
    ss.force_state(db, row, FsmState.CLAIMS_READY)
    return {
        "contributions": ast.contributions,
        "claim_cards": [c.model_dump() for c in ast.claim_cards],
        "fsm_state": row.fsm_state,
    }


@router.post("/sessions/{session_id}/claims/confirm")
def claims_confirm(session_id: str, body: ClaimsConfirmBody, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    if body.contributions is not None:
        ast.contributions = body.contributions
    if body.claim_cards is not None:
        from uuid import uuid4

        from app.domain.spec_ast import ClaimEvidenceCard

        ast.claim_cards = [
            ClaimEvidenceCard(
                id=c.get("id") or str(uuid4()),
                claim=c.get("claim", ""),
                baseline=c.get("baseline", ""),
                metric=c.get("metric", ""),
                evidence=c.get("evidence", ""),
                falsification=c.get("falsification", ""),
            )
            for c in body.claim_cards
        ]
    ss.record_decision(db, session_id, "claims", [], "confirm", "user confirmed claims")
    ss.save_ast(db, row, ast)
    return {"ok": True}


@router.post("/sessions/{session_id}/experiment")
def experiment(session_id: str, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    try:
        plan = plan_experiments(ast)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"LLM lỗi: {exc}") from exc
    ast.experiment = plan
    ss.save_ast(db, row, ast)
    ss.force_state(db, row, FsmState.EXPERIMENT_READY)
    return {**plan.model_dump(), "fsm_state": row.fsm_state}


@router.post("/sessions/{session_id}/feasibility")
def feasibility(session_id: str, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    est = estimate_feasibility(ast)
    ast.feasibility = est
    ss.save_ast(db, row, ast)
    ss.force_state(db, row, FsmState.FEASIBILITY_CHECKED)
    return {**est.model_dump(), "fsm_state": row.fsm_state}


@router.post("/sessions/{session_id}/feasibility/choose")
def feasibility_choose(session_id: str, body: FeasibilityChooseBody, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    if not ast.feasibility:
        raise HTTPException(400, "Chưa có feasibility")
    if body.choice != "accept":
        ast.feasibility = apply_scale_down(ast.feasibility, body.choice)
    ss.record_decision(db, session_id, "feasibility", [], body.choice, body.choice)
    ast.decision_history.append({"step": "feasibility", "choice_key": body.choice, "choice_text": body.choice})
    ss.save_ast(db, row, ast)
    return ast.feasibility.model_dump()


@router.post("/sessions/{session_id}/spec/assemble")
def assemble(session_id: str, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    md = assemble_markdown(ast)
    version = ss.snapshot_version(db, session_id, ast, md, label="draft")
    ss.force_state(db, row, FsmState.SPEC_DRAFT)
    return {
        "version_id": version.id,
        "version_no": version.version_no,
        "markdown": md,
        "fsm_state": row.fsm_state,
    }

@router.post("/sessions/{session_id}/judges/aggregate")
def judge_aggregate(session_id: str, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    agg = aggregate_findings(ast.judge_findings)
    ast.aggregate = agg
    ss.save_ast(db, row, ast)
    run = ss.get_latest_judge_run(db, session_id)
    if run:
        run.aggregate_json = json.dumps(agg, ensure_ascii=False)
        run.status = "completed"
        db.add(run)
    ss.force_state(db, row, FsmState.REVISION)
    return {**agg, "fsm_state": row.fsm_state, "revise_count": row.revise_count}

@router.post("/sessions/{session_id}/judges/{judge_type}")
def judge_one(session_id: str, judge_type: str, db: Session = Depends(get_db)):
    if judge_type not in JUDGE_TYPES:
        raise HTTPException(400, "judge_type không hợp lệ")
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    versions = ss.list_versions(db, session_id)
    if not versions:
        raise HTTPException(400, "Chưa assemble spec")
    version = versions[-1]
    run = ss.get_latest_judge_run(db, session_id)
    if not run or run.version_id != version.id or run.status == "completed":
        run = ss.create_judge_run(db, session_id, version.id, round_no=row.revise_count + 1)
    try:
        result = run_judge(ast, judge_type)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"Judge lỗi: {exc}") from exc
    ss.add_judge_findings(db, run.id, judge_type, result["findings"], result)
    # merge into working ast findings for this judge type (replace same judge)
    remaining = [f for f in ast.judge_findings if f.judge_type != judge_type]
    remaining.extend(findings_to_models(result["findings"]))
    ast.judge_findings = remaining
    if judge_type == "readiness":
        ast = apply_readiness(ast, result.get("readiness"))
    ss.save_ast(db, row, ast)
    ss.force_state(db, row, FsmState.JUDGING)
    return {"run_id": run.id, **result, "fsm_state": row.fsm_state}



@router.post("/sessions/{session_id}/revise")
def revise(session_id: str, body: ReviseBody, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    settings = get_settings()
    if body.choice == "finalize":
        return finalize(session_id, db)
    if row.revise_count >= settings.max_revise_rounds:
        raise HTTPException(400, f"Đã đạt max {settings.max_revise_rounds} vòng revise")
    ast = ss.load_ast(row)
    text = body.other_text or body.choice
    try:
        ast, meta = apply_revision(ast, body.choice, text)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"Revise lỗi: {exc}") from exc
    row.revise_count += 1
    ast.decision_history.append({"step": "revise", "choice_key": body.choice, "choice_text": text})
    ss.record_decision(db, session_id, "revise", [], body.choice, text)
    # clear previous findings for re-judge
    ast.judge_findings = []
    ast.aggregate = None
    md = assemble_markdown(ast)
    version = ss.snapshot_version(db, session_id, ast, md, label=f"revise-{row.revise_count}")
    ss.save_ast(db, row, ast)
    ss.force_state(db, row, FsmState.JUDGING)
    return {
        "version_id": version.id,
        "diff": meta["diff"],
        "diffs": meta["diff"],
        "summary": meta["summary"],
        "revise_count": row.revise_count,
        "markdown": md,
        "fsm_state": row.fsm_state,
    }


@router.post("/sessions/{session_id}/finalize")
def finalize(session_id: str, db: Session = Depends(get_db)):
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    md = assemble_markdown(ast)
    version = ss.snapshot_version(db, session_id, ast, md, label="final")
    ss.force_state(db, row, FsmState.FINAL)
    return {"version_id": version.id, "markdown": md, "fsm_state": row.fsm_state}


@router.get("/sessions/{session_id}/export")
def export_spec(session_id: str, format: str = Query("md"), db: Session = Depends(get_db)):
    row = _row(db, session_id)
    ast = ss.load_ast(row)
    if format == "json":
        return ast.model_dump()
    versions = ss.list_versions(db, session_id)
    if versions:
        return {"markdown": versions[-1].markdown or assemble_markdown(ast)}
    return {"markdown": assemble_markdown(ast)}


@router.get("/sessions/{session_id}/versions")
def versions(session_id: str, db: Session = Depends(get_db)):
    rows = ss.list_versions(db, session_id)
    return [
        {"id": v.id, "version_no": v.version_no, "label": v.label, "created_at": v.created_at.isoformat()}
        for v in rows
    ]


@router.get("/sessions/{session_id}/versions/{version_id}/diff")
def version_diff(session_id: str, version_id: str, db: Session = Depends(get_db)):
    rows = ss.list_versions(db, session_id)
    current = next((v for v in rows if v.id == version_id), None)
    if not current:
        raise HTTPException(404, "Version not found")
    prev = None
    for v in rows:
        if v.version_no == current.version_no - 1:
            prev = v
    from app.services.revision_service import _section_diff

    before = prev.markdown if prev else ""
    after = current.markdown
    return {"diff": _section_diff(before, after), "from": prev.id if prev else None, "to": current.id}


def _row(db: Session, session_id: str):
    """Fetch a session row or raise 404.  Returns 400 for malformed IDs."""
    import re

    if not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", session_id):
        raise HTTPException(400, "session_id không đúng định dạng UUID")
    try:
        return ss.get_session(db, session_id)
    except KeyError:
        raise HTTPException(404, "Session not found") from None
