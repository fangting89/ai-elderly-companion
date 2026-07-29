"""Unit tests for medication dose status classification. Pure logic, no I/O."""

from datetime import datetime, timedelta

from backend.medications import GRACE_MINUTES, classify_dose_status


def test_future_dose_is_pending():
    now = datetime(2026, 1, 1, 8, 0)
    scheduled = now + timedelta(hours=1)
    assert classify_dose_status(scheduled, None, now) == "pending"


def test_taken_dose_is_taken_even_if_past_due():
    scheduled = datetime(2026, 1, 1, 8, 0)
    taken_at = datetime(2026, 1, 1, 8, 5)
    now = datetime(2026, 1, 1, 10, 0)
    assert classify_dose_status(scheduled, taken_at, now) == "taken"


def test_just_past_due_within_grace_period_is_still_pending():
    scheduled = datetime(2026, 1, 1, 8, 0)
    now = scheduled + timedelta(minutes=GRACE_MINUTES - 5)
    assert classify_dose_status(scheduled, None, now) == "pending"


def test_past_grace_period_is_missed():
    scheduled = datetime(2026, 1, 1, 8, 0)
    now = scheduled + timedelta(minutes=GRACE_MINUTES + 5)
    assert classify_dose_status(scheduled, None, now) == "missed"


def test_exactly_at_grace_boundary_is_missed():
    scheduled = datetime(2026, 1, 1, 8, 0)
    now = scheduled + timedelta(minutes=GRACE_MINUTES)
    assert classify_dose_status(scheduled, None, now) == "missed"


def test_dose_due_right_now_is_still_pending():
    scheduled = datetime(2026, 1, 1, 8, 0)
    assert classify_dose_status(scheduled, None, scheduled) == "pending"
