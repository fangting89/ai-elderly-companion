# Security Policy

## Scope

This is a personal portfolio project, not a production system, and is not
currently deployed anywhere reachable beyond a local machine. It's intended
to be run locally for demonstration and evaluation purposes.

## Data handling

- All data (profiles, chat history, medication records, uploaded photos and
  documents) is stored locally in a single SQLite file. Nothing is sent to a
  third party except the Anthropic API, which receives only the content
  needed to fulfil a given request (a message, an uploaded image, and
  relevant profile context).
- Photographed documents (letters, bills, messages) can contain personal
  identifiers such as NRIC numbers or home addresses. The AI is explicitly
  instructed not to restate these in full in any generated summary or
  explanation, describing them generically instead. This is a prompt-level
  instruction, not a guaranteed deterministic filter — treat it as a
  mitigation, not an absolute guarantee, when handling real personal
  documents.
- Scam-risk classification is computed from independently extracted signals
  using deterministic scoring, rather than left to a single model judgment
  call, so the safety-relevant decision is testable and reproducible.

## Known limitations

- **The FastAPI layer (`api/`) has no authentication.** Any client that can
  reach it can act as any elder or family profile — there is no session,
  login, or access control beyond filtering by an explicitly passed
  identifier. This is acceptable for local, single-user demo use only. Do
  not expose this API beyond `localhost` without adding real
  authentication first.
- No encryption at rest is applied to the local SQLite database or uploaded
  files.

## Reporting a concern

This is an actively developed solo project. If you find a security issue,
please open an issue in this repository describing it — for anything
sensitive, reach out to the maintainer directly rather than filing it
publicly.
