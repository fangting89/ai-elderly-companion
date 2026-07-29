"""Local SQLite connection, schema initialization, and demo profile seeding.

No external account or manual setup is required — the schema self-applies
and a demo elder/family profile pair is seeded on first run.
"""

import sqlite3
import uuid
from dataclasses import dataclass
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
