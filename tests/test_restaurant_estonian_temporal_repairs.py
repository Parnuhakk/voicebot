"""ASR-shaped dates and clocks must retain the actual requested booking fields."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.booking_response import trusted_booking_response
from app.restaurant_call import COPY, parse_restaurant_request
from app.restaurant_dates import CALENDAR_SPELLING, resolve_restaurant_date
from app.restaurant_times import parse_spoken_time
from tests.test_restaurant_http import start, tomorrow, turn

pytest_plugins = ["tests.test_restaurant_conversation", "tests.test_restaurant_http"]
NOW = datetime(2026, 10, 4, 12, tzinfo=ZoneInfo("Europe/Tallinn"))


@pytest.mark.parametrize(
    "text,expected",
    [
        ("pärast kahte päeva", "2026-10-06"),
        ("pärast 2 päeva", "2026-10-06"),
        ("pärast kolme nädalat", "2026-10-25"),
        ("üle homme", "2026-10-06"),
        ("üle homseks", "2026-10-06"),
        ("viiendal kuupäeval oktoobris", "2026-10-05"),
        ("5-ndal oktoobril", "2026-10-05"),
        ("5. kuupäeval oktoobris", "2026-10-05"),
        ("viiendal oktoobril 2027. aastal", "2027-10-05"),
        ("viiendal oktoobril aastal 2027", "2027-10-05"),
        ("viiendal oktoobril aastal kaks tuhat kakskümmend seitse", "2027-10-05"),
    ],
)
def test_estonian_date_scaffolding_cannot_drop_a_relative_prefix_or_explicit_year(
    text, expected
):
    resolved = resolve_restaurant_date(text, NOW, allow_bare_day=True)
    assert resolved.value == expected and resolved.issue is None
    assert not resolved.remaining_text.strip(" .!?,")
    assert parse_restaurant_request(
        text,
        {"start_time": "18:30", "party_size": 4},
        now=NOW,
        expected_field="date",
    ) == {"date": expected, "start_time": "18:30", "party_size": 4}


@pytest.mark.parametrize("text", ["pärast kahte päeva", "üle homme", "nädala pärast"])
def test_relative_date_words_are_not_fuzzy_calendar_repairs(text):
    assert CALENDAR_SPELLING.normalize(text, date_reply=True).text == text


@pytest.mark.parametrize(
    "now,text,expected",
    [
        (NOW, "ülejärgmisel reedel", "2026-10-16"),
        (NOW, "ülejärgmisel esmaspäeval", "2026-10-12"),
        (
            datetime(2026, 10, 5, 12, tzinfo=ZoneInfo("Europe/Tallinn")),
            "ülejärgmisel reedel",
            "2026-10-16",
        ),
    ],
)
def test_short_weekday_after_next_does_not_silently_select_next_weekday(
    now, text, expected
):
    resolved = resolve_restaurant_date(text, now, allow_bare_day=True)
    assert resolved.value == expected and resolved.issue is None
    assert not resolved.remaining_text.strip()


@pytest.mark.parametrize(
    "answers",
    [
        ("viiendal kuupäeval", "oktoobris 2027. aastal"),
        ("oktoobris 2027. aastal", "5-ndal"),
        ("oktoobris", "2027. aastal", "viiendal kuupäeval"),
        ("oktoobris", "aastal kaks tuhat kakskümmend seitse", "viiendal"),
    ],
)
def test_split_calendar_answers_retain_the_explicit_year_and_other_details(answers):
    inquiry = {"start_time": "18:30", "party_size": 4}
    for answer in answers:
        inquiry = parse_restaurant_request(
            answer, inquiry, now=NOW, expected_field="date_incomplete"
        )
    assert inquiry == {"date": "2027-10-05", "start_time": "18:30", "party_size": 4}


@pytest.mark.parametrize(
    "text,expected",
    [
        ("kell 18. 30", "18:30"),
        ("kell 18 : 30", "18:30"),
        ("kell 18 . 30.", "18:30"),
        ("kell kuus, kolmkümmend õhtul", "18:30"),
        ("kolm veerand seitse õhtul", "18:45"),
        ("poolseitse õhtul", "18:30"),
        ("jah, seitse õhtul", "19:00"),
        ("pigem seitse õhtul", "19:00"),
        ("kell kuus pärast lõunat", "18:00"),
    ],
)
@pytest.mark.parametrize("expected_field", ["time", "ambiguous_time"])
def test_asr_clock_formats_keep_minutes_and_replace_the_pending_hour(
    text, expected, expected_field
):
    prior = {"date": "2026-10-06", "party_size": 4}
    if expected_field == "ambiguous_time":
        prior["time_candidates"] = ("06:00", "18:00")
    selection = parse_spoken_time(
        text, allow_bare=True, pending=prior.get("time_candidates")
    )
    assert selection and selection.value == expected and not selection.invalid
    assert parse_restaurant_request(
        text, prior, now=NOW, expected_field=expected_field
    ) == {"date": "2026-10-06", "party_size": 4, "start_time": expected}


@pytest.mark.parametrize("text", ["kell 18. 70", "kell 18 : 3", "kell 18. 300"])
def test_malformed_spaced_minutes_clear_a_previous_valid_clock(text):
    prior = {"date": "2026-10-06", "party_size": 4, "start_time": "18:00"}
    selection = parse_spoken_time(text)
    assert selection and selection.invalid and selection.value is None
    assert parse_restaurant_request(text, prior, now=NOW, expected_field="time") == {
        "date": "2026-10-06",
        "party_size": 4,
        "time_invalid": True,
    }
    assert prior["start_time"] == "18:00"


@pytest.mark.parametrize(
    "text", ["banaan õhtul", "seitseteist banaani õhtul", "poolbanaan õhtul"]
)
def test_unknown_period_answer_cannot_select_an_old_ambiguous_hour(text):
    selection = parse_spoken_time(text, allow_bare=True, pending=("06:00", "18:00"))
    assert selection is None or selection.value is None
    inquiry = parse_restaurant_request(
        text,
        {"date": "2026-10-06", "party_size": 4, "time_candidates": ("06:00", "18:00")},
        now=NOW,
        expected_field="ambiguous_time",
    )
    assert "start_time" not in inquiry


@pytest.mark.parametrize("text", ["05. 10. 2026", "05 . 10 . 2026"])
def test_spaced_numeric_calendar_date_is_never_a_clock(text):
    assert parse_spoken_time(text, allow_bare=True) is None


@pytest.mark.parametrize("text", ["18 . 11", "18. 11", "18 / 11", "18 - 11"])
def test_spaced_short_date_answer_cannot_replace_the_retained_clock(make_state, text):
    state = make_state()
    for answer in ("Soovin lauda broneerida", "kell 18:30", "Meid on neli", text):
        state.observe_user_text(answer, detected_language="et")
        state.guard_reply("", [])
    assert state.booking_inquiry == {
        "start_time": "18:30",
        "party_size": 4,
        "date_issue": "date_ambiguous",
    }
    assert "name" not in (trusted_booking_response(state) or {})
    state.observe_user_text("homme", detected_language="et")
    action = trusted_booking_response(state)
    assert action["arguments"] == {
        "date": tomorrow(),
        "start_time": "18:30",
        "party_size": 4,
    }


@pytest.mark.parametrize(
    "text",
    [
        "pärast kahte päeva või kolme päeva",
        "pärast 2 päeva kuni 3 päeva",
        "pärast kahte päeva, või kolme päeva",
        "pärast 2 päeva–3 päeva",
        "pärast 2 päeva-3 päeva",
        "pärast 2 päeva—3 päeva",
    ],
)
def test_reverse_relative_date_choice_cannot_select_an_endpoint(make_state, text):
    resolved = resolve_restaurant_date(text, NOW, allow_bare_day=True)
    assert resolved.value is None and resolved.issue == "date_ambiguous"
    state = make_state()
    state.observe_user_text(
        f"Soovin lauda broneerida {text} kell 18:30 neljale", detected_language="et"
    )
    assert "date" not in state.booking_inquiry
    assert state.booking_inquiry["date_issue"] == "date_ambiguous"
    assert "name" not in (trusted_booking_response(state) or {})
    assert not state.pending and not state.bookings


@pytest.mark.parametrize(
    "choice",
    [
        "pärast kahte päeva või kolme päeva",
        "pärast kahte päeva, või kolme päeva",
        "pärast 2 päeva–3 päeva",
        "pärast 2 päeva-3 päeva",
        "pärast 2 päeva—3 päeva",
    ],
)
def test_relative_date_choice_keeps_other_details_while_asking_for_one_day(
    make_state, choice
):
    state = make_state()
    for answer in (
        "Soovin lauda broneerida",
        "kell 18:30",
        "Meid on neli",
        choice,
    ):
        state.observe_user_text(answer, detected_language="et")
        state.guard_reply("", [])
    assert state.booking_inquiry == {
        "start_time": "18:30",
        "party_size": 4,
        "date_issue": "date_ambiguous",
    }
    assert "name" not in (trusted_booking_response(state) or {})


@pytest.mark.parametrize("text", ["18:30:", "18 : 30 ::", "18 : 30 :x"])
def test_dangling_clock_colon_cannot_accept_a_valid_prefix(make_state, text):
    clock = parse_spoken_time("kell " + text)
    assert clock and clock.invalid and clock.value is None
    state = make_state()
    state.observe_user_text(
        f"Soovin lauda broneerida homme kell {text} neljale", detected_language="et"
    )
    assert "start_time" not in state.booking_inquiry
    assert state.booking_inquiry["time_invalid"]
    assert "name" not in (trusted_booking_response(state) or {})
    assert not state.pending and not state.bookings


@pytest.mark.parametrize("answer", ["õhtul", "jah, õhtul", "pigem õhtul"])
def test_whole_period_answer_still_resolves_an_owned_ambiguous_hour(make_state, answer):
    selection = parse_spoken_time(answer, allow_bare=True, pending=("06:30", "18:30"))
    assert selection and selection.value == "18:30" and not selection.invalid
    state = make_state()
    for text in (
        "Soovin lauda broneerida",
        "Homme",
        "Meid on neli",
        "pool seitse",
        answer,
    ):
        state.observe_user_text(text, detected_language="et")
        if text != answer:
            state.guard_reply("", [])
    assert state.booking_inquiry == {
        "date": tomorrow(),
        "party_size": 4,
        "start_time": "18:30",
    }
    assert trusted_booking_response(state)["arguments"]["start_time"] == "18:30"
    assert not state.pending and not state.bookings


@pytest.mark.parametrize(
    "answer,expected",
    [("jah, seitse õhtul", "19:00"), ("kolm veerand seitse õhtul", "18:45")],
)
def test_shared_dialogue_retains_date_and_party_when_replacing_pending_clock(
    make_state, answer, expected
):
    state = make_state()
    for text in (
        "Soovin lauda broneerida",
        "Homme",
        "Meid on neli",
        "Kell kuus",
        answer,
    ):
        state.observe_user_text(text, detected_language="et")
        if text != answer:
            state.guard_reply("", [])
    assert state.booking_inquiry == {
        "date": tomorrow(),
        "start_time": expected,
        "party_size": 4,
    }
    action = trusted_booking_response(state)
    assert action["name"] == "plan_restaurant_reservation"
    assert action["arguments"]["start_time"] == expected
    assert not state.pending and not state.bookings


def test_date_answer_correction_clears_the_old_day_instead_of_reusing_it(make_state):
    state = make_state()
    for text in (
        "Soovin lauda broneerida",
        "Homme",
        "kell 18:30",
        "tegelikult kuuendal",
    ):
        state.observe_user_text(text, detected_language="et")
        state.guard_reply("", [])
    inquiry = state.booking_inquiry
    assert inquiry is not None
    assert inquiry["date_issue"] == "date_incomplete" and inquiry["date_day"] == 6
    assert "date" not in inquiry and inquiry["start_time"] == "18:30"
    assert not state.pending and not state.bookings


@pytest.mark.parametrize(
    "fragment,expected",
    [
        ("Kuues kuupäeval oktoobris 2026.", "2026-10-06"),
        ("6. oktoobris 2027.", "2027-10-06"),
    ],
)
def test_native_vad_terminal_year_word_does_not_erase_a_completed_date(
    make_state, fragment, expected
):
    state = make_state()
    for text in ("Soovin lauda broneerida", fragment, "Aastal."):
        state.observe_user_text(text, detected_language="et")
        reply = state.guard_reply("", [])
    assert state.booking_inquiry == {"date": expected}
    assert reply == COPY["et"]["time"]
    assert "name" not in (trusted_booking_response(state) or {})
    assert not state.pending and not state.bookings


def test_unowned_year_word_is_not_a_booking_detail_or_confirmation(make_state):
    state = make_state()
    state.observe_user_text("Aastal.", detected_language="et")
    assert not state.booking_inquiry
    assert "name" not in (trusted_booking_response(state) or {})
    assert not state.pending and not state.bookings


@pytest.mark.parametrize(
    "clock,expected", [("kell 18. 30", "18:30"), ("kolm veerand seitse õhtul", "18:45")]
)
def test_http_stepwise_clock_is_the_exact_time_in_the_delivered_recap(
    client, clock, expected
):
    session = start(client, "et")["session_id"]
    assert (
        COPY["et"]["date"]
        in turn(client, session, "Soovin lauda broneerida", language="et")["reply"]
    )
    assert COPY["et"]["time"] in turn(client, session, "Homme", language="et")["reply"]
    assert COPY["et"]["party"] in turn(client, session, clock, language="et")["reply"]
    result = turn(client, session, "Meid on neli", language="et")
    state = client.app.state.demo_sessions.sessions[session].tools
    recap_start = datetime.fromisoformat(state.pending["recap"]["start"])
    assert recap_start.strftime("%H:%M") == expected
    assert recap_start.date().isoformat() == tomorrow()
    assert result["recap_delivery_id"] and not result["booking_changes"]
    assert not state.bookings
    corrected = turn(
        client,
        session,
        "jah, aga kell 18. 70",
        language="et",
        receipt=result["recap_delivery_id"],
    )
    assert not corrected["booking_changes"]
    assert state.pending is None and not state.bookings
