import type { Language } from '@/lib/api'

// Mirrors backend/strings.py's structure and (where the same content
// applies) its exact translations -- ported, not re-translated from
// scratch, for everything that overlaps between the two apps. Only
// React-only copy (weather blurbs, the Check-In prompt, the Home nudge/
// happening-near-you cards) is newly translated here.
//
// Elder-facing pages only (Home, Point & Ask, Medication, Calendar) --
// family-facing pages (Dashboard, Send a note, Memory bank, Family
// Medication, Settings) stay English: family already operates the admin
// flow in English regardless.
//
// Machine-drafted translations for Mandarin Chinese, Malay, and Tamil; a
// native-speaker review is recommended before any real-world use.

export type StringKey =
  | 'nav_home'
  | 'nav_point_and_ask'
  | 'nav_medication'
  | 'nav_calendar'
  | 'home_family_view_link'
  | 'home_greeting'
  | 'home_greeting_morning'
  | 'home_greeting_afternoon'
  | 'home_greeting_evening'
  | 'home_happening_title'
  | 'home_happening_body'
  | 'home_happening_button'
  | 'home_happening_reminder_toast_title'
  | 'home_happening_reminder_toast_body'
  | 'home_boundary_statement'
  | 'home_hint_point_and_ask'
  | 'home_hint_medication'
  | 'home_hint_calendar'
  | 'weather_right_now'
  | 'weather_blurb_clear'
  | 'weather_blurb_cloudy'
  | 'weather_blurb_rain'
  | 'weather_blurb_storm'
  | 'weather_blurb_clear_night'
  | 'weather_blurb_cloudy_night'
  | 'weather_blurb_rain_night'
  | 'weather_blurb_storm_night'
  | 'check_in_placeholder'
  | 'check_in_send_button'
  | 'check_in_sending'
  | 'check_in_family_nudge_accept_button'
  | 'check_in_family_nudge_accepted_label'
  | 'check_in_nothing_more_today'
  | 'check_in_extend_prompt'
  | 'point_and_ask_intro'
  | 'point_and_ask_tips'
  | 'point_and_ask_category_letter'
  | 'point_and_ask_category_bill'
  | 'point_and_ask_category_sms'
  | 'point_and_ask_camera_button'
  | 'point_and_ask_gallery_button'
  | 'point_and_ask_example_label'
  | 'point_and_ask_example_caption'
  | 'point_and_ask_spinner'
  | 'point_and_ask_result_title'
  | 'point_and_ask_error_message'
  | 'point_and_ask_disclaimer'
  | 'scam_warning_title'
  | 'scam_warning_body'
  | 'blurry_photo_message'
  | 'medication_title'
  | 'medication_subtitle'
  | 'medication_loading'
  | 'medication_empty_title'
  | 'medication_empty_body'
  | 'medication_taken_label'
  | 'medication_missed_label'
  | 'medication_mark_taken_button'
  | 'medication_disclaimer'
  | 'calendar_title'
  | 'calendar_subtitle'
  | 'calendar_add_button'
  | 'calendar_add_title_label'
  | 'calendar_add_day_label'
  | 'calendar_add_time_label'
  | 'calendar_add_with_whom_label'
  | 'calendar_add_save_button'
  | 'calendar_add_cancel_button'

const strings: Record<Language, Record<StringKey, string>> = {
  English: {
    nav_home: 'Home',
    nav_point_and_ask: 'Point & Ask',
    nav_medication: 'Medication',
    nav_calendar: 'Calendar',
    home_family_view_link: 'Family view',
    home_greeting: 'Hello',
    home_greeting_morning: 'Good morning',
    home_greeting_afternoon: 'Good afternoon',
    home_greeting_evening: 'Good evening',
    home_happening_title: 'Happening near you',
    home_happening_body:
      'Morning qigong at the pavilion downstairs, tomorrow at 7.30am. Mrs Lim from the fourth floor goes every week.',
    home_happening_button: 'Remind me tomorrow morning',
    home_happening_reminder_toast_title: 'Got it',
    home_happening_reminder_toast_body:
      "I'll bring this up again tomorrow morning.",
    home_boundary_statement:
      "I'm here to keep you company between visits, never instead of them. When something matters, I'll gently let your family know.",
    home_hint_point_and_ask: 'Letters and messages',
    home_hint_medication: "Today's doses",
    home_hint_calendar: "What's coming up",
    weather_right_now: 'Right now',
    weather_blurb_clear:
      'Comfortable for a short walk downstairs, bring your hat.',
    weather_blurb_cloudy: 'A calm, overcast day, still fine for a short walk.',
    weather_blurb_rain:
      'Best to stay indoors for now, or bring an umbrella if you go out.',
    weather_blurb_storm: 'Best to stay indoors until it passes.',
    weather_blurb_clear_night: 'A clear, quiet night, a good time to rest.',
    weather_blurb_cloudy_night:
      'A quiet, overcast night, nothing to worry about.',
    weather_blurb_rain_night: 'Raining tonight, good to stay in and rest.',
    weather_blurb_storm_night:
      'Thunderstorms tonight, best to stay indoors and rest.',
    check_in_placeholder: 'Say as much or as little as you like...',
    check_in_send_button: 'Send',
    check_in_sending: 'Sending...',
    check_in_family_nudge_accept_button: "I'll reach out",
    check_in_family_nudge_accepted_label: 'Glad to hear it.',
    check_in_nothing_more_today:
      "You've already checked in with me today, see you tomorrow.",
    check_in_extend_prompt: 'Want to share a bit more?',
    point_and_ask_intro:
      'Take or upload a photo of a letter, message, or document.',
    point_and_ask_tips:
      'Tips: lay it flat, use good light, and get close enough that the words fill the photo.',
    point_and_ask_category_letter: 'A letter',
    point_and_ask_category_bill: 'A bill',
    point_and_ask_category_sms: 'A strange SMS',
    point_and_ask_camera_button: 'Take a Photo',
    point_and_ask_gallery_button: 'Choose from photos',
    point_and_ask_example_label: 'See an example',
    point_and_ask_example_caption: 'A clear, well-lit photo looks like this.',
    point_and_ask_spinner: 'Looking at this...',
    point_and_ask_result_title: "Here's what this says",
    point_and_ask_error_message: 'Something went wrong. Please try again.',
    point_and_ask_disclaimer:
      "I can read and explain, but I can't sign or pay anything for you. For big decisions, ask your family too.",
    scam_warning_title: 'This looks like it could be a scam.',
    scam_warning_body:
      "Please don't reply, click any links, or send money or personal details. Ask a family member before doing anything else about this.",
    blurry_photo_message:
      "The photo isn't clear enough to read. Please try taking another photo with better lighting.",
    medication_title: 'Medication today',
    medication_subtitle: 'still to take, no rush, just when it’s time',
    medication_loading: "Loading today's medicine...",
    medication_empty_title: 'No medicine added yet.',
    medication_empty_body: 'Ask your family to add it for you.',
    medication_taken_label: 'Taken',
    medication_missed_label: 'Missed earlier today',
    medication_mark_taken_button: "I've taken this",
    medication_disclaimer:
      'I only keep track of what you tell me here. If something changes, your doctor and your family are the ones to speak to.',
    calendar_title: "What's coming up",
    calendar_subtitle: 'The next few days',
    calendar_add_button: 'Add something',
    calendar_add_title_label: 'What is it?',
    calendar_add_day_label: 'Which day?',
    calendar_add_time_label: 'What time?',
    calendar_add_with_whom_label: 'With whom? (optional)',
    calendar_add_save_button: 'Save',
    calendar_add_cancel_button: 'Cancel',
  },
  'Mandarin Chinese': {
    nav_home: '首页',
    nav_point_and_ask: '拍照询问',
    nav_medication: '药物',
    nav_calendar: '日历',
    home_family_view_link: '家人视图',
    home_greeting: '你好',
    home_greeting_morning: '早上好',
    home_greeting_afternoon: '下午好',
    home_greeting_evening: '晚上好',
    home_happening_title: '附近活动',
    home_happening_body:
      '明天早上7点30分，楼下凉亭有晨间气功。四楼的林太太每周都去。',
    home_happening_button: '明天早上提醒我',
    home_happening_reminder_toast_title: '好的',
    home_happening_reminder_toast_body: '我明天早上会再次提醒您。',
    home_boundary_statement:
      '我在这里陪伴您度过探访之间的时光，但永远不能替代探访。如果有重要的事，我会轻轻地让您的家人知道。',
    home_hint_point_and_ask: '信件和信息',
    home_hint_medication: '今天的用药',
    home_hint_calendar: '即将到来的安排',
    weather_right_now: '现在',
    weather_blurb_clear: '适合下楼散步，记得戴帽子。',
    weather_blurb_cloudy: '天气平静多云，散步也没问题。',
    weather_blurb_rain: '最好留在室内，出门请带伞。',
    weather_blurb_storm: '最好留在室内，等雨过去。',
    weather_blurb_clear_night: '夜晚晴朗宁静，正好休息。',
    weather_blurb_cloudy_night: '夜晚宁静多云，没什么好担心的。',
    weather_blurb_rain_night: '今晚有雨，最好留在室内休息。',
    weather_blurb_storm_night: '今晚有雷雨，最好留在室内休息。',
    check_in_placeholder: '想说什么都可以，多说少说都行……',
    check_in_send_button: '发送',
    check_in_sending: '发送中...',
    check_in_family_nudge_accept_button: '我会联系他们',
    check_in_family_nudge_accepted_label: '很高兴听到这个消息。',
    check_in_nothing_more_today: '您今天已经和我聊过了，明天再见。',
    check_in_extend_prompt: '想多说一点吗？',
    point_and_ask_intro: '拍摄或上传一封信、短信或文件的照片。',
    point_and_ask_tips:
      '小提示：把它放平，光线要充足，靠近一点让文字填满照片。',
    point_and_ask_category_letter: '一封信',
    point_and_ask_category_bill: '一张账单',
    point_and_ask_category_sms: '一条可疑短信',
    point_and_ask_camera_button: '拍照',
    point_and_ask_gallery_button: '从相册选择',
    point_and_ask_example_label: '查看示例',
    point_and_ask_example_caption: '清晰、光线良好的照片是这样的。',
    point_and_ask_spinner: '正在查看...',
    point_and_ask_result_title: '内容是这样的',
    point_and_ask_error_message: '出了点问题，请再试一次。',
    point_and_ask_disclaimer:
      '我能读懂并解释，但不能替您签字或付款。重要决定，请也问问家人。',
    scam_warning_title: '这看起来可能是一个骗局。',
    scam_warning_body:
      '请不要回复、点击任何链接，或提供金钱或个人资料。在采取任何行动之前，请先询问家人。',
    blurry_photo_message:
      '这张照片不够清楚，无法阅读。请在光线更好的地方重新拍一张。',
    medication_title: '今天的用药',
    medication_subtitle: '还需服用，不用着急，到时间再吃',
    medication_loading: '正在加载今天的用药...',
    medication_empty_title: '还没有添加药物。',
    medication_empty_body: '请让家人帮您添加。',
    medication_taken_label: '已服用',
    medication_missed_label: '今天早些时候错过了',
    medication_mark_taken_button: '我已经吃了',
    medication_disclaimer:
      '我只记录您告诉我的内容。如果有变化，请咨询您的医生和家人。',
    calendar_title: '即将到来的安排',
    calendar_subtitle: '接下来的几天',
    calendar_add_button: '添加安排',
    calendar_add_title_label: '是什么事？',
    calendar_add_day_label: '哪一天？',
    calendar_add_time_label: '几点？',
    calendar_add_with_whom_label: '和谁一起？（可选）',
    calendar_add_save_button: '保存',
    calendar_add_cancel_button: '取消',
  },
  Malay: {
    nav_home: 'Laman Utama',
    nav_point_and_ask: 'Tunjuk & Tanya',
    nav_medication: 'Ubat',
    nav_calendar: 'Kalendar',
    home_family_view_link: 'Paparan keluarga',
    home_greeting: 'Helo',
    home_greeting_morning: 'Selamat pagi',
    home_greeting_afternoon: 'Selamat tengah hari',
    home_greeting_evening: 'Selamat petang',
    home_happening_title: 'Berlaku berdekatan anda',
    home_happening_body:
      'Qigong pagi di pavilion bawah, esok pukul 7.30 pagi. Puan Lim dari tingkat empat pergi setiap minggu.',
    home_happening_button: 'Ingatkan saya esok pagi',
    home_happening_reminder_toast_title: 'Baiklah',
    home_happening_reminder_toast_body:
      'Saya akan ingatkan anda lagi esok pagi.',
    home_boundary_statement:
      'Saya di sini untuk menemani anda antara lawatan, bukan menggantikannya. Apabila sesuatu itu penting, saya akan memberitahu keluarga anda dengan lembut.',
    home_hint_point_and_ask: 'Surat dan mesej',
    home_hint_medication: 'Dos hari ini',
    home_hint_calendar: 'Apa yang akan datang',
    weather_right_now: 'Sekarang',
    weather_blurb_clear:
      'Selesa untuk berjalan sebentar di bawah, bawa topi anda.',
    weather_blurb_cloudy:
      'Hari yang tenang dan mendung, masih baik untuk berjalan sebentar.',
    weather_blurb_rain:
      'Lebih baik berada di dalam buat masa ini, atau bawa payung jika keluar.',
    weather_blurb_storm: 'Lebih baik berada di dalam sehingga ia berlalu.',
    weather_blurb_clear_night:
      'Malam yang jernih dan tenang, masa yang baik untuk berehat.',
    weather_blurb_cloudy_night:
      'Malam yang tenang dan mendung, tiada apa yang perlu dirisaukan.',
    weather_blurb_rain_night:
      'Hujan malam ini, lebih baik berada di dalam dan berehat.',
    weather_blurb_storm_night:
      'Ribut petir malam ini, lebih baik berada di dalam dan berehat.',
    check_in_placeholder: 'Cakap sebanyak atau seringkas yang anda mahu...',
    check_in_send_button: 'Hantar',
    check_in_sending: 'Menghantar...',
    check_in_family_nudge_accept_button: 'Saya akan hubungi mereka',
    check_in_family_nudge_accepted_label: 'Gembira mendengarnya.',
    check_in_nothing_more_today:
      'Anda sudah bersembang dengan saya hari ini, jumpa lagi esok.',
    check_in_extend_prompt: 'Nak kongsi lagi sedikit?',
    point_and_ask_intro:
      'Ambil atau muat naik gambar surat, mesej, atau dokumen.',
    point_and_ask_tips:
      'Petua: letakkan rata, guna cahaya yang baik, dan dekatkan supaya tulisan memenuhi gambar.',
    point_and_ask_category_letter: 'Surat',
    point_and_ask_category_bill: 'Bil',
    point_and_ask_category_sms: 'SMS mencurigakan',
    point_and_ask_camera_button: 'Ambil Gambar',
    point_and_ask_gallery_button: 'Pilih dari galeri',
    point_and_ask_example_label: 'Lihat contoh',
    point_and_ask_example_caption:
      'Gambar yang jelas dan bercahaya baik kelihatan begini.',
    point_and_ask_spinner: 'Sedang melihat...',
    point_and_ask_result_title: 'Ini kandungannya',
    point_and_ask_error_message: 'Ada masalah. Sila cuba lagi.',
    point_and_ask_disclaimer:
      'Saya boleh membaca dan menerangkan, tetapi tidak boleh menandatangani atau membayar untuk anda. Untuk keputusan besar, tanya keluarga anda juga.',
    scam_warning_title: 'Ini kelihatan seperti penipuan.',
    scam_warning_body:
      'Sila jangan balas, klik sebarang pautan, atau hantar wang atau maklumat peribadi. Tanya ahli keluarga sebelum membuat apa-apa tindakan mengenai perkara ini.',
    blurry_photo_message:
      'Gambar ini tidak cukup jelas untuk dibaca. Sila cuba ambil gambar lain dengan pencahayaan yang lebih baik.',
    medication_title: 'Ubat hari ini',
    medication_subtitle:
      'masih perlu diambil, tidak perlu tergesa-gesa, ikut masa sahaja',
    medication_loading: 'Memuatkan ubat hari ini...',
    medication_empty_title: 'Belum ada ubat ditambah.',
    medication_empty_body: 'Minta keluarga anda menambahnya untuk anda.',
    medication_taken_label: 'Sudah diambil',
    medication_missed_label: 'Terlepas awal tadi',
    medication_mark_taken_button: 'Saya sudah makan ini',
    medication_disclaimer:
      'Saya hanya merekod apa yang anda beritahu saya di sini. Jika ada perubahan, doktor dan keluarga anda adalah pihak yang perlu dihubungi.',
    calendar_title: 'Apa yang akan datang',
    calendar_subtitle: 'Beberapa hari akan datang',
    calendar_add_button: 'Tambah sesuatu',
    calendar_add_title_label: 'Apakah acaranya?',
    calendar_add_day_label: 'Hari apa?',
    calendar_add_time_label: 'Pukul berapa?',
    calendar_add_with_whom_label: 'Dengan siapa? (pilihan)',
    calendar_add_save_button: 'Simpan',
    calendar_add_cancel_button: 'Batal',
  },
  Tamil: {
    nav_home: 'முகப்பு',
    nav_point_and_ask: 'புகைப்படம் எடுத்து கேளுங்கள்',
    nav_medication: 'மருந்து',
    nav_calendar: 'நாட்காட்டி',
    home_family_view_link: 'குடும்ப பார்வை',
    home_greeting: 'வணக்கம்',
    home_greeting_morning: 'காலை வணக்கம்',
    home_greeting_afternoon: 'மதிய வணக்கம்',
    home_greeting_evening: 'மாலை வணக்கம்',
    home_happening_title: 'உங்கள் அருகில் நடக்கிறது',
    home_happening_body:
      'நாளை காலை 7.30 மணிக்கு கீழே உள்ள பெவிலியனில் காலை சிகோங். நான்காம் மாடி லிம் அம்மையார் ஒவ்வொரு வாரமும் செல்கிறார்.',
    home_happening_button: 'நாளை காலை எனக்கு நினைவூட்டுங்கள்',
    home_happening_reminder_toast_title: 'சரி',
    home_happening_reminder_toast_body:
      'நாளை காலை மீண்டும் உங்களுக்கு நினைவூட்டுவேன்.',
    home_boundary_statement:
      'நான் உங்களுடன் வருகைகளுக்கு இடையே துணையாக இருக்கிறேன், ஒருபோதும் அதற்கு பதிலாக அல்ல. ஏதாவது முக்கியமானது இருந்தால், நான் மெதுவாக உங்கள் குடும்பத்திற்குத் தெரிவிப்பேன்.',
    home_hint_point_and_ask: 'கடிதங்களும் செய்திகளும்',
    home_hint_medication: 'இன்றைய மருந்துகள்',
    home_hint_calendar: 'அடுத்து என்ன வருகிறது',
    weather_right_now: 'இப்போது',
    weather_blurb_clear:
      'கீழே சிறிது நடக்க வசதியானது, உங்கள் தொப்பியை கொண்டு வாருங்கள்.',
    weather_blurb_cloudy:
      'அமைதியான, மேகமூட்டமான நாள், சிறிது நடப்பதற்கு இன்னும் நல்லது.',
    weather_blurb_rain:
      'தற்போதைக்கு உள்ளே இருப்பது நல்லது, அல்லது வெளியே சென்றால் குடை கொண்டு செல்லுங்கள்.',
    weather_blurb_storm: 'மழை நிற்கும் வரை உள்ளே இருப்பது நல்லது.',
    weather_blurb_clear_night:
      'தெளிவான, அமைதியான இரவு, ஓய்வெடுக்க நல்ல நேரம்.',
    weather_blurb_cloudy_night:
      'அமைதியான, மேகமூட்டமான இரவு, கவலைப்பட ஒன்றுமில்லை.',
    weather_blurb_rain_night:
      'இன்று இரவு மழை, உள்ளே இருந்து ஓய்வெடுப்பது நல்லது.',
    weather_blurb_storm_night:
      'இன்று இரவு இடியுடன் கூடிய மழை, உள்ளே இருந்து ஓய்வெடுப்பது நல்லது.',
    check_in_placeholder:
      'நீங்கள் விரும்பியதை அதிகமாகவோ குறைவாகவோ சொல்லுங்கள்...',
    check_in_send_button: 'அனுப்பு',
    check_in_sending: 'அனுப்புகிறேன்...',
    check_in_family_nudge_accept_button: 'நான் தொடர்பு கொள்கிறேன்',
    check_in_family_nudge_accepted_label: 'அதைக் கேட்டதில் மகிழ்ச்சி.',
    check_in_nothing_more_today:
      'இன்று ஏற்கனவே என்னுடன் பேசிவிட்டீர்கள், நாளை சந்திப்போம்.',
    check_in_extend_prompt: 'இன்னும் கொஞ்சம் பகிர விரும்புகிறீர்களா?',
    point_and_ask_intro:
      'ஒரு கடிதம், செய்தி அல்லது ஆவணத்தின் புகைப்படத்தை எடுக்கவும் அல்லது பதிவேற்றவும்.',
    point_and_ask_tips:
      'குறிப்புகள்: அதை தட்டையாக வையுங்கள், நல்ல வெளிச்சத்தில் எடுங்கள், எழுத்துக்கள் புகைப்படத்தை நிரப்பும் அளவுக்கு நெருங்கி எடுங்கள்.',
    point_and_ask_category_letter: 'ஒரு கடிதம்',
    point_and_ask_category_bill: 'ஒரு பில்',
    point_and_ask_category_sms: 'சந்தேகத்திற்குரிய SMS',
    point_and_ask_camera_button: 'புகைப்படம் எடுக்கவும்',
    point_and_ask_gallery_button: 'படங்களிலிருந்து தேர்ந்தெடுக்கவும்',
    point_and_ask_example_label: 'ஒரு உதாரணத்தைப் பார்க்கவும்',
    point_and_ask_example_caption:
      'தெளிவான, நல்ல வெளிச்சமுள்ள புகைப்படம் இப்படி இருக்கும்.',
    point_and_ask_spinner: 'இதைப் பார்க்கிறேன்...',
    point_and_ask_result_title: 'இதில் இருப்பது இதுதான்',
    point_and_ask_error_message: 'ஏதோ தவறு நடந்தது. மீண்டும் முயற்சிக்கவும்.',
    point_and_ask_disclaimer:
      'நான் படித்து விளக்க முடியும், ஆனால் உங்களுக்காக கையெழுத்திட அல்லது பணம் செலுத்த முடியாது. பெரிய முடிவுகளுக்கு, உங்கள் குடும்பத்தினரிடமும் கேளுங்கள்.',
    scam_warning_title: 'இது ஒரு மோசடி போல் தெரிகிறது.',
    scam_warning_body:
      'தயவுசெய்து பதிலளிக்க வேண்டாம், எந்த இணைப்புகளையும் கிளிக் செய்ய வேண்டாம், பணம் அல்லது தனிப்பட்ட தகவல்களை அனுப்ப வேண்டாம். இது பற்றி எதுவும் செய்யும் முன் குடும்ப உறுப்பினரிடம் கேளுங்கள்.',
    blurry_photo_message:
      'இந்த புகைப்படம் படிக்க போதுமான தெளிவாக இல்லை. சிறந்த வெளிச்சத்தில் மற்றொரு புகைப்படம் எடுக்க முயற்சிக்கவும்.',
    medication_title: 'இன்றைய மருந்து',
    medication_subtitle:
      'இன்னும் எடுக்க வேண்டியவை, அவசரமில்லை, நேரம் ஆனதும் எடுத்துக்கொள்ளுங்கள்',
    medication_loading: 'இன்றைய மருந்தை ஏற்றுகிறேன்...',
    medication_empty_title: 'இன்னும் மருந்து சேர்க்கப்படவில்லை.',
    medication_empty_body:
      'உங்கள் குடும்பத்தினரிடம் அதைச் சேர்க்கச் சொல்லுங்கள்.',
    medication_taken_label: 'எடுத்துக்கொண்டேன்',
    medication_missed_label: 'இன்று முன்னதாக தவறவிட்டது',
    medication_mark_taken_button: 'நான் இதை எடுத்துக்கொண்டேன்',
    medication_disclaimer:
      'நீங்கள் இங்கே சொல்வதை மட்டுமே நான் கண்காணிக்கிறேன். ஏதாவது மாறினால், உங்கள் மருத்துவரும் குடும்பத்தினரும் தான் பேச வேண்டியவர்கள்.',
    calendar_title: 'அடுத்து என்ன வருகிறது',
    calendar_subtitle: 'அடுத்த சில நாட்கள்',
    calendar_add_button: 'ஒன்றைச் சேர்க்கவும்',
    calendar_add_title_label: 'என்ன நிகழ்ச்சி?',
    calendar_add_day_label: 'எந்த நாள்?',
    calendar_add_time_label: 'என்ன நேரம்?',
    calendar_add_with_whom_label: 'யாருடன்? (விருப்பத்திற்குரியது)',
    calendar_add_save_button: 'சேமி',
    calendar_add_cancel_button: 'ரத்து செய்',
  },
}

export function getString(language: Language, key: StringKey): string {
  return strings[language][key]
}

/** Replace `{placeholder}` tokens, e.g. getStringWith('en', 'home_call_button', { name: 'Kok Wai' }). */
export function getStringWith(
  language: Language,
  key: StringKey,
  params: Record<string, string>,
): string {
  let text = getString(language, key)
  for (const [k, v] of Object.entries(params)) {
    text = text.replaceAll(`{${k}}`, v)
  }
  return text
}
