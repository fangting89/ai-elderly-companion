"""Unit tests for family_notes, against an isolated in-memory DB (not the
real data/app.db) so nothing here touches real data.
"""

import sqlite3
from pathlib import Path

import pytest

from backend import family_notes

SCHEMA_PATH = Path(__file__).parent.parent / "sql" / "schema.sql"


@pytest.fixture
def conn(monkeypatch):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA_PATH.read_text())
    connection.execute(
        "insert into profiles (id, role, display_name) values ('elder-1', 'elder', 'Test Elder')"
    )
    connection.commit()
    monkeypatch.setattr(family_notes, "get_connection", lambda: connection)
    return connection


def test_no_note_returns_none(conn):
    assert family_notes.get_latest_note("elder-1") is None


def test_added_note_is_returned(conn):
    family_notes.add_note("elder-1", "Wei Ling", "Your daughter", "Love you, Ma")
    note = family_notes.get_latest_note("elder-1")
    assert note.sender_name == "Wei Ling"
    assert note.relation == "Your daughter"
    assert note.text == "Love you, Ma"


def test_most_recently_added_note_wins(conn):
    family_notes.add_note("elder-1", "Wei Ling", "Your daughter", "First note")
    family_notes.add_note("elder-1", "Wei Ling", "Your daughter", "Second note")
    assert family_notes.get_latest_note("elder-1").text == "Second note"


def test_notes_are_scoped_to_elder(conn):
    conn.execute(
        "insert into profiles (id, role, display_name) values ('elder-2', 'elder', 'Other Elder')"
    )
    conn.commit()
    family_notes.add_note("elder-1", "Wei Ling", "Your daughter", "For elder 1")
    assert family_notes.get_latest_note("elder-2") is None
