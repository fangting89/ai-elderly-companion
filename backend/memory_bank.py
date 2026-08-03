"""Memory bank: family-provided facts/photos that give the companion context
about the elder's life, and reminiscence prompts generated from them.

Facts/photos are supplied by family, never invented by the AI -- the
companion only ever references what's actually stored here.
"""

import random
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from backend.claude_client import CHAT_MODEL, call_prose
from backend.db import get_connection

EntryType = Literal["photo", "fact"]
UPLOADS_DIR = Path(__file__).parent.parent / "data" / "uploads"


@dataclass
class MemoryBankEntry:
    id: str
    elder_id: str
    added_by: str
    entry_type: EntryType
    content_text: str | None
    image_path: str | None


def add_fact(elder_id: str, added_by: str, content_text: str) -> None:
    """Add a text fact to an elder's memory bank.

    Args:
        elder_id: the elder profile this fact is about.
        added_by: the family profile id adding it.
        content_text: the fact itself, e.g. "Loves gardening, especially roses."
    """
    conn = get_connection()
    conn.execute(
        "insert into memory_bank_entries (id, elder_id, added_by, entry_type, content_text) "
        "values (?, ?, ?, 'fact', ?)",
        (str(uuid.uuid4()), elder_id, added_by, content_text),
    )
    conn.commit()


def add_photo(elder_id: str, added_by: str, image_bytes: bytes, caption: str) -> None:
    """Add a photo (with a caption used as chat context) to an elder's memory bank.

    Args:
        elder_id: the elder profile this photo is about.
        added_by: the family profile id adding it.
        image_bytes: the photo's raw bytes.
        caption: a short description of the photo -- the image itself isn't
            re-sent to the model on every chat turn, only this text is.
    """
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}.jpg"
    (UPLOADS_DIR / filename).write_bytes(image_bytes)
    conn = get_connection()
    conn.execute(
        "insert into memory_bank_entries "
        "(id, elder_id, added_by, entry_type, content_text, image_path) "
        "values (?, ?, ?, 'photo', ?, ?)",
        (str(uuid.uuid4()), elder_id, added_by, caption, f"data/uploads/{filename}"),
    )
    conn.commit()


def list_entries(elder_id: str) -> list[MemoryBankEntry]:
    """List all memory bank entries for an elder, most recent first.

    Args:
        elder_id: the elder profile to list entries for.

    Returns:
        list[MemoryBankEntry]: the elder's memory bank entries.
    """
    rows = (
        get_connection()
        .execute(
            "select * from memory_bank_entries where elder_id = ? order by created_at desc",
            (elder_id,),
        )
        .fetchall()
    )
    return [
        MemoryBankEntry(
            id=row["id"],
            elder_id=row["elder_id"],
            added_by=row["added_by"],
            entry_type=row["entry_type"],
            content_text=row["content_text"],
            image_path=row["image_path"],
        )
        for row in rows
    ]


def delete_entry(entry_id: str) -> None:
    """Delete a memory bank entry, removing its photo file from disk if any.

    Args:
        entry_id: the memory bank entry to delete.
    """
    conn = get_connection()
    row = conn.execute(
        "select image_path from memory_bank_entries where id = ?", (entry_id,)
    ).fetchone()
    if row is not None and row["image_path"]:
        (UPLOADS_DIR / Path(row["image_path"]).name).unlink(missing_ok=True)
    conn.execute("delete from memory_bank_entries where id = ?", (entry_id,))
    conn.commit()


def get_context_facts(elder_id: str, limit: int = 10) -> list[str]:
    """Return recent memory bank facts as plain text, for chat context.

    Args:
        elder_id: the elder profile to fetch facts for.
        limit: max number of facts to include.

    Returns:
        list[str]: fact strings (photo captions count as facts too).
    """
    entries = list_entries(elder_id)[:limit]
    return [entry.content_text for entry in entries if entry.content_text]


def generate_reminiscence_prompt(elder_id: str, target_language: str) -> str | None:
    """Generate a warm conversation opener from a random stored memory.

    Args:
        elder_id: the elder profile to generate an opener for.
        target_language: language to write the opener in.

    Returns:
        str | None: the opener text, or None if no memories are stored yet.
    """
    facts = get_context_facts(elder_id)
    if not facts:
        return None
    fact = random.choice(facts)
    language_clause = "" if target_language == "English" else f" Write it in {target_language}."
    # Reminiscence should be a bridge to a real relationship, not just a
    # closed loop with the AI -- about half the time, if the fact names or
    # implies a specific person (a relative, a friend), gently nudge toward
    # sharing the memory with them, rather than only reminiscing about it here.
    bridge_clause = (
        " If this memory involves a specific family member or friend, gently "
        "suggest, in passing, that it might be nice to call or tell them about "
        "this memory -- but only if it fits naturally, don't force it."
        if random.random() < 0.5
        else ""
    )
    system = (
        "You write a single warm, short conversation-opening message for an "
        "elderly person, based on one fact their family shared about them. "
        f"Reference it naturally, like a fond memory.{language_clause}{bridge_clause} Do not "
        "invent any details beyond what's given."
    )
    return call_prose(model=CHAT_MODEL, system=system, messages=[{"role": "user", "content": fact}])
