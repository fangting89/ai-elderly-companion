"""Read-only aggregate queries for the family dashboard.

No alert generation happens here -- backend.escalation already writes alerts
at the point each trigger occurs; this module only reads what's already there.
"""

from datetime import date, timedelta

from backend.db import get_connection

_SENTIMENT_SCORE = {"distress": 0, "low": 1, "neutral": 2, "positive": 3}


def get_adherence_by_day(elder_id: str, days: int = 7) -> list[dict]:
    """Return daily medication dose status counts for the last N days.

    Args:
        elder_id: the elder profile to fetch adherence for.
        days: how many trailing days to include.

    Returns:
        list[dict]: long-format rows of {"date", "status", "count"}, suitable
            for a stacked bar chart.
    """
    start = (date.today() - timedelta(days=days - 1)).isoformat()
    rows = (
        get_connection()
        .execute(
            "select date(scheduled_for) as day, status, count(*) as count "
            "from medication_logs where elder_id = ? and date(scheduled_for) >= ? "
            "group by day, status order by day asc",
            (elder_id, start),
        )
        .fetchall()
    )
    return [{"date": row["day"], "status": row["status"], "count": row["count"]} for row in rows]


def get_sentiment_trend(elder_id: str, days: int = 14) -> list[dict]:
    """Return the average daily chat sentiment score for the last N days.

    Args:
        elder_id: the elder profile to fetch the trend for.
        days: how many trailing days to include.

    Returns:
        list[dict]: rows of {"date", "score"}. Sentiment is mapped
            distress=0, low=1, neutral=2, positive=3 and averaged per day;
            days with no messages are omitted.
    """
    start = (date.today() - timedelta(days=days - 1)).isoformat()
    rows = (
        get_connection()
        .execute(
            "select date(created_at) as day, sentiment from chat_messages "
            "where elder_id = ? and sender = 'elder' and sentiment is not null "
            "and date(created_at) >= ? order by day asc",
            (elder_id, start),
        )
        .fetchall()
    )
    by_day: dict[str, list[int]] = {}
    for row in rows:
        by_day.setdefault(row["day"], []).append(_SENTIMENT_SCORE[row["sentiment"]])
    return [
        {"date": day, "score": sum(scores) / len(scores)} for day, scores in sorted(by_day.items())
    ]


def get_alerts(elder_id: str, limit: int = 20) -> list[dict]:
    """Return recent alerts for an elder, most recent first.

    Args:
        elder_id: the elder profile to fetch alerts for.
        limit: max number of alerts to return.

    Returns:
        list[dict]: rows with id, alert_type, message, status, created_at.
    """
    rows = (
        get_connection()
        .execute(
            "select id, alert_type, message, status, created_at from alerts "
            "where elder_id = ? order by created_at desc limit ?",
            (elder_id, limit),
        )
        .fetchall()
    )
    return [dict(row) for row in rows]


def acknowledge_alert(alert_id: str) -> None:
    """Mark an alert as acknowledged.

    Args:
        alert_id: the alert's id.
    """
    conn = get_connection()
    conn.execute("update alerts set status = 'acknowledged' where id = ?", (alert_id,))
    conn.commit()


def get_repeated_question_weekly_counts(elder_id: str) -> tuple[int, int]:
    """Return this week's vs. last week's repeated-question count.

    Thin re-export of backend.escalation's version so the dashboard doesn't
    need to import escalation internals directly.

    Args:
        elder_id: the elder profile to check.

    Returns:
        tuple[int, int]: (this_week_count, last_week_count).
    """
    from backend.escalation import get_repeated_question_weekly_counts as _get_counts

    return _get_counts(elder_id)
