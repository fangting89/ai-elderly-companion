"""Functional round-trip tests for the FastAPI app, against an isolated
in-memory sqlite connection (not the real data/app.db) so nothing here
touches real data.

backend.db.get_connection is decorated with Streamlit's @st.cache_resource,
which isn't reliable to clear-and-recreate across many rapid test calls in
bare (non-Streamlit-runtime) mode -- state leaked between tests when this
file tried that approach. Instead, every module that does
`from backend.db import get_connection` gets its own bound copy patched
directly to the same shared per-test connection, matching the pattern
already used in test_family_notes.py/test_escalation.py.
"""

import sqlite3
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SCHEMA_PATH = Path(__file__).parent.parent / "sql" / "schema.sql"

# Every backend module that imports get_connection directly (`from
# backend.db import get_connection`) and that api/main.py exercises,
# transitively or not.
_MODULES_USING_GET_CONNECTION = [
    "backend.db",
    "backend.medications",
    "backend.memory_bank",
    "backend.family_notes",
    "backend.chat",
    "backend.companion_line",
    "backend.escalation",
]


@pytest.fixture
def client(tmp_path, monkeypatch):
    import importlib

    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA_PATH.read_text())

    for module_name in _MODULES_USING_GET_CONNECTION:
        module = importlib.import_module(module_name)
        monkeypatch.setattr(module, "get_connection", lambda conn=connection: conn)

    import backend.db as db

    db._seed_demo_profiles(connection)

    import backend.memory_bank as memory_bank

    monkeypatch.setattr(memory_bank, "UPLOADS_DIR", tmp_path / "uploads")

    from api.main import app

    return TestClient(app)


@pytest.fixture
def elder_id(client):
    import backend.db as db

    conn = db.get_connection()
    return conn.execute("select id from profiles where role = 'elder'").fetchone()[0]


def test_demo_profile_returns_seeded_ids(client, elder_id):
    response = client.get("/api/demo-profile")
    assert response.status_code == 200
    body = response.json()
    assert body["elderId"] == elder_id
    assert body["elderName"]
    assert body["familyId"]
    assert body["familyName"]
    assert body["preferredLanguage"] == "Mandarin Chinese"


def test_set_language_then_demo_profile_reflects_it(client, elder_id):
    response = client.post(
        "/api/profile/language", data={"elder_id": elder_id, "language": "Tamil"}
    )
    assert response.status_code == 200

    profile = client.get("/api/demo-profile").json()
    assert profile["preferredLanguage"] == "Tamil"


def test_photos_empty_by_default(client, elder_id):
    response = client.get("/api/photos", params={"elder_id": elder_id})
    assert response.status_code == 200
    assert response.json() == []


def test_upload_photo_then_list(client, elder_id):
    upload = client.post(
        "/api/photos",
        data={"elder_id": elder_id, "added_by": elder_id, "caption": "Lunch with Wei Ling"},
        files={"file": ("photo.jpg", b"fake-image-bytes", "image/jpeg")},
    )
    assert upload.status_code == 200

    listing = client.get("/api/photos", params={"elder_id": elder_id})
    assert listing.status_code == 200
    photos = listing.json()
    assert len(photos) == 1
    assert photos[0]["caption"] == "Lunch with Wei Ling"
    assert photos[0]["image_url"].startswith("/data/uploads/")


def test_latest_family_note_none_by_default(client, elder_id):
    response = client.get("/api/family-notes/latest", params={"elder_id": elder_id})
    assert response.status_code == 200
    assert response.json() is None


def test_send_family_note_then_fetch_latest(client, elder_id):
    send = client.post(
        "/api/family-notes",
        data={
            "elder_id": elder_id,
            "sender_name": "Wei Ling",
            "relation": "Your daughter",
            "text": "Love you, Ma",
        },
    )
    assert send.status_code == 200

    latest = client.get("/api/family-notes/latest", params={"elder_id": elder_id})
    assert latest.status_code == 200
    note = latest.json()
    assert note["senderName"] == "Wei Ling"
    assert note["relation"] == "Your daughter"
    assert note["text"] == "Love you, Ma"


def test_send_family_note_rejects_empty_text(client, elder_id):
    response = client.post(
        "/api/family-notes",
        data={"elder_id": elder_id, "sender_name": "Wei Ling", "relation": "", "text": "   "},
    )
    assert response.status_code == 422


def test_unknown_elder_id_returns_empty_not_error(client):
    response = client.get("/api/photos", params={"elder_id": str(uuid.uuid4())})
    assert response.status_code == 200
    assert response.json() == []


def test_medications_lists_seeded_defaults(client, elder_id):
    # _seed_demo_profiles seeds 2 realistic medications by default -- this
    # confirms the API surfaces them correctly, not that the list starts empty.
    response = client.get("/api/medications", params={"elder_id": elder_id})
    assert response.status_code == 200
    names = {m["name"] for m in response.json()}
    assert names == {"Metformin", "Amlodipine"}


def test_add_medication_then_list_and_todays_doses(client, elder_id):
    add = client.post(
        "/api/medications",
        data={
            "elder_id": elder_id,
            "name": "Vitamin D",
            "dosage": "1 tablet",
            "times_per_day": "09:00, 21:00",
        },
    )
    assert add.status_code == 200

    listing = client.get("/api/medications", params={"elder_id": elder_id}).json()
    assert len(listing) == 3
    added = next(m for m in listing if m["name"] == "Vitamin D")
    assert added["timesPerDay"] == ["09:00", "21:00"]

    doses = client.get("/api/medications/today", params={"elder_id": elder_id}).json()
    vitamin_d_doses = [d for d in doses if d["medicationName"] == "Vitamin D"]
    assert len(vitamin_d_doses) == 2


def test_add_medication_rejects_no_times(client, elder_id):
    response = client.post(
        "/api/medications",
        data={
            "elder_id": elder_id,
            "name": "Vitamin D",
            "dosage": "1 tablet",
            "times_per_day": " , ",
        },
    )
    assert response.status_code == 422


def test_mark_dose_taken(client, elder_id):
    client.post(
        "/api/medications",
        data={
            "elder_id": elder_id,
            "name": "Vitamin D",
            "dosage": "1 tablet",
            "times_per_day": "09:00",
        },
    )
    doses = client.get("/api/medications/today", params={"elder_id": elder_id}).json()
    vitamin_d_dose = next(d for d in doses if d["medicationName"] == "Vitamin D")

    response = client.post(f"/api/medications/{vitamin_d_dose['logId']}/taken")
    assert response.status_code == 200

    doses_after = client.get("/api/medications/today", params={"elder_id": elder_id}).json()
    updated = next(d for d in doses_after if d["logId"] == vitamin_d_dose["logId"])
    assert updated["status"] == "taken"


def test_point_and_ask_wires_elder_id_and_file(client, elder_id, monkeypatch):
    import api.main as api_main
    from backend.point_and_ask import PointAndAskResult

    captured = {}

    def fake_process_photo(elder_id_arg, image_bytes):
        captured["elder_id"] = elder_id_arg
        captured["image_bytes"] = image_bytes
        return PointAndAskResult(
            classification="scam",
            risk_level="high",
            content_summary="A fake scam letter.",
            explanation=None,
        )

    monkeypatch.setattr(api_main.point_and_ask, "process_photo", fake_process_photo)

    response = client.post(
        "/api/point-and-ask",
        data={"elder_id": elder_id},
        files={"file": ("letter.jpg", b"fake-bytes", "image/jpeg")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["classification"] == "scam"
    assert body["riskLevel"] == "high"
    assert captured["elder_id"] == elder_id
    assert captured["image_bytes"] == b"fake-bytes"


def test_check_in_opener_on_fresh_elder(client, elder_id):
    response = client.get("/api/check-in/opener", params={"elder_id": elder_id})
    assert response.status_code == 200
    body = response.json()
    assert body is not None
    assert body["text"]


def test_check_in_reply_wires_elder_id_and_text(client, elder_id, monkeypatch):
    import api.main as api_main
    from backend.chat import ChatReply

    captured = {}

    def fake_send_message(elder_id_arg, user_text, bounded=False):
        captured["elder_id"] = elder_id_arg
        captured["user_text"] = user_text
        captured["bounded"] = bounded
        return ChatReply(text="That sounds lovely, thanks for telling me.", can_continue=False)

    monkeypatch.setattr(api_main.chat, "send_message", fake_send_message)

    response = client.post(
        "/api/check-in", data={"elder_id": elder_id, "text": "I had a good walk today"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "That sounds lovely, thanks for telling me."
    assert body["canContinue"] is False
    assert captured["elder_id"] == elder_id
    assert captured["user_text"] == "I had a good walk today"
    assert captured["bounded"] is True


def test_check_in_reply_rejects_empty_text(client, elder_id):
    response = client.post("/api/check-in", data={"elder_id": elder_id, "text": "   "})
    assert response.status_code == 422


def test_family_nudge_opener_relocalizes_after_language_change(client, elder_id):
    # A fresh elder has no chat history and no prior mention of their family
    # member, so the family-contact nudge is guaranteed to be today's opener
    # (see backend.companion_line.decide_todays_opener's priority order).
    # Seeded default language is Mandarin Chinese.
    first = client.get("/api/check-in/opener", params={"elder_id": elder_id}).json()
    assert first["lineType"] == "family_nudge"
    assert "Mei Lin" in first["text"]
    chinese_text = first["text"]

    client.post("/api/profile/language", data={"elder_id": elder_id, "language": "English"})

    second = client.get("/api/check-in/opener", params={"elder_id": elder_id}).json()
    assert second["lineType"] == "family_nudge"
    assert "Mei Lin" in second["text"]
    assert second["text"] != chinese_text


def test_family_nudge_accepted_endpoint(client, elder_id):
    opener = client.get("/api/check-in/opener", params={"elder_id": elder_id}).json()
    assert opener["familyNudgeAccepted"] is False

    response = client.post("/api/check-in/family-nudge-accepted", data={"elder_id": elder_id})
    assert response.status_code == 200

    opener_after = client.get("/api/check-in/opener", params={"elder_id": elder_id}).json()
    assert opener_after["familyNudgeAccepted"] is True


def test_delete_photo(client, elder_id):
    client.post(
        "/api/photos",
        data={"elder_id": elder_id, "added_by": elder_id, "caption": "Lunch with Wei Ling"},
        files={"file": ("photo.jpg", b"fake-image-bytes", "image/jpeg")},
    )
    photos = client.get("/api/photos", params={"elder_id": elder_id}).json()
    assert len(photos) == 1

    response = client.delete(f"/api/photos/{photos[0]['id']}")
    assert response.status_code == 200

    photos_after = client.get("/api/photos", params={"elder_id": elder_id}).json()
    assert photos_after == []
