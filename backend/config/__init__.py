"""App configuration: every tunable value (models, temperature, thresholds,
prompts) lives in conf/*.yaml, not in code. See docs/ARCHITECTURE.md's Key
Architectural Decisions for why.

Usage:
    from backend.config import get_settings

    grace = get_settings().medications.grace_minutes
"""

from functools import cache

from backend.config.loader import load_config
from backend.config.schemas import Settings

__all__ = ["Settings", "get_settings"]


# Loads and validates conf/*.yaml once, reused for the life of the process
@cache
def get_settings() -> Settings:
    """Return the app's cached, validated configuration.

    Returns:
        Settings: the validated configuration, loaded once and reused.
    """
    return load_config()
