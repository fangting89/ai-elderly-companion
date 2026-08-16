"""Unit tests for strings.get_string's language fallback behavior."""

import pytest

from backend.strings import _STRINGS, StringKey, get_string


def test_known_language_and_key_returns_that_languages_text():
    assert get_string("English", "daily_checkin") == _STRINGS["English"]["daily_checkin"]
    assert get_string("Malay", "daily_checkin") != _STRINGS["English"]["daily_checkin"]


def test_unsupported_language_falls_back_to_english():
    assert get_string("Klingon", "daily_checkin") == _STRINGS["English"]["daily_checkin"]


@pytest.mark.parametrize("language", ["English", "Mandarin Chinese", "Malay", "Tamil"])
def test_every_supported_language_has_every_key(language):
    for key in StringKey.__args__:
        assert get_string(language, key)  # every key resolves to a non-empty string
