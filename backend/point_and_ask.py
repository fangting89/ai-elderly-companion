"""Point & Ask: classify an uploaded photo, then explain it or flag it as a scam.

The vision model only ever extracts signals (image quality, scam-behavior
booleans) via forced tool-use. The actual branch decision (explain vs. scam
vs. unclear) is deterministic Python arithmetic over those signals, not
another LLM call, which keeps the safety-relevant decision testable and
reproducible.
"""

import base64
import json
import uuid
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Literal

from PIL import Image

from backend.claude_client import CHAT_MODEL, TAG_MODEL, call_prose, call_structured
from backend.db import get_connection, get_profile
from backend.escalation import check_and_alert

Classification = Literal["explain", "scam", "unclear"]
RiskLevel = Literal["low", "medium", "high"]

MAX_IMAGE_DIMENSION = 1568  # Anthropic's recommended max edge for vision cost/quality balance
UPLOADS_DIR = Path(__file__).parent.parent / "data" / "uploads"

CLASSIFY_SYSTEM_PROMPT = (
    "You analyze a photo of a letter, message, or document sent to an elderly "
    "person. Extract only what is visible; never invent details. Judge each "
    "signal independently: a separate scoring system decides overall risk, "
    "not you. In content_summary, never restate a full NRIC number, full home "
    "address, or other sensitive personal identifier even if visible in the "
    "photo. Describe it generically instead (e.g. 'asks the reader to "
    "confirm their NRIC')."
)

CLASSIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "image_quality": {
            "type": "string",
            "enum": ["clear", "blurry", "unreadable"],
            "description": "Whether the photo is clear enough to read reliably.",
        },
        "urgency": {
            "type": "boolean",
            "description": (
                "Creates pressure to act immediately (e.g. same-day deadline, 'act now')."
            ),
        },
        "secrecy_request": {
            "type": "boolean",
            "description": "Asks the recipient to keep this private or not tell family/bank.",
        },
        "authority_impersonation": {
            "type": "boolean",
            "description": (
                "Claims to be from a bank, government agency, courier, or other authority."
            ),
        },
        "money_request": {
            "type": "boolean",
            "description": (
                "Asks for money, payment, gift cards, wire transfer, or bank/personal details."
            ),
        },
        "content_summary": {
            "type": "string",
            "description": "One or two factual sentences on what the document/message says.",
        },
    },
    "required": [
        "image_quality",
        "urgency",
        "secrecy_request",
        "authority_impersonation",
        "money_request",
        "content_summary",
    ],
}


@dataclass
class ClassifyResult:
    image_quality: Literal["clear", "blurry", "unreadable"]
    urgency: bool
    secrecy_request: bool
    authority_impersonation: bool
    money_request: bool
    content_summary: str


@dataclass
class PointAndAskResult:
    """explanation is generated directly in the elder's preferred language --
    never an English draft they'd need to read first."""

    classification: Classification
    risk_level: RiskLevel
    content_summary: str
    explanation: str | None


def _resize_if_needed(image_bytes: bytes) -> tuple[bytes, str]:
    """Downscale an image if it exceeds the recommended max dimension.

    Args:
        image_bytes: raw image bytes.

    Returns:
        tuple[bytes, str]: possibly-resized image bytes, and its media type.
    """
    img = Image.open(BytesIO(image_bytes))
    img_format = (img.format or "JPEG").upper()
    media_type = f"image/{'jpeg' if img_format == 'JPEG' else img_format.lower()}"
    if max(img.size) <= MAX_IMAGE_DIMENSION:
        return image_bytes, media_type
    img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION))
    buffer = BytesIO()
    img.convert("RGB").save(buffer, format=img_format if img_format != "PNG" else "PNG")
    return buffer.getvalue(), media_type


def _image_block(image_bytes: bytes, media_type: str) -> dict:
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": base64.standard_b64encode(image_bytes).decode("utf-8"),
        },
    }


def score_risk(result: ClassifyResult) -> RiskLevel:
    """Deterministically score scam risk from extracted signals.

    money_request and secrecy_request are the core diagnostic signals: real
    correspondence essentially never demands payment/personal details under
    pressure, or asks the recipient to hide it from family. urgency and
    authority_impersonation alone are common in legitimate mail too (a real
    deadline, a real government notice) and only escalate severity once a
    core signal is already present.

    Args:
        result: the classify step's extracted signals.

    Returns:
        RiskLevel: "low", "medium", or "high".
    """
    core_signals = sum([result.money_request, result.secrecy_request])
    if core_signals == 0:
        return "low"
    aggravating_signals = sum([result.urgency, result.authority_impersonation])
    total = core_signals * 2 + aggravating_signals
    if total >= 5:
        return "high"
    if total >= 3:
        return "medium"
    return "low"


def decide_branch(result: ClassifyResult, risk_level: RiskLevel) -> Classification:
    """Deterministically route to the explain, scam, or unclear branch.

    Args:
        result: the classify step's extracted signals.
        risk_level: the scored risk level.

    Returns:
        Classification: which branch the UI should render.
    """
    if result.image_quality == "unreadable":
        return "unclear"
    if risk_level in ("medium", "high"):
        return "scam"
    return "explain"


def classify_image(image_bytes: bytes, media_type: str) -> ClassifyResult:
    """Run the vision classify step on an uploaded photo.

    Args:
        image_bytes: raw (already resized) image bytes.
        media_type: MIME type of the image.

    Returns:
        ClassifyResult: extracted signals and image quality.
    """
    tags = call_structured(
        model=TAG_MODEL,
        system=CLASSIFY_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    _image_block(image_bytes, media_type),
                    {"type": "text", "text": "Analyze this document photo."},
                ],
            }
        ],
        tool_name="classify_document",
        tool_description="Extract scam signals and image quality from a document photo.",
        tool_schema=CLASSIFY_SCHEMA,
    )
    return ClassifyResult(**tags)


def explain_image(image_bytes: bytes, media_type: str, target_language: str) -> str:
    """Generate a plain-language explanation of a document photo, in the given language.

    Args:
        image_bytes: raw (already resized) image bytes.
        media_type: MIME type of the image.
        target_language: language to write the explanation in (this is the
            only version generated -- no separate English draft).

    Returns:
        str: the explanation, written directly in target_language.
    """
    language_clause = "" if target_language == "English" else f" Write it in {target_language}."
    system = (
        "You explain a document photo to an elderly person in simple, plain "
        f"language.{language_clause} Never give legal or financial advice; "
        "suggest they involve family for anything involving money or deadlines. "
        "Never restate a full NRIC number, full home address, or other sensitive "
        "personal identifier even if visible in the photo. Refer to it generically "
        "instead (e.g. 'your NRIC number')."
    )
    return call_prose(
        model=CHAT_MODEL,
        system=system,
        messages=[
            {
                "role": "user",
                "content": [
                    _image_block(image_bytes, media_type),
                    {"type": "text", "text": "Explain this document."},
                ],
            }
        ],
    )


def _save_upload(image_bytes: bytes, media_type: str) -> str:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    ext = media_type.split("/")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    (UPLOADS_DIR / filename).write_bytes(image_bytes)
    return f"data/uploads/{filename}"


def _persist(
    elder_id: str,
    image_path: str,
    classification: Classification,
    risk_level: RiskLevel,
    result: ClassifyResult,
    explanation: str | None,
) -> None:
    conn = get_connection()
    conn.execute(
        "insert into documents "
        "(id, elder_id, image_path, classification, summary_text, translated_text, "
        "scam_risk_level, scam_signals) values (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            str(uuid.uuid4()),
            elder_id,
            image_path,
            classification,
            result.content_summary,
            explanation,
            risk_level if classification == "scam" else None,
            json.dumps(
                {
                    "urgency": result.urgency,
                    "secrecy_request": result.secrecy_request,
                    "authority_impersonation": result.authority_impersonation,
                    "money_request": result.money_request,
                }
            ),
        ),
    )
    conn.commit()


def process_photo(elder_id: str, raw_image_bytes: bytes) -> PointAndAskResult:
    """Run the full Point & Ask pipeline on an uploaded photo and persist the result.

    Args:
        elder_id: the elder profile this photo belongs to.
        raw_image_bytes: the uploaded file's raw bytes.

    Returns:
        PointAndAskResult: the branch, risk, and content to show in the UI.
    """
    profile = get_profile(elder_id)
    target_language = profile.preferred_language if profile else "English"

    image_bytes, media_type = _resize_if_needed(raw_image_bytes)

    result = classify_image(image_bytes, media_type)
    risk_level = score_risk(result)
    classification = decide_branch(result, risk_level)

    explanation = None
    if classification == "explain":
        explanation = explain_image(image_bytes, media_type, target_language)

    image_path = _save_upload(image_bytes, media_type)
    _persist(elder_id, image_path, classification, risk_level, result, explanation)

    if classification == "scam":
        check_and_alert(
            elder_id,
            "scam_detected",
            {"risk_level": risk_level, "summary": result.content_summary},
        )

    return PointAndAskResult(
        classification=classification,
        risk_level=risk_level,
        content_summary=result.content_summary,
        explanation=explanation,
    )
