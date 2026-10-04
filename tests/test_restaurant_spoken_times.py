"""Requested clock facts and clarification across ET/EN/RU; no live providers."""

import asyncio
import base64
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.booking_response import trusted_booking_response
from app.restaurant_call import COPY, parse_restaurant_request
from app.restaurant_times import TIME_INPUT_EXAMPLES, parse_spoken_time
from tests.test_restaurant_http import AUTH, start, turn

pytest_plugins = ["tests.test_restaurant_conversation", "tests.test_restaurant_http"]


NOW = datetime(2026, 10, 3, 12, tzinfo=ZoneInfo("Europe/Tallinn"))


@pytest.mark.parametrize(
    "text,expected",
    [
        ("at 6 o clock in the evening", "18:00"),
        ("at 6 o'clock PM", "18:00"),
        ("at six o’clock in the evening", "18:00"),
        ("at six oclock in the morning", "06:00"),
        ("6pm", "18:00"),
        ("at 6 p.m.", "18:00"),
        ("at six thirty PM", "18:30"),
        ("at six oh five PM", "18:05"),
        ("at twenty-one forty-five", "21:45"),
        ("at half past six in the evening", "18:30"),
        ("half six in the evening", "18:30"),
        ("at a quarter past eight in the evening", "20:15"),
        ("a quarter to six in the evening", "17:45"),
        ("ten past six in the evening", "18:10"),
        ("twenty to seven in the evening", "18:40"),
        ("at noon", "12:00"),
        ("at midnight", "00:00"),
        ("at 12 am", "00:00"),
        ("at 12 pm", "12:00"),
        ("kell 6 õhtul", "18:00"),
        ("kella kuus õhtul", "18:00"),
        ("kell kuus hommikul", "06:00"),
        ("kell kuus kolmkümmend õhtul", "18:30"),
        ("kell kuus ja kolmkümmend õhtul", "18:30"),
        ("kell kaheksateist kolmkümmend", "18:30"),
        ("kell kakskümmend üks nelikümmend viis", "21:45"),
        ("kell kakskümmendüks kolmkümmend", "21:30"),
        ("pool seitse õhtul", "18:30"),
        ("veerand seitse õhtul", "18:15"),
        ("kolmveerand seitse õhtul", "18:45"),
        ("pool üks öösel", "00:30"),
        ("kolmveerand üks päeval", "12:45"),
        ("kell keskpäeval", "12:00"),
        ("keskööl", "00:00"),
        ("в 6 вечера", "18:00"),
        ("в шесть вечера", "18:00"),
        ("в шесть утра", "06:00"),
        ("в шесть часов вечера", "18:00"),
        ("в шесть тридцать вечера", "18:30"),
        ("в шесть часов тридцать минут вечера", "18:30"),
        ("в восемнадцать тридцать", "18:30"),
        ("полседьмого вечера", "18:30"),
        ("пол седьмого вечера", "18:30"),
        ("половина седьмого вечера", "18:30"),
        ("четверть седьмого вечера", "18:15"),
        ("без четверти семь вечера", "18:45"),
        ("без десяти семь вечера", "18:50"),
        ("без двадцати пяти минут семь вечера", "18:35"),
        ("в полдень", "12:00"),
        ("в полночь", "00:00"),
        ("в час дня", "13:00"),
        ("в час ночи", "01:00"),
        ("18:30", "18:30"),
        ("at 06:05", "06:05"),
        ("kell 00.15", "00:15"),
    ],
)
def test_spoken_and_numeric_clocks_keep_exact_requested_time(text, expected):
    selection = parse_spoken_time(text)
    assert selection and selection.value == expected
    assert not selection.invalid and selection.candidates is None


@pytest.mark.parametrize(
    "text,am,pm",
    [
        ("at 6 o clock", "06:00", "18:00"),
        ("at six o’clock", "06:00", "18:00"),
        ("kell kuus", "06:00", "18:00"),
        ("в шесть часов", "06:00", "18:00"),
        ("at half past six", "06:30", "18:30"),
        ("pool seitse", "06:30", "18:30"),
        ("полседьмого", "06:30", "18:30"),
        ("veerand üks", "00:15", "12:15"),
        ("at 12", "00:00", "12:00"),
        ("at 6:30", "06:30", "18:30"),
    ],
)
def test_ambiguous_clocks_offer_both_periods_instead_of_guessing(text, am, pm):
    selection = parse_spoken_time(text)
    assert selection and selection.candidates == (am, pm)
    assert selection.value is None and not selection.invalid


@pytest.mark.parametrize(
    "text",
    [
        "at 25:00",
        "kell 18:70",
        "в 24:00",
        "at 6 75 pm",
        "at six sixty pm",
        "kell kuus kuuskümmend õhtul",
        "в шесть семьдесят вечера",
        "at 18:300",
        "kell 18:3",
        "at 100:00",
        "at 18 am",
        "at 13 pm",
        "at 13:00 pm",
        "kell 18 hommikul",
        "at six in the morning or evening",
        "at six or seven in the evening",
        "at 18:00 or at 19:00",
        "at six in the evening or seven",
        "between six and seven",
    ],
)
def test_invalid_conflicting_and_alternative_times_need_clarification(text):
    selection = parse_spoken_time(text)
    assert selection and selection.invalid and selection.value is None


@pytest.mark.parametrize(
    "text", ["2026-10-06", "06.10.2026", "for six", "six people", "18", "six"]
)
def test_dates_party_counts_and_unprompted_bare_numbers_are_not_clocks(text):
    assert parse_spoken_time(text) is None


@pytest.mark.parametrize(
    "text", ["six", "6", "six thirty", "шесть", "kuus", "kuus kolmkümmend"]
)
def test_bare_numbers_only_select_time_after_a_time_question(text):
    assert parse_spoken_time(text) is None
    parsed = parse_spoken_time(text, allow_bare=True)
    assert parsed is not None and parsed.candidates is not None


@pytest.mark.parametrize(
    "language,utterance,period,expected_question",
    [
        (
            "en",
            "I'd like a table for four tomorrow at 6 o clock",
            "in the evening",
            "Do you mean AM or PM?",
        ),
        (
            "et",
            "Soovin homme lauda neljale kell kuus",
            "õhtul",
            "Kas mõtlete hommikul või õhtul?",
        ),
        (
            "ru",
            "Столик на четверых завтра в шесть часов",
            "вечером",
            "Вы имеете в виду утром или вечером?",
        ),
    ],
)
def test_time_clarification_retains_date_and_party_and_blocks_actions(
    make_state, language, utterance, period, expected_question
):
    state = make_state(language)
    state.observe_user_text(utterance, language=language)
    before = state.booking_inquiry
    assert before["party_size"] == 4 and before["time_candidates"] == ("06:00", "18:00")
    assert "start_time" not in before
    assert trusted_booking_response(state) == {"content": expected_question}
    result = asyncio.run(
        state.dispatch(
            "plan_restaurant_reservation",
            {"date": before["date"], "start_time": "18:00", "party_size": 4},
        )
    )
    assert result["error"] == "clarification_required" and state.pending is None
    state.observe_user_text(period, language=language)
    assert state.booking_inquiry == {
        "date": before["date"],
        "party_size": 4,
        "start_time": "18:00",
    }
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": state.booking_inquiry,
    }


def test_time_and_party_counts_stay_separate_and_invalid_corrections_clear_old_time():
    inquiry = parse_restaurant_request(
        "A table tomorrow at six o'clock in the evening for four", now=NOW
    )
    assert inquiry == {"date": "2026-10-04", "start_time": "18:00", "party_size": 4}
    corrected = parse_restaurant_request("at 25:00", inquiry, now=NOW)
    assert "start_time" not in corrected and corrected["time_invalid"] is True
    assert corrected["party_size"] == 4 and corrected["date"] == inquiry["date"]
    assert parse_restaurant_request("at 19:30", corrected, now=NOW) == {
        "date": inquiry["date"],
        "party_size": 4,
        "start_time": "19:30",
    }


@pytest.mark.parametrize(
    "language,time_reply",
    [("en", "six thirty"), ("et", "pool seitse"), ("ru", "полседьмого")],
)
def test_time_reply_does_not_become_guest_count(make_state, language, time_reply):
    state = make_state(language)
    state.observe_user_text("table tomorrow", language=language)
    state.observe_user_text(time_reply, language=language)
    assert state.clarification == "ambiguous_time"
    assert "party_size" not in state.booking_inquiry
    state.observe_user_text("pm", language=language)
    assert state.booking_inquiry["start_time"] == "18:30"
    state.observe_user_text("four", language=language)
    assert state.booking_inquiry["party_size"] == 4


@pytest.mark.parametrize(
    "utterance",
    [
        "Book a table tomorrow at 7.05 pm for four",
        "Book a table tomorrow at 7:05 pm for four",
    ],
)
def test_small_clock_minutes_are_not_an_ambiguous_english_date(make_state, utterance):
    state = make_state("en")
    state.observe_user_text(utterance, language="en")
    assert state.clarification is None
    assert state.booking_inquiry["start_time"] == "19:05"


@pytest.mark.parametrize(
    "language,initial_request,period,expected_question",
    [
        ("en", "A table for four tomorrow at 6 o clock", "pm", "Do you mean AM or PM?"),
        (
            "et",
            "Soovin homme lauda neljale pool seitse",
            "õhtul",
            "Kas mõtlete hommikul või õhtul?",
        ),
        (
            "ru",
            "Столик на четверых завтра полседьмого",
            "вечером",
            "Вы имеете в виду утром или вечером?",
        ),
    ],
)
def test_http_spoken_time_clarification_and_exact_recap_without_model(
    client, language, initial_request, period, expected_question
):
    session = start(client, language)
    first = turn(client, session["session_id"], initial_request, language=language)
    assert first["reply"] == client.provider.spoken[-1] == expected_question
    assert first["booking_changes"] == [] and not first.get("recap_delivery_id")
    second = turn(client, session["session_id"], period, language=language)
    expected = "18:00" if language == "en" else "18:30"
    state = client.app.state.demo_sessions.sessions[session["session_id"]].tools
    assert second["recap_delivery_id"]
    assert (
        datetime.fromisoformat(state.pending["recap"]["start"]).strftime("%H:%M")
        == expected
    )
    assert state.pending["recap"]["party_size"] == 4
    assert second["reply"] == state.render_recap()
    assert second["booking_changes"] == []


def test_public_clock_examples_are_parsed_in_each_language(client):
    examples = client.get("/api/public/restaurant").json()["booking_time_examples"]
    assert examples == TIME_INPUT_EXAMPLES
    for phrases in examples.values():
        parsed = [parse_spoken_time(phrase) for phrase in phrases]
        assert all(clock is not None for clock in parsed)
        assert [clock.value for clock in parsed if clock is not None] == [
            "18:00",
            "18:30",
            "18:30",
        ]


def test_unicode_time_reply_and_period_only_response_keep_booking_context(make_state):
    state = make_state("et")
    state.observe_user_text("Soovin homme lauda neljale kell kuus", language="et")
    state.observe_user_text(unicodedata.normalize("NFD", "õhtul"), language="et")
    assert state.booking_inquiry["start_time"] == "18:00"
    state = make_state("en")
    state.observe_user_text("A table for four tomorrow", language="en")
    state.observe_user_text("in the evening", language="en")
    assert trusted_booking_response(state) == {"content": COPY["en"]["invalid_time"]}
    assert "start_time" not in state.booking_inquiry


@pytest.mark.parametrize(
    "text,expected",
    [
        ("at 1800", "18:00"),
        ("at 1830", "18:30"),
        ("kell 1800", "18:00"),
        ("kella 0130", "01:30"),
        ("в 1830", "18:30"),
        ("к 1230", "12:30"),
    ],
)
def test_compact_transcribed_clocks_require_explicit_time_context(text, expected):
    selection = parse_spoken_time(text)
    assert selection and selection.value == expected
    assert selection.candidates is None and not selection.invalid


@pytest.mark.parametrize(
    "text",
    [
        "at 2460",
        "kell 1870",
        "в 2400",
        "at 1800 am",
        "at 1800 pm",
        "at 1800 or 1900",
        "at 1800 or at 1900",
        "between 1800 and 1900",
        "from 1800 to 1900",
        "not at 1800",
        "mitte kell 1800",
        "не в 1800",
        "around at 1800",
        "umbes kell 1800",
        "примерно в 1800",
        "at 1800 guests",
        "at 1800 30",
        "at 18000",
        "at 1800.5",
    ],
)
def test_compact_invalid_approximate_or_conflicting_clocks_never_select(text):
    selection = parse_spoken_time(text)
    assert selection is None or selection.invalid and selection.value is None


@pytest.mark.parametrize(
    "text",
    ["1800", "2026", "2026-10-06", "06.10.2026", "1800 guests", "for 1800 people"],
)
def test_unprompted_compact_numbers_dates_and_guest_counts_are_not_clocks(text):
    assert parse_spoken_time(text) is None


@pytest.mark.parametrize("text,expected", [("1800", "18:00"), ("0130", "01:30")])
def test_compact_bare_clock_requires_a_time_question(text, expected):
    assert parse_spoken_time(text) is None
    assert parse_spoken_time(text, allow_bare=True).value == expected


@pytest.mark.parametrize(
    "language,text",
    [
        ("en", "Please reserve a table tomorrow at 1800 for two guests total."),
        ("et", "Soovin homme lauda kahele inimesele kell 1800."),
        ("ru", "Забронируйте столик завтра в 1800 для двух гостей."),
    ],
)
def test_compact_request_preserves_date_and_total_party(make_state, language, text):
    state = make_state(language)
    state.observe_user_text(text, language=language)
    inquiry = state.booking_inquiry
    assert inquiry["start_time"] == "18:00" and inquiry["party_size"] == 2
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": inquiry,
    }
    assert state.pending is None and not state.bookings


@pytest.mark.parametrize(
    "text", ["at 1800 and 1900", "kell 1800 ja 1900", "в 1800 и 1900"]
)
def test_coordinated_compact_clocks_require_clarification(text):
    selection = parse_spoken_time(text)
    assert selection and selection.invalid and selection.value is None


@pytest.mark.parametrize(
    "language,text",
    [
        ("en", "Reserve a table tomorrow at 1800 and 1900 for two guests."),
        ("et", "Soovin homme lauda kahele kell 1800 ja 1900."),
        ("ru", "Столик завтра в 1800 и 1900 для двух гостей."),
    ],
)
def test_coordinated_compact_request_cannot_plan_a_chosen_clock(
    make_state, language, text
):
    state = make_state(language)
    state.observe_user_text(text, language=language)
    assert state.booking_inquiry["party_size"] == 2
    assert state.booking_inquiry["date"] and "start_time" not in state.booking_inquiry
    assert trusted_booking_response(state) == {
        "content": COPY[language]["invalid_time"]
    }
    assert state.pending is None and not state.bookings


@pytest.mark.parametrize("separator", ["-", "–", "—", "/"])
@pytest.mark.parametrize(
    "prefix,allow_bare", [("at ", False), ("kell ", False), ("в ", False), ("", True)]
)
def test_compact_separator_range_never_selects_either_endpoint(
    separator, prefix, allow_bare
):
    selection = parse_spoken_time(
        prefix + "1800" + separator + "1900", allow_bare=allow_bare
    )
    assert selection and selection.invalid and selection.value is None


@pytest.mark.parametrize("separator", ["-", "–", "—", "/"])
@pytest.mark.parametrize("suffix", [" o'clock", "o'clock", "часов"])
def test_compact_range_with_clock_suffix_cannot_select_the_last_endpoint(
    separator, suffix
):
    selection = parse_spoken_time("1800" + separator + "1900" + suffix)
    assert selection and selection.invalid and selection.value is None


@pytest.mark.parametrize("separator", ["-", "–", "—", "/"])
@pytest.mark.parametrize(
    "language,template",
    [
        ("en", "Reserve a table tomorrow for four at {clock}."),
        ("et", "Soovin homme lauda neljale kell {clock}."),
        ("ru", "Столик завтра на четверых в {clock}."),
    ],
)
def test_compact_separator_booking_request_preserves_details_without_a_hold(
    client, language, template, separator
):
    session = start(client, language)["session_id"]
    result = turn(
        client,
        session,
        template.format(clock="1800" + separator + "1900"),
        language=language,
    )
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.booking_inquiry["party_size"] == 4 and state.booking_inquiry["date"]
    assert "start_time" not in state.booking_inquiry
    assert result["reply"] == COPY[language]["invalid_time"]
    assert result["booking_changes"] == [] and result["recap_delivery_id"] is None
    assert state.pending is None and not state.holds and not state.bookings


@pytest.mark.parametrize(
    "clock",
    ["1800 hours", "18:00 hours", "eighteen hours", "18 hours", "six o'clock hours PM"],
)
def test_clock_unit_hours_cannot_steal_the_initial_booking(make_state, clock):
    state = make_state("et")
    state.observe_user_text(
        f"Please reserve a table tomorrow at {clock} for two guests total.",
        detected_language="en",
    )
    assert state.language == "en"
    assert state.booking_inquiry is not None
    assert state.booking_inquiry["start_time"] == "18:00"
    assert state.booking_inquiry["party_size"] == 2 and state.booking_inquiry["date"]
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": state.booking_inquiry,
    }
    assert state.pending is None and not state.holds and not state.bookings


@pytest.mark.parametrize(
    "clock",
    [
        "2500 hours",
        "1860 hours",
        "1800 hours and 1900 hours",
        "1800 hours or 1900 hours",
        "18 hours or 19 hours",
        "eighteen hours or nineteen hours",
        "18 hours or six hours",
    ],
)
def test_invalid_clock_units_still_clarify_without_a_hold(make_state, clock):
    state = make_state("en")
    state.observe_user_text(
        f"Reserve a table tomorrow at {clock} for two guests.", detected_language="en"
    )
    assert (
        state.booking_inquiry is not None and "start_time" not in state.booking_inquiry
    )
    assert state.clarification == "invalid_time"
    assert trusted_booking_response(state) == {"content": COPY["en"]["invalid_time"]}
    assert state.pending is None and not state.holds and not state.bookings


@pytest.mark.parametrize(
    "clock",
    ["18 hours thirty hours", "eighteen hours thirty hours", "18 hours and 19 hours"],
)
def test_repeated_hours_units_never_expose_a_malformed_plan(make_state, clock):
    state = make_state("en")
    state.observe_user_text(
        f"Reserve a table tomorrow at {clock} for two guests.", detected_language="en"
    )
    decision = trusted_booking_response(state) or {}
    assert decision.get("name") != "plan_restaurant_reservation"
    assert state.pending is None and not state.holds and not state.bookings


@pytest.mark.parametrize(
    "clock",
    [
        "six PM hours or seven hours",
        "six PM hours or seven",
        "at six PM hours or seven hours",
        "6 PM hours or 7 hours",
        "6 PM hours or 7",
    ],
)
def test_unparsed_suffix_alternatives_never_expose_the_first_time(make_state, clock):
    state = make_state("en")
    state.observe_user_text(
        f"Reserve a table tomorrow {clock} for two guests.", detected_language="en"
    )
    decision = trusted_booking_response(state) or {}
    assert decision.get("name") != "plan_restaurant_reservation"
    assert state.pending is None and not state.holds and not state.bookings


@pytest.mark.parametrize("clock", ["6 hours", "six hours"])
def test_ambiguous_clock_units_ask_am_pm_instead_of_opening_hours(make_state, clock):
    state = make_state("en")
    state.observe_user_text(
        f"Reserve a table tomorrow at {clock} for two guests.", detected_language="en"
    )
    assert state.booking_inquiry is not None
    assert state.booking_inquiry["time_candidates"] == ("06:00", "18:00")
    assert trusted_booking_response(state) == {"content": COPY["en"]["ambiguous_time"]}
    assert not state.holds and not state.bookings


@pytest.mark.parametrize(
    "text,topic",
    [
        ("What are your hours?", "hours"),
        ("Are you open tomorrow at 1800 hours?", "hours"),
        ("What are your opening hours tomorrow at 18:00 hours?", "hours"),
        ("What are your kitchen hours tomorrow at eighteen hours?", "kitchen"),
        ("How long can we keep a table, for how many hours?", "duration"),
    ],
)
def test_real_hours_and_duration_questions_survive_clock_unit_filter(text, topic):
    from app.restaurant_answers import match_question

    question = match_question(text)
    assert question is not None and topic in question.topics


UNRESOLVED_CLOCK_UNIT_CHOICES = [
    "six PM; or 1900 hours",
    "1800 hours and 19 hours",
    "18 hours thirty hours",
]


@pytest.mark.parametrize("clock", UNRESOLVED_CLOCK_UNIT_CHOICES)
def test_unresolved_clock_unit_choices_require_explicit_native_clarification(
    make_state, clock
):
    state = make_state("en")
    state.observe_user_text(
        f"Reserve a table tomorrow at {clock} for two guests.",
        is_final=True,
        detected_language="en",
    )
    assert state.clarification == "invalid_time"
    assert trusted_booking_response(state) == {"content": COPY["en"]["invalid_time"]}
    assert state.booking_inquiry is not None
    assert "start_time" not in state.booking_inquiry
    assert state.pending is None and not state.holds and not state.bookings


@pytest.mark.parametrize("clock", UNRESOLVED_CLOCK_UNIT_CHOICES)
def test_unresolved_clock_unit_audio_cannot_plan_the_first_choice(client, clock):
    session = start(client, "auto")["session_id"]
    client.provider.transcript = f"Reserve a table tomorrow at {clock} for two guests."
    response = client.post(
        "/api/turn",
        headers=AUTH,
        json={
            "session_id": session,
            "audio_b64": base64.b64encode(b"RIFF-synthetic-fixture").decode(),
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["language"] == "en"
    assert result["reply"] == client.provider.spoken[-1] == COPY["en"]["invalid_time"]
    assert result["booking_changes"] == [] and not result["recap_delivery_id"]
    assert client.provider.recognized_languages == ["auto"]
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.booking_inquiry is not None
    assert "start_time" not in state.booking_inquiry
    assert state.pending is None and not state.holds and not state.bookings
