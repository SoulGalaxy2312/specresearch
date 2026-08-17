from __future__ import annotations

from app.integrations.groq_client import GroqClient, load_prompt


def generate_restatement(idea: str) -> dict:
    client = GroqClient()
    system = load_prompt("generators/restate.md") or (
        "Bạn là trợ lý nghiên cứu. Diễn giải lại ý tưởng bằng tiếng Việt đơn giản. "
        "Trả JSON: {\"interpretations\": [{\"id\": \"1\", \"text\": \"...\"}, ...]} với 2 phiên bản."
    )
    mock = {
        "interpretations": [
            {
                "id": "1",
                "text": (
                    f"Bạn muốn xây một quy trình tối ưu prompt nhiều vòng để giảm thông tin "
                    f"LLM bịa khi trích xuất từ tài liệu. Ý tưởng gốc: {idea[:280]}"
                ),
            },
            {
                "id": "2",
                "text": (
                    "Hệ thống sẽ tạo nhiều phiên bản prompt, chạy trên cùng tập tài liệu, "
                    "phát hiện lỗi không được nguồn hỗ trợ, rồi sửa prompt. Mục tiêu giảm hallucination khi extraction."
                ),
            },
        ]
    }
    return client.chat_json(system, f"Ý tưởng:\n{idea}", mock_payload=mock)