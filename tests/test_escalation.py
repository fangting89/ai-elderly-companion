"""Unit tests for escalation rule evaluation, against an isolated in-memory DB
(not the real data/app.db) so nothing here touches real data.
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from backend import escalation

SCHEMA_PATH = Path(__file__).parent.parent / "sql" / "schema.sql"


@pytest.fixture
def conn(monkeypatch):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA_PATH.read_text())
    connection.execute(
        "insert into profiles (id, role, display_name) values ('elder-1', 'elder', 'Test Elder')"
    )
    connection.commit()
    monkeypatch.setattr(escalation, "get_connection", lambda: connection)
    return connection


def _alert_count(conn, alert_type: str | None = None) -> int:
    if alert_type is None:
        return conn.execute("select count(*) from alerts").fetchone()[0]
    return conn.execute(
        "select count(*) from alerts where alert_type = ?", (alert_type,)
    ).fetchone()[0]


def test_distress_sentiment_always_escalates(conn):
    escalation.check_and_alert("elder-1", "chat_sentiment", {"sentiment": "distress"})
    assert _alert_count(conn, "distress") == 1


def test_single_low_sentiment_does_not_escalate(conn):
    escalation.check_and_alert("elder-1", "chat_sentiment", {"sentiment": "low"})
    assert _alert_count(conn) == 0


def test_positive_and_neutral_never_escalate(conn):
    escalation.check_and_alert("elder-1", "chat_sentiment", {"sentiment": "positive"})
    escalation.check_and_alert("elder-1", "chat_sentiment", {"sentiment": "neutral"})
    assert _alert_count(conn) == 0


def test_scam_detected_always_escalates(conn):
    escalation.check_and_alert(
        "elder-1", "scam_detected", {"risk_level": "high", "summary": "test scam"}
    )
    assert _alert_count(conn, "scam_detected") == 1


def _insert_medication(conn):
    conn.execute(
        "insert into medications (id, elder_id, name, dosage, times_per_day) "
        "values ('med-1', 'elder-1', 'Aspirin', '1 tablet', '[]')"
    )
    conn.commit()


def test_first_missed_medication_does_not_escalate(conn):
    _insert_medication(conn)
    conn.execute(
        "insert into medication_logs (id, medication_id, elder_id, scheduled_for, status) "
        "values ('log-1', 'med-1', 'elder-1', '2026-01-01 08:00:00', 'missed')"
    )
    conn.commit()
    escalation.check_and_alert(
        "elder-1", "missed_medication", {"medication_id": "med-1", "medication_name": "Aspirin"}
    )
    assert _alert_count(conn, "missed_medication") == 0


def test_repeat_missed_medication_escalates(conn):
    _insert_medication(conn)
    for day, log_id in (("01", "log-1"), ("02", "log-2")):
        conn.execute(
            "insert into medication_logs (id, medication_id, elder_id, scheduled_for, status) "
            "values (?, 'med-1', 'elder-1', ?, 'missed')",
            (log_id, f"2026-01-{day} 08:00:00"),
        )
    conn.commit()
    escalation.check_and_alert(
        "elder-1", "missed_medication", {"medication_id": "med-1", "medication_name": "Aspirin"}
    )
    assert _alert_count(conn, "missed_medication") == 1


def _insert_repeated_question_message(conn, when: datetime):
    conn.execute(
        "insert into chat_messages "
        "(id, elder_id, sender, content, repeated_question_flag, created_at) "
        "values (?, 'elder-1', 'elder', 'what time is it', 1, ?)",
        (str(uuid.uuid4()), when.strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()


def test_single_repeated_question_this_week_does_not_escalate(conn):
    _insert_repeated_question_message(conn, datetime.now() - timedelta(days=1))
    escalation.check_and_alert("elder-1", "repeated_question", {})
    assert _alert_count(conn, "repeated_question_increase") == 0


def test_rising_repeated_questions_escalates(conn):
    for days_ago in (1, 2):
        _insert_repeated_question_message(conn, datetime.now() - timedelta(days=days_ago))
    escalation.check_and_alert("elder-1", "repeated_question", {})
    assert _alert_count(conn, "repeated_question_increase") == 1


def test_stable_repeated_questions_does_not_escalate(conn):
    # 2 this week, 3 last week -- not rising, shouldn't alert.
    for days_ago in (1, 2):
        _insert_repeated_question_message(conn, datetime.now() - timedelta(days=days_ago))
    for days_ago in (8, 9, 10):
        _insert_repeated_question_message(conn, datetime.now() - timedelta(days=days_ago))
    escalation.check_and_alert("elder-1", "repeated_question", {})
    assert _alert_count(conn, "repeated_question_increase") == 0


def test_email_stub_fires_for_high_priority_alerts_only(conn, capsys):
    escalation.check_and_alert("elder-1", "chat_sentiment", {"sentiment": "distress"})
    assert "[email stub]" in capsys.readouterr().out

    _insert_medication(conn)
    for day, log_id in (("01", "log-1"), ("02", "log-2")):
        conn.execute(
            "insert into medication_logs (id, medication_id, elder_id, scheduled_for, status) "
            "values (?, 'med-1', 'elder-1', ?, 'missed')",
            (log_id, f"2026-01-{day} 08:00:00"),
        )
    conn.commit()
    escalation.check_and_alert(
        "elder-1", "missed_medication", {"medication_id": "med-1", "medication_name": "Aspirin"}
    )
    assert "[email stub]" not in capsys.readouterr().out
