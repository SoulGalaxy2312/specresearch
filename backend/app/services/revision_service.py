from __future__ import annotations

from typing import Any

from app.domain.spec_ast import SpecAST
from app.integrations.groq_client import GroqClient, load_prompt
from app.services.spec_assemble_service import assemble_markdown


def apply_revision(ast: SpecAST, choice_key: str, choice_text: str) -> tuple[SpecAST, dict[str, Any]]:
    before = assemble_markdown(ast)
    client = GroqClient()
    system = load_prompt("generators/revise.md") or (
        "Bạn sửa research spec theo quyết định người dùng. Trả JSON: "
        "{\"interpretation\":optional,\"contributions\":optional,\"claim_cards\":optional list of "
        "{claim,baseline,metric,evidence,falsification},\"experiment\":optional,"
        "\"open_issues\":optional,\"risks\":optional,\"summary_of_changes\":\"...\"}."
        " Chỉ trả các field cần sửa."
    )

    mock = _mock_revision(ast, choice_key, choice_text)
    data = client.chat_json(
        system,
        f"Choice: {choice_key}\nText: {choice_text}\nAST:{ast.model_dump_json()[:12000]}",
        temperature=0.2,
        mock_payload=mock,
    )

    if data.get("interpretation"):
        ast.interpretation = data["interpretation"]
    if data.get("contributions"):
        ast.contributions = list(data["contributions"])
    if data.get("claim_cards"):
        from uuid import uuid4

        from app.domain.spec_ast import ClaimEvidenceCard

        ast.claim_cards = [
            ClaimEvidenceCard(id=str(uuid4()), **{k: c.get(k, "") for k in ("claim", "baseline", "metric", "evidence", "falsification")})
            for c in data["claim_cards"]
        ]
    if data.get("experiment"):
        from app.domain.spec_ast import ExperimentPlan

        e = data["experiment"]
        if isinstance(e, dict):
            ast.experiment = ExperimentPlan(
                baseline_compare=e.get("baseline_compare", ast.experiment.baseline_compare if ast.experiment else ""),
                quality_eval=e.get("quality_eval", ast.experiment.quality_eval if ast.experiment else ""),
                ablation=e.get("ablation", ast.experiment.ablation if ast.experiment else ""),
                generalization=e.get("generalization", ast.experiment.generalization if ast.experiment else ""),
                fairness_constraints=e.get("fairness_constraints")
                or (ast.experiment.fairness_constraints if ast.experiment else []),
            )
    if data.get("open_issues") is not None:
        ast.open_issues = list(data["open_issues"])
    if data.get("risks") is not None:
        ast.risks = list(data["risks"])

    # deterministic fallbacks for common choices
    if choice_key == "narrow_claim" and ast.claim_cards:
        for card in ast.claim_cards:
            if "nhiều domain" in card.claim.lower() or "tổng quát" in card.claim.lower() or True:
                card.claim = card.claim.rstrip(".") + " (giới hạn trên domain paper khoa học đã đánh giá)."
                break
    if choice_key == "to_research_question" and ast.claim_cards:
        claim = ast.claim_cards[0].claim
        ast.open_issues.append(f"Chuyển claim thành RQ: {claim}")
        ast.claim_cards[0].claim = "RQ (chưa khẳng định): " + claim
    if choice_key == "expand_experiment" and ast.experiment:
        ast.experiment.generalization += (
            "\n\nBổ sung: đánh giá thêm một domain phụ (ví dụ tài chính hoặc tin tức) nếu budget cho phép."
        )

    after = assemble_markdown(ast)
    diff = _section_diff(before, after)
    return ast, {"summary": data.get("summary_of_changes") or choice_text or choice_key, "diff": diff}


def _mock_revision(ast: SpecAST, choice_key: str, choice_text: str) -> dict[str, Any]:
    return {
        "summary_of_changes": f"Áp dụng lựa chọn {choice_key}: {choice_text}",
        "open_issues": ast.open_issues
        + ([f"User other: {choice_text}"] if choice_key in {"E", "other"} and choice_text else []),
    }


def _section_diff(before: str, after: str) -> list[dict[str, str]]:
    b_sections = _split_sections(before)
    a_sections = _split_sections(after)
    keys = sorted(set(b_sections) | set(a_sections))
    diffs = []
    for k in keys:
        bv = b_sections.get(k, "")
        av = a_sections.get(k, "")
        if bv != av:
            diffs.append({"section": k, "before": bv[:2000], "after": av[:2000]})
    return diffs


def _split_sections(md: str) -> dict[str, str]:
    parts: dict[str, str] = {}
    current = "preamble"
    buf: list[str] = []
    for line in md.splitlines():
        if line.startswith("## "):
            parts[current] = "\n".join(buf).strip()
            current = line[3:].strip()
            buf = []
        else:
            buf.append(line)
    parts[current] = "\n".join(buf).strip()
    return parts