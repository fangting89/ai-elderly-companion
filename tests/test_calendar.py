"""Unit tests for calendar's event CRUD, against an isolated in-memory DB
(not the real data/app.db) so nothing here touches real data.
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from backend import calendar

SCHEMA_PATH = Path(__file__).parent.parent / "sql" / "schema.sql"


@pytest.fixture
def elder_id(monkeypatch):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA_PATH.read_text())
    elder_id = str(uuid.uuid4())
    connection.execute(
        "insert into profiles (id, role, display_name) values (?, 'elder', 'Test Elder')",
        (elder_id,),
    )
    connection.commit()
    monkeypatch.setattr(calendar, "get_connection", lambda: connection)
    return elder_id


def test_no_events_returns_empty_list(elder_id):
    assert calendar.list_upcoming_events(elder_id) == []


def test_added_event_appears_in_upcoming(elder_id):
    start = datetime.now() + timedelta(days=1)
    calendar.add_event(elder_id, "Dentist", start, notes="Bring insurance card")
    events = calendar.list_upcoming_events(elder_id)
    assert len(events) == 1
    assert events[0].title == "Dentist"
    assert events[0].notes == "Bring insurance card"
    assert events[0].event_type == "appointment"


def test_past_events_are_excluded(elder_id):
    calendar.add_event(elder_id, "Past appointment", datetime.now() - timedelta(days=1))
    assert calendar.list_upcoming_events(elder_id) == []


def test_events_ordered_soonest_first(elder_id):
    calendar.add_event(elder_id, "Later", datetime.now() + timedelta(days=10))
    calendar.add_event(elder_id, "Sooner", datetime.now() + timedelta(days=1))
    events = calendar.list_upcoming_events(elder_id)
    assert [e.title for e in events] == ["Sooner", "Later"]


def test_events_are_scoped_to_elder(elder_id):
    other_elder_id = str(uuid.uuid4())
    calendar.get_connection().execute(
        "insert into profiles (id, role, display_name) values (?, 'elder', 'Other Elder')",
        (other_elder_id,),
    )
    calendar.get_connection().commit()
    calendar.add_event(elder_id, "For elder 1", datetime.now() + timedelta(days=1))
    calendar.add_event(other_elder_id, "For elder 2", datetime.now() + timedelta(days=1))
    events = calendar.list_upcoming_events(elder_id)
    assert len(events) == 1
    assert events[0].title == "For elder 1"
