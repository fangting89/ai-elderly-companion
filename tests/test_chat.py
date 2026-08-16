"""Unit tests for backend.chat's bounded Check-In extension logic, against an
isolated in-memory DB with the Claude calls mocked out -- no real API cost.

backend.chat.send_message touches several other modules internally (get_profile,
check_and_alert, get_context_facts), each of which has its own bound
`get_connection` from `from backend.db import get_connection` -- so, matching the
pattern in test_api.py, every one of them needs patching to the same shared
in-memory connection, or a call would fall through to the real data/app.db.
"""

import importlib
import sqlite3
import uuid
from pathlib import Path

import pytest

from backend import chat

SCHEMA_PATH = Path(__file__).parent.parent / "sql" / "schema.sql"

_MODULES_USING_GET_CONNECTION = [
    "backend.db",
    "backend.chat",
    "backend.escalation",
    "backend.memory_bank",
    "backend.companion_line",
]


@pytest.fixture
def elder_id(monkeypatch):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA_PATH.read_text())
    elder_id = str(uuid.uuid4())
    connection.execute(
        "insert into profiles (id, role, display_name, preferred_language) "
        "values (?, 'elder', 'Test Elder', 'English')",
        (elder_id,),
    )
    connection.commit()

    for module_name in _MODULES_USING_GET_CONNECTION:
        module = importlib.import_module(module_name)
        monkeypatch.setattr(module, "get_connection", lambda conn=connection: conn)

    return elder_id


def _mock_claude(monkeypatch, sentiment: str, reply_text: str = "A reply.") -> dict:
    """Mock both Claude calls send_message makes, capturing the system prompt."""
    captured = {}

    def fake_call_structured(**kwargs):
        return {
            "sentiment": sentiment,
            "repeated_question_flag": False,
        }

    def fake_call_prose(*, model, system, messages):
        captured["system"] = system
        return reply_text

    monkeypatch.setattr(chat, "call_structured", fake_call_structured)
    monkeypatch.setattr(chat, "call_prose", fake_call_prose)
    return captured


def test_unbounded_never_offers_continuation(elder_id, monkeypatch):
    # send_message defaults to bounded=False -- even on a distressed
    # message, can_continue should stay False and the closing instruction
    # should never be added to the prompt.
    captured = _mock_claude(monkeypatch, sentiment="distress")
    result = chat.send_message(elder_id, "I feel very alone")
    assert result.can_continue is False
    assert "last message" not in captured["system"]


def test_bounded_first_reply_positive_does_not_extend(elder_id, monkeypatch):
    _mock_claude(monkeypatch, sentiment="positive")
    result = chat.send_message(elder_id, "I feel great today", bounded=True)
    assert result.can_continue is False


def test_bounded_first_reply_low_mood_offers_one_extension(elder_id, monkeypatch):
    captured = _mock_claude(monkeypatch, sentiment="distress")
    result = chat.send_message(elder_id, "I am feeling sad today", bounded=True)
    assert result.can_continue is True
    assert "last message" not in captured["system"]


def test_bounded_second_reply_always_closes(elder_id, monkeypatch):
    _mock_claude(monkeypatch, sentiment="distress")
    chat.send_message(elder_id, "I am feeling sad today", bounded=True)

    captured = _mock_claude(monkeypatch, sentiment="distress")
    result = chat.send_message(elder_id, "It has been a hard week", bounded=True)
    assert result.can_continue is False
    assert "last message" in captured["system"]
