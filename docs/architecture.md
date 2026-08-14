# SpecResearch Loop — Architecture

## Overview

Human-in-the-loop wizard chuyển ý tưởng nghiên cứu mơ hồ thành research specification có grounding, feasibility và multi-judge critique.

## Stack

| Layer | Choice |
|-------|--------|
| Frontend | React + TypeScript (Vite) |
| Backend | FastAPI |
| DB | SQLite (SQLAlchemy) |
| LLM | Groq `qwen/qwen3.6-27b` (1 model) |
| Retrieval | OpenAlex metadata-only |

## Runtime topology

```
Browser Wizard
  -> FastAPI /api/v1/*
       -> Wizard FSM + Spec AST (working JSON on session)
       -> Generator / Judge services -> Groq
       -> Related work -> OpenAlex
       -> SQLite persistence (sessions, versions, decisions, judges, sources)
```

## Source of truth

- **Spec AST** (`working_ast_json` + `spec_versions.ast_json`) là source of truth.
- Markdown là projection từ AST (`spec_assemble_service`).

## FSM

`IDEA → RESTATED → DECOMPOSED → RELATED_WORK → GAP_CHOSEN → CLAIMS_READY → EXPERIMENT_READY → FEASIBILITY_CHECKED → SPEC_DRAFT → JUDGING → REVISION ↔ JUDGING → FINAL`

## Judge isolation (ADR D5)

- Một model Groq.
- 5 prompt/role riêng: gap, contribution, experiment, evidence, readiness.
- Context độc lập (chỉ nhận spec markdown).
- Không đọc findings của nhau.
- Client gọi tuần tự 5 endpoint rồi `aggregate`.

## Grounding (ADR D3/D4)

- Related work chỉ từ OpenAlex metadata (+ paper thủ công).
- Citation verifier rule-based trên abstract overlap → SUPPORTS/PARTIAL/NOT/UNVERIFIABLE.
- Critical assertions không verify được phải mang nhãn phù hợp.

## Failure policy

- OpenAlex lỗi → `related_work_status=DEGRADED` + manual add.
- Groq lỗi → retry 1 lần; UI hiện lỗi + giữ state.
- `MOCK_LLM=1` hoặc thiếu `GROQ_API_KEY` → mock payloads để demo offline.

## Key modules

### Backend

- `app/api/routes.py` — HTTP API
- `app/domain/spec_ast.py` — AST + FSM enums
- `app/services/*` — business + AI orchestration
- `app/integrations/groq_client.py`, `openalex_client.py`
- `app/db/models.py` — minimal schema

### Frontend

- `pages/WizardPage.tsx` — stepper orchestration
- `steps/*` — từng gate
- `components/ChoiceGroup.tsx` — options + Other
- `lib/api.ts`, `lib/session.ts`

## Versioning & revise

- Snapshot sau assemble, mỗi revise, và finalize.
- Max 2 vòng revise; 0 MAJOR cho phép finalize sớm.
- Diff section-level giữa markdown trước/sau.

## Out of scope (MVP)

Auth, cloud sync, PDF full-text, multi-model judges, background jobs, graph UX.
