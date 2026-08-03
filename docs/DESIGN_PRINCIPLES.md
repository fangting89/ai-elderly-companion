# Design Principles

## Core stance

One AI companion for elderly users that reduces daily friction around
loneliness, medication management, dementia support, and scam protection,
while explicitly keeping family involved for anything financial,
health-critical, or requiring human judgment.

**AI augments family care. It does not replace it.**

## Pillars

| Pillar | What it covers |
|---|---|
| Loneliness & Connection | Daily chat, check-ins, nudges to contact real family members |
| Medication & Health | Reminders, adherence tracking |
| Dementia Support | Patient repeated answers, family-provided "memory bank" facts/photos, reminiscence prompts |
| Scam Protection | Photo/message in, explain it or flag it as a scam |
| Cognitive Change Signals (quiet) | Passive pattern detection (repetition frequency, sentiment trend) surfaced only to family, never the elder |

## The Escalation Rules

The core differentiator: implemented as real, testable logic, not a
disclaimer or a hope that the model behaves.

| Situation | AI handles alone | Escalates to family |
|---|---|---|
| General chat / companionship | Yes | None |
| Low mood, one-off | Yes (empathetic reply, suggests calling someone) | Only if it persists 3+ days |
| Missed one dose | Yes (gentle reminder) | None |
| Missed medication repeatedly | None | Yes, immediately |
| Same question repeated, stable frequency | Yes (patient, consistent answer) | Only if frequency is rising over time |
| Photo/message flagged as scam | Yes (warns elder, blocks the action) | Yes, immediately |
| Legit high-stakes document (bill, legal notice) | Yes (explains it) | Yes if it involves money/deadlines, or elder requests it |
| Sustained distress / crisis language | None | Yes, immediately, high priority |
| New facts about elder's life/routine | None | Family adds directly (AI never fabricates) |

"Rising frequency" for repeated questions is computed as the count of
flagged repeated-question messages this week versus the prior week;
escalation only fires if this week's count is higher, not on any single
occurrence.

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

Supported languages: English, Mandarin Chinese, Malay, and Tamil,
Singapore's four official languages.

Family sets the elder's language preference on their behalf, rather than
the elder navigating a settings menu themselves. Someone who doesn't read
English well shouldn't need to use an English-only settings page to fix
that.

Family-facing pages (dashboard, settings) stay in English, since family
already operates the admin flow in English to set the preference in the
first place.

## Ethical Stance

A warm, always-available AI risks becoming a substitute for real human
contact rather than a bridge to it, especially for a lonely user. This is
treated as an active design constraint throughout the product, not a
disclaimer added afterward:

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
- **A companion boundary statement** is surfaced directly to the elder:
  the AI is there to keep company between visits, never instead of them,
  and anything that matters is passed along to family.
- **Anything financially or medically significant, or suggesting
  sustained distress, is escalated to family rather than resolved by the
  AI alone**, per the Escalation Rules above.
