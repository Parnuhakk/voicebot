"""Spoken English dates/times through HTTP, native hooks and consent guards."""

import asyncio
import base64
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
import pytest

from app.booking_response import trusted_booking_response
from app.providers.groq import GroqClient
from app.restaurant_call import COPY, parse_restaurant_request
from app.restaurant_dates import resolve_restaurant_date
from app.restaurant_times import parse_spoken_time
from tests.test_restaurant_http import AUTH, start, tomorrow

pytest_plugins = ["tests.test_restaurant_http", "tests.test_restaurant_conversation"]
NOW = datetime(2026, 10, 3, 12, tzinfo=ZoneInfo("Europe/Tallinn"))
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")


def ordinal(day):
    return str(day) + ("th" if 10 <= day % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th"))


@pytest.mark.parametrize("text", [
    "4th October", "4 October", "the fourth of October", "October fourth",
    "October the 4th", "October 4th, 2026", "4th Oct.", "Oct. 4th",
])
def test_english_named_dates_are_one_calendar_date(text):
    resolved = resolve_restaurant_date(text, NOW)
    assert resolved.value == "2026-10-04" and resolved.issue is None
    inquiry = parse_restaurant_request("table " + text + " at 6 pm for four", now=NOW)
    assert inquiry == {"date": "2026-10-04", "start_time": "18:00", "party_size": 4}


@pytest.mark.parametrize("day", range(1, 32))
def test_all_numeric_english_ordinals(day):
    resolved = resolve_restaurant_date(ordinal(day) + " October 2026", NOW)
    assert resolved.value == f"2026-10-{day:02d}" and resolved.issue is None


@pytest.mark.parametrize("text,day", [
    ("first", 1), ("second", 2), ("third", 3), ("twelfth", 12),
    ("twenty first", 21), ("twenty-second", 22), ("thirty first", 31),
])
def test_spoken_ordinals_are_not_trimmed_or_reduced_to_units(text, day):
    resolved = resolve_restaurant_date(text + " of October 2026", NOW)
    assert resolved.value == f"2026-10-{day:02d}" and resolved.issue is None


@pytest.mark.parametrize("month,name", list(enumerate(MONTHS, 1)))
def test_all_english_months(month, name):
    resolved = resolve_restaurant_date(f"4th {name} 2027", NOW)
    assert resolved.value == f"2027-{month:02d}-04" and resolved.issue is None


@pytest.mark.parametrize("text", ["31st February", "thirty second October", "forty fourth October", "4th or 5th October", "4th October and 5th October", "not 4th October"])
def test_invalid_or_conflicting_dates_cannot_become_a_selected_day(text):
    resolved = resolve_restaurant_date(text, NOW)
    assert resolved.value is None and resolved.issue


def test_may_permission_and_neighbouring_clock_are_not_year_or_date():
    assert resolve_restaurant_date("May I book a table?", NOW).issue is None
    request = parse_restaurant_request("table 4th October 18:00 for four", now=NOW)
    assert request == {"date": "2026-10-04", "start_time": "18:00", "party_size": 4}


@pytest.mark.parametrize("text,expected", [("12pm", "12:00"), ("11am", "11:00")])
def test_month_neighbouring_am_pm_clock_is_not_a_short_year(text, expected):
    request = parse_restaurant_request("table 4th October " + text + " for four", now=NOW)
    assert request == {"date": "2026-10-04", "start_time": expected, "party_size": 4}


@pytest.mark.parametrize("text", ["6 o clock", "6 o'clock", "six o’clock", "six oclock", "at six", "6:00"])
def test_twelve_hour_time_is_recognized_and_remembered_without_guessing(text):
    resolution = parse_spoken_time(text)
    assert not resolution.invalid
    assert resolution.candidates == ("06:00", "18:00") and resolution.value is None


@pytest.mark.parametrize("text,expected", [
    ("6 o clock in the evening", "18:00"), ("six o'clock pm", "18:00"),
    ("at six in the morning", "06:00"), ("6:30 pm", "18:30"),
    ("18:00", "18:00"), ("06:00", "06:00"), ("12 noon", "12:00"),
    ("at twenty-one", "21:00"), ("at twenty three", "23:00"),
    ("12 midnight", "00:00"), ("noon", "12:00"), ("midnight", "00:00"),
])
def test_explicit_times(text, expected):
    resolution = parse_spoken_time(text)
    assert resolution.value == expected and not resolution.invalid


@pytest.mark.parametrize("text,expected", [("pm", "18:00"), ("in the evening", "18:00"), ("am", "06:00"), ("in the morning", "06:00")])
def test_daypart_answer_resolves_previous_hour(text, expected):
    previous = parse_restaurant_request("six o'clock", {"date": "2026-10-04", "party_size": 4}, now=NOW)
    resolved = parse_restaurant_request(text, previous, now=NOW)
    assert resolved == {"date": "2026-10-04", "party_size": 4, "start_time": expected}


@pytest.mark.parametrize("text", ["25 o'clock", "6:90 pm", "13 pm", "6 am in the evening", "at six or seven", "not at six", "at twenty four", "at twenty-four", "18:999", "at 100", "at -6", "six o'clock in the morning and at night"])
def test_invalid_time_clears_previous_selection(text):
    result = parse_restaurant_request(text, {"date": "2026-10-04", "party_size": 4, "start_time": "18:00"}, now=NOW)
    assert "start_time" not in result and (result.get("time_invalid") or result.get("time_candidates"))


@pytest.mark.parametrize("text", ["not pm", "not in the evening", "morning or evening", "not noon", "morning and night"])
def test_negated_or_conflicting_daypart_does_not_select_a_time(text):
    resolved = parse_spoken_time(text, pending=("06:00", "18:00"))
    assert resolved.value is None and (resolved.invalid or resolved.candidates)


def test_bare_number_depends_on_the_question_and_time_numbers_are_not_guest_counts():
    previous = {"date": "2026-10-04"}
    time = parse_restaurant_request("six", previous, now=NOW, expected_field="time")
    assert "party_size" not in time and time["time_candidates"] == ("06:00", "18:00")
    party = parse_restaurant_request("six", previous, now=NOW, expected_field="party")
    assert party["party_size"] == 6 and "time_candidates" not in party


@pytest.mark.parametrize("audio", [False, True])
def test_complete_http_followups_keep_date_time_and_party_without_early_booking(client, audio):
    assert client.get("/api/status").json()["capabilities"]["restaurant_english_dates_times_ready"]
    day = datetime.fromisoformat(tomorrow())
    date_text = f"{ordinal(day.day)} {MONTHS[day.month - 1]}"
    session_id = start(client, "en")["session_id"]
    transcript = ""
    provider = GroqClient("fixture", transport=httpx.MockTransport(
        lambda _: httpx.Response(200, json={"text": transcript, "language": "english"})
    ))
    if audio:
        client.app.state.stack["stt"] = provider
    try:
        for text, expected in [
            ("I'd like a table for four", COPY["en"]["date"]),
            (date_text, COPY["en"]["time"]),
            ("6 o clock", COPY["en"]["ambiguous_time"]),
            ("in the evening", None),
        ]:
            transcript = text
            response = client.post("/api/turn", headers=AUTH, json={
                "session_id": session_id, "language": "en",
                **({"audio_b64": base64.b64encode(b"fixture-audio").decode()} if audio else {"text": text}),
            })
            assert response.status_code == 200, response.text
            result = response.json()
            assert result["warnings"] == [] and not result["fallback_used"]
            assert result["input_status"] == ("recognized" if audio else "typed")
            assert result["booking_ids"] == [] and result["booking_changes"] == []
            if expected:
                assert result["reply"] == expected and result["tools_used"] == 0
            else:
                assert result["recap_delivery_id"] and "6:00 PM" in result["reply"]
        state = client.app.state.demo_sessions.sessions[session_id].tools
        assert state.pending["recap"]["party_size"] == 4
        assert state.booking_inquiry["date"] == tomorrow()
        assert state.booking_inquiry["start_time"] == "18:00"
    finally:
        provider.close()


def test_ambiguous_time_cannot_be_overridden_by_model_arguments(make_state):
    async def run():
        state = make_state("en")
        state.observe_user_text("table tomorrow for four", language="en")
        state.guard_reply("", [])
        state.observe_user_text("6 o'clock", language="en")
        assert state.guard_reply("", []) == COPY["en"]["ambiguous_time"]
        result = await state.dispatch("plan_restaurant_reservation", {"date": tomorrow(), "start_time": "18:00", "party_size": 4})
        assert result == {"error": "clarification_required"}
        assert not state.holds and not state.bookings
        state.observe_user_text("pm", language="en")
        response = trusted_booking_response(state)
        assert response["arguments"]["start_time"] == "18:00"
    asyncio.run(run())


def test_native_final_turn_hook_remembers_english_date_and_time(make_state):
    agents = pytest.importorskip("livekit.agents")
    from app.worker import TelephoneAgent

    async def run():
        state = make_state("en")
        agent = TelephoneAgent(state)
        day = datetime.fromisoformat(tomorrow())
        for text in ["table for four", f"{ordinal(day.day)} {MONTHS[day.month - 1]}", "six o'clock", "pm"]:
            message = agents.llm.ChatMessage(role="user", content=[text])
            agent._detected_language = "en"
            await agent.on_user_turn_completed(agents.llm.ChatContext(), message)
            state.guard_reply("", [])
        assert state.booking_inquiry == {"date": tomorrow(), "party_size": 4, "start_time": "18:00"}
        assert not state.holds and not state.bookings
    asyncio.run(run())
