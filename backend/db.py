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
from functools import cache
from pathlib import Path
from typing import Literal

DB_PATH = Path(__file__).parent.parent / "data" / "app.db"  # the sqlite file on disk
SCHEMA_PATH = Path(__file__).parent.parent / "sql" / "schema.sql"  # table definitions

# The 4 languages the app supports
SupportedLanguage = Literal["English", "Mandarin Chinese", "Malay", "Tamil"]


# One row from the profiles table -- either an elder or a family member
@dataclass
class Profile:
    id: str
    role: Literal["elder", "family"]
    display_name: str
    elder_id: str | None
    preferred_language: SupportedLanguage


@cache
def get_connection() -> sqlite3.Connection:
    """Return a cached SQLite connection, schema-initialized and demo-seeded.

    Cached so the whole app shares one connection instead of reopening the
    file per request -- fine here since sqlite3's own locking serializes
    writes anyway, and this stays a single-process app.

    Returns:
        sqlite3.Connection: a connection with row access by column name.
    """
    # 1. Make sure the data/ folder exists, then open (or create) the db file
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    # FastAPI can serve requests on different threads; sqlite3 connections
    # are thread-confined by default and would raise on the second thread
    # to touch this one without this flag.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # lets us read columns by name, e.g. row["id"]

    # 2. Create any tables that don't exist yet
    conn.executescript(SCHEMA_PATH.read_text())
    conn.commit()

    # 3. Patch up tables that existed before a schema change, and seed demo data
    _migrate(conn)
    _seed_demo_profiles(conn)
    return conn


# Adds columns/tables that a schema update introduced, for a db file created before that update
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


# Fills a fresh/empty database with one demo elder, one family member, and sample data
def _seed_demo_profiles(conn: sqlite3.Connection) -> None:
    """Insert a demo elder and linked family profile if none exist yet."""
    # Only seed once -- skip if any profile already exists
    existing = conn.execute("select count(*) from profiles").fetchone()[0]
    if existing > 0:
        return

    # 1. Create the elder and the family member linked to them
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

    # 2. Give the elder a couple of sample medications
    for name, dosage, times in (
        ("Metformin", "500mg", ["08:00", "20:00"]),
        ("Amlodipine", "5mg", ["08:00"]),
    ):
        conn.execute(
            "insert into medications (id, elder_id, name, dosage, times_per_day) "
            "values (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), elder_id, name, dosage, json.dumps(times)),
        )

    # 3. Add a couple of upcoming appointments
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

    # 4. Add a couple of cultural events too, so the calendar isn't purely
    # medical/admin -- placeholder dates relative to seed time, standing in
    # for real lunar-calendar lookups.
    for title, days_out in (("Mid-Autumn Festival", 45), ("Deepavali", 120)):
        start_time = (datetime.now() + timedelta(days=days_out)).strftime("%Y-%m-%d %H:%M")
        conn.execute(
            "insert into calendar_events (id, elder_id, title, event_type, start_time, notes) "
            "values (?, ?, ?, 'other', ?, ?)",
            (str(uuid.uuid4()), elder_id, title, start_time, "Cultural calendar awareness"),
        )
    conn.commit()


# Converts one raw sqlite row into a Profile object
def _row_to_profile(row: sqlite3.Row) -> Profile:
    return Profile(
        id=row["id"],
        role=row["role"],
        display_name=row["display_name"],
        elder_id=row["elder_id"],
        preferred_language=row["preferred_language"],
    )


# Finds the (single, seeded) demo elder or family profile
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


# Looks up any profile (elder or family) by its id
def get_profile(profile_id: str) -> Profile | None:
    """Fetch a profile by id.

    Args:
        profile_id: the profile's id.

    Returns:
        Profile | None: the matching profile, or None if not found.
    """
    row = get_connection().execute("select * from profiles where id = ?", (profile_id,)).fetchone()
    return _row_to_profile(row) if row is not None else None


# Saves a new language choice for an elder, e.g. from the Family Settings page
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
