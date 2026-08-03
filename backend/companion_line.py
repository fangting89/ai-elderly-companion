"""Decides what the companion's daily opening line should be, and logs which
kind was shown so it isn't repeated too often and so the family dashboard can
count how many led to a real family contact.

This replaces a purely-fixed daily greeting with a small, deterministic
priority mechanism -- the "social nudge" and reminiscence prompt become real,
guaranteed behavior instead of something that only happens if the model
happens to bring it up in conversation.
"""

import uuid
from datetime import datetime

from backend.db import get_connection
from backend.memory_bank import generate_reminiscence_prompt, get_context_facts
from backend.strings import get_string

FAMILY_NUDGE_SILENCE_DAYS = 5
FAMILY_NUDGE_COOLDOWN_DAYS = 2
REMINISCENCE_COOLDOWN_DAYS = 3
_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def _log_event(elder_id: str, event_type: str) -> None:
    conn = get_connection()
    conn.execute(
        "insert into companion_events (id, elder_id, event_type) values (?, ?, ?)",
        (str(uuid.uuid4()), elder_id, event_type),
    )
    conn.commit()


def _days_since_event(elder_id: str, event_type: str) -> int | None:
    row = (
        get_connection()
        .execute(
            "select created_at from companion_events where elder_id = ? and event_type = ? "
            "order by created_at desc limit 1",
            (elder_id, event_type),
        )
        .fetchone()
    )
    if row is None:
        return None
    last = datetime.strptime(row["created_at"], _TIMESTAMP_FORMAT)
    return (datetime.now() - last).days


def family_display_name(elder_id: str) -> str | None:
    row = (
        get_connection()
        .execute(
            "select display_name from profiles where role = 'family' and elder_id = ?", (elder_id,)
        )
        .fetchone()
    )
    return row["display_name"] if row else None


def _days_since_family_mentioned(elder_id: str, family_name: str) -> int:
    row = (
        get_connection()
        .execute(
            "select created_at from chat_messages where elder_id = ? and sender = 'elder' "
            "and content like ? order by created_at desc limit 1",
            (elder_id, f"%{family_name}%"),
        )
        .fetchone()
    )
    if row is None:
        return FAMILY_NUDGE_SILENCE_DAYS + 1  # never mentioned -- treat as overdue
    last = datetime.strptime(row["created_at"], _TIMESTAMP_FORMAT)
    return (datetime.now() - last).days


def decide_todays_opener(elder_id: str, language: str) -> tuple[str, str] | None:
    """Decide today's companion opener, if the elder hasn't chatted yet today.

    Priority: a family-contact nudge, then a reminiscence prompt (if memories
    are stored and neither was shown too recently), then the plain daily
    check-in as the fallback.

    Args:
        elder_id: the elder profile to generate an opener for.
        language: the elder's preferred language.

    Returns:
        tuple[str, str] | None: (opener text, line_type), where line_type is
            "family_nudge", "reminiscence", or "daily_checkin" -- or None if
            the elder has already chatted today (nothing to open with).
    """
    already_chatted = (
        get_connection()
        .execute(
            "select 1 from chat_messages where elder_id = ? "
            "and date(created_at) = date('now') limit 1",
            (elder_id,),
        )
        .fetchone()
    )
    if already_chatted is not None:
        return None

    family_name = family_display_name(elder_id)
    nudge_cooldown = _days_since_event(elder_id, "family_nudge_shown")
    if (
        family_name
        and _days_since_family_mentioned(elder_id, family_name) >= FAMILY_NUDGE_SILENCE_DAYS
        and (nudge_cooldown is None or nudge_cooldown >= FAMILY_NUDGE_COOLDOWN_DAYS)
    ):
        _log_event(elder_id, "family_nudge_shown")
        template = get_string(language, "family_nudge_line")
        return template.format(name=family_name), "family_nudge"

    reminiscence_cooldown = _days_since_event(elder_id, "reminiscence_shown")
    if get_context_facts(elder_id) and (
        reminiscence_cooldown is None or reminiscence_cooldown >= REMINISCENCE_COOLDOWN_DAYS
    ):
        opener = generate_reminiscence_prompt(elder_id, language)
        if opener is not None:
            _log_event(elder_id, "reminiscence_shown")
            return opener, "reminiscence"

    return get_string(language, "daily_checkin"), "daily_checkin"


def get_todays_line_type(elder_id: str) -> str:
    """Determine what kind of opener was shown today, for UI purposes (e.g.
    whether Home should show the "yes, remind me" quick action).

    Args:
        elder_id: the elder profile to check.

    Returns:
        str: "family_nudge", "reminiscence", or "daily_checkin" (the
            default if nothing more specific was logged today).
    """
    for event_type, line_type in (
        ("family_nudge_shown", "family_nudge"),
        ("reminiscence_shown", "reminiscence"),
    ):
        row = (
            get_connection()
            .execute(
                "select 1 from companion_events where elder_id = ? and event_type = ? "
                "and date(created_at) = date('now') limit 1",
                (elder_id, event_type),
            )
            .fetchone()
        )
        if row is not None:
            return line_type
    return "daily_checkin"


def family_nudge_accepted_today(elder_id: str) -> bool:
    """Check whether the elder already accepted today's family-contact nudge.

    Without this check, the Home screen would keep re-rendering the ask and
    its button on every rerun/revisit that same day, even right after the
    elder said yes -- reading as the companion not remembering what it just
    said.

    Args:
        elder_id: the elder profile to check.

    Returns:
        bool: True if a family_nudge_accepted event was logged today.
    """
    row = (
        get_connection()
        .execute(
            "select 1 from companion_events where elder_id = ? "
            "and event_type = 'family_nudge_accepted' and date(created_at) = date('now') limit 1",
            (elder_id,),
        )
        .fetchone()
    )
    return row is not None


def log_family_nudge_accepted(elder_id: str) -> None:
    """Record that the elder acted on a family-contact nudge.

    Feeds the family dashboard's "connections facilitated" metric.

    Args:
        elder_id: the elder profile confirming they'll reach out.
    """
    _log_event(elder_id, "family_nudge_accepted")
