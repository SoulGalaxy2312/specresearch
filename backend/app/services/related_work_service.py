from __future__ import annotations

from uuid import uuid4

from app.domain.spec_ast import RelatedWorkEntry, SourceRef, SpecAST
from app.integrations.groq_client import GroqClient, load_prompt
from app.integrations.openalex_client import OpenAlexClient
from app.services.verifier_service import verify_statement_against_abstract


def run_related_work(ast: SpecAST, limit: int = 10) -> SpecAST:
    client = GroqClient()
    oa = OpenAlexClient()
    system = load_prompt("generators/keywords.md") or (
        "Tạo từ khóa tìm kiếm paper (tiếng Anh). Trả JSON: {\"queries\":[\"...\"]} tối đa 3 query."
    )
    mock_kw = {
        "queries": [
            "prompt optimization LLM hallucination",
            "claim verification evidence grounding",
            "automatic prompt engineering OPRO DSPy",
        ]
    }
    kw = client.chat_json(
        system,
        f"Interpretation:\n{ast.interpretation}\nCards:\n" + "\n".join(f"- {c.card_type}: {c.content}" for c in ast.cards),
        mock_payload=mock_kw,
    )
    queries = kw.get("queries") or ["prompt optimization LLM"]
    sources_raw: list[dict] = []
    degraded = False
    for q in queries[:3]:
        found = oa.search(q, limit=max(3, limit // max(1, len(queries[:3]))))
        if not found:
            degraded = True
        sources_raw.extend(found)
    # dedupe by title
    seen = set()
    unique = []
    for s in sources_raw:
        t = (s.get("title") or "").lower()
        if t in seen:
            continue
        seen.add(t)
        unique.append(s)
    unique = unique[:limit]

    if not unique:
        degraded = True
        unique = [
            {
                "id": str(uuid4()),
                "openalex_id": None,
                "title": "OPRO: Large Language Models as Optimizers (placeholder — retrieval degraded)",
                "year": 2023,
                "authors": ["Yang et al."],
                "abstract": "Uses LLMs to propose new prompts from previous prompts and scores.",
                "doi_url": "https://openalex.org",
                "cited_by_count": 0,
            }
        ]

    sources = [SourceRef.model_validate(s) for s in unique]

    synth_system = load_prompt("generators/related_work.md") or (
        "Từ danh sách paper (chỉ dùng paper được cung cấp), lập bảng related work tiếng Việt. "
        "Trả JSON: {\"entries\":[{\"source_id\":\"...\",\"did_what\":\"...\",\"feedback_used\":\"...\","
        "\"open_point\":\"...\",\"statement_for_verify\":\"...\"}]}"
    )
    papers_blob = "\n\n".join(
        f"ID:{s.id}\nTitle:{s.title}\nYear:{s.year}\nAbstract:{(s.abstract or '')[:800]}" for s in sources
    )
    mock_entries = {
        "entries": [
            {
                "source_id": sources[0].id,
                "did_what": "Đề xuất/đánh giá hướng tối ưu prompt hoặc grounding liên quan.",
                "feedback_used": "Điểm tổng hoặc phản hồi văn bản (nếu có trong abstract).",
                "open_point": "Chưa rõ tối ưu ở mức claim–evidence độc lập.",
                "statement_for_verify": sources[0].abstract or sources[0].title,
            }
        ]
    }
    # expand mock for all sources
    if len(sources) > 1:
        mock_entries["entries"] = [
            {
                "source_id": s.id,
                "did_what": f"Công trình liên quan: {s.title[:80]}",
                "feedback_used": "Chưa rõ / abstract hạn chế",
                "open_point": "Cần kiểm tra mức hỗ trợ cho claim–evidence feedback.",
                "statement_for_verify": (s.abstract or s.title)[:400],
            }
            for s in sources
        ]

    synth = client.chat_json(synth_system, papers_blob, mock_payload=mock_entries)
    entries: list[RelatedWorkEntry] = []
    source_by_id = {s.id: s for s in sources}
    for e in synth.get("entries", []):
        sid = e.get("source_id")
        if sid not in source_by_id:
            continue
        src = source_by_id[sid]
        label = verify_statement_against_abstract(e.get("statement_for_verify") or e.get("did_what", ""), src.abstract)
        entries.append(
            RelatedWorkEntry(
                id=str(uuid4()),
                source_id=sid,
                did_what=e.get("did_what", ""),
                feedback_used=e.get("feedback_used", ""),
                open_point=e.get("open_point", ""),
                support_label=label,
            )
        )

    ast.sources = sources
    ast.related_work = entries
    ast.related_work_status = "DEGRADED" if degraded else "OK"
    return ast


def add_manual_paper(ast: SpecAST, title: str, url: str, abstract: str | None) -> SpecAST:
    src = SourceRef(
        id=str(uuid4()),
        title=title,
        doi_url=url,
        abstract=abstract,
        authors=[],
        year=None,
    )
    ast.sources.append(src)
    label = verify_statement_against_abstract(abstract or title, abstract)
    ast.related_work.append(
        RelatedWorkEntry(
            id=str(uuid4()),
            source_id=src.id,
            did_what="Paper thêm thủ công bởi người dùng.",
            feedback_used="N/A",
            open_point="Cần đối chiếu với gap đề xuất.",
            support_label=label,
        )
    )
    return ast
