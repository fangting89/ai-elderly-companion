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
    "medication_mark_taken_button",
    "medication_add_expander",
    "medication_name_label",
    "medication_dosage_label",
    "medication_times_label",
    "calendar_add_expander",
    "calendar_title_label",
    "calendar_date_label",
    "calendar_time_label",
    "calendar_notes_label",
    "calendar_no_events_message",
    "add_button",
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
        "medication_mark_taken_button": "Mark taken",
        "medication_add_expander": "Add a medication",
        "medication_name_label": "Medication name",
        "medication_dosage_label": "Dosage",
        "medication_times_label": "Times per day (comma-separated, e.g. 08:00, 20:00)",
        "calendar_add_expander": "Add an event",
        "calendar_title_label": "Title",
        "calendar_date_label": "Date",
        "calendar_time_label": "Time",
        "calendar_notes_label": "Notes (optional)",
        "calendar_no_events_message": "No upcoming events yet.",
        "add_button": "Add",
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
        "medication_mark_taken_button": "标记为已服用",
        "medication_add_expander": "添加药物",
        "medication_name_label": "药物名称",
        "medication_dosage_label": "剂量",
        "medication_times_label": "每天服用时间（用逗号分隔，例如 08:00, 20:00）",
        "calendar_add_expander": "添加日程",
        "calendar_title_label": "标题",
        "calendar_date_label": "日期",
        "calendar_time_label": "时间",
        "calendar_notes_label": "备注（可选）",
        "calendar_no_events_message": "暂无即将到来的日程。",
        "add_button": "添加",
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
        "medication_mark_taken_button": "Tanda sudah makan",
        "medication_add_expander": "Tambah ubat",
        "medication_name_label": "Nama ubat",
        "medication_dosage_label": "Dos",
        "medication_times_label": "Waktu setiap hari (dipisahkan dengan koma, cth. 08:00, 20:00)",
        "calendar_add_expander": "Tambah acara",
        "calendar_title_label": "Tajuk",
        "calendar_date_label": "Tarikh",
        "calendar_time_label": "Masa",
        "calendar_notes_label": "Nota (pilihan)",
        "calendar_no_events_message": "Belum ada acara akan datang.",
        "add_button": "Tambah",
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
        "medication_mark_taken_button": "எடுத்துக்கொண்டதாக குறிக்கவும்",
        "medication_add_expander": "மருந்தைச் சேர்க்கவும்",
        "medication_name_label": "மருந்தின் பெயர்",
        "medication_dosage_label": "அளவு",
        "medication_times_label": "ஒரு நாளைக்கு நேரங்கள் (கமாவால் பிரிக்கவும், எ.கா. 08:00, 20:00)",
        "calendar_add_expander": "நிகழ்வைச் சேர்க்கவும்",
        "calendar_title_label": "தலைப்பு",
        "calendar_date_label": "தேதி",
        "calendar_time_label": "நேரம்",
        "calendar_notes_label": "குறிப்புகள் (விருப்பத்தேர்வு)",
        "calendar_no_events_message": "இன்னும் வரவிருக்கும் நிகழ்வுகள் இல்லை.",
        "add_button": "சேர்க்கவும்",
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
