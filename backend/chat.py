"""Chat companion: prose replies plus sentiment/repetition tagging.

Replies are generated directly in the elder's preferred language (not
translated after the fact) -- an elder who doesn't read English should
never see an English draft first.
"""

import uuid

from backend.claude_client import CHAT_MODEL, TAG_MODEL, call_prose, call_structured
from backend.db import get_connection, get_profile
from backend.escalation import check_and_alert
from backend.strings import get_string

TAG_SYSTEM_PROMPT = (
    "You classify the emotional tone of an elderly person's chat message and "
    "whether it repeats a question they've already asked in this conversation. "
    "Never invent facts about them; judge only from the text given. The "
    "message may be in any language -- classify it regardless."
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
    },
    "required": ["sentiment", "repeated_question_flag"],
}


def _system_prompt(target_language: str) -> str:
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


def _recent_messages(elder_id: str, limit: int = 20) -> list[dict[str, str]]:
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
        {"role": "user" if row["sender"] == "elder" else "assistant", "content": row["content"]}
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


def get_history(elder_id: str) -> list[dict[str, str]]:
    """Return the full chat history for display, oldest first.

    Args:
        elder_id: the elder profile whose history to fetch.

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
    return [{"sender": row["sender"], "content": row["content"]} for row in rows]


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

    history = _recent_messages(elder_id)
    turn = [*history, {"role": "user", "content": user_text}]

    tags = call_structured(
        model=TAG_MODEL,
        system=TAG_SYSTEM_PROMPT,
        messages=turn,
        tool_name="tag_message",
        tool_description="Classify the sentiment and repetition of the latest message.",
        tool_schema=TAG_SCHEMA,
    )
    sentiment = tags["sentiment"]
    repeated = tags["repeated_question_flag"]

    _insert_message(
        elder_id, "elder", user_text, sentiment=sentiment, repeated_question_flag=repeated
    )
    check_and_alert(elder_id, "chat_sentiment", {"sentiment": sentiment})

    reply = call_prose(model=CHAT_MODEL, system=_system_prompt(target_language), messages=turn)
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
    profile = get_profile(elder_id)
    target_language = profile.preferred_language if profile else "English"
    _insert_message(elder_id, "ai", get_string(target_language, "daily_checkin"))
