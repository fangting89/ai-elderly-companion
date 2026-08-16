"""Unit tests for companion_line's daily-opener priority logic (family nudge
> reminiscence > daily check-in), against an isolated in-memory DB with the
Claude call mocked out -- no real API cost.
"""

import importlib
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from backend import companion_line

SCHEMA_PATH = Path(__file__).parent.parent / "sql" / "schema.sql"

_MODULES_USING_GET_CONNECTION = [
    "backend.db",
    "backend.companion_line",
    "backend.memory_bank",
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


def _add_family(conn, elder_id: str, name: str = "Mei Lin") -> None:
    conn.execute(
        "insert into profiles (id, role, display_name, elder_id) values (?, 'family', ?, ?)",
        (str(uuid.uuid4()), name, elder_id),
    )
    conn.commit()


def _log_event(conn, elder_id: str, event_type: str, days_ago: int) -> None:
    when = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "insert into companion_events (id, elder_id, event_type, created_at) values (?, ?, ?, ?)",
        (str(uuid.uuid4()), elder_id, event_type, when),
    )
    conn.commit()


def test_already_chatted_today_returns_none(elder_id, monkeypatch):
    conn = companion_line.get_connection()
    conn.execute(
        "insert into chat_messages (id, elder_id, sender, content) "
        "values (?, ?, 'elder', 'hello')",
        (str(uuid.uuid4()), elder_id),
    )
    conn.commit()
    assert companion_line.decide_todays_opener(elder_id, "English") is None


def test_no_family_no_facts_falls_back_to_daily_checkin(elder_id):
    _, line_type = companion_line.decide_todays_opener(elder_id, "English")
    assert line_type == "daily_checkin"


def test_family_never_mentioned_triggers_nudge(elder_id):
    conn = companion_line.get_connection()
    _add_family(conn, elder_id)
    text, line_type = companion_line.decide_todays_opener(elder_id, "English")
    assert line_type == "family_nudge"
    assert "Mei Lin" in text
    row = conn.execute(
        "select 1 from companion_events where elder_id = ? and event_type = 'family_nudge_shown'",
        (elder_id,),
    ).fetchone()
    assert row is not None


def test_family_nudge_on_cooldown_falls_through(elder_id):
    conn = companion_line.get_connection()
    _add_family(conn, elder_id)
    # Shown yesterday -- within FAMILY_NUDGE_COOLDOWN_DAYS, shouldn't repeat.
    _log_event(conn, elder_id, "family_nudge_shown", days_ago=1)
    _, line_type = companion_line.decide_todays_opener(elder_id, "English")
    assert line_type == "daily_checkin"


def test_family_recently_mentioned_skips_nudge(elder_id):
    conn = companion_line.get_connection()
    _add_family(conn, elder_id, name="Mei Lin")
    # Mentioned yesterday, not today -- today must stay chat-free, or the
    # "already chatted today" guard would return None before this logic
    # is even reached.
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "insert into chat_messages (id, elder_id, sender, content, created_at) "
        "values (?, ?, 'elder', 'I spoke to Mei Lin yesterday', ?)",
        (str(uuid.uuid4()), elder_id, yesterday),
    )
    conn.commit()
    _, line_type = companion_line.decide_todays_opener(elder_id, "English")
    assert line_type == "daily_checkin"


def test_reminiscence_used_when_nudge_not_applicable(elder_id, monkeypatch):
    conn = companion_line.get_connection()
    from backend import memory_bank

    memory_bank.add_fact(elder_id, elder_id, "Loves gardening, especially roses.")
    monkeypatch.setattr(companion_line, "generate_reminiscence_prompt", lambda *a, **k: "opener")

    text, line_type = companion_line.decide_todays_opener(elder_id, "English")
    assert line_type == "reminiscence"
    assert text == "opener"
    row = conn.execute(
        "select 1 from companion_events where elder_id = ? and event_type = 'reminiscence_shown'",
        (elder_id,),
    ).fetchone()
    assert row is not None


def test_reminiscence_on_cooldown_falls_to_daily_checkin(elder_id, monkeypatch):
    conn = companion_line.get_connection()
    from backend import memory_bank

    memory_bank.add_fact(elder_id, elder_id, "Loves gardening, especially roses.")
    _log_event(conn, elder_id, "reminiscence_shown", days_ago=1)
    monkeypatch.setattr(companion_line, "generate_reminiscence_prompt", lambda *a, **k: "opener")

    _, line_type = companion_line.decide_todays_opener(elder_id, "English")
    assert line_type == "daily_checkin"


def test_get_todays_line_type_defaults_to_daily_checkin(elder_id):
    assert companion_line.get_todays_line_type(elder_id) == "daily_checkin"


def test_get_todays_line_type_reflects_family_nudge_shown(elder_id):
    conn = companion_line.get_connection()
    _log_event(conn, elder_id, "family_nudge_shown", days_ago=0)
    assert companion_line.get_todays_line_type(elder_id) == "family_nudge"


def test_family_nudge_accepted_today_false_by_default(elder_id):
    assert companion_line.family_nudge_accepted_today(elder_id) is False


def test_family_nudge_accepted_today_true_after_logging(elder_id):
    companion_line.log_family_nudge_accepted(elder_id)
    assert companion_line.family_nudge_accepted_today(elder_id) is True
