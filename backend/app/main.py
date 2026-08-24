import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.engine import make_url
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import router
from app.config import get_settings
from app.db import init_db
from app.db import models as db_models

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


def _redacted_database_url(database_url: str) -> str:
    """Render a database URL without exposing its password."""
    return make_url(database_url).render_as_string(hide_password=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    logger.info("Database URL: %s", _redacted_database_url(settings.database_url))
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
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "%s %s → unhandled error (%.0f ms)",
                request.method,
                request.url.path,
                elapsed_ms,
            )
            raise
        else:
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
    db_file = settings.sqlite_file

    # Lightweight DB connectivity check
    db_ok = False
    session_count: int | None = None
    try:
        with db_models.SessionLocal() as db:
            db.execute(text("SELECT 1"))
            session_count = db.query(db_models.SessionRow).count()
            db_ok = True
    except Exception:  # noqa: BLE001
        logger.exception("Database health check failed")

    return {
        "status": "ok" if db_ok else "degraded",
        "version": app.version,
        "mock_llm": settings.mock_llm or not bool(settings.groq_api_key),
        "model": settings.groq_model,
        "database_url": _redacted_database_url(settings.database_url),
        "db_file": str(db_file) if db_file else None,
        "db_exists": db_file.exists() if db_file else None,
        "db_connected": db_ok,
        "session_count": session_count,
    }
