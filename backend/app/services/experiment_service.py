from __future__ import annotations

from app.domain.spec_ast import ExperimentPlan, SpecAST
from app.integrations.groq_client import GroqClient, load_prompt


def plan_experiments(ast: SpecAST) -> ExperimentPlan:
    client = GroqClient()
    system = load_prompt("generators/experiment.md") or (
        "Thiết kế kế hoạch thí nghiệm 4 khối. Trả JSON: baseline_compare, quality_eval, ablation, "
        "generalization (string markdown ngắn), fairness_constraints (list)."
    )
    mock = {
        "baseline_compare": (
            "So sánh: Human-written prompt; Self-refine; Random mutation; OPRO-style; Phương pháp đề xuất. "
            "Cùng model, dataset, token budget, số lần gọi LLM."
        ),
        "quality_eval": (
            "Metric: claim precision/recall; evidence support rate; unsupported claim rate; "
            "contradiction rate; token cost; latency; JSON validity."
        ),
        "ablation": (
            "Lần lượt bỏ: claim decomposition; evidence verifier; textual feedback; "
            "candidate diversity; user confirmation."
        ),
        "generalization": (
            "Đánh giá prompt cuối trên held-out set, loại paper khác, domain khác nếu đủ budget."
        ),
        "fairness_constraints": [
            "Cùng model",
            "Cùng dataset split",
            "Cùng token/API budget",
            "Cùng số vòng tối ưu tối đa",
        ],
    }
    data = client.chat_json(
        system,
        f"Claims: {[c.model_dump() for c in ast.claim_cards]}\nContributions: {ast.contributions}",
        mock_payload=mock,
    )
    return ExperimentPlan(
        baseline_compare=data.get("baseline_compare", ""),
        quality_eval=data.get("quality_eval", ""),
        ablation=data.get("ablation", ""),
        generalization=data.get("generalization", ""),
        fairness_constraints=list(data.get("fairness_constraints") or []),
    )
