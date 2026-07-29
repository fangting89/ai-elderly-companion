# AI Elderly Companion

An AI companion app for elderly users, reducing daily friction across companionship, medication management, dementia support, and scam protection, while keeping family looped in for anything financial, health-critical, or requiring human judgment.

## Status

Early build, Phase 0 (foundations) in progress. See `BUILD_PLAN.md` for the full phased build plan, architecture, and database schema.

## Stack

- Streamlit (Python) frontend
- Supabase (Postgres, Auth, Storage)
- Anthropic Claude API (chat, vision, classification)

## Setup

1. `uv sync`
2. Create a Supabase project and run `sql/schema.sql` in its SQL editor.
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in `SUPABASE_URL`, `SUPABASE_KEY`, `ANTHROPIC_API_KEY`.
4. `uv run streamlit run app.py`

## Development

- `uv run ruff check .` and `uv run ruff format .`
- `uv run pytest`
- `pre-commit install` once, after cloning
