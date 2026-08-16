"""Unit tests for memory_bank: facts/photos CRUD and reminiscence prompt
generation, against an isolated in-memory DB with uploads redirected to a
temp directory and the Claude call mocked out -- no real API cost, no
writes to the real data/uploads.
"""

import sqlite3
import uuid
from pathlib import Path

import pytest

from backend import memory_bank

SCHEMA_PATH = Path(__file__).parent.parent / "sql" / "schema.sql"


@pytest.fixture
def elder_id(monkeypatch, tmp_path):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA_PATH.read_text())
    elder_id = str(uuid.uuid4())
    connection.execute(
        "insert into profiles (id, role, display_name) values (?, 'elder', 'Test Elder')",
        (elder_id,),
    )
    connection.commit()
    monkeypatch.setattr(memory_bank, "get_connection", lambda: connection)
    monkeypatch.setattr(memory_bank, "UPLOADS_DIR", tmp_path)
    return elder_id


def test_add_fact_then_list_entries(elder_id):
    memory_bank.add_fact(elder_id, elder_id, "Loves gardening, especially roses.")
    entries = memory_bank.list_entries(elder_id)
    assert len(entries) == 1
    assert entries[0].entry_type == "fact"
    assert entries[0].content_text == "Loves gardening, especially roses."


def test_entries_are_scoped_to_elder(elder_id):
    other_elder_id = str(uuid.uuid4())
    memory_bank.get_connection().execute(
        "insert into profiles (id, role, display_name) values (?, 'elder', 'Other Elder')",
        (other_elder_id,),
    )
    memory_bank.get_connection().commit()
    memory_bank.add_fact(elder_id, elder_id, "Fact about elder 1")
    memory_bank.add_fact(other_elder_id, other_elder_id, "Fact about elder 2")
    assert len(memory_bank.list_entries(elder_id)) == 1


def test_get_context_facts_respects_limit(elder_id):
    for i in range(5):
        memory_bank.add_fact(elder_id, elder_id, f"Fact {i}")
    assert len(memory_bank.get_context_facts(elder_id, limit=3)) == 3


def test_get_context_facts_includes_photo_captions(elder_id):
    memory_bank.add_photo(elder_id, elder_id, b"fake-image-bytes", "A photo from the garden")
    facts = memory_bank.get_context_facts(elder_id)
    assert facts == ["A photo from the garden"]


def test_add_photo_writes_file_and_row(elder_id, tmp_path):
    memory_bank.add_photo(elder_id, elder_id, b"fake-image-bytes", "Birthday party")
    entries = memory_bank.list_entries(elder_id)
    assert len(entries) == 1
    assert entries[0].entry_type == "photo"
    written_files = list(tmp_path.glob("*.jpg"))
    assert len(written_files) == 1
    assert written_files[0].read_bytes() == b"fake-image-bytes"


def test_delete_entry_removes_photo_file(elder_id, tmp_path):
    memory_bank.add_photo(elder_id, elder_id, b"fake-image-bytes", "Birthday party")
    entry_id = memory_bank.list_entries(elder_id)[0].id
    memory_bank.delete_entry(entry_id)
    assert memory_bank.list_entries(elder_id) == []
    assert list(tmp_path.glob("*.jpg")) == []


def test_delete_fact_entry_without_photo_does_not_error(elder_id):
    memory_bank.add_fact(elder_id, elder_id, "A fact with no photo")
    entry_id = memory_bank.list_entries(elder_id)[0].id
    memory_bank.delete_entry(entry_id)  # should not raise
    assert memory_bank.list_entries(elder_id) == []


def test_generate_reminiscence_prompt_returns_none_without_facts(elder_id):
    assert memory_bank.generate_reminiscence_prompt(elder_id, "English") is None


def test_generate_reminiscence_prompt_uses_stored_fact(elder_id, monkeypatch):
    memory_bank.add_fact(elder_id, elder_id, "Was a primary school teacher for 30 years.")
    captured = {}

    def fake_call_prose(*, model, system, messages):
        captured["messages"] = messages
        return "A warm opener."

    monkeypatch.setattr(memory_bank, "call_prose", fake_call_prose)
    opener = memory_bank.generate_reminiscence_prompt(elder_id, "English")
    assert opener == "A warm opener."
    assert "primary school teacher" in captured["messages"][0]["content"]
