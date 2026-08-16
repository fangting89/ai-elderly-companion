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
    "chat_share_memory_button",
    "chat_no_memories_message",
    "nav_home",
    "family_nudge_line",
    "home_reply_button",
    "home_yes_remind_button",
    "family_nudge_accepted_message",
    "companion_boundary_statement",
    "activities_card_title",
    "activities_intro",
    "voice_read_aloud_button",
    "voice_mic_button",
    "voice_not_supported_message",
    "point_and_ask_notify_family_button",
    "point_and_ask_family_notified_message",
    "point_and_ask_tips",
    "point_and_ask_camera_button",
    "point_and_ask_example_label",
    "point_and_ask_example_caption",
]

# The actual translations: one full set of strings per supported language
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
        "chat_share_memory_button": "Share a memory",
        "chat_no_memories_message": "No memories have been added yet. Ask your family to add some!",
        "nav_home": "Home",
        "family_nudge_line": (
            "It's been a little while since you've mentioned {name}. Would you "
            "like a reminder to give them a call?"
        ),
        "home_reply_button": "Reply",
        "home_yes_remind_button": "Yes, remind me",
        "family_nudge_accepted_message": "Wonderful, don't forget to give them a call!",
        "companion_boundary_statement": (
            "I'm here for the quiet moments, but I'm not a replacement for a real "
            "voice or a real visit. I'll always encourage you to reach out to the "
            "people who love you."
        ),
        "activities_card_title": "Activities Near You",
        "activities_intro": "A few things happening in your community:",
        "voice_read_aloud_button": "🔊 Read aloud",
        "voice_mic_button": "🎤 Speak instead",
        "voice_not_supported_message": "Voice isn't supported in this browser yet.",
        "point_and_ask_notify_family_button": "Let my family know now",
        "point_and_ask_family_notified_message": "Your family has already been told about this.",
        "point_and_ask_tips": (
            "Tips: lay it flat, use good light, and get close enough that the words fill the photo."
        ),
        "point_and_ask_camera_button": "Take a Photo",
        "point_and_ask_example_label": "See an example",
        "point_and_ask_example_caption": "A clear, well-lit photo looks like this.",
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
        "chat_share_memory_button": "分享一段回忆",
        "chat_no_memories_message": "还没有添加任何回忆。请让家人帮忙添加吧！",
        "nav_home": "首页",
        "family_nudge_line": "好久没听你提到{name}了，要不要我提醒你联系一下{name}？",
        "home_reply_button": "回复",
        "home_yes_remind_button": "好的，提醒我",
        "family_nudge_accepted_message": "太好了，别忘了联系他们哦！",
        "companion_boundary_statement": (
            "我在这里陪伴您度过安静的时刻，但我无法取代真实的声音和真实的陪伴。"
            "我会一直鼓励您多联系爱您的家人朋友。"
        ),
        "activities_card_title": "附近活动",
        "activities_intro": "社区里最近有这些活动：",
        "voice_read_aloud_button": "🔊 朗读",
        "voice_mic_button": "🎤 语音输入",
        "voice_not_supported_message": "此浏览器暂不支持语音功能。",
        "point_and_ask_notify_family_button": "立即通知家人",
        "point_and_ask_family_notified_message": "您的家人已经收到通知了。",
        "point_and_ask_tips": "小提示：把它放平，光线要充足，靠近一点让文字填满照片。",
        "point_and_ask_camera_button": "拍照",
        "point_and_ask_example_label": "查看示例",
        "point_and_ask_example_caption": "清晰、光线良好的照片是这样的。",
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
        "chat_share_memory_button": "Kongsi kenangan",
        "chat_no_memories_message": (
            "Belum ada kenangan ditambah. Minta ahli keluarga anda menambahnya!"
        ),
        "nav_home": "Laman Utama",
        "family_nudge_line": (
            "Sudah agak lama anda tidak menyebut {name}. Mahu saya ingatkan anda "
            "untuk hubungi {name}?"
        ),
        "home_reply_button": "Balas",
        "home_yes_remind_button": "Ya, ingatkan saya",
        "family_nudge_accepted_message": "Baguslah, jangan lupa hubungi mereka!",
        "companion_boundary_statement": (
            "Saya di sini untuk detik-detik yang tenang, tetapi saya bukan pengganti "
            "suara sebenar atau lawatan sebenar. Saya akan sentiasa menggalakkan anda "
            "menghubungi orang yang menyayangi anda."
        ),
        "activities_card_title": "Aktiviti Berdekatan",
        "activities_intro": "Beberapa aktiviti di komuniti anda:",
        "voice_read_aloud_button": "🔊 Baca kuat",
        "voice_mic_button": "🎤 Bercakap sebagai ganti",
        "voice_not_supported_message": "Suara belum disokong dalam pelayar ini.",
        "point_and_ask_notify_family_button": "Beritahu keluarga saya sekarang",
        "point_and_ask_family_notified_message": "Keluarga anda sudah diberitahu tentang ini.",
        "point_and_ask_tips": (
            "Petua: letakkan rata, guna cahaya yang baik, dan dekatkan supaya tulisan "
            "memenuhi gambar."
        ),
        "point_and_ask_camera_button": "Ambil Gambar",
        "point_and_ask_example_label": "Lihat contoh",
        "point_and_ask_example_caption": "Gambar yang jelas dan bercahaya baik kelihatan begini.",
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
        "chat_share_memory_button": "ஒரு நினைவைப் பகிரவும்",
        "chat_no_memories_message": (
            "இன்னும் நினைவுகள் எதுவும் சேர்க்கப்படவில்லை. உங்கள் குடும்பத்தினரிடம் சேர்க்கச் சொல்லுங்கள்!"
        ),
        "nav_home": "முகப்பு",
        "family_nudge_line": (
            "நீங்கள் {name} பற்றி சொல்லி சிறிது காலம் ஆகிறது. {name}-ஐ அழைக்க நினைவூட்டட்டுமா?"
        ),
        "home_reply_button": "பதிலளிக்கவும்",
        "home_yes_remind_button": "ஆம், நினைவூட்டுங்கள்",
        "family_nudge_accepted_message": "அருமை, அவர்களை அழைக்க மறக்காதீர்கள்!",
        "companion_boundary_statement": (
            "அமைதியான நேரங்களுக்கு நான் இங்கே இருக்கிறேன், ஆனால் உண்மையான குரலுக்கோ "
            "உண்மையான சந்திப்புக்கோ நான் மாற்று இல்லை. உங்களை நேசிக்கும் மக்களைத் "
            "தொடர்பு கொள்ள நான் எப்போதும் ஊக்குவிப்பேன்."
        ),
        "activities_card_title": "அருகிலுள்ள செயல்பாடுகள்",
        "activities_intro": "உங்கள் சமூகத்தில் நடக்கும் சில நிகழ்வுகள்:",
        "voice_read_aloud_button": "🔊 சத்தமாக படிக்கவும்",
        "voice_mic_button": "🎤 பேசுங்கள்",
        "voice_not_supported_message": "இந்த உலாவியில் குரல் இன்னும் ஆதரிக்கப்படவில்லை.",
        "point_and_ask_notify_family_button": "இப்போதே என் குடும்பத்திற்கு தெரிவிக்கவும்",
        "point_and_ask_family_notified_message": "உங்கள் குடும்பத்திற்கு ஏற்கனவே தெரிவிக்கப்பட்டது.",
        "point_and_ask_tips": (
            "குறிப்புகள்: அதை தட்டையாக வையுங்கள், நல்ல வெளிச்சத்தில் எடுங்கள், "
            "எழுத்துக்கள் புகைப்படத்தை நிரப்பும் அளவுக்கு நெருங்கி எடுங்கள்."
        ),
        "point_and_ask_camera_button": "புகைப்படம் எடுக்கவும்",
        "point_and_ask_example_label": "ஒரு உதாரணத்தைப் பார்க்கவும்",
        "point_and_ask_example_caption": "தெளிவான, நல்ல வெளிச்சமுள்ள புகைப்படம் இப்படி இருக்கும்.",
    },
}


# Looks up one fixed string in the given language, falling back to English
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
