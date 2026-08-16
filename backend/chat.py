"""Chat companion: prose replies plus sentiment/repetition tagging.

Replies are generated directly in the elder's preferred language (not
translated after the fact) -- an elder who doesn't read English should
never see an English draft first.
"""

import uuid
from dataclasses import dataclass

from backend.claude_client import CHAT_MODEL, TAG_MODEL, call_prose, call_structured
from backend.companion_line import decide_todays_opener, family_display_name
from backend.config import get_settings
from backend.db import get_connection, get_profile
from backend.escalation import check_and_alert
from backend.memory_bank import get_context_facts
from backend.strings import get_string

_chat_settings = get_settings().chat
_prompts = get_settings().prompts

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


# The companion's reply, returned to whoever called send_message()
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


# System prompt for the tagging call: classify tone and repetition, nothing else
TAG_SYSTEM_PROMPT = _prompts.tag_system

# The checklist the tagging call must fill in for every elder message
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
    "required": [
        "sentiment",
        "repeated_question_flag",
    ],
}


# Assembles the companion's system prompt from language, known facts, and whether to close out
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
    clauses = f"{language_clause}{memory_clause}{closing_clause}"
    return _prompts.companion_persona.format(clauses=clauses)


# Turns a stored message into the text to actually show/send to the model
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


# Fetches the last N messages for this elder, formatted for the Claude API
def _recent_messages(
    elder_id: str, language: str, limit: int = _chat_settings.recent_messages_limit
) -> list[dict[str, str]]:
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


# Saves one chat message (from the elder or the AI) to the database
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


# Counts how many messages the elder has sent today, for the bounded Check-In flow
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
            to show more than two replies; defaults to False for an
            open-ended thread.

    Returns:
        ChatReply: the companion's reply (in the elder's preferred language)
            and whether one more reply can still be sent today.
    """
    # 1. Find the elder's language and build this turn's conversation history
    profile = get_profile(elder_id)
    target_language = profile.preferred_language if profile else "English"
    history = _recent_messages(elder_id, target_language)
    turn = [*history, {"role": "user", "content": user_text}]

    # 2. AI call #1: tag the message's sentiment and whether it repeats an earlier question
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

    # 3. Save the elder's message, then let escalation.py decide if family needs to know
    _insert_message(
        elder_id, "elder", user_text, sentiment=sentiment, repeated_question_flag=repeated
    )
    check_and_alert(elder_id, "chat_sentiment", {"sentiment": sentiment})
    if repeated:
        check_and_alert(elder_id, "repeated_question", {})

    # 4. Work out if this reply can/must be the last one today (bounded Check-In flow only)
    can_continue = False
    closing = False
    if bounded:
        replies_today = _elder_replies_today_count(elder_id)
        max_replies = _chat_settings.bounded_checkin_max_replies
        can_continue = replies_today == max_replies - 1 and sentiment in _LOW_MOOD_SENTIMENTS
        closing = replies_today >= max_replies

    # 5. AI call #2: generate the actual reply, save it, and return it
    memory_facts = get_context_facts(elder_id)
    system = build_system_prompt(target_language, memory_facts, closing=closing)
    reply = call_prose(model=CHAT_MODEL, system=system, messages=turn)
    _insert_message(elder_id, "ai", reply)
    return ChatReply(text=reply, can_continue=can_continue)


# Inserts today's first AI message (nudge/reminiscence/plain check-in), if none exists yet
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
        return  # elder already chatted today -- nothing to open with
    opener_text, line_type = decision
    # Store a sentinel (not literal text) for the two fixed-string cases, so
    # they re-render in whatever language the elder has now, not the
    # language active when they were inserted.
    if line_type == "daily_checkin":
        content = _DAILY_CHECKIN_SENTINEL
    elif line_type == "family_nudge":
        content = _FAMILY_NUDGE_SENTINEL
    else:
        content = opener_text
    _insert_message(elder_id, "ai", content)


# Fetches today's already-inserted opener message, for display on Home/Check-In
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
