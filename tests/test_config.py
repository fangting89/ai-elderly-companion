"""Unit tests for backend.config: conf/*.yaml loading, validation, and
caching. Writes its own temporary conf/ directories so a bad-value test
never touches the real conf/ files.
"""

import logging

import pytest
import yaml
from pydantic import ValidationError

from backend.config import get_settings
from backend.config.loader import load_config
from backend.config.schemas import Settings

# One minimal, valid value per file, matching backend.config.schemas.Settings
_VALID_CONF = {
    "claude": {
        "tag_model": "test-tag-model",
        "chat_model": "test-chat-model",
        "prose_temperature": 1.0,
        "max_tokens": 1024,
    },
    "escalation": {
        "missed_medication_pattern_threshold": 2,
        "repeated_question_weekly_threshold": 2,
        "low_mood_streak_days": 3,
    },
    "medications": {"grace_minutes": 30},
    "chat": {"recent_messages_limit": 20, "bounded_checkin_max_replies": 2},
    "point_and_ask": {
        "max_image_dimension": 1568,
        "core_signal_weight": 2,
        "high_risk_cutoff": 5,
        "medium_risk_cutoff": 3,
    },
    "memory": {"context_facts_limit": 10, "reminiscence_nudge_probability": 0.5},
    "companion_line": {
        "family_nudge_silence_days": 5,
        "family_nudge_cooldown_days": 2,
        "reminiscence_cooldown_days": 3,
    },
    "api": {"cors_origin": "http://localhost:3000"},
    "logging": {"level": "INFO", "log_file": ""},
    "prompts": {
        "tag_system": "test tag prompt",
        "classify_system": "test classify prompt",
        "companion_persona": "test persona {clauses}",
        "explain_image_base": "test explain {language_clause}",
        "reminiscence_base": "test reminiscence {language_clause}{bridge_clause}",
        "weekly_summary_base": "test weekly summary",
    },
}


def _write_conf_dir(tmp_path, overrides: dict | None = None):
    """Write one YAML file per section into tmp_path, applying overrides.

    Args:
        tmp_path: pytest's tmp_path fixture.
        overrides: {section_name: value} -- replaces that section's whole
            content (use None to omit the file entirely).
    """
    sections = dict(_VALID_CONF)
    if overrides:
        for name, value in overrides.items():
            if value is None:
                sections.pop(name, None)
            else:
                sections[name] = value
    for name, content in sections.items():
        (tmp_path / f"{name}.yaml").write_text(yaml.dump(content))
    return tmp_path


def test_load_config_against_real_conf_dir_succeeds():
    # Smoke test: the actual shipped conf/ files parse and validate today.
    settings = load_config()
    assert isinstance(settings, Settings)
    assert settings.medications.grace_minutes > 0


def test_get_settings_is_cached():
    assert get_settings() is get_settings()


def test_valid_conf_dir_loads_expected_values(tmp_path):
    conf_dir = _write_conf_dir(tmp_path)
    settings = load_config(conf_dir)
    assert settings.medications.grace_minutes == 30
    assert settings.claude.chat_model == "test-chat-model"


def test_wrong_type_raises_validation_error(tmp_path):
    conf_dir = _write_conf_dir(tmp_path, {"medications": {"grace_minutes": "not-a-number"}})
    with pytest.raises(ValidationError):
        load_config(conf_dir)


def test_missing_section_raises_validation_error(tmp_path):
    conf_dir = _write_conf_dir(tmp_path, {"escalation": None})
    with pytest.raises(ValidationError):
        load_config(conf_dir)


def test_missing_field_within_section_raises_validation_error(tmp_path):
    conf_dir = _write_conf_dir(tmp_path, {"chat": {"recent_messages_limit": 20}})
    with pytest.raises(ValidationError):
        load_config(conf_dir)


def test_load_config_configures_a_logging_handler(tmp_path):
    conf_dir = _write_conf_dir(tmp_path)
    load_config(conf_dir)
    assert len(logging.getLogger().handlers) > 0
