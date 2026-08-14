from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    mock_llm: bool = False
    openalex_mailto: str = "specresearch@example.com"
    database_url: str = "sqlite:///./specresearch.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_revise_rounds: int = 2
    related_work_limit: int = 10

    @field_validator("database_url")
    @classmethod
    def resolve_relative_sqlite_path(cls, value: str) -> str:
        """SQLite paths are cwd-relative by default, which makes the db file land
        wherever uvicorn was launched from. Anchor them to backend/ instead."""
        if not value.startswith("sqlite"):
            return value
        scheme, separator, path_part = value.partition(":///")
        if not separator or not path_part or path_part.startswith(":memory:"):
            return value
        path = Path(path_part)
        if path.is_absolute():
            return value
        return f"{scheme}:///{(BACKEND_DIR / path).resolve().as_posix()}"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def sqlite_file(self) -> Path | None:
        if not self.database_url.startswith("sqlite"):
            return None
        _, _, path_part = self.database_url.partition(":///")
        if not path_part or path_part.startswith(":memory:"):
            return None
        return Path(path_part)


@lru_cache
def get_settings() -> Settings:
    return Settings()
