"""Chat companion: prose replies plus sentiment/repetition tagging.

Replies are generated directly in the elder's preferred language (not
translated after the fact) -- an elder who doesn't read English should
never see an English draft first.
"""

import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from backend.calendar import add_event
from backend.claude_client import CHAT_MODEL, TAG_MODEL, call_prose, call_structured
from backend.companion_line import decide_todays_opener, family_display_name
from backend.db import get_connection, get_profile
from backend.escalation import check_and_alert
from backend.memory_bank import generate_reminiscence_prompt, get_context_facts
from backend.strings import get_string

# Stored in place of the daily check-in's literal text so it always renders
# in the elder's *current* preferred_language, not whatever language was
# active on the day it was inserted.
_DAILY_CHECKIN_SENTINEL = "__daily_checkin__"

# Same idea for the family-contact nudge -- otherwise a nudge generated while
# the elder's language was e.g. Mandarin Chinese stays frozen in Chinese even
# after they switch to English, since it used to be stored as literal
# pre-formatted text rather than something re-rendered per display.
_FAMILY_NUDGE_SENTINEL = "__family_nudge__"

# Sentiments that unlock one bounded follow-up reply in the Check-In flow
# (see send_message's `bounded` parameter) -- same set escalation.py already
# treats as concerning, so the two stay in agreement about what counts.
_LOW_MOOD_SENTIMENTS = {"low", "distress"}


@dataclass
class ChatReply:
    """The companion's reply to a check-in message.

    Attributes:
        text: the reply text, in the elder's preferred language.
        can_continue: whether one more reply can still be sent today (see
            send_message's `bounded` parameter).
    """

    text: str
    can_continue: bool


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


def build_system_prompt(
    target_language: str,
    memory_facts: list[str] | None = None,
    *,
    closing: bool = False,
) -> str:
    """Build the companion's system prompt for a chat reply.

    Args:
        target_language: language to reply in.
        memory_facts: family-provided facts to ground the reply in, if any.
        closing: whether this must be the last reply in a bounded Check-In
            exchange (see send_message's `bounded` parameter), in which case
            the prompt instructs the model to close warmly rather than
            invite a further reply the UI has nowhere to show.

    Returns:
        str: the system prompt text.
    """
    language_clause = (
        ""
        if target_language == "English"
        else f" Always reply in {target_language}, never in English."
    )
    memory_clause = ""
    if memory_facts:
        facts_text = "; ".join(memory_facts)
        memory_clause = (
            " Known facts about this person from their family (reference naturally "
            f"when relevant, never invent anything beyond this): {facts_text}."
        )
    # Set when this is the last reply the bounded Check-In flow can give
    # today (see send_message's `bounded` parameter) -- without this, the
    # model may ask an open follow-up question ("want to tell me more?")
    # that the UI has nowhere left to answer, leaving the elder mid-thought.
    closing_clause = (
        " This is the last message you can send in today's check-in, so close "
        "warmly without asking any further questions, and if it feels natural, "
        "gently suggest reaching out to a family member or friend."
        if closing
        else ""
    )
    return (
        "You are a warm, patient AI companion for an elderly person."
        f"{language_clause}{memory_clause}{closing_clause} Keep replies short, kind, and simple. "
        "Never give medical, legal, or financial advice; suggest they check with family "
        "or a professional instead. If they mention a letter, message, or "
        "anything that might be a scam, gently suggest they use the Point & "
        "Ask feature or ask a family member before acting on it. You are here to "
        "help with the quiet moments, not to replace real people in their life -- "
        "when a conversation turns emotional, lonely, or nostalgic, naturally "
        "encourage them to reach out to a real family member or friend, not just "
        "you. This applies generally, not only when something is unsafe."
    )


def _render_content(elder_id: str, content: str, language: str) -> str:
    """Resolve stored message content for display/LLM context.

    The daily check-in and family-nudge lines are stored as sentinels, not
    literal text, so they always reflect the elder's *current*
    preferred_language rather than whichever language was active on the day
    they were inserted.
    """
    if content == _DAILY_CHECKIN_SENTINEL:
        return get_string(language, "daily_checkin")
    if content == _FAMILY_NUDGE_SENTINEL:
        name = family_display_name(elder_id) or ""
        return get_string(language, "family_nudge_line").format(name=name)
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
    messages = []
    for row in reversed(rows):
        content = _render_content(elder_id, row["content"], language)
        role = "user" if row["sender"] == "elder" else "assistant"
        messages.append({"role": role, "content": content})
    return messages


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
        {"sender": row["sender"], "content": _render_content(elder_id, row["content"], language)}
        for row in rows
    ]


def _elder_replies_today_count(elder_id: str) -> int:
    row = (
        get_connection()
        .execute(
            "select count(*) as c from chat_messages where elder_id = ? and sender = 'elder' "
            "and date(created_at) = date('now')",
            (elder_id,),
        )
        .fetchone()
    )
    return row["c"]


def send_message(elder_id: str, user_text: str, *, bounded: bool = False) -> ChatReply:
    """Record the elder's message, tag it, reply, and escalate if warranted.

    Args:
        elder_id: the elder profile sending this message.
        user_text: the elder's message text.
        bounded: if True, cap today's exchange at one follow-up reply beyond
            the first -- unlocked only when the first reply reads as low
            mood/distress, and always closed (no further follow-up offered)
            after that. Used by the React Check-In flow, which has nowhere
            to show more than two replies; the Streamlit Chat page leaves
            this False and keeps its existing open-ended thread.

    Returns:
        ChatReply: the companion's reply (in the elder's preferred language)
            and whether one more reply can still be sent today.
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
    if repeated:
        check_and_alert(elder_id, "repeated_question", {})
    _maybe_add_calendar_event(elder_id, tags)

    can_continue = False
    closing = False
    if bounded:
        replies_today = _elder_replies_today_count(elder_id)
        can_continue = replies_today == 1 and sentiment in _LOW_MOOD_SENTIMENTS
        closing = replies_today >= 2

    memory_facts = get_context_facts(elder_id)
    system = build_system_prompt(target_language, memory_facts, closing=closing)
    reply = call_prose(model=CHAT_MODEL, system=system, messages=turn)
    _insert_message(elder_id, "ai", reply)
    return ChatReply(text=reply, can_continue=can_continue)


def add_reminiscence_message(elder_id: str, target_language: str) -> str | None:
    """Insert a reminiscence-based conversation opener as a new AI message.

    Args:
        elder_id: the elder profile to generate an opener for.
        target_language: language to write the opener in.

    Returns:
        str | None: the opener text that was inserted, or None if no
            memories are stored yet (nothing is inserted in that case).
    """
    opener = generate_reminiscence_prompt(elder_id, target_language)
    if opener is None:
        return None
    _insert_message(elder_id, "ai", opener)
    return opener


def maybe_send_daily_checkin(elder_id: str) -> None:
    """Insert today's companion opener if none has been sent yet today.

    Delegates the "what should today's opener be" decision to
    backend.companion_line -- a family-contact nudge or reminiscence prompt
    takes priority over the plain daily check-in when conditions are met,
    so the social nudge is a real, guaranteed mechanism rather than
    something that only happens if the model brings it up unprompted.

    Args:
        elder_id: the elder profile to check in on.
    """
    profile = get_profile(elder_id)
    target_language = profile.preferred_language if profile else "English"
    decision = decide_todays_opener(elder_id, target_language)
    if decision is None:
        return
    opener_text, line_type = decision
    if line_type == "daily_checkin":
        content = _DAILY_CHECKIN_SENTINEL
    elif line_type == "family_nudge":
        content = _FAMILY_NUDGE_SENTINEL
    else:
        content = opener_text
    _insert_message(elder_id, "ai", content)


def get_todays_opener(elder_id: str, language: str) -> str | None:
    """Return today's opener message for display (e.g. on the Home screen).

    Args:
        elder_id: the elder profile to fetch the opener for.
        language: the elder's *current* preferred_language, for rendering
            the daily check-in sentinel (see _render_content).

    Returns:
        str | None: the opener text, or None if no AI message exists today.
    """
    row = (
        get_connection()
        .execute(
            "select content from chat_messages where elder_id = ? and sender = 'ai' "
            "and date(created_at) = date('now') order by created_at asc limit 1",
            (elder_id,),
        )
        .fetchone()
    )
    if row is None:
        return None
    return _render_content(elder_id, row["content"], language)
