import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import router
from app.config import get_settings
from app.db import init_db

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_LOG_DATE = "%Y-%m-%d %H:%M:%S"


def _configure_logging() -> None:
    """Set up root logger with a human-readable format.

    The level defaults to INFO but can be overridden via the LOG_LEVEL
    environment variable (DEBUG, WARNING, etc.).
    """
    import os

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(format=_LOG_FORMAT, datefmt=_LOG_DATE, level=level, force=True)
    # Silence noisy third-party loggers in non-debug mode
    if level > logging.DEBUG:
        for noisy in ("httpx", "httpcore", "uvicorn.access"):
            logging.getLogger(noisy).setLevel(logging.WARNING)


_configure_logging()

settings = get_settings()
logger = logging.getLogger("specresearch")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    logger.info("Database URL: %s", settings.database_url)
    db_file = settings.sqlite_file
    if db_file is not None:
        logger.info("SQLite file: %s (exists=%s)", db_file, db_file.exists())
    yield


# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------


class _RequestLogMiddleware(BaseHTTPMiddleware):
    """Log every request with method, path, status code, and duration."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s → %s (%.0f ms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(title="SpecResearch Loop API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(_RequestLogMiddleware)
app.include_router(router)


@app.get("/health")
def health():
    """Liveness / readiness probe.

    Returns database connectivity status and basic runtime info so
    operators can verify the backend is fully functional — not just
    that the process is alive.
    """
    from app.db import get_db
    from app.db.models import SessionRow

    db_file = settings.sqlite_file

    # Lightweight DB connectivity check
    db_ok = False
    session_count: int | None = None
    try:
        db = next(get_db())
        db.execute(SessionRow.__table__.select().limit(0))  # essentially SELECT 1
        session_count = db.query(SessionRow).count()
        db_ok = True
    except Exception:  # noqa: BLE001
        db_ok = False
    finally:
        try:
            db.close()
        except Exception:  # noqa: BLE001
            pass

    return {
        "status": "ok" if db_ok else "degraded",
        "version": app.version,
        "mock_llm": settings.mock_llm or not bool(settings.groq_api_key),
        "model": settings.groq_model,
        "database_url": settings.database_url,
        "db_file": str(db_file) if db_file else None,
        "db_exists": db_file.exists() if db_file else None,
        "db_connected": db_ok,
        "session_count": session_count,
    }

