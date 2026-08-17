from __future__ import annotations

from uuid import uuid4

from app.domain.spec_ast import ClaimEvidenceCard, SpecAST
from app.integrations.groq_client import GroqClient, load_prompt


def build_claims(ast: SpecAST) -> SpecAST:
    client = GroqClient()
    system = load_prompt("generators/claims.md") or (
        "Xây contribution và claim–evidence cards. Trả JSON: "
        "{\"contributions\":[\"...\"],\"claim_cards\":[{\"claim\":\"...\",\"baseline\":\"...\","
        "\"metric\":\"...\",\"evidence\":\"...\",\"falsification\":\"...\"}]}"
    )
    mock = {
        "contributions": [
            "Framework tối ưu prompt nhiều vòng bằng claim-level evidence feedback.",
            "Verifier phân biệt claim có evidence / thiếu evidence / mâu thuẫn.",
            "Thực nghiệm so sánh scalar, textual và claim-level feedback trong cùng budget.",
        ],
        "claim_cards": [
            {
                "claim": "Phương pháp giảm unsupported claim rate so với baseline trong cùng ngân sách.",
                "baseline": "Human prompt, self-refine, OPRO-style optimizer",
                "metric": "Unsupported claim rate; coverage; token cost",
                "evidence": "Kết quả trên validation và held-out test",
                "falsification": "Không cải thiện ổn định hoặc giảm coverage đáng kể",
            }
        ],
    }
    data = client.chat_json(
        system,
        f"Gap chosen: {ast.chosen_gap_text}\nGap: {ast.gap.model_dump() if ast.gap else {}}\nInterp: {ast.interpretation}",
        mock_payload=mock,
    )
    ast.contributions = list(data.get("contributions") or [])
    cards = []
    for c in data.get("claim_cards") or []:
        cards.append(
            ClaimEvidenceCard(
                id=str(uuid4()),
                claim=c.get("claim", ""),
                baseline=c.get("baseline", ""),
                metric=c.get("metric", ""),
                evidence=c.get("evidence", ""),
                falsification=c.get("falsification", ""),
            )
        )
    ast.claim_cards = cards
    return ast