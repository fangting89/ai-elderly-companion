"""Escalation rules engine.

check_and_alert() is the single entry point every feature module calls when
something might warrant a family alert. It owns the rule evaluation (the
Escalation Rules table in BUILD_PLAN.md) so callers just report what
happened; whether that rises to an alert is decided here.

Built incrementally: chat-sentiment, scam-detection, and missed-medication
rules exist so far. The repeated-question-frequency rule is still to come,
added without changing any existing call site.
"""

import uuid
from datetime import date, datetime, timedelta
from typing import Any, Literal

from backend.db import get_connection

TriggerType = Literal["chat_sentiment", "scam_detected", "missed_medication", "repeated_question"]


def check_and_alert(elder_id: str, trigger_type: TriggerType, context: dict[str, Any]) -> None:
    """Evaluate an escalation rule for a reported event, alerting if it applies.

    Args:
        elder_id: the elder profile this event concerns.
        trigger_type: which kind of event just happened.
        context: event-specific details used to evaluate the rule.
    """
    if trigger_type == "chat_sentiment":
        _handle_chat_sentiment(elder_id, context)
    elif trigger_type == "scam_detected":
        _handle_scam_detected(elder_id, context)
    elif trigger_type == "missed_medication":
        _handle_missed_medication(elder_id, context)


def _handle_scam_detected(elder_id: str, context: dict[str, Any]) -> None:
    risk_level = context.get("risk_level", "medium")
    summary = context.get("summary", "")
    _write_alert(
        elder_id, "scam_detected", f"A {risk_level}-risk scam attempt was detected: {summary}"
    )


def _handle_missed_medication(elder_id: str, context: dict[str, Any]) -> None:
    medication_id = context.get("medication_id")
    medication_name = context.get("medication_name", "a medication")
    prior_missed_count = (
        get_connection()
        .execute(
            "select count(*) from medication_logs where medication_id = ? and status = 'missed'",
            (medication_id,),
        )
        .fetchone()[0]
    )
    if prior_missed_count >= 2:
        _write_alert(
            elder_id, "missed_medication", f"Repeated missed doses detected for {medication_name}."
        )


def _handle_chat_sentiment(elder_id: str, context: dict[str, Any]) -> None:
    sentiment = context.get("sentiment")
    if sentiment == "distress":
        _write_alert(elder_id, "distress", "A recent message suggested significant distress.")
    elif sentiment == "low" and _low_mood_streak_days(elder_id) >= 3:
        _write_alert(
            elder_id,
            "sentiment_decline",
            "Low mood has been detected for 3 or more consecutive days.",
        )


def _low_mood_streak_days(elder_id: str) -> int:
    """Count consecutive most-recent days (ending today) with a low/distress message."""
    rows = (
        get_connection()
        .execute(
            """
        select distinct date(created_at) as day
        from chat_messages
        where elder_id = ? and sender = 'elder' and sentiment in ('low', 'distress')
        order by day desc
        """,
            (elder_id,),
        )
        .fetchall()
    )
    streak = 0
    expected = date.today()
    for row in rows:
        day = datetime.strptime(row["day"], "%Y-%m-%d").date()
        if day == expected:
            streak += 1
            expected -= timedelta(days=1)
        else:
            break
    return streak


def _write_alert(elder_id: str, alert_type: str, message: str) -> None:
    conn = get_connection()
    conn.execute(
        "insert into alerts (id, elder_id, alert_type, message) values (?, ?, ?, ?)",
        (str(uuid.uuid4()), elder_id, alert_type, message),
    )
    conn.commit()
