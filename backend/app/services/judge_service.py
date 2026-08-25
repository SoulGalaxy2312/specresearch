from __future__ import annotations

from typing import Any

from app.domain.spec_ast import JudgeFinding, ReadinessScores, SpecAST
from app.integrations.groq_client import GroqClient, load_prompt
from app.services.spec_assemble_service import assemble_markdown

JUDGE_TYPES = ("gap", "contribution", "experiment", "evidence", "readiness")


def run_judge(ast: SpecAST, judge_type: str) -> dict[str, Any]:
    if judge_type not in JUDGE_TYPES:
        raise ValueError(f"Unknown judge type: {judge_type}")
    client = GroqClient()
    prompt_file = f"judges/{judge_type}.md"
    system = load_prompt(prompt_file) or _default_judge_system(judge_type)

    user = build_judge_context(ast, judge_type)
    print(
        f"[JUDGE] type={judge_type}, "
        f"system_chars={len(system)}, "
        f"user_chars={len(user)}"
    )

    mock = _mock_judge(judge_type)
    data = client.chat_json(system, user, temperature=0.1, mock_payload=mock)
    findings = []
    for f in data.get("findings") or []:
        findings.append(
            {
                "target": f.get("target", "overall"),
                "target_id": f.get("target_id"),
                "issue": f.get("issue", ""),
                "reason": f.get("reason", ""),
                "severity": f.get("severity", "MINOR"),
                "suggestion": f.get("suggestion", ""),
                "judge_type": judge_type,
            }
        )
    readiness = data.get("readiness")
    return {"findings": findings, "readiness": readiness, "judge_type": judge_type}


def findings_to_models(raw_findings: list[dict[str, Any]]) -> list[JudgeFinding]:
    return [JudgeFinding.model_validate(f) for f in raw_findings]


def apply_readiness(ast: SpecAST, readiness: dict[str, Any] | None) -> SpecAST:
    if readiness:
        ast.readiness = ReadinessScores.model_validate(readiness)
    return ast


def _default_judge_system(judge_type: str) -> str:
    return (
        f"Bạn là Judge độc lập loại '{judge_type}'. Đánh giá research spec bằng tiếng Việt. "
        "Không được giả định ý kiến judge khác. Trả JSON: "
        "{\"findings\":[{\"target\":\"claim|gap|experiment|citation|overall\",\"target_id\":null,"
        "\"issue\":\"...\",\"reason\":\"...\",\"severity\":\"MAJOR|MINOR\",\"suggestion\":\"...\"}],"
        "\"readiness\":null hoặc object cho readiness judge}."
    )


def _mock_judge(judge_type: str) -> dict[str, Any]:
    base = {
        "gap": {
            "findings": [
                {
                    "target": "gap",
                    "target_id": None,
                    "issue": "Gap cần gắn rõ hơn với limitation của related work đã liệt kê.",
                    "reason": "Một số dòng related work chỉ mô tả chung.",
                    "severity": "MINOR",
                    "suggestion": "Trích limitation cụ thể từ 2–3 paper trong matrix.",
                }
            ],
            "readiness": None,
        },
        "contribution": {
            "findings": [
                {
                    "target": "claim",
                    "target_id": None,
                    "issue": "Claim về khả năng tổng quát có thể đang rộng hơn thí nghiệm.",
                    "reason": "Protocol mới nêu generalization nhưng chưa bắt buộc multi-domain.",
                    "severity": "MAJOR",
                    "suggestion": "Thu hẹp claim về domain paper khoa học hoặc bổ sung domain.",
                }
            ],
            "readiness": None,
        },
        "experiment": {
            "findings": [
                {
                    "target": "experiment",
                    "target_id": None,
                    "issue": "Cần nêu rõ số seed và tiêu chí chọn winner rõ hơn.",
                    "reason": "Fairness constraints có nhưng thiếu chi tiết thống kê.",
                    "severity": "MINOR",
                    "suggestion": "Thêm số lần lặp và khoảng tin cậy nếu khả thi.",
                }
            ],
            "readiness": None,
        },
        "evidence": {
            "findings": [
                {
                    "target": "citation",
                    "target_id": None,
                    "issue": "Một số nhận định related work ở mức PARTIAL/UNVERIFIABLE.",
                    "reason": "Chỉ có abstract metadata.",
                    "severity": "MINOR",
                    "suggestion": "Đánh dấu UNSUPPORTED rõ trên UI và tránh overclaim từ abstract.",
                }
            ],
            "readiness": None,
        },
        "readiness": {
            "findings": [
                {
                    "target": "overall",
                    "target_id": None,
                    "issue": "Spec đủ để tiếp tục nghiên cứu sau khi thu hẹp claim.",
                    "reason": "Có gap, claim-evidence, protocol và budget.",
                    "severity": "MINOR",
                    "suggestion": "Finalize sau khi xử lý MAJOR từ Contribution Judge.",
                }
            ],
            "readiness": {
                "originality": "Acceptable",
                "significance": "Acceptable",
                "soundness": "Acceptable",
                "clarity": "Strong",
                "reproducibility": "Acceptable",
                "overall": "NeedsWork",
            },
        },
    }
    return base[judge_type]

def build_judge_context(ast: SpecAST, judge_type: str) -> str:
    def cards(*types: str) -> list[str]:
        wanted = set(types)
        return [
            f"- **{c.card_type.value}** [{c.status.value}]: {c.content}"
            for c in ast.cards
            if c.card_type.value in wanted
        ]

    def claim_evidence_matrix() -> list[str]:
        lines: list[str] = []

        for card in ast.claim_cards:
            lines.extend([
                f"### Claim: {card.claim}",
                f"- Baseline: {card.baseline}",
                f"- Metric: {card.metric}",
                f"- Evidence: {card.evidence}",
                f"- Falsification: {card.falsification}",
                "",
            ])

        return lines

    def related_work(include_title: bool = True) -> list[str]:
        lines: list[str] = []

        source_by_id = {s.id: s for s in ast.sources}

        for e in ast.related_work:
            source = source_by_id.get(e.source_id)

            if include_title:
                title = source.title if source else e.source_id
                year = (
                    f" ({source.year})"
                    if source and source.year
                    else ""
                )
                lines.append(f"### {title}{year}")

            lines.append(f"- Did what: {e.did_what}")
            lines.append(f"- Feedback used: {e.feedback_used}")
            lines.append(f"- Open point: {e.open_point}")
            lines.append(f"- Support: {e.support_label}")
            lines.append("")

        return lines

    # ============================================================
    # CONTRIBUTION
    # ============================================================

    if judge_type == "contribution":
        lines = [
            "# Contribution Judge Context",
            "",
            "## Problem / Research Question / Gap / Contribution / Claim",
        ]

        lines.extend(
            cards(
                "Problem",
                "ResearchQuestion",
                "Gap",
                "Contribution",
                "Claim",
            )
        )

        lines.extend([
            "",
            "## Expected Contributions",
        ])

        for contribution in ast.contributions:
            lines.append(f"- {contribution}")

        lines.extend([
            "",
            "## Claim–Evidence Matrix",
        ])

        lines.extend(claim_evidence_matrix())

        lines.extend([
            "",
            "## Related Work",
        ])

        lines.extend(
            related_work(include_title=False)
        )

        return "\n".join(lines)

    # ============================================================
    # EVIDENCE
    # ============================================================

    if judge_type == "evidence":
        lines = [
            "# Evidence Judge Context",
            "",
            "## Claims",
        ]

        lines.extend(cards("Claim"))

        lines.extend([
            "",
            "## Claim–Evidence Matrix",
        ])

        lines.extend(claim_evidence_matrix())

        lines.extend([
            "",
            "## Related Work / Citations",
        ])

        lines.extend(
            related_work(include_title=True)
        )

        return "\n".join(lines)

    # ============================================================
    # EXPERIMENT
    # ============================================================

    if judge_type == "experiment":
        lines = [
            "# Experiment Judge Context",
            "",
            "## Research Question / Gap / Contribution / Claim",
        ]

        lines.extend(
            cards(
                "ResearchQuestion",
                "Gap",
                "Contribution",
                "Claim",
            )
        )

        lines.extend([
            "",
            "## Claim–Evidence Matrix",
        ])

        lines.extend(claim_evidence_matrix())

        if ast.experiment:
            exp = ast.experiment

            lines.extend([
                "",
                "## Experimental Protocol",
                "",
                "### Baseline",
                exp.baseline_compare or "_(chưa có)_",
                "",
                "### Quality Evaluation",
                exp.quality_eval or "_(chưa có)_",
                "",
                "### Ablation",
                exp.ablation or "_(chưa có)_",
                "",
                "### Generalization",
                exp.generalization or "_(chưa có)_",
            ])

            if exp.fairness_constraints:
                lines.extend([
                    "",
                    "### Fairness Constraints",
                ])

                for item in exp.fairness_constraints:
                    lines.append(f"- {item}")

        else:
            lines.extend([
                "",
                "## Experimental Protocol",
                "_(chưa có)_",
            ])

        return "\n".join(lines)

    # ============================================================
    # GAP
    # ============================================================

    if judge_type == "gap":
        lines = [
            "# Research Gap Judge Context",
            "",
            "## Problem / Research Question / Gap",
        ]

        lines.extend(
            cards(
                "Problem",
                "ResearchQuestion",
                "Gap",
            )
        )

        if ast.gap:
            lines.extend([
                "",
                "## Structured Research Gap",
                "",
                f"- Statement: {ast.gap.statement}",
                f"- Prior work: {ast.gap.prior_work}",
                f"- Limitation: {ast.gap.limitation}",
                f"- Why it matters: {ast.gap.why_matters}",
                f"- How to test: {ast.gap.how_to_test}",
            ])

        if ast.chosen_gap_text:
            lines.extend([
                "",
                "## Chosen Gap",
                ast.chosen_gap_text,
            ])

        lines.extend([
            "",
            "## Related Work",
        ])

        lines.extend(
            related_work(include_title=True)
        )

        return "\n".join(lines)

    # ============================================================
    # READINESS
    # ============================================================

    if judge_type == "readiness":
        lines = [
            "# Conference Readiness Judge Context",
            "",
            "## Research Specification",
            "",
            "### Problem / Research Question / Gap / Contribution / Claim",
        ]

        lines.extend(
            cards(
                "Problem",
                "ResearchQuestion",
                "Gap",
                "Contribution",
                "Claim",
                "Evidence",
                "Constraint",
                "OpenQuestion",
            )
        )

        lines.extend([
            "",
            "## Expected Contributions",
        ])

        for contribution in ast.contributions:
            lines.append(f"- {contribution}")

        lines.extend([
            "",
            "## Claim–Evidence Matrix",
        ])

        lines.extend(claim_evidence_matrix())

        # ----------------------------
        # Related Work
        # ----------------------------

        lines.extend([
            "",
            "## Related Work",
        ])

        lines.extend(
            related_work(include_title=False)
        )

        # ----------------------------
        # Experiment
        # ----------------------------

        if ast.experiment:
            exp = ast.experiment

            lines.extend([
                "",
                "## Experimental Protocol",
                "",
                "### Baseline",
                exp.baseline_compare or "_(chưa có)_",
                "",
                "### Quality Evaluation",
                exp.quality_eval or "_(chưa có)_",
                "",
                "### Ablation",
                exp.ablation or "_(chưa có)_",
                "",
                "### Generalization",
                exp.generalization or "_(chưa có)_",
            ])

            if exp.fairness_constraints:
                lines.extend([
                    "",
                    "### Fairness Constraints",
                ])

                for item in exp.fairness_constraints:
                    lines.append(f"- {item}")

        # ----------------------------
        # Feasibility
        # ----------------------------

        if ast.feasibility:
            f = ast.feasibility

            lines.extend([
                "",
                "## Compute / Feasibility",
                f"- Model: {f.model}",
                f"- VRAM: {f.vram_gb} GB",
                f"- Candidates/round: {f.candidates_per_round}",
                f"- Rounds: {f.rounds}",
                f"- Dev/Val samples: {f.samples_dev}/{f.samples_val}",
                f"- Estimated tokens: {f.estimated_tokens}",
                f"- Estimated hours: {f.estimated_hours}",
                f"- Over budget: {f.over_budget}",
                f"- Narrative: {f.narrative}",
            ])

            for assumption in f.assumptions:
                lines.append(f"- Assumption: {assumption}")

        # ----------------------------
        # Risks
        # ----------------------------

        lines.extend([
            "",
            "## Risks and Limitations",
        ])

        for risk in ast.risks or []:
            lines.append(f"- {risk}")

        # ----------------------------
        # Open Issues
        # ----------------------------

        lines.extend([
            "",
            "## Open Issues",
        ])

        if ast.open_issues:
            for issue in ast.open_issues:
                lines.append(f"- {issue}")
        else:
            for c in ast.cards:
                if c.status.value in {
                    "AMBIGUOUS",
                    "MISSING",
                    "UNSUPPORTED",
                }:
                    lines.append(
                        f"- [{c.status.value}] "
                        f"{c.card_type.value}: {c.content}"
                    )

        return "\n".join(lines)

    # ============================================================
    # FALLBACK
    # ============================================================

    return assemble_markdown(ast)