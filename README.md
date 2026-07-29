# AI Elderly Companion

An AI companion app for elderly users, reducing daily friction across companionship, medication management, dementia support, and scam protection, while keeping family looped in for anything financial, health-critical, or requiring human judgment.

## Status

Early build, Phase 0 (foundations) in progress. See `BUILD_PLAN.md` for the full phased build plan, architecture, and database schema.

## Stack

- Streamlit (Python) frontend
- SQLite (local file, schema self-applies on first run, no setup required)
- Anthropic Claude API (chat, vision, classification)

Demo mode: a sidebar role selector switches between a seeded elder and family
profile — no login required.

## Setup

1. `uv sync`
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in `ANTHROPIC_API_KEY`.
3. `uv run streamlit run app.py`

## Development

- `uv run ruff check .` and `uv run ruff format .`
- `uv run pytest`
- `pre-commit install` once, after cloning
