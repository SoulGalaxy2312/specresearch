from __future__ import annotations

from app.domain.spec_ast import SpecAST


def assemble_markdown(ast: SpecAST) -> str:
    lines: list[str] = []
    lines.append("# Research Specification")
    lines.append("")
    lines.append("## Problem statement")
    lines.append(ast.interpretation or ast.raw_idea or "_(chưa có)_")
    lines.append("")
    lines.append("## Research questions & cards")
    for c in ast.cards:
        lines.append(f"- **{c.card_type.value}** [{c.status.value}]: {c.content}")
    lines.append("")
    lines.append("## Related-work matrix")
    if ast.related_work_status == "DEGRADED":
        lines.append("> Cảnh báo: related work ở chế độ DEGRADED (retrieval lỗi hoặc thiếu dữ liệu).")
    src = {s.id: s for s in ast.sources}
    lines.append("| Nghiên cứu | Đã làm gì? | Feedback | Điểm mở | Support |")
    lines.append("|---|---|---|---|---|")
    for e in ast.related_work:
        s = src.get(e.source_id)
        title = s.title if s else e.source_id
        year = f" ({s.year})" if s and s.year else ""
        lines.append(
            f"| {title}{year} | {e.did_what} | {e.feedback_used} | {e.open_point} | {e.support_label} |"
        )
    lines.append("")
    lines.append("## Research gap")
    if ast.gap:
        lines.append(ast.gap.statement)
        lines.append("")
        lines.append(f"- Prior work: {ast.gap.prior_work}")
        lines.append(f"- Limitation: {ast.gap.limitation}")
        lines.append(f"- Why it matters: {ast.gap.why_matters}")
        lines.append(f"- How to test: {ast.gap.how_to_test}")
    if ast.chosen_gap_text:
        lines.append(f"\n**Hướng đã chọn:** {ast.chosen_gap_text}")
    lines.append("")
    lines.append("## Expected contributions")
    for c in ast.contributions:
        lines.append(f"- {c}")
    lines.append("")
    lines.append("## Claim–evidence matrix")
    for card in ast.claim_cards:
        lines.append(f"### Claim: {card.claim}")
        lines.append(f"- Baseline: {card.baseline}")
        lines.append(f"- Metric: {card.metric}")
        lines.append(f"- Evidence: {card.evidence}")
        lines.append(f"- Falsification: {card.falsification}")
        lines.append("")
    lines.append("## Experimental protocol")
    if ast.experiment:
        lines.append("### So sánh baseline")
        lines.append(ast.experiment.baseline_compare)
        lines.append("### Đánh giá chất lượng")
        lines.append(ast.experiment.quality_eval)
        lines.append("### Ablation")
        lines.append(ast.experiment.ablation)
        lines.append("### Generalization")
        lines.append(ast.experiment.generalization)
        if ast.experiment.fairness_constraints:
            lines.append("### Fairness constraints")
            for f in ast.experiment.fairness_constraints:
                lines.append(f"- {f}")
    lines.append("")
    lines.append("## Compute budget")
    if ast.feasibility:
        f = ast.feasibility
        lines.append(f"- Model: {f.model}")
        lines.append(f"- VRAM: {f.vram_gb} GB")
        lines.append(f"- Candidates/round: {f.candidates_per_round}")
        lines.append(f"- Rounds: {f.rounds}")
        lines.append(f"- Dev/Val samples: {f.samples_dev}/{f.samples_val}")
        lines.append(f"- Estimated tokens: {f.estimated_tokens}")
        lines.append(f"- Estimated hours: {f.estimated_hours}")
        lines.append(f"- Over budget: {f.over_budget}")
        lines.append(f"- Narrative: {f.narrative}")
        for a in f.assumptions:
            lines.append(f"  - Assumption: {a}")
    lines.append("")
    lines.append("## Risks and limitations")
    for r in ast.risks or ["Metadata-only related work có thể làm evidence check yếu.", "Một LLM cho mọi Judge có thể correlated bias."]:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("## Open issues")
    for o in ast.open_issues:
        lines.append(f"- {o}")
    if not ast.open_issues:
        for c in ast.cards:
            if c.status.value in {"AMBIGUOUS", "MISSING", "UNSUPPORTED"}:
                lines.append(f"- [{c.status.value}] {c.card_type.value}: {c.content}")
    lines.append("")
    lines.append("## Decision history")
    for d in ast.decision_history:
        lines.append(f"- {d.get('step')}: {d.get('choice_key')} — {d.get('choice_text')}")
    if ast.readiness:
        lines.append("")
        lines.append("## Conference readiness (Judge)")
        r = ast.readiness
        lines.append(
            f"- Originality: {r.originality}; Significance: {r.significance}; "
            f"Soundness: {r.soundness}; Clarity: {r.clarity}; Reproducibility: {r.reproducibility}"
        )
        lines.append(f"- Overall: {r.overall}")
    if ast.aggregate:
        lines.append("")
        lines.append("## Judge aggregate")
        lines.append(f"- Major count: {ast.aggregate.get('major_count')}")
        lines.append(f"- Consensus items: {len(ast.aggregate.get('consensus') or [])}")
        lines.append(f"- Disagreement items: {len(ast.aggregate.get('disagreement') or [])}")
    lines.append("")
    return "\n".join(lines)
