"""API for the React frontend.

Reuses backend/*.py directly -- no business logic is duplicated here. No
auth/session system, matching the Streamlit app's zero-auth "View as"
simplicity: elder_id/added_by are passed explicitly per request.

CAUTION: unlike Streamlit (a single trusted process), this is a real
network-facing HTTP API -- any client that can reach it can pass any
elder_id and read/write that elder's data. Fine for local demo use
(localhost only); would need real authentication/authorization before any
deployment reachable beyond your own machine.
"""

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend import chat, companion_line, family_notes, medications, memory_bank, point_and_ask
from backend.db import get_profile, get_profile_by_role, update_preferred_language
from backend.memory_bank import UPLOADS_DIR

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="You Little Companion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

app.mount("/data/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.get("/api/demo-profile")
def demo_profile() -> dict:
    """Return the seeded demo elder/family profile ids and current language.

    No auth/login exists in this app (matching the Streamlit "View as"
    simplicity) -- the frontend uses this to know who "the elder" and "the
    family member" are without hardcoding a UUID that changes on reseed.

    Returns:
        dict: {"elderId", "elderName", "familyId", "familyName", "preferredLanguage"}.
    """
    elder = get_profile_by_role("elder")
    family = get_profile_by_role("family")
    if elder is None or family is None:
        raise HTTPException(status_code=404, detail="No demo profile seeded yet.")
    return {
        "elderId": elder.id,
        "elderName": elder.display_name,
        "familyId": family.id,
        "familyName": family.display_name,
        "preferredLanguage": elder.preferred_language,
    }


@app.post("/api/profile/language")
def set_language(elder_id: str = Form(...), language: str = Form(...)) -> dict:
    """Set an elder's preferred language.

    Args:
        elder_id: the elder profile to update.
        language: one of the four supported languages.

    Returns:
        dict: {"status": "ok"}.
    """
    update_preferred_language(elder_id, language)  # type: ignore[arg-type]
    return {"status": "ok"}


@app.get("/api/photos")
def list_photos(elder_id: str, limit: int = 20) -> list[dict]:
    """Return the most recent uploaded photos for the Home photo deck.

    Args:
        elder_id: the elder profile to fetch photos for.
        limit: max number of photos to return.

    Returns:
        list[dict]: {"id", "image_url", "caption"} for each photo, most recent first.
    """
    entries = memory_bank.list_entries(elder_id)
    photos = [e for e in entries if e.entry_type == "photo"][:limit]
    return [
        {"id": e.id, "image_url": f"/{e.image_path}", "caption": e.content_text or ""}
        for e in photos
    ]


@app.post("/api/photos")
async def upload_photo(
    elder_id: str = Form(...),
    added_by: str = Form(...),
    caption: str = Form(...),
    file: UploadFile = File(...),  # noqa: B008 -- FastAPI's own dependency-injection pattern
) -> dict:
    """Upload a photo to the elder's memory bank (shown in the Home photo deck).

    Args:
        elder_id: the elder profile this photo is for.
        added_by: the family profile id uploading it.
        caption: a short description shown in the photo deck.
        file: the image file.

    Returns:
        dict: {"status": "ok"}.
    """
    image_bytes = await file.read()
    memory_bank.add_photo(elder_id, added_by, image_bytes, caption)
    return {"status": "ok"}


@app.delete("/api/photos/{entry_id}")
def delete_photo(entry_id: str) -> dict:
    """Delete a photo from the elder's memory bank.

    Args:
        entry_id: the memory bank entry to delete.

    Returns:
        dict: {"status": "ok"}.
    """
    memory_bank.delete_entry(entry_id)
    return {"status": "ok"}


@app.get("/api/family-notes/latest")
def latest_family_note(elder_id: str) -> dict | None:
    """Return the most recent family note for an elder, if any.

    Args:
        elder_id: the elder profile to check.

    Returns:
        dict | None: the note's fields, or None if none exist yet.
    """
    note = family_notes.get_latest_note(elder_id)
    if note is None:
        return None
    return {
        "id": note.id,
        "senderName": note.sender_name,
        "relation": note.relation,
        "text": note.text,
        "createdAt": note.created_at,
    }


@app.post("/api/family-notes")
def send_family_note(
    elder_id: str = Form(...),
    sender_name: str = Form(...),
    relation: str = Form(""),
    text: str = Form(...),
) -> dict:
    """Send a family note to an elder's Home screen.

    Args:
        elder_id: the elder profile this note is for.
        sender_name: the family member's display name.
        relation: how they're described to the elder, e.g. "Your daughter".
        text: the note's text.

    Returns:
        dict: {"status": "ok"}.
    """
    if not text.strip():
        raise HTTPException(status_code=422, detail="Note text can't be empty.")
    family_notes.add_note(elder_id, sender_name, relation or None, text.strip())
    return {"status": "ok"}


@app.post("/api/point-and-ask")
async def point_and_ask_photo(
    elder_id: str = Form(...),
    file: UploadFile = File(...),  # noqa: B008 -- FastAPI's own dependency-injection pattern
) -> dict:
    """Classify an uploaded photo of a letter/message and explain or flag it.

    Args:
        elder_id: the elder profile this photo belongs to.
        file: the photographed/uploaded image.

    Returns:
        dict: {"classification", "riskLevel", "explanation", "contentSummary"}.
    """
    image_bytes = await file.read()
    result = point_and_ask.process_photo(elder_id, image_bytes)
    return {
        "classification": result.classification,
        "riskLevel": result.risk_level,
        "explanation": result.explanation,
        "contentSummary": result.content_summary,
    }


@app.get("/api/medications")
def list_medications(elder_id: str) -> list[dict]:
    """List all medications a family member has added for an elder.

    Args:
        elder_id: the elder profile to list medications for.

    Returns:
        list[dict]: {"id", "name", "dosage", "timesPerDay"} for each medication.
    """
    return [
        {"id": m.id, "name": m.name, "dosage": m.dosage, "timesPerDay": m.times_per_day}
        for m in medications.list_medications(elder_id)
    ]


@app.post("/api/medications")
def add_medication(
    elder_id: str = Form(...),
    name: str = Form(...),
    dosage: str = Form(...),
    times_per_day: str = Form(...),
) -> dict:
    """Add a medication for an elder -- a family-only action.

    Args:
        elder_id: the elder profile this medication belongs to.
        name: medication name.
        dosage: dosage description, e.g. "1 tablet".
        times_per_day: comma-separated "HH:MM" times, e.g. "08:00,20:00".

    Returns:
        dict: {"status": "ok"}.
    """
    times = [t.strip() for t in times_per_day.split(",") if t.strip()]
    if not times:
        raise HTTPException(status_code=422, detail="At least one time is required.")
    medications.add_medication(elder_id, name, dosage, times)
    return {"status": "ok"}


@app.get("/api/medications/today")
def todays_doses(elder_id: str) -> list[dict]:
    """Return today's medication doses with up-to-date status for an elder.

    Args:
        elder_id: the elder profile to fetch doses for.

    Returns:
        list[dict]: {"logId", "medicationName", "dosage", "scheduledFor", "status"}.
    """
    return [
        {
            "logId": d.log_id,
            "medicationName": d.medication_name,
            "dosage": d.dosage,
            "scheduledFor": d.scheduled_for.isoformat(),
            "status": d.status,
        }
        for d in medications.get_todays_doses(elder_id)
    ]


@app.post("/api/medications/{log_id}/taken")
def mark_dose_taken(log_id: str) -> dict:
    """Mark a dose as taken.

    Args:
        log_id: the medication log entry's id.

    Returns:
        dict: {"status": "ok"}.
    """
    medications.mark_taken(log_id)
    return {"status": "ok"}


@app.get("/api/check-in/opener")
def check_in_opener(elder_id: str) -> dict | None:
    """Return today's companion opener line for the Check-In page.

    Inserts today's opener (a family-contact nudge, a reminiscence prompt, or
    the plain daily check-in, in that priority order) if none exists yet
    today -- the exact same mechanism the Home screen's card already uses.

    Args:
        elder_id: the elder profile to check in on.

    Returns:
        dict | None: {"text", "lineType", "familyNudgeAccepted"}, or None if
            the elder already exchanged a message today (nothing new to open
            with). "familyNudgeAccepted" is only meaningful when "lineType"
            is "family_nudge".
    """
    profile = get_profile(elder_id)
    language = profile.preferred_language if profile else "English"
    chat.maybe_send_daily_checkin(elder_id)
    opener = chat.get_todays_opener(elder_id, language)
    if opener is None:
        return None
    line_type = companion_line.get_todays_line_type(elder_id)
    return {
        "text": opener,
        "lineType": line_type,
        "familyNudgeAccepted": companion_line.family_nudge_accepted_today(elder_id)
        if line_type == "family_nudge"
        else False,
    }


@app.post("/api/check-in/family-nudge-accepted")
def check_in_family_nudge_accepted(elder_id: str = Form(...)) -> dict:
    """Record that the elder acted on today's family-contact nudge.

    Args:
        elder_id: the elder profile confirming they'll reach out.

    Returns:
        dict: {"status": "ok"}.
    """
    companion_line.log_family_nudge_accepted(elder_id)
    return {"status": "ok"}


@app.post("/api/check-in")
def check_in_reply(elder_id: str = Form(...), text: str = Form(...)) -> dict:
    """Send the elder's check-in reply and get the companion's response.

    Reuses backend.chat.send_message directly, so the real safety-relevant
    behavior (sentiment escalation, repeated-question detection, calendar
    auto-add) stays intact -- only the frontend's presentation is different
    (at most two exchanges, not a persistent thread). Passes bounded=True so
    a low-mood/distress first reply unlocks exactly one follow-up reply
    before the companion closes the check-in for today.

    Args:
        elder_id: the elder profile sending this message.
        text: the elder's message text.

    Returns:
        dict: {"reply", "canContinue"} -- canContinue is True only when one
            more reply box should be shown today.
    """
    if not text.strip():
        raise HTTPException(status_code=422, detail="Message can't be empty.")
    result = chat.send_message(elder_id, text.strip(), bounded=True)
    return {"reply": result.text, "canContinue": result.can_continue}
