# Roadmap

`README.md` and `ARCHITECTURE.md` document what's been built and why; this
file covers what's still open and where this could go next.

---

## Known gaps

- **Family Dashboard shows placeholder data.** The real backend
  (`backend/dashboard.py`, `backend/escalation.py`) already computes mood
  trends, adherence, and alerts; the dashboard page isn't wired to it yet.
- **Point & Ask has no hallucination double-check.** One classify call,
  one explain call, whatever comes out is shown as-is; no second read to
  hedge disagreements, and no graded confidence for a borderline-quality
  photo (today it's a binary readable/unreadable split).
- **Legit high-stakes documents (bills, legal notices) don't escalate.**
  The explanation tells the elder to involve family for anything with
  money or deadlines, but that's advice inside the reply text; no alert is
  actually written, unlike the scam-detection branch.
- **Medication reminders are pull, not push.** Due/missed status only
  updates when the elder opens the Medication page.
- **"Activities Near You" shows example content**, not real nearby events.

## Future Vision

Open-ended directions this project could grow into:

- **Add events by voice/chat, as a real, confirmed feature.** Either a
  separate "add something to my calendar" voice/chat entry point outside
  the bounded check-in, or an explicit confirmation in the AI's reply
  ("Got it, I've added that to your calendar") so it's a felt feature
  family and the elder can both rely on, not a silent side effect.
- **Smart home integration.** Fall/activity tracking and location-based
  wandering safety, extending the companion beyond a phone/tablet into
  ambient sensing for an elder living alone, surfaced to family with the
  same escalate-only-when-it-matters philosophy as everything else here.
- **Cognitive games.** Light memory/attention exercises woven into daily
  check-ins, scored as another quiet signal for family (never shown to the
  elder as a "test"), alongside mood and repeated-question trends.
- **"Is it real?" media verification.** Paste a link (a TikTok video, a
  forwarded clip, a voice note) and get a plain-language read on whether
  it's likely AI-generated, extending Point & Ask's scam-protection
  instinct from photographed documents to viral media and deepfakes, a
  fast-growing scam vector for this demographic.
- **A live activities feed**, connecting "Activities Near You" to real
  local event sources (community centre listings, library programmes)
  instead of a static example list.
- **Multi-elder support**, so one family account can look after more than
  one elder.
