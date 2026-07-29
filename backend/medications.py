"""Medication tracking: CRUD, daily log generation, and status classification.

Status classification is a pure function (classify_dose_status), separate
from the I/O and escalation side effects in get_todays_doses -- same split
used for the Point & Ask risk scorer, and for the same reason: the
safety-relevant decision needs to be independently testable.
"""

import json
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Literal

from backend.db import get_connection
from backend.escalation import check_and_alert

DoseStatus = Literal["pending", "taken", "missed"]
GRACE_MINUTES = 30
_SCHEDULED_FOR_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass
class Medication:
    id: str
    elder_id: str
    name: str
    dosage: str
    times_per_day: list[str]


@dataclass
class DoseEntry:
    log_id: str
    medication_id: str
    medication_name: str
    dosage: str
    scheduled_for: datetime
    status: DoseStatus


def add_medication(elder_id: str, name: str, dosage: str, times_per_day: list[str]) -> None:
    """Add a new medication for an elder.

    Args:
        elder_id: the elder profile this medication belongs to.
        name: medication name.
        dosage: dosage description (e.g. "1 tablet").
        times_per_day: list of "HH:MM" times, e.g. ["08:00", "20:00"].
    """
    conn = get_connection()
    conn.execute(
        "insert into medications (id, elder_id, name, dosage, times_per_day) "
        "values (?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), elder_id, name, dosage, json.dumps(times_per_day)),
    )
    conn.commit()


def list_medications(elder_id: str) -> list[Medication]:
    """List all medications for an elder.

    Args:
        elder_id: the elder profile to list medications for.

    Returns:
        list[Medication]: the elder's medications.
    """
    rows = (
        get_connection()
        .execute("select * from medications where elder_id = ?", (elder_id,))
        .fetchall()
    )
    return [
        Medication(
            id=row["id"],
            elder_id=row["elder_id"],
            name=row["name"],
            dosage=row["dosage"],
            times_per_day=json.loads(row["times_per_day"]),
        )
        for row in rows
    ]


def classify_dose_status(
    scheduled_for: datetime, taken_at: datetime | None, now: datetime
) -> DoseStatus:
    """Deterministically classify a single dose's status.

    Args:
        scheduled_for: when the dose was scheduled.
        taken_at: when it was actually taken, or None if not yet taken.
        now: the current time to classify against.

    Returns:
        DoseStatus: "taken", "missed", or "pending".
    """
    if taken_at is not None:
        return "taken"
    if now >= scheduled_for + timedelta(minutes=GRACE_MINUTES):
        return "missed"
    return "pending"


def _ensure_todays_logs(elder_id: str) -> None:
    conn = get_connection()
    today = date.today().isoformat()
    for med in list_medications(elder_id):
        for time_str in med.times_per_day:
            scheduled_for = f"{today} {time_str}:00"
            existing = conn.execute(
                "select 1 from medication_logs where medication_id = ? and scheduled_for = ?",
                (med.id, scheduled_for),
            ).fetchone()
            if existing is None:
                conn.execute(
                    "insert into medication_logs "
                    "(id, medication_id, elder_id, scheduled_for, status) "
                    "values (?, ?, ?, ?, 'pending')",
                    (str(uuid.uuid4()), med.id, elder_id, scheduled_for),
                )
    conn.commit()


def get_todays_doses(elder_id: str) -> list[DoseEntry]:
    """Return today's medication doses with up-to-date status.

    Generates today's expected log rows if missing, then reclassifies any
    still-pending dose against the current time -- persisting and
    escalating (if this is a repeat miss for that medication) any dose that
    has newly become missed.

    Args:
        elder_id: the elder profile to fetch doses for.

    Returns:
        list[DoseEntry]: today's doses, ordered by scheduled time.
    """
    _ensure_todays_logs(elder_id)
    conn = get_connection()
    today = date.today().isoformat()
    now = datetime.now()

    rows = conn.execute(
        "select medication_logs.id as log_id, medication_logs.medication_id, "
        "medication_logs.scheduled_for, medication_logs.status, medication_logs.taken_at, "
        "medications.name, medications.dosage "
        "from medication_logs "
        "join medications on medications.id = medication_logs.medication_id "
        "where medication_logs.elder_id = ? and date(medication_logs.scheduled_for) = ? "
        "order by medication_logs.scheduled_for asc",
        (elder_id, today),
    ).fetchall()

    doses = []
    for row in rows:
        scheduled_for = datetime.strptime(row["scheduled_for"], _SCHEDULED_FOR_FORMAT)
        taken_at = (
            datetime.strptime(row["taken_at"], _SCHEDULED_FOR_FORMAT) if row["taken_at"] else None
        )
        status = classify_dose_status(scheduled_for, taken_at, now)

        if status == "missed" and row["status"] != "missed":
            conn.execute(
                "update medication_logs set status = 'missed' where id = ?", (row["log_id"],)
            )
            conn.commit()
            check_and_alert(
                elder_id,
                "missed_medication",
                {"medication_id": row["medication_id"], "medication_name": row["name"]},
            )

        doses.append(
            DoseEntry(
                log_id=row["log_id"],
                medication_id=row["medication_id"],
                medication_name=row["name"],
                dosage=row["dosage"],
                scheduled_for=scheduled_for,
                status=status,
            )
        )
    return doses


def mark_taken(log_id: str) -> None:
    """Mark a dose as taken.

    Args:
        log_id: the medication_logs row id to mark.
    """
    conn = get_connection()
    conn.execute(
        "update medication_logs set status = 'taken', taken_at = ? where id = ?",
        (datetime.now().strftime(_SCHEDULED_FOR_FORMAT), log_id),
    )
    conn.commit()
