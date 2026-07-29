-- Run in the Supabase SQL editor for a fresh project.
-- Elder-family linking is manual for the POC: after both accounts exist,
-- set the family member's profiles.elder_id to the elder's profiles.id directly.

create table profiles (
  id uuid primary key references auth.users(id),
  role text not null check (role in ('elder', 'family')),
  display_name text not null,
  elder_id uuid references profiles(id),  -- set for family role; null for elder role
  created_at timestamptz default now()
);

create table medications (
  id uuid primary key default gen_random_uuid(),
  elder_id uuid not null references profiles(id),
  name text not null,
  dosage text not null,
  times_per_day jsonb not null,  -- e.g. ["08:00", "20:00"]
  created_at timestamptz default now()
);

create table medication_logs (
  id uuid primary key default gen_random_uuid(),
  medication_id uuid not null references medications(id),
  elder_id uuid not null references profiles(id),
  scheduled_for timestamptz not null,
  taken_at timestamptz,
  status text not null check (status in ('pending', 'taken', 'missed'))
);

create table calendar_events (
  id uuid primary key default gen_random_uuid(),
  elder_id uuid not null references profiles(id),
  title text not null,
  event_type text not null check (event_type in ('appointment', 'medication', 'other')),
  start_time timestamptz not null,
  notes text,
  created_at timestamptz default now()
);

create table chat_messages (
  id uuid primary key default gen_random_uuid(),
  elder_id uuid not null references profiles(id),
  sender text not null check (sender in ('elder', 'ai')),
  content text not null,
  sentiment text check (sentiment in ('positive', 'neutral', 'low', 'distress')),
  repeated_question_flag boolean default false,
  created_at timestamptz default now()
);

create table documents (
  id uuid primary key default gen_random_uuid(),
  elder_id uuid not null references profiles(id),
  image_url text not null,
  classification text check (classification in ('explain', 'scam', 'unclear')),
  summary_text text,
  translated_text text,
  scam_risk_level text check (scam_risk_level in ('low', 'medium', 'high')),
  scam_signals jsonb,
  created_at timestamptz default now()
);

create table memory_bank_entries (
  id uuid primary key default gen_random_uuid(),
  elder_id uuid not null references profiles(id),
  added_by uuid not null references profiles(id),
  entry_type text not null check (entry_type in ('photo', 'fact')),
  content_text text,
  image_url text,
  created_at timestamptz default now()
);

create table alerts (
  id uuid primary key default gen_random_uuid(),
  elder_id uuid not null references profiles(id),
  alert_type text not null check (alert_type in
    ('missed_medication', 'scam_detected', 'sentiment_decline',
     'repeated_question_increase', 'distress')),
  message text not null,
  status text not null default 'open' check (status in ('open', 'acknowledged')),
  created_at timestamptz default now()
);

-- Row Level Security
-- Elder role: full access to rows where elder_id = auth.uid() (or id = auth.uid() for profiles).
-- Family role: read-only access to their linked elder's rows, plus insert on memory_bank_entries.

alter table profiles enable row level security;
alter table medications enable row level security;
alter table medication_logs enable row level security;
alter table calendar_events enable row level security;
alter table chat_messages enable row level security;
alter table documents enable row level security;
alter table memory_bank_entries enable row level security;
alter table alerts enable row level security;

create policy "profiles: view own or linked elder" on profiles
  for select using (
    id = auth.uid()
    or id = (select elder_id from profiles where id = auth.uid())
  );

create policy "profiles: elder manages own row" on profiles
  for update using (id = auth.uid());

create policy "medications: elder full access" on medications
  for all using (elder_id = auth.uid());

create policy "medications: family read" on medications
  for select using (elder_id = (select elder_id from profiles where id = auth.uid()));

create policy "medication_logs: elder full access" on medication_logs
  for all using (elder_id = auth.uid());

create policy "medication_logs: family read" on medication_logs
  for select using (elder_id = (select elder_id from profiles where id = auth.uid()));

create policy "calendar_events: elder full access" on calendar_events
  for all using (elder_id = auth.uid());

create policy "calendar_events: family read" on calendar_events
  for select using (elder_id = (select elder_id from profiles where id = auth.uid()));

create policy "chat_messages: elder full access" on chat_messages
  for all using (elder_id = auth.uid());

create policy "chat_messages: family read" on chat_messages
  for select using (elder_id = (select elder_id from profiles where id = auth.uid()));

create policy "documents: elder full access" on documents
  for all using (elder_id = auth.uid());

create policy "documents: family read" on documents
  for select using (elder_id = (select elder_id from profiles where id = auth.uid()));

create policy "memory_bank_entries: elder full access" on memory_bank_entries
  for all using (elder_id = auth.uid());

create policy "memory_bank_entries: family read" on memory_bank_entries
  for select using (elder_id = (select elder_id from profiles where id = auth.uid()));

create policy "memory_bank_entries: family insert" on memory_bank_entries
  for insert with check (elder_id = (select elder_id from profiles where id = auth.uid()));

create policy "alerts: elder full access" on alerts
  for all using (elder_id = auth.uid());

create policy "alerts: family read" on alerts
  for select using (elder_id = (select elder_id from profiles where id = auth.uid()));
