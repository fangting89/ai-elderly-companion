"""One-off generator for synthetic Point & Ask eval fixture images.

Renders each case's message as a plain text image (simulating a photographed
letter/message screenshot) plus one random-noise image for the unreadable
case. Run once whenever the case list below changes:

    uv run python eval/generate_point_and_ask_images.py
"""

import json
import random
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

IMAGES_DIR = Path(__file__).parent / "point_and_ask_images"
CASES_PATH = Path(__file__).parent / "point_and_ask_eval_cases.json"

CASES = [
    {
        "id": "case_01_scam_bank",
        "message": (
            "URGENT: Your bank account will be frozen today unless you verify "
            "your details now. Reply with your OTP immediately. Please don't "
            "tell your bank about this message."
        ),
        "expected_classification": "scam",
    },
    {
        "id": "case_02_scam_prize",
        "message": (
            "Congratulations! You've won a S$500 prize. Claim within 24 "
            "hours by sending your bank account number."
        ),
        "expected_classification": "scam",
    },
    {
        "id": "case_03_scam_tax",
        "message": (
            "This is the Inland Revenue Authority. You owe back taxes. Pay "
            "immediately via gift cards or face legal action. Keep this "
            "confidential."
        ),
        "expected_classification": "scam",
    },
    {
        "id": "case_04_legit_checkin",
        "message": (
            "Hi Grandma, just checking in, how are you feeling today? Let "
            "me know if you need anything. Love, Mei Lin"
        ),
        "expected_classification": "explain",
    },
    {
        "id": "case_05_legit_passport",
        "message": (
            "Reminder: Your passport will expire next month. Please renew "
            "it at the nearest ICA office before it expires."
        ),
        "expected_classification": "explain",
    },
    {
        "id": "case_07_scam_parcel",
        "message": (
            "Your parcel delivery failed. Click here and enter your address "
            "and payment details immediately to reschedule delivery today."
        ),
        "expected_classification": "scam",
    },
    {
        "id": "case_08_legit_medical",
        "message": (
            "Appointment Reminder: Dr. Lim, Tuesday 3pm, Raffles Medical. Please bring your NRIC."
        ),
        "expected_classification": "explain",
    },
    {
        "id": "case_09_scam_grandchild",
        "message": (
            "Grandma it's me, I'm in trouble and need money urgently, "
            "please don't tell mom and dad, send $2000 to this account now."
        ),
        "expected_classification": "scam",
    },
    {
        "id": "case_10_legit_community",
        "message": (
            "Community Center Event: Tai Chi in the Park, every Saturday "
            "8am. All welcome, no registration needed."
        ),
        "expected_classification": "explain",
    },
]


def _render_text_image(text: str, path: Path) -> None:
    img = Image.new("RGB", (900, 700), color="white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=28)
    wrapped = "\n".join(textwrap.wrap(text, width=38))
    draw.multiline_text((40, 40), wrapped, fill="black", font=font, spacing=10)
    img.save(path)


def _render_noise_image(path: Path) -> None:
    img = Image.new("RGB", (900, 700))
    pixels = img.load()
    for x in range(img.width):
        for y in range(img.height):
            pixels[x, y] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
    img.save(path)


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for case in CASES:
        filename = f"{case['id']}.png"
        _render_text_image(case["message"], IMAGES_DIR / filename)
        manifest.append(
            {
                "image": f"point_and_ask_images/{filename}",
                "expected_classification": case["expected_classification"],
            }
        )

    noise_filename = "case_06_unreadable.png"
    _render_noise_image(IMAGES_DIR / noise_filename)
    manifest.append(
        {"image": f"point_and_ask_images/{noise_filename}", "expected_classification": "unclear"}
    )

    CASES_PATH.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Generated {len(manifest)} images and {CASES_PATH.name}")


if __name__ == "__main__":
    main()
