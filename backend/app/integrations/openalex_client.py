from __future__ import annotations

from typing import Any
from uuid import uuid4

import httpx

from app.config import get_settings

class OpenAlexClient:
    BASE = "https://api.openalex.org/works"

    def __init__(self) -> None:
        self.settings = get_settings()

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        params = {
            "search": query,
            "per_page": limit,
            "mailto": self.settings.openalex_mailto
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(self.BASE, params = params)
                resp.raise_for_status()
                data = resp.json()
        except Exception: # noqa: BLE001
            return []

        results: list[dict[str, Any]] = []
        for item in data.get("results", [])[:limit]:
            authorships = item.get("authorships") or []
            authors = []
            for a in authorships[:8]:
                name = (a.get("author") or {}).get("display_name")
                if name:
                    authors.append(name)
            abstract = _invert_abstract(item.get("abstract_inverted_index"))
            primary = item.get("primary_location") or {}
            landing = primary.get("landing_page_url") or item.get("id") or ""
            results.append(
                {
                    "id": str(uuid4()),
                    "openalex_id": item.get("id"),
                    "title": item.get("display_name") or "Untitled",
                    "year": item.get("publication_year"),
                    "authors": authors,
                    "abstract": abstract,
                    "doi_url": landing,
                    "cited_by_count": item.get("cited_by_count") or 0,
                }
            )
        return results

def _invert_abstract(inverted: dict[str, list[int]] | None) -> str | None:
    if not inverted:
        return None
    positions: list[tuple[int, str]] = []
    for word, idxs in inverted.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort(key=lambda x: x[0])
    return " ".join(w for _, w in positions)