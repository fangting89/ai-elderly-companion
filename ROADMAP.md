# Roadmap / Future Work

This project is ongoing. `docs/ARCHITECTURE.md` and `docs/DESIGN_PRINCIPLES.md`
document what's been built and why; this file documents what's next: known
gaps, planned extensions, and things deliberately left out of scope for now.

---

## Known gaps to close

- **Wire the React Family Dashboard to real data.** The backend
  (`backend/dashboard.py`, `backend/escalation.py`) is fully built and
  tested, but the newer, more polished React frontend just isn't connected
  to it yet, and currently shows hardcoded mock charts/alerts/summary.
  Highest-value fix on this list: real backend already exists, this is
  wiring, not new logic.
- **Add real authentication to the FastAPI layer** (`api/`). Currently any
  client can act as any elder or family member: no session, no auth,
  `elder_id` is just a request parameter. Flagged in `api/main.py`'s
  docstring, not yet fixed.
- **Hallucination double-check for Point & Ask.** The sibling ReadForMeLeh
  project reads a photographed letter twice and hedges any field the two
  reads disagree on (a real fix for a documented wrong-balance incident
  there). Point & Ask has no equivalent: one classify call, one explain
  call, whatever comes out is shown as-is.
- **Field-level hedging on blurry-but-readable photos.** `image_quality`
  only branches on `unreadable` vs. everything else: a photo that's
  readable but not confidently precise gets full unhedged prose, with no
  middle ground.
- **Explicit prompt-injection defense clause for Point & Ask's classify
  step.** ReadForMeLeh states outright that letter text addressed to "the
  AI/SYSTEM" is itself a red flag; Point & Ask's defense is softer/implicit
  ("a separate scoring system decides, not you").
- **A real medication reminder, not just a status page.** Documented POC
  limitation: due/missed status only recomputes when the Medication page
  loads. No push notification if the elder never opens it.
- **Decide on two-way family messaging.** Currently one-way only (family →
  elder note card on Home, no reply path back): either build a reply path
  for real, or treat this as intentionally closed.
- **Manually verify voice in a live browser.** Read-aloud/mic input exist in
  both apps and pass automated checks, but real audio behavior has never
  been manually confirmed in a browser session for either implementation.
  Also: Safari/iOS lack `SpeechRecognition` support, worth testing given
  iPads are a plausible device for this demographic.
- **A UI/font polish pass** for elderly-friendly readability across the
  React app, and a rehearsed demo script to go with it.

## New features / natural extensions

- **Surface the "connections facilitated" stat** on the dashboard once it's
  wired to real data. The underlying data (`companion_events`) is already
  collected, just not displayed anywhere yet.
- **Give "Activities Near You" a real, joinable events feed.** The card is
  now wired to a backend endpoint (`/api/activities`), but the underlying
  list in `backend/activities.py` is still a static placeholder, not real
  events. Investigated feasibility: there's no public API for the
  hyperlocal layer this app's examples show (void-deck Tai Chi, an RC's
  mahjong afternoon) -- that layer has no digital footprint anywhere,
  API or otherwise, so no amount of engineering surfaces it. The one
  credible real, free, no-auth source found is the National Library
  Board's Events API, which includes senior/active-ageing programmes
  across library branches islandwide -- real, joinable, but
  library-centric rather than neighbourhood-centric. A "near you" feed of
  any kind also needs a prerequisite that doesn't exist yet: the app has
  no elder location/postal code field at all (`web/src/lib/weather.ts`
  hardcodes one fixed Singapore-wide coordinate for the whole app).
  Realistic path: a hybrid of NLB's real feed (needs the location field
  added) for the national/library layer, plus a family-added-activities
  flow (same pattern as calendar events) for the hyperlocal layer no API
  will ever reach.
- **Replace the professional-support resource card** with a real feed:
  even a small curated list of real Singapore eldercare/befriending
  services would beat the current hardcoded stand-in.
- **Wire the email-alert stub to a real provider** (Resend/SendGrid).
  Already documented as "a drop-in swap" in `backend/escalation.py`, never
  actually swapped in; currently just a logged `print()`.
- **Configurable escalation thresholds.** Family-tunable sensitivity
  (currently hardcoded constants, e.g. a 5-day family-silence threshold):
  turns a fixed rule engine into something family can actually adjust.
- **Export/share the weekly AI summary**: as a message to another family
  member, or to bring along when talking to a doctor.
- **A real "add a new elder" onboarding flow.** Right now there's only ever
  the one auto-seeded demo elder/family pair; no path to create a second
  one.

## Engineering maturity

- **Containerize and deploy.** A live demo link is worth more in a
  portfolio than "clone and run locally." Docker packaging is a direct
  reuse of the MLOps assignment pattern.
- **CI pipeline** (e.g. GitHub Actions running `ruff` and `pytest` on every
  push). No CI currently exists for this repo.
- **Extend the LLM-as-judge eval pattern to Point & Ask.** The
  reply-quality judge added to the chat eval only covers one of the two AI
  features. The same pattern (explanation quality, not just classification
  accuracy) is a natural, cheap extension to `eval/run_point_and_ask_eval.py`.
- **Turn eval into a CI-gated check**, not just a manually-run script.
- **A basic cost/latency view** from the per-call logging added to
  `backend/claude_client.py`. Currently just log lines; aggregating them
  (even a small script tallying spend and p95 latency) turns raw logs into
  a real LLMOps artifact.

## Explicitly deferred, documented non-goals, not gaps

Cognitive games, GPS/wandering safety, deepfake/AI-image forensics, and
fall detection were all deliberately excluded from this build as out of
MVP scope. Listed here for completeness: these were considered and
consciously deferred, not forgotten.
