from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.domain.spec_ast import JudgeFinding


def aggregate_findings(findings: list[JudgeFinding]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[JudgeFinding]] = defaultdict(list)
    for f in findings:
        key = (f.target, f.severity.upper())
        groups[key].append(f)

    consensus = []
    disagreement = []
    for (target, severity), items in groups.items():
        judges = {i.judge_type for i in items if i.judge_type}
        entry = {
            "target": target,
            "severity": severity,
            "count": len(items),
            "judges": sorted(j for j in judges if j),
            "issues": [i.issue for i in items],
            "suggestions": [i.suggestion for i in items],
        }
        if len(judges) >= 2 or len(items) >= 2:
            consensus.append(entry)
        else:
            disagreement.append(entry)

    major_count = sum(1 for f in findings if f.severity.upper() == "MAJOR")
    return {
        "consensus": consensus,
        "disagreement": disagreement,
        "major_count": major_count,
        "can_finalize_early": major_count == 0,
        "revision_options": _revision_options(findings),
    }


def _revision_options(findings: list[JudgeFinding]) -> list[dict[str, str]]:
    majors = [f for f in findings if f.severity.upper() == "MAJOR"]
    if not majors:
        return [
            {
                "key": "finalize",
                "label": "Xác nhận bản cuối",
                "explanation": "Không còn MAJOR — có thể finalize.",
                "example": "",
            },
            {
                "key": "minor_polish",
                "label": "Chỉnh nhỏ theo MINOR",
                "explanation": "Sửa làm rõ trước khi xuất bản.",
                "example": "",
            },
            {"key": "E", "label": "Other", "explanation": "Nhập hướng sửa riêng.", "example": ""},
        ]
    sample = majors[0]
    return [
        {
            "key": "narrow_claim",
            "label": "Thu hẹp claim",
            "explanation": sample.suggestion or "Thu hẹp phạm vi khẳng định cho khớp thí nghiệm.",
            "example": "Chỉ khẳng định trên domain đã thử.",
        },
        {
            "key": "expand_experiment",
            "label": "Mở rộng thí nghiệm",
            "explanation": "Bổ sung protocol để hỗ trợ claim rộng hơn.",
            "example": "Thêm domain hoặc held-out set.",
        },
        {
            "key": "to_research_question",
            "label": "Chuyển thành research question",
            "explanation": "Không khẳng định trước khi có bằng chứng.",
            "example": "",
        },
        {"key": "E", "label": "Other", "explanation": "Nhập hướng riêng.", "example": ""},
    ]
