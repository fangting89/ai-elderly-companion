"""Shared Anthropic client, plus the two call shapes every feature uses:
call_structured() for forced-tool-use JSON output, call_prose() for plain
text replies.
"""

import logging
import os
import time
from functools import cache
from typing import Any

import anthropic
from dotenv import load_dotenv

from backend.config import get_settings

_claude_settings = get_settings().claude

# Stronger model for anything the elder reads as prose; cheaper/faster
# model for behind-the-scenes classification and tagging.
CHAT_MODEL = _claude_settings.chat_model
TAG_MODEL = _claude_settings.tag_model

logger = logging.getLogger(__name__)

load_dotenv()


# Writes one line to the log with how long the call took and how many tokens it used
def _log_call(model: str, kind: str, started_at: float, response: anthropic.types.Message) -> None:
    """Log latency and token usage for one Claude call.

    Basic LLMOps observability: cost and latency are computed from these
    log lines at review time rather than tracked live, keeping this a
    plain log statement, not a metrics dependency.

    Args:
        model: model id that was called.
        kind: which call site this came from, "structured" or "prose".
        started_at: a time.monotonic() timestamp captured before the call.
        response: the Claude API response, for its token usage counts.
    """
    elapsed_ms = (time.monotonic() - started_at) * 1000
    logger.info(
        "claude_call model=%s kind=%s latency_ms=%.0f input_tokens=%d output_tokens=%d",
        model,
        kind,
        elapsed_ms,
        response.usage.input_tokens,
        response.usage.output_tokens,
    )


# Builds the Anthropic client once and reuses it (cached) for every call.
@cache
def get_client() -> anthropic.Anthropic:
    """Return a cached Anthropic client built from the ANTHROPIC_API_KEY env var.

    Returns:
        anthropic.Anthropic: an authenticated Anthropic client instance.
    """
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


# Calls Claude and forces it to answer via a fixed tool/schema instead of free text
def call_structured(
    *,
    model: str,
    system: str,
    messages: list[dict[str, Any]],
    tool_name: str,
    tool_description: str,
    tool_schema: dict[str, Any],
    max_tokens: int = _claude_settings.max_tokens,
) -> dict[str, Any]:
    """Call Claude with a single forced tool, returning its structured input.

    Always runs at temperature=0, since forced tool-use output here always
    drives a branching decision (classification, tagging, risk scoring).

    Args:
        model: model id to call.
        system: system prompt.
        messages: conversation messages in Anthropic Messages API format.
        tool_name: name of the single tool Claude is forced to call.
        tool_description: description shown to the model for the tool.
        tool_schema: JSON schema for the tool's input.
        max_tokens: max tokens for the response.

    Returns:
        dict[str, Any]: the tool call's input, matching tool_schema.

    Raises:
        ValueError: if Claude's response contains no tool_use block.
    """
    # Call Claude, forcing it to respond by calling our one tool (so the
    # reply is guaranteed to be structured JSON, not free text).
    started_at = time.monotonic()
    response = get_client().messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0,
        system=system,
        messages=messages,
        tools=[{"name": tool_name, "description": tool_description, "input_schema": tool_schema}],
        tool_choice={"type": "tool", "name": tool_name},
    )
    _log_call(model, "structured", started_at, response)

    # Pull the tool call's arguments out of the response and return them.
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise ValueError("Claude did not return a tool_use block")


# Calls Claude and returns a plain text reply, no forced structure
def call_prose(
    *,
    model: str,
    system: str,
    messages: list[dict[str, Any]],
    max_tokens: int = _claude_settings.max_tokens,
) -> str:
    """Call Claude for a free-form prose reply, at the configured temperature.

    Args:
        model: model id to call.
        system: system prompt.
        messages: conversation messages in Anthropic Messages API format.
        max_tokens: max tokens for the response.

    Returns:
        str: the reply text.
    """
    # Call Claude for an ordinary text reply.
    started_at = time.monotonic()
    response = get_client().messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=_claude_settings.prose_temperature,
        system=system,
        messages=messages,
    )
    _log_call(model, "prose", started_at, response)

    # Join all text blocks into one string reply.
    return "".join(block.text for block in response.content if block.type == "text")
