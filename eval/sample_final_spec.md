# Sample Research Specification (demo — MOCK path)

## Problem statement

Xây quy trình tối ưu prompt nhiều vòng để giảm thông tin LLM bịa khi trích xuất từ paper khoa học.

## Research questions & cards

- **Problem** [PROPOSED]: Prompt thủ công cho LLM extraction thường không ổn định và dễ hallucination.
- **ResearchQuestion** [PROPOSED]: Tối ưu prompt nhiều vòng bằng phản hồi claim–evidence có giảm unsupported claims không?
- **Gap** [CONFIRMED]: Các phương pháp tối ưu prompt hiện tại có thể chưa tối ưu trực tiếp ở mức claim–evidence.
- **Contribution** [PROPOSED]: Framework tối ưu prompt dựa trên evidence feedback ở mức claim.
- **Claim** [PROPOSED]: Phương pháp giảm tỷ lệ unsupported claim so với baseline trong cùng ngân sách inference (giới hạn trên domain paper khoa học đã đánh giá).
- **Evidence** [MISSING]: Kết quả thực nghiệm trên held-out data (chưa có).
- **Constraint** [PROPOSED]: Có thể chạy với GPU consumer hoặc API budget giới hạn.
- **OpenQuestion** [CONFIRMED]: Tối ưu một prompt extraction (đã chọn).

## Related-work matrix

| Nghiên cứu | Đã làm gì? | Feedback | Điểm mở | Support |
|---|---|---|---|---|
| OPRO-style / Prompt optimization literature | Đề xuất prompt từ score | Điểm tổng | Chưa claim-level | PARTIAL |

## Research gap

Các phương pháp tối ưu prompt hiện dùng điểm tổng hoặc textual feedback; chưa rõ claim-level evidence feedback có giảm unsupported claims trong cùng ngân sách inference không.

**Hướng đã chọn:** Tập trung claim–evidence verifier.

## Expected contributions

- Framework tối ưu prompt nhiều vòng bằng claim-level evidence feedback.
- Verifier phân biệt claim có evidence / thiếu evidence / mâu thuẫn.
- Thực nghiệm so sánh scalar, textual và claim-level feedback trong cùng budget.

## Claim–evidence matrix

### Claim: Phương pháp giảm unsupported claim rate so với baseline trong cùng ngân sách (domain paper khoa học).

- Baseline: Human prompt, self-refine, OPRO-style optimizer
- Metric: Unsupported claim rate; coverage; token cost
- Evidence: Validation và held-out test
- Falsification: Không cải thiện ổn định hoặc giảm coverage đáng kể

## Experimental protocol

### So sánh baseline
Human-written; Self-refine; Random mutation; OPRO-style; Proposed — cùng model/dataset/budget.

### Đánh giá chất lượng
Claim precision/recall; support rate; unsupported rate; cost; latency.

### Ablation
Bỏ claim decomposition; verifier; textual feedback; diversity; user confirmation.

### Generalization
Held-out set; loại paper khác trong cùng domain khoa học.

## Compute budget

- Model: 7B–8B 4-bit · Candidates 10 · Rounds 10 · Dev/Val 50/300
- Estimated tokens/hours: rule-based estimator

## Risks and limitations

- Metadata-only related work làm evidence check yếu.
- Một LLM cho mọi Judge có thể correlated bias.

## Decision history

- restate: confirm
- gap: B
- feasibility: accept
