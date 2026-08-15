# AI Elderly Companion

An AI companion for elderly users that reduces daily friction around
companionship, medication management, dementia support, and scam
protection, while keeping family involved for anything financial,
health-critical, or requiring human judgment. AI augments family care here;
it never replaces it.

## Overview

The companion checks in daily, gently encourages real contact with family
rather than substituting for it, helps make sense of letters and messages
(flagging likely scams before any harm is done), tracks medication
adherence, and gives family a quiet, non-intrusive view into patterns worth
knowing about, without ever putting that same information in front of the
elder themselves.

The product is built around one constraint: the AI is a bridge to real
relationships, not a replacement for them. There are no engagement-maximizing
mechanics (no streaks, no gamified check-ins): success is measured by real
contact facilitated, not time spent in the app. Anything financially or
medically significant, or anything suggesting sustained distress, is
escalated to family rather than handled by the AI alone.

## Pillars

| Pillar | What it covers |
|---|---|
| Loneliness & Connection | Daily chat, check-ins, nudges to contact real family members |
| Medication & Health | Reminders, adherence tracking |
| Dementia Support | Patient repeated answers, family-provided "memory bank" facts/photos, reminiscence prompts |
| Scam Protection | Photo/message in, explain it or flag it as a scam |
| Cognitive Change Signals (quiet) | Passive pattern detection (repetition frequency, sentiment trend) surfaced only to family, never the elder |

## Key Features

**Daily check-ins & companionship**: a short daily conversation that adapts
to context: a gentle nudge to reach out to family after a few quiet days, a
warm reminiscence prompt drawn from real memories family has shared, or a
simple how-are-you-feeling check-in. Replies stay natural and unscripted,
while safety-relevant signals (mood, distress, repetition) are tracked
underneath.

**Point & Ask**: photograph a letter, bill, or suspicious message to get a
plain-language explanation, or a clear scam warning if something looks
wrong. Risk is scored from independently extracted signals (urgency, money
requests, authority impersonation, requests for secrecy) rather than left to
a single model judgment call, and a scam detection immediately notifies
family.

**Medication & calendar**: family adds medications and appointments; the
elder sees a simple, always-current view of what's due, what's been taken,
and what's coming up.

**Memory bank & reminiscence**: family shares facts and photos about the
elder's life. The companion draws on these facts (and only these; it never
invents details) to make conversation feel personal and to occasionally
suggest reconnecting with the specific people those memories involve.

**Family dashboard**: a quiet, family-only view of patterns (mood trends,
question-repetition frequency, medication adherence) and any alerts that
need attention, framed as an impression to prompt a real check-in, not a
diagnosis to rely on.

**Multi-language support**: fully localized across English, Mandarin
Chinese, Malay, and Tamil for every elder-facing screen, not just chat
content. Set by family on the elder's behalf, since navigating an
English-only settings menu isn't a realistic ask for someone who doesn't
read English well.

## Escalation Model

The core differentiator: the decision of when the AI hands something to
family is implemented as real, testable logic, not a disclaimer or a hope
that the model behaves well.

| Situation | AI handles alone | Escalates to family |
|---|---|---|
| General chat / companionship | Yes | None |
| Low mood, one-off | Yes (empathetic reply, suggests calling someone) | Only if it persists 3+ days |
| Missed one dose | Yes (shown as missed, asked about at the next check-in) | None |
| Missed medication repeatedly | None | Yes, immediately |
| Same question repeated, stable frequency | Yes (patient, consistent answer) | Only if frequency is rising over time |
| Photo/message flagged as scam | Yes (warns elder, blocks the action) | Yes, immediately |
| Legit high-stakes document (bill, legal notice) | Yes (explains it, and verbally suggests involving family for money/deadlines) | Not yet — no alert is written for this case today |
| Sustained distress / crisis language | None | Yes, immediately, high priority |
| New facts about elder's life/routine | None | Family adds directly (AI never fabricates) |

Scam risk and mood/repetition trends are scored from independently
extracted signals using deterministic rules, not left to a single
generative judgment call — the model classifies, code decides.

## Ethical Stance

A warm, always-available AI risks becoming a substitute for real human
contact rather than a bridge to it, especially for a lonely user. This is
an active design constraint throughout the product, not a disclaimer added
afterward:

- **No engagement-maximizing mechanics.** No streaks, no gamified
  check-ins. Success is measured by real contact facilitated, not time
  spent in the app.
- **The daily companion actively encourages reaching out to real people**,
  not just in safety moments but in ordinary emotionally-themed exchanges,
  and reminiscence prompts occasionally suggest sharing a memory with the
  specific person it involves.
- **Conversations are bounded, not open-ended.** A daily check-in is
  normally a single exchange. When the first reply reads as low mood or
  distress, exactly one follow-up reply is allowed before the companion
  closes the conversation for the day, always toward encouraging contact
  with family. This prevents two failure modes at once: an AI that cuts
  someone off mid-disclosure, and an AI that becomes an open-ended
  substitute for a real relationship.
- **A companion boundary statement is surfaced directly to the elder**:
  the AI is there to keep company between visits, never instead of them,
  and anything that matters is passed along to family.
- **Anything financially or medically significant, or suggesting
  sustained distress, is escalated to family rather than resolved by the
  AI alone**, per the Escalation Model above.
- **Family communication stays one-way** — a note to the elder, not a
  reply thread. A two-way channel would work against the same goal:
  nudging toward a real phone call, not becoming another app-mediated
  conversation to check.

## Language Support

Language is treated as a real barrier for elderly users, not an
afterthought bolted onto chat content. If someone doesn't read English
well enough to need chat or document content in another language, they
likely can't reliably navigate English-only tab labels either, so partial
localization (content translated, chrome left in English) doesn't actually
solve the problem. Full elder-facing localization covers the entire
surface: nav titles, labels, placeholders, buttons, not just conversation.

Two kinds of content, treated differently:

- **Dynamic LLM content** (chat replies, Point & Ask explanations) is
  generated directly in the elder's preferred language by the model
  itself, never an English draft translated after the fact.
- **Everything fixed** (safety-critical messages, UI chrome) comes from a
  single reviewed strings dictionary, one entry per supported language.
  Consistency matters more than variation for something like a scam
  warning, and a fixed set of strings can actually be checked for
  completeness across every language.

Family sets the elder's language preference on their behalf, rather than
the elder navigating a settings menu themselves — someone who doesn't read
English well shouldn't need to use an English-only settings page to fix
that. Family-facing pages (dashboard, settings) stay in English, since
family already operates the admin flow in English to set the preference in
the first place.

## Screenshots

### Home and daily check-in

The elder's landing screen: a photo from the memory bank, a note from
family, and the day's opening question.

![Home screen](docs/screenshots/home.png)

### Point & Ask

A photographed message classified as a scam, with the warning written in
plain language and no action the elder can take alone.

![Point and Ask showing a scam warning](docs/screenshots/point-and-ask.png)

### Family dashboard

The family-only view: a weekly summary in the companion's voice, then
what's worth knowing, adherence, and mood.

![Family dashboard](docs/screenshots/family-dashboard.png)

## Architecture

A React frontend talks to a thin FastAPI layer over one Python backend and
one SQLite database:

- **Backend**: Python, SQLite, and the Anthropic Claude API (a faster model
  for classification/tagging decisions, a stronger model for conversational
  replies and explanations). Safety-relevant decisions (scam risk, escalation
  triggers) are computed deterministically from model-extracted signals
  rather than left to a single generative judgment call.
- **React app**: TanStack Start, React 19, Tailwind, backed by a thin
  FastAPI layer that reuses the backend directly.

See `docs/ARCHITECTURE.md` for the full database schema and key
architectural decisions.

## Getting Started

```bash
# Terminal 1: API
uv sync
cp .env.example .env   # fill in ANTHROPIC_API_KEY
uv run uvicorn api.main:app --port 8000

# Terminal 2: frontend
cd web
bun install
bun run dev
```

Then open `http://localhost:3000`.

The app reads from a local SQLite database and seeds a demo elder and
family profile automatically on first run, with no account or manual setup
required.

## Testing & Evaluation

```bash
uv run pytest              # unit + API tests
uv run ruff check .         # lint
uv run ruff format .        # format
```

A separate labeled evaluation set (`eval/`) checks the AI features against
known-answer cases: classification accuracy where there's a single correct
answer, and an LLM-as-judge pass/fail check for free-form replies where
there isn't.

## Project Structure

```
ai-elderly-companion/
├── api/, web/           # FastAPI + React app
├── backend/             # Business logic shared across every API endpoint
├── docs/                # Architecture, security, and roadmap docs
├── eval/, notebooks/    # Evaluation sets and prompt exploration
├── tests/               # Unit and API tests
└── sql/                 # Database schema
```

## Further Reading

- `docs/ARCHITECTURE.md`: full database schema and key architectural decisions
- `docs/SECURITY.md`: known limitations and how to report a concern
- `docs/ROADMAP.md`: known gaps and where this could go next
