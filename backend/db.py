"""Local SQLite connection, schema initialization, and demo data seeding.

No external account or manual setup is required — the schema self-applies
and a demo elder/family profile pair, with realistic medications and
calendar events, is seeded on first run.
"""

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

import streamlit as st

DB_PATH = Path(__file__).parent.parent / "data" / "app.db"
SCHEMA_PATH = Path(__file__).parent.parent / "sql" / "schema.sql"

SupportedLanguage = Literal["English", "Mandarin Chinese", "Malay", "Tamil"]


@dataclass
class Profile:
    id: str
    role: Literal["elder", "family"]
    display_name: str
    elder_id: str | None
    preferred_language: SupportedLanguage


@st.cache_resource
def get_connection() -> sqlite3.Connection:
    """Return a cached SQLite connection, schema-initialized and demo-seeded.

    Returns:
        sqlite3.Connection: a connection with row access by column name.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_PATH.read_text())
    conn.commit()
    _migrate(conn)
    _seed_demo_profiles(conn)
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Add columns to already-existing tables that predate them.

    `executescript`'s `create table if not exists` never touches a table
    that already exists, so schema additions to existing tables need an
    explicit, idempotent migration step here.
    """
    columns = {row["name"] for row in conn.execute("pragma table_info(profiles)")}
    if "preferred_language" not in columns:
        conn.execute(
            "alter table profiles add column preferred_language text not null default 'English'"
        )
        conn.commit()

    chat_columns = {row["name"] for row in conn.execute("pragma table_info(chat_messages)")}
    if "sender_name" not in chat_columns:
        # SQLite can't ALTER a CHECK constraint, so allowing sender='family'
        # and adding sender_name both require rebuilding the table.
        conn.executescript(
            """
            create table chat_messages_new (
              id text primary key,
              elder_id text not null references profiles(id),
              sender text not null check (sender in ('elder', 'ai', 'family')),
              content text not null,
              sentiment text check (sentiment in ('positive', 'neutral', 'low', 'distress')),
              repeated_question_flag integer default 0,
              sender_name text,
              created_at text default (datetime('now'))
            );
            insert into chat_messages_new
              (id, elder_id, sender, content, sentiment, repeated_question_flag, created_at)
              select id, elder_id, sender, content, sentiment, repeated_question_flag, created_at
              from chat_messages;
            drop table chat_messages;
            alter table chat_messages_new rename to chat_messages;
            """
        )
        conn.commit()


def _seed_demo_profiles(conn: sqlite3.Connection) -> None:
    """Insert a demo elder and linked family profile if none exist yet."""
    existing = conn.execute("select count(*) from profiles").fetchone()[0]
    if existing > 0:
        return

    elder_id = str(uuid.uuid4())
    family_id = str(uuid.uuid4())
    conn.execute(
        "insert into profiles (id, role, display_name, preferred_language) "
        "values (?, 'elder', ?, ?)",
        (elder_id, "Grandma Tan", "Mandarin Chinese"),
    )
    conn.execute(
        "insert into profiles (id, role, display_name, elder_id) values (?, 'family', ?, ?)",
        (family_id, "Mei Lin", elder_id),
    )
    for name, dosage, times in (
        ("Metformin", "500mg", ["08:00", "20:00"]),
        ("Amlodipine", "5mg", ["08:00"]),
    ):
        conn.execute(
            "insert into medications (id, elder_id, name, dosage, times_per_day) "
            "values (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), elder_id, name, dosage, json.dumps(times)),
        )

    for title, days_out, hour_minute in (
        ("Dentist Appointment", 6, "15:00"),
        ("Optician Appointment", 5, "11:00"),
    ):
        start_time = (datetime.now() + timedelta(days=days_out)).strftime(f"%Y-%m-%d {hour_minute}")
        conn.execute(
            "insert into calendar_events (id, elder_id, title, event_type, start_time) "
            "values (?, ?, ?, 'appointment', ?)",
            (str(uuid.uuid4()), elder_id, title, start_time),
        )

    # Shows the calendar isn't purely medical/admin -- placeholder dates
    # relative to seed time, standing in for real lunar-calendar lookups.
    for title, days_out in (("Mid-Autumn Festival", 45), ("Deepavali", 120)):
        start_time = (datetime.now() + timedelta(days=days_out)).strftime("%Y-%m-%d %H:%M")
        conn.execute(
            "insert into calendar_events (id, elder_id, title, event_type, start_time, notes) "
            "values (?, ?, ?, 'other', ?, ?)",
            (str(uuid.uuid4()), elder_id, title, start_time, "Cultural calendar awareness"),
        )
    conn.commit()


def _row_to_profile(row: sqlite3.Row) -> Profile:
    return Profile(
        id=row["id"],
        role=row["role"],
        display_name=row["display_name"],
        elder_id=row["elder_id"],
        preferred_language=row["preferred_language"],
    )


def get_profile_by_role(role: Literal["elder", "family"]) -> Profile | None:
    """Fetch the demo profile matching a role.

    Args:
        role: "elder" or "family".

    Returns:
        Profile | None: the matching profile, or None if not seeded yet.
    """
    row = (
        get_connection()
        .execute("select * from profiles where role = ? limit 1", (role,))
        .fetchone()
    )
    return _row_to_profile(row) if row is not None else None


def get_profile(profile_id: str) -> Profile | None:
    """Fetch a profile by id.

    Args:
        profile_id: the profile's id.

    Returns:
        Profile | None: the matching profile, or None if not found.
    """
    row = get_connection().execute("select * from profiles where id = ?", (profile_id,)).fetchone()
    return _row_to_profile(row) if row is not None else None


def update_preferred_language(elder_id: str, language: SupportedLanguage) -> None:
    """Set an elder's preferred language.

    Args:
        elder_id: the elder profile to update.
        language: one of the supported languages.
    """
    conn = get_connection()
    conn.execute(
        "update profiles set preferred_language = ? where id = ? and role = 'elder'",
        (language, elder_id),
    )
    conn.commit()
