# Demo checklist — SpecResearch Loop

1. `cd /Users/P035243/Projects/specresearch/backend`
2. `python3 -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cp .env.example .env` — để `MOCK_LLM=1` hoặc điền `GROQ_API_KEY` + `MOCK_LLM=0`
5. `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
6. Terminal khác: `cd /Users/P035243/Projects/specresearch/frontend && npm install && npm run dev`
7. Mở http://localhost:5173
8. Chạy hết wizard với use case #1 trong `eval/README.md`
9. Xuất Markdown + JSON AST
10. Quay video demo theo Demo checklist trong `eval/README.md`