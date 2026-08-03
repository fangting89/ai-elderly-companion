"""Shared Anthropic client and a forced-tool-use helper for structured output."""

import logging
import time
from typing import Any

import anthropic
import streamlit as st

CHAT_MODEL = "claude-sonnet-5"
TAG_MODEL = "claude-haiku-4-5-20251001"

logger = logging.getLogger(__name__)


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


@st.cache_resource
def get_client() -> anthropic.Anthropic:
    """Return a cached Anthropic client built from Streamlit secrets.

    Returns:
        anthropic.Anthropic: an authenticated Anthropic client instance.
    """
    return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])


def call_structured(
    *,
    model: str,
    system: str,
    messages: list[dict[str, Any]],
    tool_name: str,
    tool_description: str,
    tool_schema: dict[str, Any],
    max_tokens: int = 1024,
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
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise ValueError("Claude did not return a tool_use block")


def call_prose(
    *,
    model: str,
    system: str,
    messages: list[dict[str, Any]],
    max_tokens: int = 1024,
) -> str:
    """Call Claude for a free-form prose reply at default temperature.

    Args:
        model: model id to call.
        system: system prompt.
        messages: conversation messages in Anthropic Messages API format.
        max_tokens: max tokens for the response.

    Returns:
        str: the reply text.
    """
    started_at = time.monotonic()
    response = get_client().messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    _log_call(model, "prose", started_at, response)
    return "".join(block.text for block in response.content if block.type == "text")
