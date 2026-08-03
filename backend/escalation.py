"""Escalation rules engine.

check_and_alert() is the single entry point every feature module calls when
something might warrant a family alert. It owns the rule evaluation (the
Escalation Rules table in docs/DESIGN_PRINCIPLES.md) so callers just report
what happened; whether that rises to an alert is decided here.

Built incrementally: chat-sentiment, scam-detection, missed-medication, and
repeated-question-frequency rules all exist now.
"""

import uuid
from datetime import date, datetime, timedelta
from typing import Any, Literal

from backend.db import get_connection

TriggerType = Literal["chat_sentiment", "scam_detected", "missed_medication", "repeated_question"]

_HIGH_PRIORITY_ALERT_TYPES = {"distress", "scam_detected"}


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
    elif trigger_type == "repeated_question":
        _handle_repeated_question(elder_id, context)


def _handle_scam_detected(elder_id: str, context: dict[str, Any]) -> None:
    risk_level = context.get("risk_level", "medium")
    summary = context.get("summary", "")
    _write_alert(
        elder_id,
        "scam_detected",
        f"A {risk_level}-risk scam message was detected and blocked before any "
        f"harm was done. {summary}",
    )


def _handle_missed_medication(elder_id: str, context: dict[str, Any]) -> None:
    medication_id = context.get("medication_id")
    medication_name = context.get("medication_name", "a medication")
    conn = get_connection()
    prior_missed_count = conn.execute(
        "select count(*) from medication_logs where medication_id = ? and status = 'missed'",
        (medication_id,),
    ).fetchone()[0]
    if prior_missed_count < 2:
        return

    # Without this check, every subsequent missed dose past the 2nd re-fires
    # a new alert for the same ongoing pattern instead of one. Once family
    # acknowledges it, a fresh miss is allowed to alert again -- that's
    # correct, since acknowledgment means they've seen the current pattern.
    already_open = conn.execute(
        "select 1 from alerts where elder_id = ? and alert_type = 'missed_medication' "
        "and status = 'open' and message like ? limit 1",
        (elder_id, f"%{medication_name}%"),
    ).fetchone()
    if already_open is not None:
        return

    _write_alert(
        elder_id,
        "missed_medication",
        f"Repeated missed doses of {medication_name} were detected "
        "(already shown as missed on the Medication page).",
    )


def get_repeated_question_weekly_counts(elder_id: str) -> tuple[int, int]:
    """Count repeated-question chat messages this week vs. the prior week.

    Shared by the escalation rule below and the family dashboard's frequency
    panel, so the two never drift apart on what "this week" means.

    Args:
        elder_id: the elder profile to check.

    Returns:
        tuple[int, int]: (this_week_count, last_week_count), rolling 7-day windows.
    """
    conn = get_connection()
    now = datetime.now()
    this_week_start = now - timedelta(days=7)
    last_week_start = now - timedelta(days=14)

    this_week_count = conn.execute(
        "select count(*) from chat_messages where elder_id = ? and sender = 'elder' "
        "and repeated_question_flag = 1 and created_at >= ?",
        (elder_id, this_week_start.strftime("%Y-%m-%d %H:%M:%S")),
    ).fetchone()[0]
    last_week_count = conn.execute(
        "select count(*) from chat_messages where elder_id = ? and sender = 'elder' "
        "and repeated_question_flag = 1 and created_at >= ? and created_at < ?",
        (
            elder_id,
            last_week_start.strftime("%Y-%m-%d %H:%M:%S"),
            this_week_start.strftime("%Y-%m-%d %H:%M:%S"),
        ),
    ).fetchone()[0]
    return this_week_count, last_week_count


def _handle_repeated_question(elder_id: str, context: dict[str, Any]) -> None:
    this_week, last_week = get_repeated_question_weekly_counts(elder_id)
    # Require at least 2 this week, not just any non-zero increase, so a
    # single one-off repeated question doesn't trigger a false alarm.
    if this_week >= 2 and this_week > last_week:
        _write_alert(
            elder_id,
            "repeated_question_increase",
            f"Repeated questions have increased this week ({this_week} vs {last_week} "
            "last week), which may be worth a check-in call.",
        )


def _handle_chat_sentiment(elder_id: str, context: dict[str, Any]) -> None:
    sentiment = context.get("sentiment")
    if sentiment == "distress":
        _write_alert(
            elder_id,
            "distress",
            "A recent message suggested significant distress. The companion "
            "responded with support and encouraged reaching out to family or "
            "a professional.",
        )
    elif sentiment == "low" and _low_mood_streak_days(elder_id) >= 3:
        _write_alert(
            elder_id,
            "sentiment_decline",
            "Low mood has been detected for 3 or more consecutive days. The "
            "companion has continued checking in warmly each day.",
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
    if alert_type in _HIGH_PRIORITY_ALERT_TYPES:
        _send_email_notification(elder_id, alert_type, message)


def _send_email_notification(elder_id: str, alert_type: str, message: str) -> None:
    """Send (or, without an email provider configured, log) a family notification.

    No provider (Resend/SendGrid) is wired up for this POC -- logging here
    stands in for the real call so the trigger path is complete and the
    actual send is a drop-in swap later.

    Args:
        elder_id: the elder profile the alert concerns.
        alert_type: which Escalation Rule triggered this.
        message: the alert's human-readable text.
    """
    print(f"[email stub] High-priority alert for elder {elder_id} ({alert_type}): {message}")
