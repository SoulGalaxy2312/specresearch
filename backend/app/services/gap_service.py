from __future__ import annotations

from app.domain.spec_ast import ChoiceOption, GapProposal, SpecAST
from app.integrations.groq_client import GroqClient, load_prompt


def propose_gap(ast: SpecAST) -> GapProposal:
    client = GroqClient()
    system = load_prompt("generators/gap.md") or (
        "Đề xuất research gap có cấu trúc (không được nói 'chưa thấy paper giống hệt'). "
        "Trả JSON với keys: statement, prior_work, limitation, why_matters, how_to_test, "
        "options (A-E với key,label,explanation,example)."
    )
    ctx = {
        "interpretation": ast.interpretation,
        "related_work": [e.model_dump() for e in ast.related_work[:8]],
        "sources": [{"id": s.id, "title": s.title} for s in ast.sources[:8]],
    }
    mock = {
        "statement": (
            "Các phương pháp tối ưu prompt hiện dùng điểm tổng hoặc textual feedback; "
            "chưa rõ claim-level evidence feedback có giảm unsupported claims trong cùng ngân sách inference không."
        ),
        "prior_work": "OPRO/PromptBreeder/TextGrad/DSPy tối ưu prompt hoặc pipeline bằng score hoặc LLM feedback.",
        "limitation": "Phản hồi thường không tách claim và kiểm tra evidence độc lập.",
        "why_matters": "Hallucination khi extraction thường xảy ra ở mức claim cụ thể, không chỉ điểm tổng.",
        "how_to_test": "So sánh scalar vs textual vs claim-level feedback trên cùng budget và đo unsupported claim rate.",
        "options": [
            {
                "key": "A",
                "label": "Tập trung thuật toán tối ưu prompt",
                "explanation": "Điểm mới ở mutation/selection/search.",
                "example": "Search policy mới trên candidate prompts.",
            },
            {
                "key": "B",
                "label": "Tập trung claim–evidence verifier",
                "explanation": "Điểm mới ở cách kiểm tra hallucination.",
                "example": "Phân loại supported / missing / contradict.",
            },
            {
                "key": "C",
                "label": "Human-in-the-loop",
                "explanation": "Điểm mới ở cách user xác nhận quá trình.",
                "example": "User duyệt candidate mỗi vòng.",
            },
            {
                "key": "D",
                "label": "Kết hợp các hướng",
                "explanation": "Một contribution chính + phụ.",
                "example": "Verifier chính + optimizer phụ.",
            },
            {"key": "E", "label": "Other", "explanation": "Nhập hướng riêng.", "example": None},
        ],
    }
    data = client.chat_json(system, str(ctx), mock_payload=mock)
    options = [ChoiceOption.model_validate(o) for o in data.get("options", [])]
    return GapProposal(
        statement=data.get("statement", ""),
        prior_work=data.get("prior_work", ""),
        limitation=data.get("limitation", ""),
        why_matters=data.get("why_matters", ""),
        how_to_test=data.get("how_to_test", ""),
        options=options,
    )
