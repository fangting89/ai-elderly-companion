"""Unit tests for point_and_ask's full process_photo() pipeline (classify ->
score -> branch -> explain/escalate -> save), against an isolated in-memory
DB with uploads redirected to a temp directory and the Claude calls mocked
out -- no real API cost. backend/tests/test_risk_scoring.py already covers
score_risk()/decide_branch() as pure functions; this file covers the
orchestration around them.
"""

import importlib
import io
import sqlite3
import uuid
from pathlib import Path

import pytest
from PIL import Image

from backend import point_and_ask

SCHEMA_PATH = Path(__file__).parent.parent / "sql" / "schema.sql"

_MODULES_USING_GET_CONNECTION = ["backend.db", "backend.point_and_ask", "backend.escalation"]

_SAFE_SIGNALS = {
    "image_quality": "clear",
    "urgency": False,
    "secrecy_request": False,
    "authority_impersonation": False,
    "money_request": False,
    "content_summary": "A friendly reminder about an appointment.",
}

_SCAM_SIGNALS = {
    "image_quality": "clear",
    "urgency": True,
    "secrecy_request": True,
    "authority_impersonation": True,
    "money_request": True,
    "content_summary": "Demands urgent payment and secrecy.",
}


def _fake_photo_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), color="white").save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def elder_id(monkeypatch, tmp_path):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA_PATH.read_text())
    elder_id = str(uuid.uuid4())
    connection.execute(
        "insert into profiles (id, role, display_name, preferred_language) "
        "values (?, 'elder', 'Test Elder', 'English')",
        (elder_id,),
    )
    connection.commit()

    for module_name in _MODULES_USING_GET_CONNECTION:
        module = importlib.import_module(module_name)
        monkeypatch.setattr(module, "get_connection", lambda conn=connection: conn)

    monkeypatch.setattr(point_and_ask, "UPLOADS_DIR", tmp_path)
    return elder_id


def _mock_classify(monkeypatch, signals: dict) -> None:
    monkeypatch.setattr(point_and_ask, "call_structured", lambda **kwargs: dict(signals))


def _documents_rows(elder_id: str) -> list:
    return (
        point_and_ask.get_connection()
        .execute("select * from documents where elder_id = ?", (elder_id,))
        .fetchall()
    )


def _alert_count(elder_id: str, alert_type: str) -> int:
    return (
        point_and_ask.get_connection()
        .execute(
            "select count(*) from alerts where elder_id = ? and alert_type = ?",
            (elder_id, alert_type),
        )
        .fetchone()[0]
    )


def test_safe_document_explains_and_does_not_escalate(elder_id, monkeypatch):
    _mock_classify(monkeypatch, _SAFE_SIGNALS)
    monkeypatch.setattr(point_and_ask, "call_prose", lambda **kwargs: "Here's what it says.")

    result = point_and_ask.process_photo(elder_id, _fake_photo_bytes())

    assert result.classification == "explain"
    assert result.risk_level == "low"
    assert result.explanation == "Here's what it says."
    assert len(_documents_rows(elder_id)) == 1
    assert _alert_count(elder_id, "scam_detected") == 0


def test_scam_document_escalates_and_skips_explanation(elder_id, monkeypatch):
    _mock_classify(monkeypatch, _SCAM_SIGNALS)

    def _fail_if_called(**kwargs):
        raise AssertionError("explain_image should not run on the scam branch")

    monkeypatch.setattr(point_and_ask, "call_prose", _fail_if_called)

    result = point_and_ask.process_photo(elder_id, _fake_photo_bytes())

    assert result.classification == "scam"
    assert result.risk_level == "high"
    assert result.explanation is None
    row = _documents_rows(elder_id)[0]
    assert row["scam_risk_level"] == "high"
    assert _alert_count(elder_id, "scam_detected") == 1


def test_unreadable_document_is_unclear_and_does_not_escalate(elder_id, monkeypatch):
    signals = dict(_SAFE_SIGNALS, image_quality="unreadable")
    _mock_classify(monkeypatch, signals)

    result = point_and_ask.process_photo(elder_id, _fake_photo_bytes())

    assert result.classification == "unclear"
    assert result.explanation is None
    assert _alert_count(elder_id, "scam_detected") == 0


def test_photo_file_is_saved_to_uploads_dir(elder_id, monkeypatch, tmp_path):
    _mock_classify(monkeypatch, _SAFE_SIGNALS)
    monkeypatch.setattr(point_and_ask, "call_prose", lambda **kwargs: "Explanation.")

    point_and_ask.process_photo(elder_id, _fake_photo_bytes())

    saved_files = list(tmp_path.glob("*.png"))
    assert len(saved_files) == 1
