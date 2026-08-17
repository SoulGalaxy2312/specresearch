# SpecResearch Loop

Website MVP giúp chuyển ý tưởng nghiên cứu mơ hồ thành research specification có bằng chứng, kế hoạch thí nghiệm và phản biện đa Judge.

**Repo:** `/Users/P035243/Projects/specresearch`

## Stack

- **Backend:** FastAPI + SQLite + SQLAlchemy
- **Frontend:** React + TypeScript (Vite)
- **LLM:** Groq (`qwen/qwen3.6-27b`)
- **Retrieval:** OpenAlex (metadata-only)

---

## Chạy lần đầu (2 terminal)

### Terminal 1 — Backend (bắt buộc chạy từ thư mục `backend`)

```bash
cd /Users/P035243/Projects/specresearch/backend

# 1) Virtualenv (chỉ cần lần đầu)
python3 -m venv .venv
source .venv/bin/activate

# 2) Cài dependency (chỉ cần lần đầu, hoặc khi requirements đổi)
pip install -r requirements.txt

# 3) Cấu hình môi trường (chỉ cần lần đầu)
cp .env.example .env
# Mở file .env và chọn MỘT trong hai:
#   A) Demo không cần Groq:  MOCK_LLM=1
#   B) Dùng Groq thật:       MOCK_LLM=0  và  GROQ_API_KEY=gsk_...

# 4) Chạy API
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Nếu lệnh `uvicorn` không tìm thấy sau khi activate venv:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Kiểm tra backend sống:

- Health: http://127.0.0.1:8000/health
- Swagger: http://127.0.0.1:8000/docs

Giữ terminal này chạy.

### Terminal 2 — Frontend

```bash
cd /Users/P035243/Projects/specresearch/frontend

# Lần đầu
npm install

# Chạy Vite (proxy /api -> backend :8000)
npm run dev
```

Mở UI: **http://localhost:5173**

Vite đã proxy `/api` và `/health` sang `http://127.0.0.1:8000`, nên frontend gọi API qua cùng origin — **cần backend đang chạy trước**.

---

## Chạy lại lần sau

```bash
# Terminal 1
cd /Users/P035243/Projects/specresearch/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2
cd /Users/P035243/Projects/specresearch/frontend
npm run dev
```

---

## Biến môi trường (`backend/.env`)

| Biến | Mô tả |
|------|--------|
| `MOCK_LLM` | `1` = mock (không cần key). `0` = gọi Groq thật |
| `GROQ_API_KEY` | API key Groq (bắt buộc khi `MOCK_LLM=0`) |
| `GROQ_MODEL` | Mặc định `qwen/qwen3.6-27b` |
| `OPENALEX_MAILTO` | Email lịch sự cho OpenAlex |
| `DATABASE_URL` | Mặc định `sqlite:///./specresearch.db` (file tạo trong `backend/`) |
| `CORS_ORIGINS` | Mặc định cho phép `http://localhost:5173` |

---

## Cấu trúc

```
specresearch/
  backend/     FastAPI  → uvicorn app.main:app --port 8000
  frontend/    Vite     → npm run dev → :5173
  prompts/     Generator + Judge prompts
  eval/        Use cases + baseline checklist + sample spec
  docs/        Architecture
```

---

## Lỗi thường gặp

| Triệu chứng | Cách xử lý |
|-------------|------------|
| `ModuleNotFoundError: No module named 'app'` | Đang không đứng trong `backend/`. `cd .../backend` rồi chạy lại uvicorn |
| `uvicorn: command not found` | `source .venv/bin/activate` hoặc dùng `python -m uvicorn ...` |
| Frontend gọi API lỗi / Network Error | Backend chưa chạy, hoặc sai port (phải là 8000) |
| LLM lỗi / thiếu key | Đặt `MOCK_LLM=1` trong `.env`, hoặc điền `GROQ_API_KEY` và `MOCK_LLM=0` |
| `npm install` 403 (registry công ty) | Dùng registry nội bộ NAB hoặc hỏi admin npm; frontend cần `node_modules` trước khi `npm run dev` |