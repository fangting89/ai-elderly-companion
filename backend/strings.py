"""Fixed, safety-critical elder-facing strings, per supported language.

These are reviewed once and never LLM-regenerated -- consistency matters
more than variation for a scam warning or a "photo isn't readable" notice,
and it costs no API call. Machine-drafted translations for Mandarin Chinese,
Malay, and Tamil; a native-speaker review is recommended before any
real-world use.
"""

from typing import Literal

StringKey = Literal[
    "scam_warning_title", "scam_warning_body", "blurry_photo_message", "daily_checkin"
]

_STRINGS: dict[str, dict[StringKey, str]] = {
    "English": {
        "scam_warning_title": "This looks like it could be a scam.",
        "scam_warning_body": (
            "Please don't reply, click any links, or send money or personal details. "
            "Ask a family member before doing anything else about this."
        ),
        "blurry_photo_message": (
            "The photo isn't clear enough to read. Please try taking another photo "
            "with better lighting."
        ),
        "daily_checkin": "Good morning! How are you feeling today? Did you take your medication?",
    },
    "Mandarin Chinese": {
        "scam_warning_title": "这看起来可能是一个骗局。",
        "scam_warning_body": (
            "请不要回复、点击任何链接，或提供金钱或个人资料。在采取任何行动之前，请先询问家人。"
        ),
        "blurry_photo_message": "这张照片不够清楚，无法阅读。请在光线更好的地方重新拍一张。",
        "daily_checkin": "早上好！您今天感觉怎么样？吃药了吗？",
    },
    "Malay": {
        "scam_warning_title": "Ini kelihatan seperti penipuan.",
        "scam_warning_body": (
            "Sila jangan balas, klik sebarang pautan, atau hantar wang atau maklumat peribadi. "
            "Tanya ahli keluarga sebelum membuat apa-apa tindakan mengenai perkara ini."
        ),
        "blurry_photo_message": (
            "Gambar ini tidak cukup jelas untuk dibaca. Sila cuba ambil gambar lain "
            "dengan pencahayaan yang lebih baik."
        ),
        "daily_checkin": (
            "Selamat pagi! Bagaimana perasaan anda hari ini? Adakah anda sudah makan ubat?"
        ),
    },
    "Tamil": {
        "scam_warning_title": "இது ஒரு மோசடி போல் தெரிகிறது.",
        "scam_warning_body": (
            "தயவுசெய்து பதிலளிக்க வேண்டாம், எந்த இணைப்புகளையும் கிளிக் செய்ய வேண்டாம், "
            "பணம் அல்லது தனிப்பட்ட தகவல்களை அனுப்ப வேண்டாம். இது பற்றி எதுவும் செய்யும் "
            "முன் குடும்ப உறுப்பினரிடம் கேளுங்கள்."
        ),
        "blurry_photo_message": (
            "இந்த புகைப்படம் படிக்க போதுமான தெளிவாக இல்லை. சிறந்த வெளிச்சத்தில் "
            "மற்றொரு புகைப்படம் எடுக்க முயற்சிக்கவும்."
        ),
        "daily_checkin": ("காலை வணக்கம்! இன்று உங்கள் உணர்வு எப்படி இருக்கிறது? மருந்து சாப்பிட்டீர்களா?"),
    },
}


def get_string(language: str, key: StringKey) -> str:
    """Look up a fixed safety-critical string for a language.

    Args:
        language: the elder's preferred language.
        key: which string to fetch.

    Returns:
        str: the string in that language, or the English version if the
            language isn't in the table.
    """
    return _STRINGS.get(language, _STRINGS["English"])[key]
