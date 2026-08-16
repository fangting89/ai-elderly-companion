# Architecture

See the root `README.md` for the product pitch: pillars, key features,
escalation model, ethical stance, and language support. This file is the
technical reference: schema, architectural decisions, and how each AI
pipeline actually works.

**Contents**: [Overview](#overview) · [Data Flow](#data-flow) ·
[Repository Structure](#repository-structure) ·
[Database Schema](#database-schema-sqlite) ·
[Key Architectural Decisions](#key-architectural-decisions) ·
[Chat Pipeline](#chat-pipeline) ·
[Point & Ask Pipeline](#point--ask-pipeline) ·
[Medication Pipeline](#medication-pipeline) ·
[Claude Client](#claude-client) ·
[Prompt Inventory](#prompt-inventory) ·
[Configuration](#configuration) ·
[Getting Started](#getting-started)

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

## Data Flow

One SQLite file, one shared connection, and a straight line from database
to screen:

```
data/app.db (one SQLite file on disk)
        |
backend/db.py -- get_connection() -- the only door in
        |
backend/*.py  -- chat.py, medications.py, escalation.py, etc.
                 each one runs its own SQL through that connection
                 and owns the actual business logic
        |
api/main.py   -- FastAPI endpoints, thin wrappers with no logic of
                 their own -- they just call into backend/*.py and
                 return JSON
        |
web/ (React)  -- fetches those endpoints, renders the screens
```

`backend/db.py`'s `get_connection()` is the one function every other
backend module calls to reach the database -- nothing talks to SQLite
directly. `api/main.py` never contains business logic itself; it only
translates HTTP requests into calls on `backend/*.py` and serializes the
result. That separation is deliberate: swapping SQLite for a real
production database, or adding authentication, only touches `db.py` and
`api/main.py` -- every backend module and the frontend keep working
unchanged. See `SECURITY.md` for what's demo-scale today (SQLite,
zero-auth, auto-seeded demo data) versus what the pattern itself already
supports.

## Repository Structure

```
ai-elderly-companion/
├── backend/
│   ├── db.py                  # sqlite connection, schema init, demo seed
│   ├── config/                # loads and validates conf/*.yaml, configures logging
│   ├── claude_client.py       # Claude API wrapper: forced tool-use, prose calls
│   ├── chat.py                # prose reply + sentiment/repetition tagging
│   ├── point_and_ask.py       # classify -> explain | scam branch
│   ├── strings.py             # fixed safety-critical strings, per language
│   ├── companion_line.py      # daily-opener priority mechanism
│   ├── family_notes.py        # one-way family note -> elder Home screen
│   ├── activities.py          # static "Activities Near You" placeholder
│   ├── medications.py, calendar.py
│   ├── memory_bank.py         # family facts/photos, reminiscence prompts
│   ├── dashboard.py           # aggregate queries -- currently unreachable,
│   │                           # see Prompt Inventory below
│   └── escalation.py          # check_and_alert(), writes alerts
├── conf/                        # tunable values: models, thresholds, prompts
├── api/                        # FastAPI layer for the React frontend below,
│                               # reusing backend/*.py directly
├── web/                         # React/TanStack Start frontend
├── eval/                        # labeled evaluation sets for the AI features
├── notebooks/                    # interactive prompt exploration
├── tests/                        # unit and API tests
└── sql/schema.sql                # database schema, auto-applied on startup
```

## Database Schema (SQLite)

Full `CREATE TABLE` statements live in `sql/schema.sql` (auto-applied on
startup by `backend/db.py`, idempotent). Summary of what each table holds:

| Table | Holds |
| --- | --- |
| `profiles` | One row per elder or family member; `elder_id` links a family row to the elder it belongs to. |
| `medications` | An elder's medications and their scheduled times per day. |
| `medication_logs` | One row per expected dose, tracking taken/missed/pending status. |
| `calendar_events` | Appointments and other calendar entries. |
| `chat_messages` | Every chat message, elder or AI, with sentiment/repetition tags. |
| `documents` | Point & Ask uploads: the photo, its classification, and the explanation or scam summary. |
| `memory_bank_entries` | Family-added photos and facts used to ground chat replies. |
| `alerts` | Family-facing alerts (missed medication, scam detected, sentiment decline, etc.). |
| `companion_events` | Tracks what the daily-opener mechanism last showed, and feeds the "connections facilitated" dashboard metric. |
| `family_notes` | One-way notes from family, shown on the elder's Home screen. |

## Key Architectural Decisions

- **Model extracts, code decides.** The model only ever pulls out signals
  (scam-behavior booleans, dose timing, sentiment); plain code decides what
  they mean. Never a single model judgment call for anything safety-related.
  See Point & Ask, Medication, and Chat Pipeline below.
- **Escalate at the trigger, not on dashboard load.** Alerts are written the
  moment something happens (a scam classification, a distress message, a
  missed dose), inside the module that detects it. The dashboard only reads
  the `alerts` table; it never generates one.
- **Reply in-language, don't translate after.** Dynamic content (chat
  replies, Point & Ask explanations) is generated directly in the elder's
  preferred language. Fixed safety-critical text (warnings, UI chrome) comes
  from one reviewed strings dictionary, per language: English, Mandarin
  Chinese, Malay, Tamil. See the README for the full language model.
- **Access control is filtering, not policy.** Every query filters
  explicitly by `elder_id`/`role` in application code; there's no
  database-level enforcement, and the API has no authentication of its own.
  See `SECURITY.md` for the current state of this gap.
- **Two-tier configuration.** `.env` holds the one secret
  (`ANTHROPIC_API_KEY`), read via `python-dotenv`. Every tunable value
  (model names, temperature, escalation thresholds, risk-scoring weights,
  AI system prompts) lives in `conf/*.yaml` instead, validated at startup.
  See Configuration below.

## Chat Pipeline

`backend/chat.py`, entry point `send_message()`. Every chat reply makes
two separate Claude calls, mirroring Point & Ask's classify-then-act
split: a cheap call tags the message, then a stronger call writes the
actual reply, once escalation and the bounded-conversation gate have been
resolved in between.

```
Elder types a reply
        |
        v
Tag call: call_structured(), cheap model                  [AI call]
   -> sentiment, repeated_question_flag?
        |
        v
Save elder message                                        [plumbing]
   -- if concerning --> check_and_alert() (escalation.py)
                         writes a family alert
        |
        v
Bounded Check-In gate                                      [deterministic]
   -- one reply left & low mood --> one more reply allowed
   -- otherwise                 --> closing (last message today)
        |
        v
Reply call: call_prose(), stronger model                    [AI call]
   via build_system_prompt() (language, known facts, closing tone)
        |
        v
Save AI reply                                                [plumbing]
        |
        v
Return ChatReply(text, can_continue) to the caller
```

### Sentinel resolution

Fixed chat openers (the daily check-in, the family-contact nudge) are
stored as short placeholders, not literal text, so they never go stale --
a nudge saved while the elder's language was Mandarin still renders
correctly in English later, since it's rebuilt fresh every time it's read.

```
Two writers, same table:
  maybe_send_daily_checkin()  -> saves a sentinel (e.g. "__family_nudge__")
  send_message()              -> saves the real message text
        |
        v
  chat_messages
        |
        v
  get_todays_opener() / _recent_messages()                  [reads]
        |
        v
  _render_content(): is this a sentinel?                [deterministic]
     -- yes --> rebuild real text now, in the current language
     -- no  --> return the stored text as-is
```

### Function reference

| Kind | Function | What it does |
| --- | --- | --- |
| AI call | `send_message()`'s tag call | Classifies sentiment and repetition via `call_structured()`. |
| plumbing | `_insert_message()` | The single place that writes a row to `chat_messages`. |
| deterministic | `_render_content()` | Resolves a stored sentinel into real, current text, or passes real messages through untouched. |
| AI call | `send_message()`'s reply call | Writes the actual reply via `call_prose()`, using `build_system_prompt()`. |
| escalation | `check_and_alert()` | Called after every elder message with its sentiment, and again if it's flagged as repeated. |

The chat history length and the bounded Check-In reply cap are
configurable in `conf/chat.yaml`.

## Point & Ask Pipeline

`backend/point_and_ask.py`, entry point `process_photo()`. An elder photographs
a letter or message; the app decides whether to explain it or flag it as a
scam. Every step below is one of three kinds:

- **AI call**: the model observes and describes, never judges.
- **Deterministic code**: plain Python decides, no model involved.
- **Plumbing**: moves or stores data, no judgment either way.

```
Photo uploaded
        |
        v
_resize_if_needed()                                         [plumbing]
        |
        v
classify_image()                                             [AI call]
   forced checklist: image_quality, urgency, secrecy_request,
   authority_impersonation, money_request, content_summary
   (never a free-text verdict)
        |
        v
score_risk()                                                  [deterministic]
   (money_request + secrecy_request) x 2 + urgency + authority_impersonation
   -> low / medium / high
        |
        v
decide_branch()                                                [deterministic]
   -- unreadable        --> "unclear"
   -- medium/high risk  --> "scam"
   -- otherwise          --> "explain"
        |
        v
explain_image()                                    [AI call, "explain" branch only]
   writes directly in the elder's own language
        |
        v
_save_upload() + _persist()                                     [plumbing]
   photo file + a row in the `documents` table
        |
        v
   -- "scam" branch only --> check_and_alert() (escalation.py)
                              family gets a scam_detected alert
        |
        v
Result returned -- frontend renders the matching screen
```

All three branches (unclear / scam / explain) converge on the same save
step: every photo is saved and logged regardless of outcome. Only a `scam`
classification additionally raises a `scam_detected` alert.

**How `score_risk()` weighs signals:** `money_request` and `secrecy_request`
are the core diagnostic signals: real correspondence essentially never
demands payment/personal details under pressure, or asks the recipient to
hide it from family. A zero on both always scores "low", regardless of the
rest. `urgency` and `authority_impersonation` are common in legitimate mail
too (a real deadline, a real government notice), so they only escalate
severity once a core signal is already present. The weight and cutoffs
below are configurable in `conf/point_and_ask.yaml`; the values shown are
the defaults:

```
score = (money_request + secrecy_request) x 2 + urgency + authority_impersonation

score == 0        -> low     (no core signal at all)
1 <= score <= 2    -> low
3 <= score <= 4    -> medium
score >= 5         -> high
```

### Function reference

| Kind | Function | What it does |
| --- | --- | --- |
| plumbing | `_resize_if_needed()` | Shrinks the photo if it exceeds the configured max dimension. |
| AI call | `classify_image()` | Sends the photo to Claude, forced to answer a fixed checklist, never a free-text verdict. |
| deterministic | `score_risk()` | Weighted arithmetic over the checklist answers → low / medium / high. |
| deterministic | `decide_branch()` | Picks unclear / scam / explain from image quality and risk level. |
| AI call | `explain_image()` | Only on the safe branch: writes the plain-language explanation, directly in the elder's language. |
| plumbing | `_save_upload()` | Writes the photo file to `data/uploads/`. |
| plumbing | `_persist()` | Saves the whole result as one row in the `documents` table. |
| scam-only | `check_and_alert()` | Only on the scam branch: raises a `scam_detected` alert for the family. |

## Medication Pipeline

`backend/medications.py`, entry point `get_todays_doses()`. No AI involved
at all; this is a pure status-classification pipeline, run every time the
elder's Medicine page (or the family's dashboard, once wired) asks what's
due today.

```
get_todays_doses() called
        |
        v
_ensure_todays_logs()                                        [plumbing]
   creates today's expected dose rows (one per scheduled
   time), if missing
        |
        v
for each of today's doses:
        |
        v
classify_dose_status()                                        [deterministic]
   -- taken_at set?                          --> "taken"
   -- now >= scheduled + grace period?       --> "missed"
   -- otherwise                               --> "pending"
        |
        v
just flipped to "missed"?
   -- yes --> save the new status, call check_and_alert() (escalation.py)
   -- no  --> nothing to do, just include it in the results
        |
        v
return today's doses
```

Same split as Point & Ask: `classify_dose_status()` is a pure function
(scheduled time, taken time, now → a status), with zero database or
escalation logic in it, independently testable for the same reason as
`score_risk()`. The grace period defaults to 30 minutes, configurable in
`conf/medications.yaml`.

### Function reference

| Kind | Function | What it does |
| --- | --- | --- |
| plumbing | `_ensure_todays_logs()` | Creates today's expected dose rows if they don't exist yet. |
| deterministic | `classify_dose_status()` | Pure function: scheduled time, taken time, now → taken / missed / pending. |
| escalation | `check_and_alert()` | Called only when a dose just flipped to missed. |
| plumbing | `mark_taken()` | Records a dose as taken, called when the elder taps "I took it." |

## Claude Client

`backend/claude_client.py`. Every AI call in the app funnels through here,
regardless of which feature triggered it:

```
chat.py / point_and_ask.py / memory_bank.py / dashboard.py
        |
        v
Need a decision (JSON, predictable), or a reply (free text, read by a human)?
   -- decision --> call_structured(): forced tool-use, temperature=0
   -- reply    --> call_prose(): plain text, configured temperature
        |
        v
get_client()                                                  [cached]
   one Anthropic client, built once (@cache) and reused every
   call -- only the connection is cached, never a question or answer
        |
        v
Anthropic API (Claude)
        |
        v
_log_call()
   writes one log line per call: model, latency, input/output tokens
        |
        v
Result handed back to caller
```

Model names, `call_prose()`'s temperature, and each call's default max
tokens are read from `conf/claude.yaml`. `call_structured()`'s
`temperature=0` is not configurable: it backs every deterministic decision
in the app, and pinning it to zero is a safety property, not a style
choice. Logging is configured once at startup from `conf/logging.yaml`
(level, and an optional log file), so `_log_call()`'s output is real: every
Claude call writes one line with its model, latency, and token counts.

## Prompt Inventory

Every AI system prompt in the app, in one place: useful for reviewing
wording or safety language (e.g. the "never invent" instruction that
appears, independently worded, in every prompt below) without hunting
through each feature file individually.

| Text | Prompt | Used by | Reachable? |
| --- | --- | --- | --- |
| `conf/prompts.yaml` | `tag_system` | `chat.py`'s `send_message()`: tags sentiment and repetition | Yes |
| `conf/prompts.yaml` | `companion_persona` | `chat.py`'s `build_system_prompt()`: the actual reply | Yes |
| `conf/prompts.yaml` | `classify_system` | `point_and_ask.py`'s `classify_image()` | Yes |
| `conf/prompts.yaml` | `explain_image_base` | `point_and_ask.py`'s `explain_image()` | Yes |
| `conf/prompts.yaml` | `reminiscence_base` | `memory_bank.py`'s `generate_reminiscence_prompt()`, used by `companion_line.py`'s daily-opener decision | Yes |
| `conf/prompts.yaml` | `weekly_summary_base` | `dashboard.py`'s `get_weekly_summary()`: nothing, `dashboard.py` isn't imported anywhere | No, unreachable |

Every prompt's fixed text lives in `conf/prompts.yaml`, one entry per
prompt, editable without touching Python. The two fully static prompts
(`tag_system`, `classify_system`) are used as-is. The other four are
templates: the code that assembles each one (`build_system_prompt()`,
`explain_image()`, `generate_reminiscence_prompt()`) still decides what
goes into placeholders like `{language_clause}`, since that logic depends
on runtime state (the elder's language, known facts, whether this is the
closing message).

The prompt text itself is deliberately kept out of a shared `prompts/`
code module and out of each feature file, living in config instead. At
this scale (a handful of prompts, one developer) that keeps the wording
editable on its own, while the assembly logic and the schema/parsing that
consumes each prompt's output stay next to the feature that owns them.

## Configuration

Every backend module reads its tunable values from a validated
`Settings` object instead of a hardcoded literal:

```
conf/*.yaml (one file per module: claude, escalation, medications,
             chat, point_and_ask, memory, companion_line, api,
             logging, prompts)
        |
        v
backend/config/loader.py: load_config()                    [plumbing]
   reads every YAML file, keyed by filename
        |
        v
backend/config/schemas.py: Settings                        [validation]
   one Pydantic model per file; a wrong type or missing field
   raises a clear error at startup, not a silent bad value
        |
        v
backend/config/__init__.py: get_settings()                    [cached]
   loaded once (@cache) and reused for the life of the process;
   also configures logging as a side effect of loading
        |
        v
Every backend module reads what it needs at import time
```

Each YAML file maps to the backend module it configures, and is commented
in place, for example `conf/medications.yaml`:

```yaml
# Minutes after the scheduled time before a dose counts as missed, rather
# than still pending.
grace_minutes: 30
```

Changing a value (a threshold, a model name, a prompt's wording) means
editing the relevant `conf/*.yaml` file and restarting the app; no Python
changes needed. `call_structured()`'s `temperature=0` is the one deliberate
exception, kept out of config since it is a safety property rather than a
tuning knob (see Claude Client above).

## Getting Started

See the root `README.md` for setup and run instructions.
