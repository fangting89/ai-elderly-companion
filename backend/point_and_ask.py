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
from backend.config import get_settings
from backend.db import get_connection, get_profile
from backend.escalation import check_and_alert

Classification = Literal["explain", "scam", "unclear"]  # the 3 possible outcomes
RiskLevel = Literal["low", "medium", "high"]

_point_and_ask_settings = get_settings().point_and_ask
_prompts = get_settings().prompts

# Anthropic's recommended max edge for vision cost/quality balance
MAX_IMAGE_DIMENSION = _point_and_ask_settings.max_image_dimension
UPLOADS_DIR = Path(__file__).parent.parent / "data" / "uploads"  # where uploaded photos are saved

# System prompt for the AI's first look at the photo: extract facts only, don't judge scam risk
CLASSIFY_SYSTEM_PROMPT = _prompts.classify_system

# Forces the AI to answer via a fixed checklist instead of free text
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


# Holds the AI's checklist answers from classify_image()
@dataclass
class ClassifyResult:
    image_quality: Literal["clear", "blurry", "unreadable"]
    urgency: bool
    secrecy_request: bool
    authority_impersonation: bool
    money_request: bool
    content_summary: str


# The final answer sent back to the frontend to render
@dataclass
class PointAndAskResult:
    """explanation is generated directly in the elder's preferred language --
    never an English draft they'd need to read first."""

    classification: Classification
    risk_level: RiskLevel
    content_summary: str
    explanation: str | None


# Shrinks a photo if it's bigger than the vision API's recommended size
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


# Packages a photo into the shape Anthropic's API expects
def _image_block(image_bytes: bytes, media_type: str) -> dict:
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": base64.standard_b64encode(image_bytes).decode("utf-8"),
        },
    }


# Turns the AI's checklist answers into a low/medium/high score, with plain math
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
    # money/secrecy are the real tells; no core signal means low risk regardless of the rest
    core_signals = sum([result.money_request, result.secrecy_request])
    if core_signals == 0:
        return "low"
    # urgency/authority only escalate severity once a core signal is already present
    aggravating_signals = sum([result.urgency, result.authority_impersonation])
    total = core_signals * _point_and_ask_settings.core_signal_weight + aggravating_signals
    if total >= _point_and_ask_settings.high_risk_cutoff:
        return "high"
    if total >= _point_and_ask_settings.medium_risk_cutoff:
        return "medium"
    return "low"


# Picks which of the 3 screens (explain/scam/unclear) the elder sees
def decide_branch(result: ClassifyResult, risk_level: RiskLevel) -> Classification:
    """Deterministically route to the explain, scam, or unclear branch.

    Args:
        result: the classify step's extracted signals.
        risk_level: the scored risk level.

    Returns:
        Classification: which branch the UI should render.
    """
    if result.image_quality == "unreadable":
        return "unclear"  # can't read it -> ask them to retake the photo
    if risk_level in ("medium", "high"):
        return "scam"  # risky -> show the warning screen
    return "explain"  # otherwise -> show the plain-language explanation


# AI call #1: fills in the checklist, doesn't judge scam risk itself
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


# AI call #2: only for safe documents, writes the explanation directly in target_language
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
    system = _prompts.explain_image_base.format(language_clause=language_clause)
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


# Writes the photo to disk under data/uploads/ and returns its path
def _save_upload(image_bytes: bytes, media_type: str) -> str:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    ext = media_type.split("/")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    (UPLOADS_DIR / filename).write_bytes(image_bytes)
    return f"data/uploads/{filename}"


# Saves the whole result as one row in the documents table
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


# The conductor: runs the whole pipeline top to bottom for one uploaded photo
def process_photo(elder_id: str, raw_image_bytes: bytes) -> PointAndAskResult:
    """Run the full Point & Ask pipeline on an uploaded photo and persist the result.

    Args:
        elder_id: the elder profile this photo belongs to.
        raw_image_bytes: the uploaded file's raw bytes.

    Returns:
        PointAndAskResult: the branch, risk, and content to show in the UI.
    """
    # 1. Find out what language to reply in
    profile = get_profile(elder_id)
    target_language = profile.preferred_language if profile else "English"

    # 2. Shrink the photo if needed
    image_bytes, media_type = _resize_if_needed(raw_image_bytes)

    # 3. AI extracts signals, then plain code scores risk and picks the outcome
    result = classify_image(image_bytes, media_type)
    risk_level = score_risk(result)
    classification = decide_branch(result, risk_level)

    # 4. Only generate an explanation if the document is safe
    explanation = None
    if classification == "explain":
        explanation = explain_image(image_bytes, media_type, target_language)

    # 5. Save the photo file and the result row
    image_path = _save_upload(image_bytes, media_type)
    _persist(elder_id, image_path, classification, risk_level, result, explanation)

    # 6. Flag family if it's a scam
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
