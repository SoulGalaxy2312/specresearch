from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import KnowledgeItemRow


SEED_KNOWLEDGE: list[dict[str, Any]] = [
    {
        "id": "paper-opro-2023",
        "category": "research",
        "title": "OPRO - Large Language Models as Optimizers",
        "summary": (
            "OPRO dùng LLM như một optimizer: mô tả bài toán bằng ngôn ngữ tự nhiên, "
            "đưa các lời giải/prompt trước đó cùng điểm số vào context, rồi để LLM đề xuất "
            "candidate mới. Đây là baseline tốt cho bài toán tối ưu prompt nhiều vòng."
        ),
        "source_url": "https://arxiv.org/abs/2309.03409",
        "tags": ["prompt-optimization", "baseline", "llm-as-optimizer"],
        "payload": {
            "year": 2023,
            "use_in_project": "Dùng làm baseline OPRO-style trong experiment plan.",
            "risk": "Feedback dạng scalar có thể không chỉ ra lỗi claim-evidence cụ thể.",
        },
    },
    {
        "id": "paper-promptbreeder-2023",
        "category": "research",
        "title": "PromptBreeder - Self-Referential Prompt Evolution",
        "summary": (
            "PromptBreeder tiến hóa quần thể task prompts và mutation prompts qua nhiều thế hệ. "
            "Nó phù hợp để so sánh với hướng search/evolution nhưng có thể tốn nhiều lượt gọi model."
        ),
        "source_url": "https://arxiv.org/abs/2309.16797",
        "tags": ["prompt-evolution", "baseline", "mutation"],
        "payload": {
            "year": 2023,
            "use_in_project": "Dùng làm baseline evolutionary prompt optimization.",
            "risk": "Chi phí inference cao nếu population/generation lớn.",
        },
    },
    {
        "id": "paper-dspy-2023",
        "category": "research",
        "title": "DSPy - Self-Improving LM Pipelines",
        "summary": (
            "DSPy biểu diễn pipeline LM bằng module khai báo và dùng compiler để tối ưu theo metric. "
            "Dữ liệu này giúp hệ thống phân biệt tối ưu prompt đơn lẻ với tối ưu cả pipeline."
        ),
        "source_url": "https://arxiv.org/abs/2310.03714",
        "tags": ["pipeline", "compiler", "baseline"],
        "payload": {
            "year": 2023,
            "use_in_project": "Dùng làm related work cho pipeline optimization.",
            "risk": "So sánh cần cùng task, metric và budget để công bằng.",
        },
    },
    {
        "id": "paper-textgrad-2024",
        "category": "research",
        "title": "TextGrad - Textual Feedback Optimization",
        "summary": (
            "TextGrad dùng phản hồi văn bản như gradient để cải thiện biến trong hệ thống AI phức hợp. "
            "Nó liên quan trực tiếp đến ý tưởng dùng feedback chi tiết thay vì chỉ dùng điểm tổng."
        ),
        "source_url": "https://arxiv.org/abs/2406.07496",
        "tags": ["textual-feedback", "optimization", "compound-ai"],
        "payload": {
            "year": 2024,
            "use_in_project": "Dùng làm baseline textual feedback hoặc related work.",
            "risk": "LLM feedback có thể bias, cần verifier hoặc hidden set.",
        },
    },
    {
        "id": "method-claim-evidence-verifier",
        "category": "backend-method",
        "title": "Claim-Evidence Verifier",
        "summary": (
            "Backend cần xem mỗi claim như một đơn vị kiểm chứng riêng: claim, baseline, metric, evidence "
            "và falsification. Những claim không được source hỗ trợ phải được đánh dấu PARTIAL, "
            "UNSUPPORTED hoặc UNVERIFIABLE thay vì viết quá chắc chắn."
        ),
        "source_url": "docs/architecture.md",
        "tags": ["verifier", "evidence", "backend"],
        "payload": {
            "required_fields": ["claim", "baseline", "metric", "evidence", "falsification"],
            "supports_assignment_requirement": "Phát hiện citation/evidence yếu và claim bị phóng đại.",
        },
    },
    {
        "id": "method-multi-judge-isolation",
        "category": "backend-method",
        "title": "Multi-Judge Isolation",
        "summary": (
            "Các Judge phải đánh giá độc lập trước khi aggregate. Mỗi Judge chỉ nhận spec markdown "
            "và prompt vai trò riêng, giúp giảm bias do đọc nhận xét của Judge khác quá sớm."
        ),
        "source_url": "docs/architecture.md",
        "tags": ["judge", "bias-reduction", "backend"],
        "payload": {
            "judges": ["gap", "contribution", "experiment", "evidence", "readiness"],
            "supports_assignment_requirement": "Chạy nhiều Judge độc lập và tổng hợp đồng thuận/bất đồng thuận.",
        },
    },
    {
        "id": "design-academic-workbench",
        "category": "design-system",
        "title": "Academic Workbench Design System",
        "summary": (
            "UI giữ identity học thuật: nền sáng ấm, forest green làm accent, typography serif cho nội dung "
            "đọc dài và sans-serif cho controls. Mục tiêu là dense, rõ thứ bậc, không biến thành landing page."
        ),
        "source_url": "docs/ui-guide.md",
        "tags": ["ui", "design-system", "academic"],
        "payload": {
            "accent": "forest green",
            "layout": "sidebar stepper + document panel + dashboard surfaces",
            "avoid": ["generic SaaS hero", "excessive decoration", "unrelated gradients"],
        },
    },
    {
        "id": "design-pipeline-observability",
        "category": "design-system",
        "title": "Pipeline Observability",
        "summary": (
            "UI cần thể hiện pipeline flow, trạng thái từng bước, phiên làm việc hiện tại, lịch sử quyết định "
            "và dữ liệu nền backend để người dùng hiểu hệ thống đang làm gì."
        ),
        "source_url": "docs/ui-guide.md",
        "tags": ["pipeline", "sessions", "history"],
        "payload": {
            "surfaces": ["Pipeline", "Sessions", "Knowledge", "Chat"],
            "supports_assignment_requirement": "Thể hiện flow, session và lịch sử rõ ràng hơn.",
        },
    },
]


def seed_initial_data(db: Session) -> None:
    existing = {row.id for row in db.query(KnowledgeItemRow.id).all()}
    for item in SEED_KNOWLEDGE:
        if item["id"] in existing:
            continue
        db.add(
            KnowledgeItemRow(
                id=item["id"],
                category=item["category"],
                title=item["title"],
                summary=item["summary"],
                source_url=item["source_url"],
                tags_json=json.dumps(item["tags"], ensure_ascii=False),
                payload_json=json.dumps(item["payload"], ensure_ascii=False),
            )
        )
    db.flush()
