from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Optional

from app.config import get_settings

PROMPTS_ROOT = Path(__file__).resolve().parents[3] / "prompts"
logger = logging.getLogger(__name__)

def load_prompt(relative_path: str) -> str:
    path = PROMPTS_ROOT / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

def extract_json(text: str) -> Any:
    text = text.strip()

    # 1. Remove <think>...</think>
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    ).strip()

    # 2. Remove markdown code fence
    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"\s*```$",
            "",
            text,
        ).strip()

    # 3. Try parsing the whole response
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 4. Find the first JSON object/array
    object_start = text.find("{")
    array_start = text.find("[")

    pairs = (
        (("[", "]"), ("{", "}"))
        if array_start != -1
        and (object_start == -1 or array_start < object_start)
        else (("{", "}"), ("[", "]"))
    )

    for start, end in pairs:
        candidate = _extract_balanced_json(text, start, end)

        if candidate:
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

    # 5. Let json.loads raise the original error
    return json.loads(text)


def _extract_balanced_json(text: str, start_char: str, end_char: str) -> str | None:
    start = text.find(start_char)
    if start == -1:
        return None

    depth = 0
    in_string = False
    escaped = False
    for idx in range(start, len(text)):
        char = text[idx]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == start_char:
            depth += 1
        elif char == end_char:
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]

    return None

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

        from groq import Groq, APIStatusError
        import time
        import re

        client = Groq(
            api_key=self.settings.groq_api_key,
            max_retries=0,
        )
        last_err: Exception | None = None
        for attempt in range(1, 3):
            try:
                completion = client.chat.completions.create(
                    model=self.settings.groq_model,
                    temperature=temperature,
                    max_completion_tokens=2048,
                    reasoning_effort="none",
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    response_format={"type": "json_object"},
                )
                content = completion.choices[0].message.content or "{}"
                print("===== GROQ RESULT =====")
                print("finish_reason =", completion.choices[0].finish_reason)
                print("content length =", len(content))
                print("content head =", repr(content[:500]))
                print("content tail =", repr(content[-1000:]))
                print("=======================")
                return extract_json(content)

            except APIStatusError as exc:
                last_err = exc

                print("===== GROQ ERROR =====")
                print("attempt =", attempt)
                print("status_code =", exc.status_code)
                print("type =", type(exc).__name__)
                print("str =", str(exc))
                print("======================")

                if exc.status_code in (400, 413):
                    raise

                if exc.status_code == 429 and attempt < 2:
                    match = re.search(
                        r"try again in ([\d.]+)s",
                        str(exc),
                    )

                    wait_seconds = float(match.group(1)) if match else 35.0

                    print(f"Rate limited. Waiting {wait_seconds:.1f}s...")
                    time.sleep(wait_seconds + 1)

                    continue

                if attempt == 2:
                    raise
                
            except Exception as exc:
                last_err = exc

                print("===== GROQ ERROR =====")
                print("attempt =", attempt)
                print("type =", type(exc).__name__)
                print("repr =", repr(exc))
                print("str =", str(exc))
                print("======================")

                logger.exception(
                    "Groq JSON request failed "
                    "(attempt %d/2, model=%s)",
                    attempt,
                    self.settings.groq_model,
                )

        raise RuntimeError("Groq call failed after retry") from last_err

    def chat_text(self, system: str, user: str, *, temperature: float = 0.3, mock_text: str = "") -> str:
        if self.settings.mock_llm or not self.settings.groq_api_key:
            return mock_text
        from groq import Groq

        client = Groq(api_key=self.settings.groq_api_key)
        last_err: Exception | None = None
        for attempt in range(1, 3):
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
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                logger.warning(
                    "Groq text request failed (attempt %s/2, model=%s, error=%s)",
                    attempt,
                    self.settings.groq_model,
                    type(exc).__name__,
                )
        raise RuntimeError("Groq call failed after retry") from last_err
