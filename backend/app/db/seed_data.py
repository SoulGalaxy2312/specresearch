from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    ChatMessageRow,
    DecisionRow,
    KnowledgeItemRow,
    SessionRow,
    SourceRow,
    SpecVersionRow,
)


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
        "id": "paper-self-refine-2023",
        "category": "research",
        "title": "Self-Refine - Iterative Refinement with Self-Feedback",
        "summary": (
            "Self-Refine tạo output ban đầu, sinh feedback cho chính output đó, rồi refine lặp lại "
            "mà không cần training thêm. Đây là baseline tự sửa nhiều vòng đơn giản cho các bước revise."
        ),
        "source_url": "https://arxiv.org/abs/2303.17651",
        "tags": ["self-feedback", "iterative-refinement", "baseline"],
        "payload": {
            "year": 2023,
            "use_in_project": "Dùng làm baseline cho vòng feedback-refine.",
            "risk": "Cùng một model tự phản biện có thể bỏ sót lỗi của chính nó.",
        },
    },
    {
        "id": "paper-reflexion-2023",
        "category": "research",
        "title": "Reflexion - Verbal Reinforcement Learning",
        "summary": (
            "Reflexion lưu phản hồi bằng ngôn ngữ vào episodic memory để agent ra quyết định tốt hơn ở lượt sau. "
            "Ý tưởng này hỗ trợ thiết kế chat/session history cho SpecResearch."
        ),
        "source_url": "https://arxiv.org/abs/2303.11366",
        "tags": ["memory", "agent", "verbal-feedback"],
        "payload": {
            "year": 2023,
            "use_in_project": "Gợi ý dùng chat history và decision history như memory theo session.",
            "risk": "Memory sai hoặc quá dài có thể làm model lệch hướng.",
        },
    },
    {
        "id": "paper-ragas-2023",
        "category": "research",
        "title": "RAGAS - Automated Evaluation of RAG",
        "summary": (
            "RAGAS đánh giá RAG theo nhiều chiều như retrieval quality, faithfulness và answer quality "
            "mà không luôn cần ground-truth annotation."
        ),
        "source_url": "https://arxiv.org/abs/2309.15217",
        "tags": ["rag", "evaluation", "faithfulness"],
        "payload": {
            "year": 2023,
            "use_in_project": "Dùng để thiết kế metric citation/evidence support.",
            "risk": "Metric tự động vẫn cần kiểm tra thủ công trên use case nhỏ.",
        },
    },
    {
        "id": "paper-crag-2024",
        "category": "research",
        "title": "CRAG - Corrective Retrieval Augmented Generation",
        "summary": (
            "CRAG thêm retrieval evaluator để đánh giá chất lượng tài liệu truy hồi và chọn hành động sửa phù hợp. "
            "Nó hữu ích cho ý tưởng cảnh báo source yếu hoặc quá gián tiếp."
        ),
        "source_url": "https://arxiv.org/abs/2401.15884",
        "tags": ["retrieval", "evaluator", "correction"],
        "payload": {
            "year": 2024,
            "use_in_project": "Dùng làm cảm hứng cho source confidence và degraded retrieval path.",
            "risk": "Cần tránh đánh đồng retrieval confidence với evidence support.",
        },
    },
    {
        "id": "baseline-b0-single-shot",
        "category": "evaluation",
        "title": "Baseline B0 - Single-shot Spec",
        "summary": (
            "B0 dùng một prompt duy nhất để viết research spec, không có wizard, không có grounding và không có Judge. "
            "Baseline này giúp chứng minh Full workflow giảm overclaim tốt hơn."
        ),
        "source_url": "eval/b0_single_shot_prompt.md",
        "tags": ["baseline", "evaluation", "single-shot"],
        "payload": {
            "compare_against": ["unsupported assertions", "missing sections", "major findings"],
            "expected_weakness": "Dễ sinh spec nghe hợp lý nhưng thiếu quyết định người dùng và citation grounding.",
        },
    },
    {
        "id": "baseline-b1-single-judge",
        "category": "evaluation",
        "title": "Baseline B1 - Wizard with One Judge",
        "summary": (
            "B1 chạy wizard nhưng chỉ dùng một Judge tổng hợp. Nó giúp so sánh với thiết kế 5 Judge độc lập "
            "về khả năng phát hiện disagreement."
        ),
        "source_url": "eval/b1_single_judge_prompt.md",
        "tags": ["baseline", "judge", "evaluation"],
        "payload": {
            "compare_against": ["judge disagreement", "major findings", "revise quality"],
            "expected_weakness": "Một Judge tổng hợp dễ bỏ sót góc nhìn chuyên biệt.",
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
        "id": "method-session-memory",
        "category": "backend-method",
        "title": "Session Memory and Chat History",
        "summary": (
            "Mỗi session phải có lịch sử riêng gồm idea, restatement, decision và chat note. "
            "Khi tạo session mới, lịch sử cũ không mất mà vẫn truy xuất lại từ DB."
        ),
        "source_url": "backend/app/db/models.py",
        "tags": ["session", "chat-history", "persistence"],
        "payload": {
            "tables": ["sessions", "decisions", "chat_messages", "spec_versions"],
            "supports_assignment_requirement": "Xem lại lịch sử từng session và tiếp tục pipeline.",
        },
    },
    {
        "id": "method-feasibility-budget",
        "category": "backend-method",
        "title": "Feasibility Budget Estimator",
        "summary": (
            "Backend ước lượng model, VRAM, số candidate, số vòng, số mẫu, token và thời gian để kiểm tra "
            "kế hoạch có phù hợp tài nguyên như RTX 3090 hay không."
        ),
        "source_url": "backend/app/services/feasibility_service.py",
        "tags": ["feasibility", "budget", "rtx-3090"],
        "payload": {
            "signals": ["vram_gb", "estimated_tokens", "estimated_hours", "over_budget"],
            "fallback": "Đề xuất scale-down nếu vượt tài nguyên.",
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
    {
        "id": "design-session-dashboard",
        "category": "design-system",
        "title": "Session Dashboard",
        "summary": (
            "Sessions page cần hiển thị danh sách phiên có phân trang, trạng thái FSM, số nguồn, số version, "
            "số chat message và các nút resume từng stage."
        ),
        "source_url": "frontend/src/pages/WizardPage.tsx",
        "tags": ["sessions", "pagination", "resume"],
        "payload": {
            "components": ["session-card", "mini-pipeline", "pagination"],
            "design_goal": "Người dùng xem được lịch sử và quay lại bất kỳ bước nào.",
        },
    },
    {
        "id": "design-chat-analytics",
        "category": "design-system",
        "title": "Chat Analytics",
        "summary": (
            "Chat history không chỉ là log văn bản; nó cần có thống kê tổng số message, số nguồn, số version "
            "và biểu đồ chủ đề người dùng hay hỏi."
        ),
        "source_url": "frontend/src/pages/WizardPage.tsx",
        "tags": ["chat", "analytics", "charts"],
        "payload": {
            "topics": ["idea", "related work", "experiment", "judge", "feasibility"],
            "visual": "bar chart đơn giản bằng CSS để không thêm dependency.",
        },
    },
    {
        "id": "design-knowledge-detail",
        "category": "design-system",
        "title": "Knowledge Detail Page",
        "summary": (
            "Knowledge page cần cho phép lọc category và mở chi tiết để xem toàn bộ summary, tags, source URL "
            "và payload JSON thay vì chỉ xem card rút gọn."
        ),
        "source_url": "frontend/src/pages/WizardPage.tsx",
        "tags": ["knowledge", "detail", "backend-data"],
        "payload": {
            "categories": ["research", "evaluation", "backend-method", "design-system"],
            "action": "Xem toàn bộ",
        },
    },
]

DEMO_SESSIONS: list[dict[str, Any]] = [
    {
        "id": "11111111-1111-4111-8111-111111111111",
        "fsm_state": "FINAL",
        "raw_idea": "Tối ưu prompt nhiều vòng để giảm hallucination khi LLM trích xuất thông tin từ paper.",
        "interpretation": "Xây một pipeline sinh candidate prompt, chạy extraction trên tập paper, dùng verifier phát hiện unsupported claims rồi revise prompt qua nhiều vòng.",
        "sources": [
            {
                "id": "src-opro-demo",
                "openalex_id": "https://openalex.org/W4389540418",
                "title": "Large Language Models as Optimizers",
                "year": 2023,
                "authors": ["Chengrun Yang", "Xuezhi Wang", "Yifeng Lu"],
                "abstract": "LLMs can optimize prompts by using previous solutions and scores as natural-language feedback.",
                "doi_url": "https://arxiv.org/abs/2309.03409",
                "cited_by_count": 420,
            },
            {
                "id": "src-self-refine-demo",
                "openalex_id": "https://openalex.org/W4386054695",
                "title": "Self-Refine: Iterative Refinement with Self-Feedback",
                "year": 2023,
                "authors": ["Aman Madaan", "Niket Tandon", "Prakhar Gupta"],
                "abstract": "A language model can iteratively produce feedback and refine its own output.",
                "doi_url": "https://arxiv.org/abs/2303.17651",
                "cited_by_count": 780,
            },
        ],
        "related_work": [
            {
                "id": "rw-opro-demo",
                "source_id": "src-opro-demo",
                "did_what": "Dùng LLM như optimizer sinh lời giải/prompt mới từ lịch sử điểm số.",
                "feedback_used": "Scalar scores và các candidate trước đó.",
                "open_point": "Chưa tập trung vào claim-level evidence verification khi trích xuất từ paper.",
                "support_label": "SUPPORTS",
            },
            {
                "id": "rw-self-refine-demo",
                "source_id": "src-self-refine-demo",
                "did_what": "Lặp feedback rồi refine output bằng chính model.",
                "feedback_used": "Textual self-feedback.",
                "open_point": "Cần verifier độc lập để tránh model tự bỏ sót lỗi hallucination.",
                "support_label": "PARTIAL",
            },
        ],
        "cards": [
            {"id": "card-problem-demo", "card_type": "Problem", "status": "CONFIRMED", "content": "LLM extraction từ paper dễ sinh unsupported claims nếu prompt quá rộng."},
            {"id": "card-rq-demo", "card_type": "ResearchQuestion", "status": "CONFIRMED", "content": "Feedback dạng claim-evidence có giảm hallucination hơn scalar score trong prompt optimization không?"},
            {"id": "card-gap-demo", "card_type": "Gap", "status": "CONFIRMED", "content": "Các baseline prompt optimization chưa gắn feedback trực tiếp với citation support."},
            {"id": "card-claim-demo", "card_type": "Claim", "status": "CONFIRMED", "content": "Claim-level verifier giúp giảm số assertion không được abstract/source hỗ trợ."},
        ],
        "gap": {
            "statement": "Thiếu pipeline tối ưu prompt dùng feedback claim-evidence để giảm hallucination trong extraction từ paper.",
            "prior_work": "OPRO tối ưu prompt bằng score; Self-Refine dùng self-feedback.",
            "limitation": "Ít nhấn mạnh source support ở mức từng claim.",
            "why_matters": "Research spec cần tránh overclaim và citation không khớp.",
            "how_to_test": "So sánh unsupported claims giữa B0, OPRO-style và verifier-guided prompt optimization.",
            "options": [
                {"key": "A", "label": "Tập trung verifier", "explanation": "Ưu tiên claim-evidence feedback.", "example": "Mỗi claim phải có source label."},
                {"key": "B", "label": "Tập trung search", "explanation": "Ưu tiên thuật toán sinh prompt.", "example": "Beam/evolution prompt candidates."},
            ],
        },
        "contributions": [
            "Pipeline tối ưu prompt nhiều vòng với feedback claim-evidence.",
            "Verifier rule-based đánh dấu SUPPORTS/PARTIAL/UNSUPPORTED/UNVERIFIABLE.",
            "Bộ metric demo đo unsupported claims và judge findings.",
        ],
        "claim_cards": [
            {
                "id": "claim-demo-1",
                "claim": "Verifier-guided feedback giảm unsupported claims so với single-shot prompt.",
                "baseline": "B0 single-shot và OPRO-style scalar feedback.",
                "metric": "Số assertion UNSUPPORTED trên mỗi paper.",
                "evidence": "So sánh trên tập paper validation nhỏ.",
                "falsification": "Không giảm hoặc làm giảm recall extraction đáng kể.",
            }
        ],
        "experiment": {
            "baseline_compare": "B0 single-shot, OPRO-style scalar feedback, Self-Refine feedback.",
            "quality_eval": "Unsupported claims, citation faithfulness, extraction F1 thủ công trên 30 paper.",
            "ablation": "Bỏ verifier, bỏ judge, bỏ revision memory.",
            "generalization": "Test trên NLP, HCI và Software Engineering papers.",
            "fairness_constraints": ["Cùng model", "Cùng token budget", "Cùng tập paper"],
        },
        "feasibility": {
            "model": "llama-3.3-70b-versatile",
            "vram_gb": 24,
            "candidates_per_round": 4,
            "rounds": 3,
            "samples_dev": 20,
            "samples_val": 30,
            "estimated_hours": 6.5,
            "estimated_tokens": 850000,
            "over_budget": False,
            "narrative": "Khả thi cho demo lớp nếu dùng metadata/abstract và mock mode khi thiếu key.",
            "scale_down_options": [
                {"key": "accept", "label": "Giữ kế hoạch", "explanation": "Budget vẫn hợp lý.", "example": "30 paper validation."},
                {"key": "small", "label": "Giảm mẫu", "explanation": "Dùng 10 dev và 15 val.", "example": "Demo nhanh hơn."},
            ],
            "assumptions": ["Không tải full-text PDF", "Dùng abstract metadata"],
        },
        "judge_findings": [
            {
                "target": "claim",
                "target_id": "claim-demo-1",
                "issue": "Claim cần ghi rõ domain paper khoa học, không khẳng định mọi extraction task.",
                "reason": "Experiment chỉ dùng paper abstract.",
                "severity": "MINOR",
                "suggestion": "Thu hẹp claim trong final spec.",
                "judge_type": "contribution",
            }
        ],
        "aggregate": {
            "consensus": [{"target": "claim", "severity": "MINOR", "count": 1, "judges": ["contribution"], "issues": ["Claim hơi rộng"], "suggestions": ["Thu hẹp domain"]}],
            "disagreement": [],
            "major_count": 0,
            "can_finalize_early": True,
            "revision_options": [{"key": "finalize", "label": "Finalize", "explanation": "Không còn MAJOR.", "example": None}],
        },
        "versions": [
            {
                "id": "21111111-1111-4111-8111-111111111111",
                "version_no": 1,
                "label": "draft",
                "markdown": "# Research Spec Draft\n\n## Problem\nLLM extraction từ paper dễ sinh unsupported claims.\n\n## Gap\nFeedback tối ưu prompt chưa gắn chặt với citation support.\n",
            },
            {
                "id": "21111111-1111-4111-8111-111111111112",
                "version_no": 2,
                "label": "final",
                "markdown": "# Final Research Spec\n\n## Problem\nLLM extraction từ paper dễ sinh unsupported claims.\n\n## Contribution\nVerifier-guided prompt optimization dùng claim-evidence feedback.\n\n## Experiment\nSo sánh B0, OPRO-style và Self-Refine trên cùng tập paper.\n",
            },
        ],
        "decisions": [
            {"id": "31111111-1111-4111-8111-111111111111", "step": "restate", "choice_key": "confirm", "choice_text": "Xác nhận interpretation về prompt optimization."},
            {"id": "31111111-1111-4111-8111-111111111112", "step": "gap", "choice_key": "A", "choice_text": "Tập trung verifier claim-evidence."},
            {"id": "31111111-1111-4111-8111-111111111113", "step": "revise", "choice_key": "finalize", "choice_text": "Không còn MAJOR."},
        ],
        "chat": [
            {"id": "41111111-1111-4111-8111-111111111111", "role": "user", "step": "Ý tưởng", "content": "Em muốn giảm hallucination khi LLM trích xuất từ paper."},
            {"id": "41111111-1111-4111-8111-111111111112", "role": "assistant", "step": "Related work", "content": "Có thể dùng OPRO và Self-Refine làm baseline, nhưng cần verifier độc lập."},
            {"id": "41111111-1111-4111-8111-111111111113", "role": "user", "step": "Judge", "content": "Judge còn bảo claim hơi rộng, em sẽ giới hạn domain paper khoa học."},
        ],
    },
    {
        "id": "11111111-1111-4111-8111-222222222222",
        "fsm_state": "REVISION",
        "raw_idea": "Đánh giá độ trung thực citation trong hệ thống RAG tiếng Việt.",
        "interpretation": "Xây benchmark nhỏ để đo citation faithfulness cho câu trả lời RAG tiếng Việt và đề xuất rule-based verifier.",
        "sources": [
            {
                "id": "src-ragas-demo",
                "openalex_id": "https://openalex.org/W4391689604",
                "title": "RAGAS: Automated Evaluation of Retrieval Augmented Generation",
                "year": 2023,
                "authors": ["Shahul Es", "Jithin James", "Luis Espinosa-Anke"],
                "abstract": "RAGAS proposes reference-free metrics to evaluate retrieval augmented generation.",
                "doi_url": "https://arxiv.org/abs/2309.15217",
                "cited_by_count": 650,
            }
        ],
        "related_work": [
            {
                "id": "rw-ragas-demo",
                "source_id": "src-ragas-demo",
                "did_what": "Đề xuất metric tự động cho RAG.",
                "feedback_used": "Faithfulness và answer relevance.",
                "open_point": "Cần adaptation cho tiếng Việt và citation span.",
                "support_label": "SUPPORTS",
            }
        ],
        "cards": [
            {"id": "card-rag-problem", "card_type": "Problem", "status": "CONFIRMED", "content": "RAG có thể trả lời đúng giọng nhưng citation không thật sự hỗ trợ câu trả lời."},
            {"id": "card-rag-open", "card_type": "OpenQuestion", "status": "AMBIGUOUS", "content": "Nên chấm citation ở mức câu hay mức span?"},
        ],
        "gap": None,
        "contributions": ["Checklist đánh giá citation faithfulness tiếng Việt.", "Verifier rule-based cho citation span."],
        "claim_cards": [],
        "experiment": None,
        "feasibility": None,
        "judge_findings": [
            {
                "target": "experiment",
                "target_id": None,
                "issue": "Cần mô tả rõ annotation protocol.",
                "reason": "Metric tự động cần tập vàng nhỏ để kiểm tra.",
                "severity": "MAJOR",
                "suggestion": "Thêm 50 QA có citation label thủ công.",
                "judge_type": "experiment",
            }
        ],
        "aggregate": {
            "consensus": [{"target": "experiment", "severity": "MAJOR", "count": 1, "judges": ["experiment"], "issues": ["Thiếu annotation protocol"], "suggestions": ["Thêm gold labels"]}],
            "disagreement": [],
            "major_count": 1,
            "can_finalize_early": False,
            "revision_options": [
                {"key": "add_annotation", "label": "Bổ sung annotation", "explanation": "Thêm protocol chấm citation thủ công.", "example": "50 QA sample."}
            ],
        },
        "versions": [
            {
                "id": "21111111-1111-4111-8111-222222222222",
                "version_no": 1,
                "label": "draft",
                "markdown": "# RAG Citation Faithfulness\n\n## Problem\nCitation không luôn hỗ trợ câu trả lời.\n\n## Revision Needed\nBổ sung annotation protocol.\n",
            }
        ],
        "decisions": [
            {"id": "31111111-1111-4111-8111-222222222222", "step": "restate", "choice_key": "edit", "choice_text": "Tập trung tiếng Việt và citation span."}
        ],
        "chat": [
            {"id": "41111111-1111-4111-8111-222222222221", "role": "user", "step": "Ý tưởng", "content": "Em muốn kiểm tra citation trong RAG tiếng Việt có thật sự hỗ trợ câu trả lời không."},
            {"id": "41111111-1111-4111-8111-222222222222", "role": "assistant", "step": "Judge", "content": "Experiment Judge yêu cầu thêm annotation protocol để claim đủ chắc."},
        ],
    },
    {
        "id": "11111111-1111-4111-8111-333333333333",
        "fsm_state": "RELATED_WORK",
        "raw_idea": "Thiết kế design system cho công cụ research workflow học thuật.",
        "interpretation": "Tạo design system tập trung vào pipeline observability, session history và đọc hiểu spec dài.",
        "sources": [],
        "related_work": [],
        "cards": [
            {"id": "card-ds-problem", "card_type": "Problem", "status": "CONFIRMED", "content": "UI research tool dễ bị giống dashboard chung chung, thiếu cảm giác học thuật."},
            {"id": "card-ds-constraint", "card_type": "Constraint", "status": "CONFIRMED", "content": "Giữ typography serif cho nội dung dài và dùng forest green làm accent."},
        ],
        "gap": None,
        "contributions": [],
        "claim_cards": [],
        "experiment": None,
        "feasibility": None,
        "judge_findings": [],
        "aggregate": None,
        "versions": [],
        "decisions": [
            {"id": "31111111-1111-4111-8111-333333333333", "step": "decompose", "choice_key": "A", "choice_text": "Ưu tiên academic workbench thay vì SaaS dashboard."}
        ],
        "chat": [
            {"id": "41111111-1111-4111-8111-333333333331", "role": "user", "step": "Design system", "content": "UI nên có pipeline flow, session history và màu sắc chuyên nghiệp hơn."},
            {"id": "41111111-1111-4111-8111-333333333332", "role": "assistant", "step": "Design system", "content": "Có thể tách thành Pipeline, Sessions, Knowledge và Chat history để nhìn giống nhiều trang."},
        ],
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
    seed_demo_sessions(db)


def seed_demo_sessions(db: Session) -> None:
    existing_sessions = {row.id for row in db.query(SessionRow.id).all()}
    for demo in DEMO_SESSIONS:
        if demo["id"] in existing_sessions:
            continue

        ast = {
            "raw_idea": demo["raw_idea"],
            "interpretation": demo["interpretation"],
            "cards": demo["cards"],
            "sources": demo["sources"],
            "related_work": demo["related_work"],
            "related_work_status": "OK",
            "gap": demo["gap"],
            "chosen_gap_key": "A" if demo["gap"] else None,
            "chosen_gap_text": demo["gap"]["statement"] if demo["gap"] else None,
            "contributions": demo["contributions"],
            "claim_cards": demo["claim_cards"],
            "experiment": demo["experiment"],
            "feasibility": demo["feasibility"],
            "open_issues": [],
            "risks": [],
            "decision_history": [
                {
                    "step": decision["step"],
                    "choice_key": decision["choice_key"],
                    "choice_text": decision["choice_text"],
                }
                for decision in demo["decisions"]
            ],
            "judge_findings": demo["judge_findings"],
            "readiness": {
                "originality": "Acceptable",
                "significance": "Acceptable",
                "soundness": "Acceptable",
                "clarity": "Strong",
                "reproducibility": "Acceptable",
                "overall": "Acceptable" if demo["fsm_state"] == "FINAL" else "NeedsWork",
            },
            "aggregate": demo["aggregate"],
        }

        db.add(
            SessionRow(
                id=demo["id"],
                fsm_state=demo["fsm_state"],
                raw_idea=demo["raw_idea"],
                confirmed_interpretation=demo["interpretation"],
                revise_count=1 if demo["fsm_state"] in {"REVISION", "FINAL"} else 0,
                working_ast_json=json.dumps(ast, ensure_ascii=False),
            )
        )

        for source in demo["sources"]:
            db.add(
                SourceRow(
                    id=source["id"],
                    session_id=demo["id"],
                    openalex_id=source.get("openalex_id") or "",
                    title=source["title"],
                    year=source.get("year") or 0,
                    authors_json=json.dumps(source.get("authors") or [], ensure_ascii=False),
                    abstract=source.get("abstract") or "",
                    doi_url=source.get("doi_url") or "",
                    cited_by_count=source.get("cited_by_count") or 0,
                )
            )

        for version in demo["versions"]:
            db.add(
                SpecVersionRow(
                    id=version["id"],
                    session_id=demo["id"],
                    version_no=version["version_no"],
                    label=version["label"],
                    ast_json=json.dumps(ast, ensure_ascii=False),
                    markdown=version["markdown"],
                )
            )

        for decision in demo["decisions"]:
            db.add(
                DecisionRow(
                    id=decision["id"],
                    session_id=demo["id"],
                    step=decision["step"],
                    options_json="[]",
                    choice_key=decision["choice_key"],
                    choice_text=decision["choice_text"],
                )
            )

        for message in demo["chat"]:
            db.add(
                ChatMessageRow(
                    id=message["id"],
                    session_id=demo["id"],
                    role=message["role"],
                    content=message["content"],
                    step=message["step"],
                )
            )

    db.flush()
