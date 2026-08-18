import pytest

from app.integrations.groq_client import extract_json


def test_extract_json_from_plain_object():
    assert extract_json('{"ok": true, "items": [1, 2]}') == {"ok": True, "items": [1, 2]}


def test_extract_json_from_fenced_block():
    assert extract_json('```json\n{"answer": "yes"}\n```') == {"answer": "yes"}


def test_extract_json_from_embedded_text_with_nested_braces():
    payload = 'Result:\n{"text": "brace } inside string", "nested": {"value": 1}}\nThanks'
    assert extract_json(payload) == {"text": "brace } inside string", "nested": {"value": 1}}


def test_extract_json_from_embedded_array():
    assert extract_json('prefix [{"a": 1}, {"b": 2}] suffix') == [{"a": 1}, {"b": 2}]


def test_extract_json_raises_on_invalid_payload():
    with pytest.raises(ValueError):
        extract_json("no json here")
