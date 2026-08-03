-- SQLite schema. Auto-applied on app startup by backend/db.py — no manual
-- setup required. All statements are idempotent (safe to re-run).

create table if not exists profiles (
  id text primary key,
  role text not null check (role in ('elder', 'family')),
  display_name text not null,
  elder_id text references profiles(id),
  preferred_language text not null default 'English'
    check (preferred_language in ('English', 'Mandarin Chinese', 'Malay', 'Tamil')),
  created_at text default (datetime('now'))
);

create table if not exists medications (
  id text primary key,
  elder_id text not null references profiles(id),
  name text not null,
  dosage text not null,
  times_per_day text not null,  -- JSON array, e.g. ["08:00", "20:00"]
  created_at text default (datetime('now'))
);

create table if not exists medication_logs (
  id text primary key,
  medication_id text not null references medications(id),
  elder_id text not null references profiles(id),
  scheduled_for text not null,
  taken_at text,
  status text not null check (status in ('pending', 'taken', 'missed'))
);

create table if not exists calendar_events (
  id text primary key,
  elder_id text not null references profiles(id),
  title text not null,
  event_type text not null check (event_type in ('appointment', 'medication', 'other')),
  start_time text not null,
  notes text,
  created_at text default (datetime('now'))
);

create table if not exists chat_messages (
  id text primary key,
  elder_id text not null references profiles(id),
  sender text not null check (sender in ('elder', 'ai', 'family')),
  content text not null,
  sentiment text check (sentiment in ('positive', 'neutral', 'low', 'distress')),
  repeated_question_flag integer default 0,
  sender_name text,  -- set for sender='family' rows, e.g. "Mei Lin"
  created_at text default (datetime('now'))
);

create table if not exists documents (
  id text primary key,
  elder_id text not null references profiles(id),
  image_path text not null,
  classification text check (classification in ('explain', 'scam', 'unclear')),
  summary_text text,
  translated_text text,
  scam_risk_level text check (scam_risk_level in ('low', 'medium', 'high')),
  scam_signals text,  -- JSON
  created_at text default (datetime('now'))
);

create table if not exists memory_bank_entries (
  id text primary key,
  elder_id text not null references profiles(id),
  added_by text not null references profiles(id),
  entry_type text not null check (entry_type in ('photo', 'fact')),
  content_text text,
  image_path text,
  created_at text default (datetime('now'))
);

create table if not exists alerts (
  id text primary key,
  elder_id text not null references profiles(id),
  alert_type text not null check (alert_type in
    ('missed_medication', 'scam_detected', 'sentiment_decline',
     'repeated_question_increase', 'distress')),
  message text not null,
  status text not null default 'open' check (status in ('open', 'acknowledged')),
  created_at text default (datetime('now'))
);

-- Generic event log: lets the companion-line mechanism know what it last
-- showed (avoid repeating a nudge every page load) and doubles as the data
-- source for the "connections facilitated" family-dashboard metric.
create table if not exists companion_events (
  id text primary key,
  elder_id text not null references profiles(id),
  event_type text not null check (event_type in
    ('family_nudge_shown', 'family_nudge_accepted', 'reminiscence_shown')),
  created_at text default (datetime('now'))
);

-- Backs the React frontend's Home-screen "note from family" card. Kept
-- separate from chat_messages: Chat isn't wired to real data yet, and
-- coupling a Home-screen note to the chat schema now would be premature.
create table if not exists family_notes (
  id text primary key,
  elder_id text not null references profiles(id),
  sender_name text not null,
  relation text,
  text text not null,
  created_at text default (datetime('now'))
);
