import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings
from app.db import init_db

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


app = FastAPI(title="SpecResearch Loop API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/health")
def health():
    db_file = settings.sqlite_file
    return {
        "status": "ok",
        "mock_llm": settings.mock_llm or not bool(settings.groq_api_key),
        "model": settings.groq_model,
        "database_url": settings.database_url,
        "db_file": str(db_file) if db_file else None,
        "db_exists": db_file.exists() if db_file else None,
    }
