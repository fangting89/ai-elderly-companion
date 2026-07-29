"""Chat companion: prose replies plus sentiment/repetition tagging.

Replies are generated directly in the elder's preferred language (not
translated after the fact) -- an elder who doesn't read English should
never see an English draft first.
"""

import uuid
from datetime import date, datetime, timedelta

from backend.calendar import add_event
from backend.claude_client import CHAT_MODEL, TAG_MODEL, call_prose, call_structured
from backend.db import get_connection, get_profile
from backend.escalation import check_and_alert
from backend.strings import get_string

# Stored in place of the daily check-in's literal text so it always renders
# in the elder's *current* preferred_language, not whatever language was
# active on the day it was inserted.
_DAILY_CHECKIN_SENTINEL = "__daily_checkin__"


def _tag_system_prompt() -> str:
    today = date.today()
    # LLMs are unreliable at relative-date arithmetic ("next Tuesday"), so
    # give it a grounded lookup table instead of asking it to compute one --
    # same principle as elsewhere: derive what the code depends on
    # deterministically, don't trust the model to compute it.
    upcoming_dates = "\n".join(
        f"{(today + timedelta(days=i)).isoformat()} ({(today + timedelta(days=i)).strftime('%A')})"
        for i in range(1, 15)
    )
    return (
        f"Today's date is {today.isoformat()} ({today.strftime('%A')}).\n\n"
        "Upcoming dates for reference (use these exactly; do not calculate dates yourself):\n"
        f"{upcoming_dates}\n\n"
        "You classify an elderly person's chat message: its emotional tone, "
        "whether it repeats a question already asked earlier in this "
        "conversation, and whether it describes a schedulable event (an "
        "appointment or reminder with a date) that should be added to their "
        "calendar. When a day of the week is mentioned (e.g. 'Tuesday' or "
        "'next Tuesday'), use the SOONEST matching date from the reference "
        "list above, never a date two weeks away. Never invent facts about "
        "them; judge only from the text given. The message may be in any "
        "language -- classify it regardless."
    )


TAG_SCHEMA = {
    "type": "object",
    "properties": {
        "sentiment": {
            "type": "string",
            "enum": ["positive", "neutral", "low", "distress"],
            "description": "Overall emotional tone of the message.",
        },
        "repeated_question_flag": {
            "type": "boolean",
            "description": (
                "True if this repeats a question already asked earlier in the conversation."
            ),
        },
        "mentions_schedulable_event": {
            "type": "boolean",
            "description": (
                "True if the message describes an appointment, reminder, or occasion "
                "with a date that should be added to the calendar."
            ),
        },
        "event_title": {
            "type": "string",
            "description": (
                "Short event title if mentions_schedulable_event is true, else empty string."
            ),
        },
        "event_date": {
            "type": "string",
            "description": (
                "Event date as YYYY-MM-DD, resolved relative to today's date given above, "
                "if mentions_schedulable_event is true, else empty string."
            ),
        },
        "event_time": {
            "type": "string",
            "description": (
                "Event time as 24-hour HH:MM if mentioned, '09:00' as a default if not, "
                "or empty string if mentions_schedulable_event is false."
            ),
        },
    },
    "required": [
        "sentiment",
        "repeated_question_flag",
        "mentions_schedulable_event",
        "event_title",
        "event_date",
        "event_time",
    ],
}


def build_system_prompt(target_language: str) -> str:
    language_clause = (
        ""
        if target_language == "English"
        else f" Always reply in {target_language}, never in English."
    )
    return (
        "You are a warm, patient AI companion for an elderly person."
        f"{language_clause} Keep replies short, kind, and simple. Never give "
        "medical, legal, or financial advice; suggest they check with family "
        "or a professional instead. If they mention a letter, message, or "
        "anything that might be a scam, gently suggest they use the Point & "
        "Ask feature or ask a family member before acting on it."
    )


def _render_content(content: str, language: str) -> str:
    """Resolve stored message content for display/LLM context.

    The daily check-in is stored as a sentinel, not literal text, so it
    always reflects the elder's *current* preferred_language rather than
    whichever language was active on the day it was inserted.
    """
    if content == _DAILY_CHECKIN_SENTINEL:
        return get_string(language, "daily_checkin")
    return content


def _maybe_add_calendar_event(elder_id: str, tags: dict) -> None:
    """Add a calendar event if the tagging call detected one, ignoring bad dates."""
    if not tags.get("mentions_schedulable_event"):
        return
    try:
        start_time = datetime.strptime(
            f"{tags['event_date']} {tags['event_time']}", "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return
    add_event(elder_id, title=tags["event_title"], start_time=start_time)


def _recent_messages(elder_id: str, language: str, limit: int = 20) -> list[dict[str, str]]:
    rows = (
        get_connection()
        .execute(
            "select sender, content from chat_messages where elder_id = ? "
            "order by created_at desc limit ?",
            (elder_id, limit),
        )
        .fetchall()
    )
    return [
        {
            "role": "user" if row["sender"] == "elder" else "assistant",
            "content": _render_content(row["content"], language),
        }
        for row in reversed(rows)
    ]


def _insert_message(
    elder_id: str,
    sender: str,
    content: str,
    sentiment: str | None = None,
    repeated_question_flag: bool = False,
) -> None:
    conn = get_connection()
    conn.execute(
        "insert into chat_messages "
        "(id, elder_id, sender, content, sentiment, repeated_question_flag) "
        "values (?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), elder_id, sender, content, sentiment, int(repeated_question_flag)),
    )
    conn.commit()


def get_history(elder_id: str, language: str) -> list[dict[str, str]]:
    """Return the full chat history for display, oldest first.

    Args:
        elder_id: the elder profile whose history to fetch.
        language: the elder's *current* preferred_language, used to render
            the daily check-in (see _render_content).

    Returns:
        list[dict[str, str]]: messages with 'sender' and 'content' keys.
    """
    rows = (
        get_connection()
        .execute(
            "select sender, content from chat_messages where elder_id = ? order by created_at asc",
            (elder_id,),
        )
        .fetchall()
    )
    return [
        {"sender": row["sender"], "content": _render_content(row["content"], language)}
        for row in rows
    ]


def send_message(elder_id: str, user_text: str) -> str:
    """Record the elder's message, tag it, reply, and escalate if warranted.

    Args:
        elder_id: the elder profile sending this message.
        user_text: the elder's message text.

    Returns:
        str: the companion's prose reply, in the elder's preferred language.
    """
    profile = get_profile(elder_id)
    target_language = profile.preferred_language if profile else "English"

    history = _recent_messages(elder_id, target_language)
    turn = [*history, {"role": "user", "content": user_text}]

    tags = call_structured(
        model=TAG_MODEL,
        system=_tag_system_prompt(),
        messages=turn,
        tool_name="tag_message",
        tool_description=(
            "Classify the sentiment, repetition, and calendar-worthiness of the latest message."
        ),
        tool_schema=TAG_SCHEMA,
    )
    sentiment = tags["sentiment"]
    repeated = tags["repeated_question_flag"]

    _insert_message(
        elder_id, "elder", user_text, sentiment=sentiment, repeated_question_flag=repeated
    )
    check_and_alert(elder_id, "chat_sentiment", {"sentiment": sentiment})
    _maybe_add_calendar_event(elder_id, tags)

    reply = call_prose(model=CHAT_MODEL, system=build_system_prompt(target_language), messages=turn)
    _insert_message(elder_id, "ai", reply)
    return reply


def maybe_send_daily_checkin(elder_id: str) -> None:
    """Insert a daily check-in prompt from the AI if none has been sent today.

    Args:
        elder_id: the elder profile to check in on.
    """
    row = (
        get_connection()
        .execute(
            "select 1 from chat_messages where elder_id = ? and sender = 'ai' "
            "and date(created_at) = date('now') limit 1",
            (elder_id,),
        )
        .fetchone()
    )
    if row is not None:
        return
    _insert_message(elder_id, "ai", _DAILY_CHECKIN_SENTINEL)
