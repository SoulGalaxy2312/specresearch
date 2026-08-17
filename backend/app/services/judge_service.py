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
    md = assemble_markdown(ast)
    mock = _mock_judge(judge_type)
    data = client.chat_json(system, md, temperature=0.1, mock_payload=mock)
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