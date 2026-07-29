"""Fixed strings for everything the elder sees, per supported language.

Covers two categories, both fixed/reviewed rather than LLM-regenerated:
safety-critical messages (scam warning, blurry-photo notice, daily check-in)
and UI chrome on the elder's own pages (nav titles, labels, placeholders).
If someone doesn't read English well enough to need this at all, they likely
can't reliably navigate English-only tab labels either -- so chrome on the
elder-facing pages (Chat, Point & Ask, Medication, Calendar) is localized
the same way. Family-facing pages (Dashboard, Settings) stay English, since
family already operates the admin flow in English regardless.

Machine-drafted translations for Mandarin Chinese, Malay, and Tamil; a
native-speaker review is recommended before any real-world use.
"""

from typing import Literal

StringKey = Literal[
    "scam_warning_title",
    "scam_warning_body",
    "blurry_photo_message",
    "daily_checkin",
    "nav_chat",
    "nav_point_and_ask",
    "nav_medication",
    "nav_calendar",
    "chat_input_placeholder",
    "chat_thinking_spinner",
    "point_and_ask_intro",
    "point_and_ask_uploader_label",
    "point_and_ask_spinner",
    "point_and_ask_result_title",
    "coming_soon_title",
    "medication_coming_soon_body",
    "calendar_coming_soon_body",
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
        "nav_chat": "Chat",
        "nav_point_and_ask": "Point & Ask",
        "nav_medication": "Medication",
        "nav_calendar": "Calendar",
        "chat_input_placeholder": "Type a message...",
        "chat_thinking_spinner": "Thinking...",
        "point_and_ask_intro": "Take or upload a photo of a letter, message, or document.",
        "point_and_ask_uploader_label": "Choose a photo",
        "point_and_ask_spinner": "Looking at this...",
        "point_and_ask_result_title": "Here's what this says",
        "coming_soon_title": "Coming soon",
        "medication_coming_soon_body": "Today's medication list and reminders.",
        "calendar_coming_soon_body": "Upcoming appointments and reminders.",
    },
    "Mandarin Chinese": {
        "scam_warning_title": "这看起来可能是一个骗局。",
        "scam_warning_body": (
            "请不要回复、点击任何链接，或提供金钱或个人资料。在采取任何行动之前，请先询问家人。"
        ),
        "blurry_photo_message": "这张照片不够清楚，无法阅读。请在光线更好的地方重新拍一张。",
        "daily_checkin": "早上好！您今天感觉怎么样？吃药了吗？",
        "nav_chat": "聊天",
        "nav_point_and_ask": "拍照询问",
        "nav_medication": "药物",
        "nav_calendar": "日历",
        "chat_input_placeholder": "请输入信息...",
        "chat_thinking_spinner": "思考中...",
        "point_and_ask_intro": "拍摄或上传一封信、短信或文件的照片。",
        "point_and_ask_uploader_label": "选择照片",
        "point_and_ask_spinner": "正在查看...",
        "point_and_ask_result_title": "内容是这样的",
        "coming_soon_title": "即将推出",
        "medication_coming_soon_body": "今天的用药清单和提醒。",
        "calendar_coming_soon_body": "即将到来的预约和提醒。",
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
        "nav_chat": "Sembang",
        "nav_point_and_ask": "Tunjuk & Tanya",
        "nav_medication": "Ubat",
        "nav_calendar": "Kalendar",
        "chat_input_placeholder": "Taip mesej...",
        "chat_thinking_spinner": "Sedang berfikir...",
        "point_and_ask_intro": "Ambil atau muat naik gambar surat, mesej, atau dokumen.",
        "point_and_ask_uploader_label": "Pilih gambar",
        "point_and_ask_spinner": "Sedang melihat...",
        "point_and_ask_result_title": "Ini kandungannya",
        "coming_soon_title": "Akan datang",
        "medication_coming_soon_body": "Senarai ubat dan peringatan untuk hari ini.",
        "calendar_coming_soon_body": "Temujanji dan peringatan yang akan datang.",
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
        "nav_chat": "அரட்டை",
        "nav_point_and_ask": "புகைப்படம் எடுத்து கேளுங்கள்",
        "nav_medication": "மருந்து",
        "nav_calendar": "நாட்காட்டி",
        "chat_input_placeholder": "செய்தியை தட்டச்சு செய்யவும்...",
        "chat_thinking_spinner": "யோசிக்கிறேன்...",
        "point_and_ask_intro": (
            "ஒரு கடிதம், செய்தி அல்லது ஆவணத்தின் புகைப்படத்தை எடுக்கவும் அல்லது பதிவேற்றவும்."
        ),
        "point_and_ask_uploader_label": "புகைப்படத்தைத் தேர்ந்தெடுக்கவும்",
        "point_and_ask_spinner": "இதைப் பார்க்கிறேன்...",
        "point_and_ask_result_title": "இதில் இருப்பது இதுதான்",
        "coming_soon_title": "விரைவில் வரும்",
        "medication_coming_soon_body": "இன்றைய மருந்து பட்டியல் மற்றும் நினைவூட்டல்கள்.",
        "calendar_coming_soon_body": "வரவிருக்கும் சந்திப்புகள் மற்றும் நினைவூட்டல்கள்.",
    },
}


def get_string(language: str, key: StringKey) -> str:
    """Look up a fixed string for a language.

    Args:
        language: the elder's preferred language.
        key: which string to fetch.

    Returns:
        str: the string in that language, or the English version if the
            language isn't in the table.
    """
    return _STRINGS.get(language, _STRINGS["English"])[key]
