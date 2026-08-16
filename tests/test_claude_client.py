"""Unit tests for claude_client's two call shapes, with a fake Anthropic
client standing in for the real API -- no real API cost.
"""

from dataclasses import dataclass, field

import pytest

from backend import claude_client


@dataclass
class _FakeBlock:
    type: str
    input: dict | None = None
    text: str | None = None


@dataclass
class _FakeUsage:
    input_tokens: int = 10
    output_tokens: int = 5


@dataclass
class _FakeMessage:
    content: list
    usage: _FakeUsage = field(default_factory=_FakeUsage)


class _FakeMessages:
    def __init__(self, response, captured):
        self._response = response
        self._captured = captured

    def create(self, **kwargs):
        self._captured.update(kwargs)
        return self._response


class _FakeClient:
    def __init__(self, response, captured):
        self.messages = _FakeMessages(response, captured)


@pytest.fixture
def fake_client(monkeypatch):
    def _install(response):
        captured = {}
        client = _FakeClient(response, captured)
        monkeypatch.setattr(claude_client, "get_client", lambda: client)
        return captured

    return _install


def test_call_structured_returns_tool_input(fake_client):
    response = _FakeMessage(content=[_FakeBlock(type="tool_use", input={"sentiment": "positive"})])
    captured = fake_client(response)
    result = claude_client.call_structured(
        model="test-model",
        system="test system",
        messages=[{"role": "user", "content": "hi"}],
        tool_name="tag_message",
        tool_description="test",
        tool_schema={"type": "object", "properties": {}},
    )
    assert result == {"sentiment": "positive"}
    # Structured calls are always pinned to temperature=0, never config-driven.
    assert captured["temperature"] == 0


def test_call_structured_raises_without_tool_use_block(fake_client):
    response = _FakeMessage(content=[_FakeBlock(type="text", text="I refuse to use the tool.")])
    fake_client(response)
    with pytest.raises(ValueError, match="tool_use"):
        claude_client.call_structured(
            model="test-model",
            system="test system",
            messages=[{"role": "user", "content": "hi"}],
            tool_name="tag_message",
            tool_description="test",
            tool_schema={"type": "object", "properties": {}},
        )


def test_call_prose_joins_text_blocks(fake_client):
    response = _FakeMessage(
        content=[_FakeBlock(type="text", text="Hello "), _FakeBlock(type="text", text="there.")]
    )
    fake_client(response)
    result = claude_client.call_prose(
        model="test-model", system="test system", messages=[{"role": "user", "content": "hi"}]
    )
    assert result == "Hello there."


def test_call_prose_uses_configured_temperature(fake_client):
    response = _FakeMessage(content=[_FakeBlock(type="text", text="ok")])
    captured = fake_client(response)
    claude_client.call_prose(
        model="test-model", system="test system", messages=[{"role": "user", "content": "hi"}]
    )
    assert captured["temperature"] == claude_client._claude_settings.prose_temperature
