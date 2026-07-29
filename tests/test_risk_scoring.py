"""Unit tests for the deterministic Point & Ask risk scoring and routing.

Pure logic, no I/O or LLM calls.
"""

from backend.point_and_ask import ClassifyResult, decide_branch, score_risk


def _result(
    urgency=False,
    secrecy_request=False,
    authority_impersonation=False,
    money_request=False,
    image_quality="clear",
) -> ClassifyResult:
    return ClassifyResult(
        image_quality=image_quality,
        urgency=urgency,
        secrecy_request=secrecy_request,
        authority_impersonation=authority_impersonation,
        money_request=money_request,
        content_summary="test",
    )


def test_no_signals_is_low_risk():
    assert score_risk(_result()) == "low"


def test_one_signal_is_low_risk():
    assert score_risk(_result(urgency=True)) == "low"


def test_two_signals_is_medium_risk():
    assert score_risk(_result(urgency=True, money_request=True)) == "medium"


def test_three_signals_is_high_risk():
    assert score_risk(_result(urgency=True, money_request=True, secrecy_request=True)) == "high"


def test_all_four_signals_is_high_risk():
    result = _result(
        urgency=True, money_request=True, secrecy_request=True, authority_impersonation=True
    )
    assert score_risk(result) == "high"


def test_low_risk_clear_image_routes_to_explain():
    result = _result()
    assert decide_branch(result, score_risk(result)) == "explain"


def test_medium_risk_routes_to_scam():
    result = _result(urgency=True, money_request=True)
    assert decide_branch(result, score_risk(result)) == "scam"


def test_high_risk_routes_to_scam():
    result = _result(urgency=True, money_request=True, secrecy_request=True)
    assert decide_branch(result, score_risk(result)) == "scam"


def test_unreadable_image_routes_to_unclear_even_with_scam_signals():
    result = _result(
        urgency=True, money_request=True, secrecy_request=True, image_quality="unreadable"
    )
    assert decide_branch(result, score_risk(result)) == "unclear"


def test_urgency_and_authority_alone_stays_low_risk():
    """A real deadline from a real authority (e.g. a passport renewal notice)
    shouldn't alone be flagged as a scam; money_request or secrecy_request
    must be present too. Regression test for a real eval failure."""
    result = _result(urgency=True, authority_impersonation=True)
    assert score_risk(result) == "low"
    assert decide_branch(result, score_risk(result)) == "explain"


def test_blurry_but_readable_with_no_signals_routes_to_explain():
    result = _result(image_quality="blurry")
    assert decide_branch(result, score_risk(result)) == "explain"
