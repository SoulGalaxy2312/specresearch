from __future__ import annotations

import re


def verify_statement_against_abstract(statement: str, abstract: str | None) -> str:
    if not abstract or not abstract.strip():
        return "UNVERIFIABLE"
    stmt_tokens = set(_tokens(statement))
    abs_tokens = set(_tokens(abstract))
    if not stmt_tokens:
        return "UNVERIFIABLE"
    overlap = len(stmt_tokens & abs_tokens) / max(1, len(stmt_tokens))
    if overlap >= 0.35:
        return "SUPPORTS"
    if overlap >= 0.15:
        return "PARTIAL"
    return "NOT"


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-zA-ZÀ-ỹ0-9]{3,}", text.lower()) if t not in _STOP]


_STOP = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "are",
    "was",
    "were",
    "các",
    "và",
    "của",
    "cho",
    "một",
    "những",
    "trong",
    "được",
    "là",
}