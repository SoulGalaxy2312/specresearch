from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from app.config import get_settings

PROMPTS_ROOT = Path(__file__).resolve().parents[3] / "prompts"

def load_prompt(relative_path: str) -> str:
    path = PROMPTS_ROOT / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

def extract_json(text: str) -> Any:
    text = text.strip()
    if (text.startswith("```")):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}|\[[\s\S*\]", text)
        if match:
            return json.loads(match.group(0))
        raise

class GroqClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def chat_json(
        self,
        system: str,
        user: str,
        *,
        temperature: float = 0.3,
        mock_payload: Optional[dict[str, Any] | list[Any]] = None
    ) -> Any:
        if self.settings.mock_llm or not self.settings.groq_api_key:
            if mock_payload is not None:
                return mock_payload
            return {"error": "MOCK_LLM without payload"}

        from groq import Groq

        client = Groq(api_key=self.settings.groq_api_key)
        last_err: Exception | None = None
        for _ in range(2):
            try:
                completion = client.chat.completions.create(
                    model=self.settings.groq_model,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    response_format={"type": "json_object"},
                )
                content = completion.choices[0].message.content or "{}"
                return extract_json(content)
            except Exception as exc: # noqa: BLE001
                last_err = exc

        raise RuntimeError(f"Groq call failed after retry: {last_err}")

    def chat_text(self, system: str, user: str, *, temperature: float = 0.3, mock_text: str = "") -> str:
        if self.settings.mock_llm or not self.settings.groq_api_key:
            return mock_text
        from groq import Groq

        client = Groq(api_key=self.settings.groq_api_key)
        last_err: Exception | None = None
        for _ in range(2):
            try:
                completion = client.chat.completions.create(
                    model=self.settings.groq_model,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ]
                )
                return completion.choices[0].message.content or ""
            except Exception as exc: # noqa: BLE001
                last_err = exc
        raise RuntimeError(f"Groq call failed after retry: {last_err}")