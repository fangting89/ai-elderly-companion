# Architecture

See the root `README.md` for the product pitch: pillars, key features,
escalation model, ethical stance, and language support. This file is the
technical reference: schema and architectural decisions.

## Overview

A React frontend talks to a thin FastAPI layer over one Python backend and
one SQLite database:

- **Backend**: Python, SQLite, and the Anthropic Claude API (a faster model
  for classification/tagging decisions, a stronger model for conversational
  replies and explanations). Safety-relevant decisions (scam risk, escalation
  triggers) are computed deterministically from model-extracted signals,
  rather than left to a single generative judgment call.
- **React app**: TanStack Start, React 19, Tailwind, backed by a thin
  FastAPI layer that reuses the backend directly.

## Repository Structure

```
ai-elderly-companion/
├── backend/
│   ├── db.py                  # sqlite connection, schema init, demo seed
│   ├── claude_client.py       # Claude API wrapper: forced tool-use, prose calls
│   ├── chat.py                # prose reply + sentiment/repetition tagging
│   ├── point_and_ask.py       # classify -> explain | scam branch
│   ├── strings.py             # fixed safety-critical strings, per language
│   ├── companion_line.py      # daily-opener priority mechanism
│   ├── family_notes.py        # one-way family note -> elder Home screen
│   ├── activities.py          # static "Activities Near You" placeholder
│   ├── medications.py, calendar.py
│   ├── memory_bank.py         # family facts/photos, reminiscence prompts
│   ├── dashboard.py           # read-only aggregate queries, no alert writes
│   └── escalation.py          # check_and_alert(), writes alerts
├── api/                        # FastAPI layer for the React frontend below,
│                               # reusing backend/*.py directly
├── web/                         # React/TanStack Start frontend
├── eval/                        # labeled evaluation sets for the AI features
├── notebooks/                    # interactive prompt exploration
├── tests/                        # unit and API tests
└── sql/schema.sql                # database schema, auto-applied on startup
```

## Database Schema (SQLite)

```sql
create table if not exists profiles (
  id text primary key,
  role text not null check (role in ('elder', 'family')),
  display_name text not null,
  elder_id text references profiles(id),  -- set for family role; null for elder role
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

-- Lets the companion-line mechanism know what it last showed (avoid
-- repeating a nudge every page load) and doubles as the data source for
-- the "connections facilitated" family-dashboard metric.
create table if not exists companion_events (
  id text primary key,
  elder_id text not null references profiles(id),
  event_type text not null check (event_type in
    ('family_nudge_shown', 'family_nudge_accepted', 'reminiscence_shown')),
  created_at text default (datetime('now'))
);

-- One-way family note shown on the elder's Home screen, kept separate
-- from chat_messages.
create table if not exists family_notes (
  id text primary key,
  elder_id text not null references profiles(id),
  sender_name text not null,
  relation text,
  text text not null,
  created_at text default (datetime('now'))
);
```

## Key Architectural Decisions

**Safety-relevant decisions are computed deterministically, not left to a
single model judgment call.** Scam risk in Point & Ask, for example, is
scored from independently extracted signals (urgency, money requests,
authority impersonation, requests for secrecy) using plain arithmetic. The
model classifies; code decides.

**Escalation checks run at the point of the triggering event** (a scam
classification, a distress-tagged chat message, a dose flipping to missed),
inside the feature module that detects it, not on family dashboard load.
The dashboard only ever reads the `alerts` table; it never generates alerts
itself.

**Language is generated directly, not translated after the fact.** Dynamic
LLM content (chat replies, Point & Ask explanations) is generated straight
in the elder's preferred language via a parameterized system prompt.
Fixed, safety-critical content (warnings, UI chrome) comes from a single
reviewed strings dictionary, one entry per supported language: English,
Mandarin Chinese, Malay, and Tamil, Singapore's four official languages.
See the README for the full language-support model.

**Access control is plain application-level filtering**, not
database-level policy: every query filters explicitly by `elder_id` or
`role`. The FastAPI layer touches the database over real HTTP with no
authentication of its own. See `SECURITY.md` for the current state of this
gap.

**Configuration comes from a `.env` file.** `api/main.py` reads
`ANTHROPIC_API_KEY` via `python-dotenv`, loaded once in
`backend/claude_client.py`.

## Getting Started

See the root `README.md` for setup and run instructions.
