"""Exact Estonian clock/date repairs, without providers or booking consent."""

import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.restaurant_call import parse_restaurant_request
from app.restaurant_dates import CALENDAR_SPELLING, resolve_restaurant_date
from app.restaurant_times import parse_spoken_time

NOW = datetime(2026, 10, 3, 12, tzinfo=ZoneInfo("Europe/Tallinn"))
CLOCKS = [
    ("kell kaheksateist null viis", "18:05"),
    ("kell kuus null viis õhtul", "18:05"),
    ("kell kuus ja pool õhtul", "18:30"),
    ("Kuue ajal õhtul", "18:00"),
    ("Viis minutit üle kuue õhtul", "18:05"),
]


@pytest.mark.parametrize("text,expected", CLOCKS)
def test_reported_estonian_clocks_keep_exact_minutes(text, expected):
    selection = parse_spoken_time(text)
    assert selection and selection.value == expected
    assert selection.candidates is None and not selection.invalid


@pytest.mark.parametrize(
    "text,minute",
    [
        ("kell kuus null viis", "05"),
        ("kell kuus ja pool", "30"),
        ("Kuue ajal", "00"),
        ("Viis minutit üle kuue", "05"),
    ],
)
def test_new_clock_forms_do_not_guess_am_or_pm(text, minute):
    selection = parse_spoken_time(text)
    assert selection and selection.candidates == (f"06:{minute}", f"18:{minute}")
    assert selection.value is None and not selection.invalid


@pytest.mark.parametrize(
    "text,expected",
    [
        ("kell kuus null üks hommikul", "06:01"),
        ("kell kuus null üheksa õhtul", "18:09"),
        ("kell null viis", "00:05"),
        ("kell null null viis", "00:05"),
        ("kuus null viis PM", "18:05"),
        (unicodedata.normalize("NFD", "kell kuus null viis õhtul"), "18:05"),
    ],
)
def test_zero_prefixed_minutes_are_not_reinterpreted_as_hours(text, expected):
    selection = parse_spoken_time(text)
    assert selection and selection.value == expected and not selection.invalid


def test_bare_zero_prefixed_clock_requires_an_expected_time_answer():
    assert parse_spoken_time("kuus null viis") is None
    selection = parse_spoken_time("kuus null viis", allow_bare=True)
    assert selection and selection.candidates == ("06:05", "18:05")
    assert parse_spoken_time("õhtul", pending=selection.candidates).value == "18:05"


@pytest.mark.parametrize(
    "text",
    [
        "kell kuus null viisteist õhtul",
        "kell kuus null viis seitse õhtul",
        "kell kuus viis seitse õhtul",
        "kell kuus ja veerand õhtul",
        "kell kuus ja kolmveerand õhtul",
        "kell kuus ja pool viis õhtul",
        "pool seitse viis õhtul",
        "18:05 null viis",
        "keskpäeval viis",
        "Viis minutit üle kuue viis õhtul",
        "kell kuus läbi õhtul",
        "kell kuus 1000 õhtul",
        "kell kuue ajal viis õhtul",
        "kell kuus ja poolteist õhtul",
        "at six oh five seven PM",
        "в шесть тридцать пять семь вечера",
    ],
)
def test_unconsumed_adjacent_clock_numbers_and_fractions_are_invalid(text):
    selection = parse_spoken_time(text)
    assert selection and selection.invalid
    assert selection.value is None and selection.candidates is None


@pytest.mark.parametrize(
    "text",
    [
        "kell kuus null viis seitse õhtul",
        "kell kuus ja veerand õhtul",
        "pool seitse viis õhtul",
    ],
)
def test_invalid_clock_correction_clears_stale_time_but_not_date_or_party(text):
    previous = {"date": "2026-10-04", "start_time": "18:00", "party_size": 4}
    result = parse_restaurant_request(text, previous, now=NOW)
    assert result == {"date": "2026-10-04", "party_size": 4, "time_invalid": True}
    assert previous["start_time"] == "18:00"


@pytest.mark.parametrize(
    "text",
    [
        "Soovin lauda homme kell kuus null viis õhtul neljale",
        "Soovin lauda homme kell kuus null viis õhtul nelja inimesega",
        "Soovin lauda homme kell 18:05 neljale",
        "A table tomorrow at 18:05 four guests",
        "Столик завтра в 18:05 четыре гостя",
    ],
)
def test_clock_tail_validation_leaves_adjacent_guest_counts_alone(text):
    assert parse_restaurant_request(text, now=NOW) == {
        "date": "2026-10-04",
        "start_time": "18:05",
        "party_size": 4,
    }


@pytest.mark.parametrize("date_reply", [False, True])
@pytest.mark.parametrize(
    "text",
    [
        "pärast",
        "4 pärast",
        "homme pärast kuut",
        "homme parast kuut",
        "kuue ajal õhtul",
        "viis minutit üle kuue õhtul",
        "kell kuus läbi viis õhtul",
    ],
)
def test_temporal_connectors_are_never_fuzzy_calendar_words(text, date_reply):
    normalized = CALENDAR_SPELLING.normalize(text, date_reply=date_reply)
    assert normalized.text == text and not normalized.ambiguous_spans


@pytest.mark.parametrize("text", ["Nädala pärast", "NÄDALA PÄRAST"])
@pytest.mark.parametrize("date_reply", [False, True])
def test_implicit_one_week_is_seven_days_not_march(text, date_reply):
    result = resolve_restaurant_date(text, NOW, allow_bare_day=date_reply)
    assert result.value == "2026-10-10" and result.issue is None
    assert result.day is None and result.month is None
    assert not result.remaining_text.strip()


@pytest.mark.parametrize(
    "text,expected,issue",
    [
        ("ühe nädala pärast", "2026-10-10", None),
        ("kahe nädala pärast", "2026-10-17", None),
        ("-2 nädala pärast", None, "date_invalid"),
        ("nädala pärast või homme", None, "date_ambiguous"),
    ],
)
def test_implicit_week_does_not_override_explicit_counts_or_conflicts(
    text, expected, issue
):
    result = resolve_restaurant_date(text, NOW, allow_bare_day=True)
    assert result.value == expected and result.issue == issue


@pytest.mark.parametrize("quantity", ["poole", "saja", "10000"])
def test_implicit_week_never_discards_an_unsupported_quantity(quantity):
    result = resolve_restaurant_date(
        f"{quantity} nädala pärast", NOW, allow_bare_day=True
    )
    assert result.value is None and result.issue


@pytest.mark.parametrize("date_reply", [False, True])
def test_after_an_hour_keeps_tomorrow_without_inventing_a_march_date(date_reply):
    result = resolve_restaurant_date(
        "Homme pärast kuut", NOW, allow_bare_day=date_reply
    )
    assert result.value == "2026-10-04" and result.issue is None
    assert result.remaining_text.strip() == "pärast kuut"


@pytest.mark.parametrize("text", ["neljandal, palun", "neljandal palun.", "4., palun!"])
def test_polite_day_answer_retains_day_four_and_requires_a_month(text):
    previous = {"start_time": "18:00", "party_size": 2}
    result = parse_restaurant_request(text, previous, now=NOW, expected_field="date")
    assert result == {
        "start_time": "18:00",
        "party_size": 2,
        "date_issue": "date_incomplete",
        "date_day": 4,
    }
    completed = parse_restaurant_request(
        "oktoobril", result, now=NOW, expected_field="date_incomplete"
    )
    assert completed == {"date": "2026-10-04", "start_time": "18:00", "party_size": 2}


def test_polite_day_answer_uses_the_pending_month_and_year():
    result = resolve_restaurant_date(
        "neljandal, palun",
        NOW,
        allow_bare_day=True,
        pending_month=10,
        pending_year=2028,
    )
    assert result.value == "2028-10-04" and result.issue is None


def test_polite_day_is_not_a_date_without_an_expected_date_answer():
    result = resolve_restaurant_date("neljandal, palun", NOW)
    assert result.value is None and result.issue is None


@pytest.mark.parametrize("clock,expected", CLOCKS)
def test_shared_booking_parser_keeps_week_date_exact_clock_and_party(clock, expected):
    text = f"Soovin lauda nädala pärast {clock} neljale"
    assert parse_restaurant_request(text, now=NOW) == {
        "date": "2026-10-10",
        "start_time": expected,
        "party_size": 4,
    }


def test_after_six_is_not_an_exact_time_or_availability_inference():
    assert parse_restaurant_request(
        "Soovin lauda homme pärast kuut neljale", now=NOW
    ) == {
        "date": "2026-10-04",
        "party_size": 4,
    }


@pytest.mark.parametrize(
    "text",
    [clock for clock, _ in CLOCKS]
    + [
        "Nädala pärast",
        "neljandal, palun",
        "Mis kell olete homme lahti?",
    ],
)
def test_clock_and_date_repairs_do_not_establish_booking_intent(text):
    assert parse_restaurant_request(text, now=NOW) is None
