from __future__ import annotations

from uuid import uuid4

from app.domain.spec_ast import CardStatus, CardType, SpecAST, SpecCard
from app.integrations.groq_client import GroqClient, load_prompt


def decompose_idea(interpretation: str) -> tuple[SpecAST, list]:
    client = GroqClient()
    system = load_prompt("generators/decompose.md") or (
        "Phân rã ý tưởng nghiên cứu thành các thẻ. Trả JSON: "
        "{\"cards\":[{\"card_type\":\"Problem|ResearchQuestion|Gap|Contribution|Claim|Evidence|Constraint|OpenQuestion\","
        "\"status\":\"PROPOSED|MISSING|AMBIGUOUS\",\"content\":\"...\",\"meta\":{}}],"
        "\"issues\":[{\"card_hint\":\"...\",\"question\":\"...\",\"options\":[{\"key\":\"A\",\"label\":\"...\",\"explanation\":\"...\"}]}]}"
    )
    mock = {
        "cards": [
            {
                "card_type": "Problem",
                "status": "PROPOSED",
                "content": "Prompt thủ công cho LLM extraction thường không ổn định và dễ hallucination.",
                "meta": {},
            },
            {
                "card_type": "ResearchQuestion",
                "status": "PROPOSED",
                "content": "Tối ưu prompt nhiều vòng bằng phản hồi claim–evidence có giảm unsupported claims không?",
                "meta": {},
            },
            {
                "card_type": "Gap",
                "status": "AMBIGUOUS",
                "content": "Các phương pháp tối ưu prompt hiện tại có thể chưa tối ưu trực tiếp ở mức claim–evidence.",
                "meta": {},
            },
            {
                "card_type": "Contribution",
                "status": "PROPOSED",
                "content": "Framework tối ưu prompt dựa trên evidence feedback ở mức claim.",
                "meta": {},
            },
            {
                "card_type": "Claim",
                "status": "PROPOSED",
                "content": "Phương pháp giảm tỷ lệ unsupported claim so với baseline trong cùng ngân sách inference.",
                "meta": {},
            },
            {
                "card_type": "Evidence",
                "status": "MISSING",
                "content": "Kết quả thực nghiệm trên held-out data (chưa có).",
                "meta": {},
            },
            {
                "card_type": "Constraint",
                "status": "PROPOSED",
                "content": "Có thể chạy với GPU consumer (ví dụ RTX 3090) hoặc API budget giới hạn.",
                "meta": {"optional": True},
            },
            {
                "card_type": "OpenQuestion",
                "status": "AMBIGUOUS",
                "content": "Tối ưu một prompt đơn hay cả pipeline nhiều module?",
                "meta": {},
            },
        ],
        "issues": [
            {
                "card_hint": "OpenQuestion",
                "question": "Bạn muốn tối ưu phạm vi nào?",
                "options": [
                    {
                        "key": "A",
                        "label": "Một prompt extraction",
                        "explanation": "Tập trung một template prompt.",
                        "example": "Prompt trích xuất contribution từ paper.",
                    },
                    {
                        "key": "B",
                        "label": "Cả pipeline",
                        "explanation": "Gồm decompose claim + verify + refine.",
                        "example": "DSPy-style multi-module.",
                    },
                    {"key": "E", "label": "Other", "explanation": "Nhập hướng riêng.", "example": None},
                ],
            }
        ],
    }
    data = client.chat_json(system, f"Diễn giải đã xác nhận:\n{interpretation}", mock_payload=mock)
    cards: list[SpecCard] = []
    for c in data.get("cards", []):
        try:
            card_type = CardType(c["card_type"]) if c.get("card_type") in CardType._value2member_map_ else CardType.OPEN_QUESTION
            status = CardStatus(c.get("status", "PROPOSED"))
        except Exception:  # noqa: BLE001
            card_type = CardType.OPEN_QUESTION
            status = CardStatus.PROPOSED
        cards.append(
            SpecCard(
                id=str(uuid4()),
                card_type=card_type,
                status=status,
                content=c.get("content", ""),
                meta=c.get("meta") or {},
            )
        )
    return SpecAST(interpretation=interpretation, cards=cards), data.get("issues", [])
