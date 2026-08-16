"""Family notes: a short message from family shown on the elder's Home screen.

Kept separate from chat_messages -- this backs the React frontend's
Home-screen "note from family" card, independent of chat history.
"""

import uuid
from dataclasses import dataclass

from backend.db import get_connection


# One row from the family_notes table -- a note shown on the elder's Home screen
@dataclass
class FamilyNote:
    id: str
    elder_id: str
    sender_name: str
    relation: str | None
    text: str
    created_at: str


# Saves a new note from a family member for the elder to see
def add_note(elder_id: str, sender_name: str, relation: str | None, text: str) -> None:
    """Add a family note for an elder to see on their Home screen.

    Args:
        elder_id: the elder profile this note is for.
        sender_name: the family member's display name, e.g. "Wei Ling".
        relation: how they're described to the elder, e.g. "Your daughter".
        text: the note's text.
    """
    conn = get_connection()
    conn.execute(
        "insert into family_notes (id, elder_id, sender_name, relation, text) "
        "values (?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), elder_id, sender_name, relation, text),
    )
    conn.commit()


# Fetches the single most recent note, for the Home screen card
def get_latest_note(elder_id: str) -> FamilyNote | None:
    """Return the most recent family note for an elder, if any.

    Args:
        elder_id: the elder profile to check.

    Returns:
        FamilyNote | None: the latest note, or None if none exist yet.
    """
    # created_at has second-level resolution, so two notes added within the
    # same second would tie -- rowid (insertion order) breaks the tie.
    row = (
        get_connection()
        .execute(
            "select * from family_notes where elder_id = ? "
            "order by created_at desc, rowid desc limit 1",
            (elder_id,),
        )
        .fetchone()
    )
    if row is None:
        return None
    return FamilyNote(
        id=row["id"],
        elder_id=row["elder_id"],
        sender_name=row["sender_name"],
        relation=row["relation"],
        text=row["text"],
        created_at=row["created_at"],
    )
