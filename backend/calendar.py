"""Calendar: CRUD for appointments/events."""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from backend.db import get_connection

EventType = Literal["appointment", "medication", "other"]
_START_TIME_FORMAT = "%Y-%m-%d %H:%M"


@dataclass
class CalendarEvent:
    id: str
    elder_id: str
    title: str
    event_type: EventType
    start_time: datetime
    notes: str | None


def add_event(
    elder_id: str,
    title: str,
    start_time: datetime,
    event_type: EventType = "appointment",
    notes: str | None = None,
) -> None:
    """Add a calendar event.

    Args:
        elder_id: the elder profile this event belongs to.
        title: short event title.
        start_time: when the event starts.
        event_type: "appointment", "medication", or "other".
        notes: optional free-text notes.
    """
    conn = get_connection()
    conn.execute(
        "insert into calendar_events (id, elder_id, title, event_type, start_time, notes) "
        "values (?, ?, ?, ?, ?, ?)",
        (
            str(uuid.uuid4()),
            elder_id,
            title,
            event_type,
            start_time.strftime(_START_TIME_FORMAT),
            notes,
        ),
    )
    conn.commit()


def list_upcoming_events(elder_id: str) -> list[CalendarEvent]:
    """List an elder's upcoming (not-yet-past) calendar events, soonest first.

    Args:
        elder_id: the elder profile to list events for.

    Returns:
        list[CalendarEvent]: upcoming events.
    """
    rows = (
        get_connection()
        .execute(
            "select * from calendar_events where elder_id = ? and start_time >= ? "
            "order by start_time asc",
            (elder_id, datetime.now().strftime(_START_TIME_FORMAT)),
        )
        .fetchall()
    )
    return [
        CalendarEvent(
            id=row["id"],
            elder_id=row["elder_id"],
            title=row["title"],
            event_type=row["event_type"],
            start_time=datetime.strptime(row["start_time"], _START_TIME_FORMAT),
            notes=row["notes"],
        )
        for row in rows
    ]
