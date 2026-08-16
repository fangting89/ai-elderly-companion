"""Read-only aggregate queries for the family dashboard.

No alert generation happens here -- backend.escalation already writes alerts
at the point each trigger occurs; this module only reads what's already there.
"""

from datetime import date, datetime, timedelta

from backend.claude_client import CHAT_MODEL, call_prose
from backend.config import get_settings
from backend.db import get_connection

_prompts = get_settings().prompts

# Maps sentiment words to numbers and back, so mood can be averaged then relabeled
_SENTIMENT_SCORE = {"distress": 0, "low": 1, "neutral": 2, "positive": 3}
_SENTIMENT_LABEL = {0: "Distress", 1: "Low", 2: "Neutral", 3: "Positive"}


# Counts taken/missed/pending doses per day, for the adherence bar chart
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


# Averages each day's chat sentiment into one score, for the mood line chart
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


# Averages this week's mood vs. last week's, for a "better/worse" stat tile
def get_mood_weekly_comparison(elder_id: str) -> tuple[float | None, float | None]:
    """Return this week's vs. last week's average mood score.

    Mirrors get_repeated_question_weekly_counts's shape so the dashboard can
    lead with a stat tile ("Mood this week: better/worse") instead of a raw
    decimal line chart, which doesn't read at a glance.

    Args:
        elder_id: the elder profile to check.

    Returns:
        tuple[float | None, float | None]: (this_week_avg, last_week_avg),
            each None if there's no chat sentiment data in that window.
    """
    conn = get_connection()
    now = datetime.now()
    this_week_start = now - timedelta(days=7)
    last_week_start = now - timedelta(days=14)

    # Averages the sentiment scores for messages in one time window
    def _avg_sentiment(start: datetime, end: datetime | None) -> float | None:
        query = (
            "select sentiment from chat_messages where elder_id = ? and sender = 'elder' "
            "and sentiment is not null and created_at >= ?"
        )
        params: list[str] = [elder_id, start.strftime("%Y-%m-%d %H:%M:%S")]
        if end is not None:
            query += " and created_at < ?"
            params.append(end.strftime("%Y-%m-%d %H:%M:%S"))
        rows = conn.execute(query, params).fetchall()
        if not rows:
            return None
        return sum(_SENTIMENT_SCORE[row["sentiment"]] for row in rows) / len(rows)

    return _avg_sentiment(this_week_start, None), _avg_sentiment(last_week_start, this_week_start)


# Converts a 0-3 average mood score into a plain-language word
def mood_score_to_label(score: float) -> str:
    """Map an average mood score to a plain-language label.

    Args:
        score: average sentiment score (0=distress .. 3=positive).

    Returns:
        str: the nearest category label ("Distress", "Low", "Neutral", "Positive").
    """
    return _SENTIMENT_LABEL[round(min(max(score, 0), 3))]


# Fetches recent alerts for the dashboard's alerts list -- read-only, doesn't create any
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


# Marks an alert as seen, called when family taps "Acknowledge"
def acknowledge_alert(alert_id: str) -> None:
    """Mark an alert as acknowledged.

    Args:
        alert_id: the alert's id.
    """
    conn = get_connection()
    conn.execute("update alerts set status = 'acknowledged' where id = ?", (alert_id,))
    conn.commit()


# Re-exports escalation.py's weekly-count function for the dashboard's frequency panel
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


# Checks if the elder has chatted at all this week, to tell "zero" apart from "no data"
def has_chat_activity_this_week(elder_id: str) -> bool:
    """Check whether the elder has sent any chat message in the last 7 days.

    Lets the dashboard distinguish "checked, genuinely zero repeated
    questions" from "no chat activity at all" -- both would otherwise show
    the same bare 0, and the second reads as broken rather than reassuring.

    Args:
        elder_id: the elder profile to check.

    Returns:
        bool: True if at least one elder message exists in the window.
    """
    start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    row = (
        get_connection()
        .execute(
            "select 1 from chat_messages where elder_id = ? and sender = 'elder' "
            "and created_at >= ? limit 1",
            (elder_id, start),
        )
        .fetchone()
    )
    return row is not None


# Finds medications with just 1 missed dose -- a near-miss that didn't trigger an alert
def get_non_escalated_misses(elder_id: str) -> list[dict]:
    """Return medications with exactly one missed dose (a near-miss that
    didn't rise to an alert), for the dashboard's restraint framing --
    showing family what the AI handled quietly, not just what it escalated.

    Args:
        elder_id: the elder profile to check.

    Returns:
        list[dict]: rows of {"medication_name", "missed_count"}.
    """
    rows = (
        get_connection()
        .execute(
            "select medications.name as medication_name, count(*) as missed_count "
            "from medication_logs "
            "join medications on medications.id = medication_logs.medication_id "
            "where medication_logs.elder_id = ? and medication_logs.status = 'missed' "
            "group by medications.id having missed_count = 1",
            (elder_id,),
        )
        .fetchall()
    )
    return [dict(row) for row in rows]


# Counts family-contact nudges the elder actually acted on, in the last N days
def get_connections_facilitated_count(elder_id: str, days: int = 30) -> int:
    """Count family-contact nudges the elder acted on, in the last N days.

    Shown on the dashboard instead of (or alongside) raw chat-volume framing
    -- the metric that matters is real contact facilitated, not time spent
    talking to the AI.

    Args:
        elder_id: the elder profile to check.
        days: how many trailing days to include.

    Returns:
        int: number of family_nudge_accepted events.
    """
    start = (date.today() - timedelta(days=days - 1)).isoformat()
    return (
        get_connection()
        .execute(
            "select count(*) from companion_events where elder_id = ? "
            "and event_type = 'family_nudge_accepted' and date(created_at) >= ?",
            (elder_id, start),
        )
        .fetchone()[0]
    )


# Gathers this week's stats and asks Claude to write a plain-language summary for family
def get_weekly_summary(elder_id: str) -> str:
    """Generate a warm, plain-language weekly summary for family.

    Call this only on explicit request (e.g. a "Refresh" button), not
    automatically on every page load -- it's an LLM call and the Anthropic
    API is a self-funded personal budget.

    Args:
        elder_id: the elder profile to summarize.

    Returns:
        str: a short paragraph synthesizing adherence, mood, and a couple
            of things they said this week, in the companion's own voice.
    """
    # 1. Gather this week's raw data: adherence, mood, and recent messages
    adherence = get_adherence_by_day(elder_id, days=7)
    sentiment = get_sentiment_trend(elder_id, days=7)
    recent = (
        get_connection()
        .execute(
            "select content from chat_messages where elder_id = ? and sender = 'elder' "
            "and date(created_at) >= date('now', '-7 days') order by created_at desc limit 15",
            (elder_id,),
        )
        .fetchall()
    )

    # 2. Boil that down into a few plain numbers/text Claude can summarize
    taken = sum(row["count"] for row in adherence if row["status"] == "taken")
    missed = sum(row["count"] for row in adherence if row["status"] == "missed")
    avg_mood = sum(row["score"] for row in sentiment) / len(sentiment) if sentiment else None
    messages_text = "\n".join(f"- {row['content']}" for row in recent) or "No messages this week."

    # 3. Ask Claude to turn those numbers into a warm paragraph
    system = _prompts.weekly_summary_base
    context = (
        f"Doses taken this week: {taken}. Doses missed: {missed}. "
        f"Average mood score (0=distress, 3=positive): "
        f"{avg_mood if avg_mood is not None else 'no data'}.\n"
        f"Recent things they said:\n{messages_text}"
    )
    return call_prose(
        model=CHAT_MODEL, system=system, messages=[{"role": "user", "content": context}]
    )
