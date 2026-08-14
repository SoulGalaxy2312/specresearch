# Eval use cases & baseline checklist

## Use cases (5–8)

1. **Prompt opt + hallucination extraction** (đề bài): tối ưu prompt nhiều vòng giảm unsupported claims khi LLM trích xuất từ paper.
2. **RAG citation faithfulness**: verifier cho câu trả lời RAG có citation đúng span.
3. **Code review agent eval**: metric tự động cho agent review PR so với human baseline.
4. **Multilingual summarization factuality**: giảm hallucinated entities khi tóm tắt tin tức VI/EN.
5. **Active learning for labeling**: chọn mẫu labeling tối ưu với budget annotator.
6. **Tiny LLM fine-tune on domain FAQs**: claim về cải thiện exact-match trong VRAM consumer.
7. **Tool-use planning**: giảm wrong-tool calls bằng verifier kế hoạch.
8. **Dataset contamination check**: phương pháp phát hiện overlap train/test cho benchmark nhỏ.

## Baselines hệ thống

| ID | Mô tả |
|----|--------|
| **B0** | Single-shot: 1 prompt “viết research spec” → 1 Markdown, không wizard, không judge |
| **B1** | Wizard ngắn + **1** judge tổng hợp |
| **Full** | SpecResearch MVP đầy đủ (wizard + grounding + 5 judges + revise) |

## Metrics checklist (chấm thủ công mỗi use case)

| Metric | B0 | B1 | Full |
|--------|----|----|------|
| # assertion không có citation / UNSUPPORTED | | | |
| # MAJOR còn lại sau 1 vòng review | | | |
| # câu hỏi user phải trả lời | | | |
| Thời gian hoàn thành (phút) | | | |
| Đủ section spec? (0/1) problem/RQ/related/gap/contrib/claim/experiment/budget | | | |

## Cách chạy B0 (tham chiếu)

Dùng prompt trong `eval/b0_single_shot_prompt.md` với cùng model Groq, dán ý tưởng use case, lưu output Markdown.

## Cách chạy B1 (tham chiếu)

Chạy wizard đến assemble, sau đó chỉ gọi 1 judge `readiness` (hoặc prompt tổng trong `eval/b1_single_judge_prompt.md`), không chạy đủ 5 judge + aggregate.

## Demo checklist

- [ ] Tạo session, nhập use case #1
- [ ] Confirm restatement
- [ ] Decompose + resolve 1 ambiguity
- [ ] Related work table hiện sources (hoặc DEGRADED + manual)
- [ ] Chọn gap option
- [ ] Confirm claim cards
- [ ] Xem experiment + feasibility
- [ ] Assemble markdown
- [ ] Chạy 5 judges tuần tự + aggregate
- [ ] Revise narrow_claim hoặc finalize sớm nếu 0 MAJOR
- [ ] Export MD + JSON
