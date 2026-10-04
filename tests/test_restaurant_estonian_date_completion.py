"""Offline Estonian date completion with independent Tallinn calendar fixtures."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.restaurant_dates import ESTONIAN_COUNTS, resolve_restaurant_date

NOW = datetime(2026, 10, 4, 12, tzinfo=ZoneInfo("Europe/Tallinn"))
COUNT_FORMS = (
    ("üks", "ühe", "ühele"),
    ("kaks", "kahe", "kahele"),
    ("kolm", "kolme", "kolmele"),
    ("neli", "nelja", "neljale"),
    ("viis", "viie", "viiele"),
    ("kuus", "kuue", "kuuele"),
    ("seitse", "seitsme", "seitsmele"),
    ("kaheksa", "kaheksa", "kaheksale"),
    ("üheksa", "üheksa", "üheksale"),
    ("kümme", "kümne", "kümnele"),
    ("üksteist", "üheteistkümne", "üheteistkümnele"),
    ("kaksteist", "kaheteistkümne", "kaheteistkümnele"),
    ("kolmteist", "kolmeteistkümne", "kolmeteistkümnele"),
    ("neliteist", "neljateistkümne", "neljateistkümnele"),
    ("viisteist", "viieteistkümne", "viieteistkümnele"),
    ("kuusteist", "kuueteistkümne", "kuueteistkümnele"),
    ("seitseteist", "seitsmeteistkümne", "seitsmeteistkümnele"),
    ("kaheksateist", "kaheksateistkümne", "kaheksateistkümnele"),
    ("üheksateist", "üheksateistkümne", "üheksateistkümnele"),
    ("kakskümmend", "kahekümne", "kahekümnele"),
)


@pytest.mark.parametrize(
    "completion",
    ["viiendal", "5-ndal", "viiendal oktoobril", "oktoobril viiendal"],
)
def test_owned_month_year_survives_bare_or_named_day_completion(completion):
    partial = resolve_restaurant_date(
        "oktoobris 2027. aastal", NOW, allow_bare_day=True
    )
    assert (partial.value, partial.issue, partial.day, partial.month, partial.year) == (
        None,
        "date_incomplete",
        None,
        10,
        2027,
    )
    resolved = resolve_restaurant_date(
        completion,
        NOW,
        allow_bare_day=True,
        pending_month=partial.month,
        pending_year=partial.year,
    )
    assert resolved.value == "2027-10-05" and resolved.issue is None
    assert not resolved.remaining_text.strip(" .!?,")
    assert (resolved.day, resolved.month, resolved.year) == (None, None, None)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("viiendal oktoobril 2028. aastal", "2028-10-05"),
        ("viiendal oktoobril kaks tuhat kakskümmend kaheksa", "2028-10-05"),
        ("2028. aastal viiendal oktoobril", "2028-10-05"),
        ("viiendal novembril", "2026-11-05"),
        ("viiendal novembril 2028. aastal", "2028-11-05"),
    ],
)
def test_new_month_or_explicit_year_does_not_blindly_inherit_pending_year(
    text, expected
):
    resolved = resolve_restaurant_date(
        text, NOW, allow_bare_day=True, pending_month=10, pending_year=2027
    )
    assert resolved.value == expected and resolved.issue is None


def test_unowned_named_date_does_not_inherit_a_partial_year():
    resolved = resolve_restaurant_date(
        "viiendal oktoobril", NOW, pending_month=10, pending_year=2027
    )
    assert resolved.value == "2026-10-05" and resolved.issue is None


@pytest.mark.parametrize(
    "text,issue",
    [
        ("2028. aastal viiendal oktoobril 2027. aastal", "date_ambiguous"),
        ("viiendal oktoobril 27. aastal", "date_ambiguous"),
        ("viiendal või kuuendal oktoobril", "date_ambiguous"),
        ("mitte viiendal oktoobril", "date_ambiguous"),
        ("kolmekümne esimesel veebruaril", "date_invalid"),
    ],
)
def test_pending_year_cannot_override_ambiguous_negated_or_invalid_dates(text, issue):
    resolved = resolve_restaurant_date(
        text, NOW, allow_bare_day=True, pending_month=10, pending_year=2027
    )
    assert resolved.value is None and resolved.issue == issue


@pytest.mark.parametrize("number,forms", tuple(enumerate(COUNT_FORMS, 1)))
def test_exported_diner_cardinals_cover_one_through_twenty(number, forms):
    for form in forms:
        assert ESTONIAN_COUNTS.get(form) == number
    assert all(1 <= value <= 20 for value in ESTONIAN_COUNTS.values())


@pytest.mark.parametrize("forms", COUNT_FORMS)
@pytest.mark.parametrize("pending_month", [None, 10])
def test_cardinal_diner_allative_is_not_a_bare_calendar_day(forms, pending_month):
    text = forms[2]
    resolved = resolve_restaurant_date(
        text,
        NOW,
        allow_bare_day=True,
        pending_month=pending_month,
        pending_year=2027 if pending_month else None,
    )
    assert (
        resolved.value,
        resolved.issue,
        resolved.day,
        resolved.month,
        resolved.year,
    ) == (None, None, None, None, None)
    assert resolved.remaining_text == text


@pytest.mark.parametrize(
    "text,expected",
    [
        ("viiendal", "2027-10-05"),
        ("viiendale", "2027-10-05"),
        ("viis", "2027-10-05"),
        ("viie", "2027-10-05"),
        ("5", "2027-10-05"),
        ("üheteistkümnendal", "2027-10-11"),
        ("kaheteistkümnendale", "2027-10-12"),
    ],
)
def test_calendar_ordinals_and_requested_bare_cardinals_remain_supported(
    text, expected
):
    resolved = resolve_restaurant_date(
        text, NOW, allow_bare_day=True, pending_month=10, pending_year=2027
    )
    assert resolved.value == expected and resolved.issue is None
    assert text not in ESTONIAN_COUNTS or text in {"viis", "viie"}


@pytest.mark.parametrize(
    "text", ["neljale palun", "tegelikult viiele", "kaheteistkümnele!"]
)
def test_date_reply_scaffolding_does_not_turn_diner_allatives_into_days(text):
    resolved = resolve_restaurant_date(text, NOW, allow_bare_day=True, pending_month=10)
    assert resolved.value is None and resolved.issue is None and resolved.day is None
    assert resolved.remaining_text == text


@pytest.mark.parametrize(
    "text",
    ["05. 10. 2026", "05 . 10 . 2026", "5. 10. 2026.", "05.10. 2026", "2026 . 10 . 05"],
)
def test_whole_spaced_numeric_date_keeps_exact_day_month_and_year(text):
    resolved = resolve_restaurant_date(text, NOW, allow_bare_day=True)
    assert resolved.value == "2026-10-05" and resolved.issue is None
    assert not resolved.remaining_text.strip(" .!?,")


@pytest.mark.parametrize(
    "text,issue",
    [
        ("31. 04. 2026", "date_invalid"),
        ("29 . 02 . 2027", "date_invalid"),
        ("05. 13. 2026", "date_invalid"),
        ("05. 10. 0000", "date_invalid"),
        ("05. 10. 26", "date_ambiguous"),
        ("05 / 10 / 2026", "date_ambiguous"),
        ("05 . 10 / 2026", "date_ambiguous"),
        ("05 . 10 . 2026 . 2027", "date_ambiguous"),
        ("05 .. 10 . 2026", "date_ambiguous"),
        ("05 . 10 . 2026 /", "date_ambiguous"),
        ("05 . 10", "date_ambiguous"),
    ],
)
def test_spaced_numeric_dates_validate_the_whole_token_without_guessing(text, issue):
    resolved = resolve_restaurant_date(text, NOW, allow_bare_day=True)
    assert resolved.value is None and resolved.issue == issue


@pytest.mark.parametrize(
    "text", ["kuuendal päeval oktoobris", "kuuendal kuupäeval oktoobris"]
)
def test_ordinal_day_scaffolding_resolves_and_masks_the_calendar_phrase(text):
    resolved = resolve_restaurant_date(text, NOW, allow_bare_day=True)
    assert resolved.value == "2026-10-06" and resolved.issue is None
    assert not resolved.remaining_text.strip()
