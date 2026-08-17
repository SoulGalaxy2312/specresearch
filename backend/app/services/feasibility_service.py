from __future__ import annotations

from app.domain.spec_ast import ChoiceOption, FeasibilityEstimate, SpecAST
from app.integrations.groq_client import GroqClient, load_prompt


def estimate_feasibility(ast: SpecAST, profile: dict | None = None) -> FeasibilityEstimate:
    # Deterministic rule table
    p = profile or {
        "model": "7B–8B 4-bit",
        "vram_gb": 16.0,
        "candidates_per_round": 10,
        "rounds": 10,
        "samples_dev": 50,
        "samples_val": 300,
    }
    # rough token estimate
    tokens = int(
        p["candidates_per_round"]
        * p["rounds"]
        * (p["samples_dev"] * 0.3 + 5)
        * 800
    )
    hours = round(tokens / 120_000, 2)  # rough local throughput assumption
    over = p["vram_gb"] > 24 or p["rounds"] > 12 or p["samples_val"] > 500 or hours > 24

    scale = [
        ChoiceOption(
            key="reduce_rounds",
            label="Giảm số vòng xuống 5",
            explanation="Giảm chi phí tìm kiếm prompt.",
            example="rounds=5",
        ),
        ChoiceOption(
            key="reduce_samples",
            label="Giảm validation xuống 100 mẫu",
            explanation="Đánh giá đầy đủ ít mẫu hơn.",
            example="samples_val=100",
        ),
        ChoiceOption(
            key="reduce_candidates",
            label="Giảm candidates mỗi vòng xuống 5",
            explanation="Ít ứng viên hơn mỗi vòng.",
            example="candidates=5",
        ),
        ChoiceOption(
            key="accept",
            label="Giữ cấu hình hiện tại",
            explanation="Chấp nhận ước lượng và giả định.",
            example=None,
        ),
    ]

    narrative_mock = (
        f"Với model {p['model']}, {p['candidates_per_round']} candidates × {p['rounds']} vòng, "
        f"ước lượng ~{tokens:,} tokens và ~{hours} giờ. "
        + ("Có thể vượt ngân sách consumer GPU — nên scale-down." if over else "Trong tầm khả thi MVP.")
    )
    client = GroqClient()
    system = load_prompt("generators/feasibility.md") or (
        "Viết đoạn giải thích tính khả thi bằng tiếng Việt dựa trên số liệu cho sẵn. "
        "Trả JSON: {\"narrative\":\"...\"}. Không bịa số mới."
    )
    data = client.chat_json(
        system,
        f"Numbers: {p}, tokens={tokens}, hours={hours}, over={over}",
        temperature=0.2,
        mock_payload={"narrative": narrative_mock},
    )

    assumptions = [
        "Constraint phần cứng là tùy chọn; dùng profile consumer mặc định nếu user không chỉ định.",
        "Ước lượng token/time là xấp xỉ rule-based, không phải benchmark thực.",
    ]
    # pull constraint card if any
    for c in ast.cards:
        if c.card_type.value == "Constraint":
            assumptions.append(f"User constraint: {c.content}")

    return FeasibilityEstimate(
        model=p["model"],
        vram_gb=float(p["vram_gb"]),
        candidates_per_round=int(p["candidates_per_round"]),
        rounds=int(p["rounds"]),
        samples_dev=int(p["samples_dev"]),
        samples_val=int(p["samples_val"]),
        estimated_hours=float(hours),
        estimated_tokens=int(tokens),
        over_budget=bool(over),
        narrative=data.get("narrative") or narrative_mock,
        scale_down_options=scale,
        assumptions=assumptions,
    )


def apply_scale_down(est: FeasibilityEstimate, choice: str) -> FeasibilityEstimate:
    profile = {
        "model": est.model,
        "vram_gb": est.vram_gb,
        "candidates_per_round": est.candidates_per_round,
        "rounds": est.rounds,
        "samples_dev": est.samples_dev,
        "samples_val": est.samples_val,
    }
    if choice == "reduce_rounds":
        profile["rounds"] = 5
    elif choice == "reduce_samples":
        profile["samples_val"] = 100
    elif choice == "reduce_candidates":
        profile["candidates_per_round"] = 5
    # re-estimate with dummy ast
    return estimate_feasibility(SpecAST(), profile)
