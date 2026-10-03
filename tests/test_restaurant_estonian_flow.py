"""Natural Estonian details retain explicit booking and consent boundaries."""

import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.booking_response import trusted_booking_response
from app.restaurant_call import COPY, parse_restaurant_request
from app.restaurant_times import parse_spoken_time
from tests.test_restaurant_conversation import make_state, tomorrow


@pytest.mark.parametrize("text,expected", [
    ("õhtul kell seitse", "19:00"),
    ("kell seitse õhtul", "19:00"),
    ("pool kaheksa õhtul", "19:30"),
    ("veerand kaheksa õhtul", "19:15"),
    ("kolmveerand kaheksa õhtul", "19:45"),
    ("pool kaheksa hommikul", "07:30"),
    ("pool üks päeval", "12:30"),
    ("kell üheksateist", "19:00"),
    ("kell kakskümmend üks", "21:00"),
    ("kell 07:30", "07:30"),
    ("kell 14.00.", "14:00"),
])
def test_estonian_clock_expressions(text, expected):
    result = parse_spoken_time(text)
    assert result.value == expected and not result.invalid


@pytest.mark.parametrize("text,issue", [
    ("kell seitse", "ambiguous_time"),
    ("pool kaheksa", "ambiguous_time"),
    ("kell seitse või kell kaheksa õhtul", "invalid_time"),
    ("kell 25", "invalid_time"),
    ("kell 19:61", "invalid_time"),
    ("kell 19:3", "invalid_time"),
    ("kell 123", "invalid_time"),
    ("kell 19:00:30", "invalid_time"),
])
def test_unclear_time_clears_previous_time(text, issue):
    request = parse_restaurant_request(text, {
        "date": "2026-10-04", "start_time": "14:00", "party_size": 4,
    })
    if issue == "ambiguous_time":
        assert request.get("time_candidates")
    else:
        assert request.get("time_invalid")
    assert "start_time" not in request
    corrected = parse_restaurant_request("õhtul kell seitse", request)
    assert corrected["start_time"] == "19:00"
    assert "time_candidates" not in corrected and "time_invalid" not in corrected


@pytest.mark.parametrize("detail", [
    "meid on neli", "meid tuleb neli", "tuleme neljakesi", "oleme neljakesi",
])
def test_natural_estonian_booking_followups(make_state, detail):
    state = make_state()
    for utterance, question in [
        ("Sooviksin lauda broneerida", "date"),
        ("Homme", "time"),
        ("Õhtul kell seitse", "party"),
    ]:
        state.observe_user_text(utterance, language="english")
        assert state.language == "et"
        assert trusted_booking_response(state) == {"content": COPY["et"][question]}
        state.guard_reply("", [])
    state.observe_user_text(detail, language="english")
    assert state.language == "et"
    response = trusted_booking_response(state)
    assert response["name"] == "plan_restaurant_reservation"
    assert response["arguments"] == {"date": tomorrow(), "start_time": "19:00", "party_size": 4}
    assert state.bookings == set()


def test_clock_and_date_words_do_not_become_guests():
    now = datetime(2026, 10, 3, 12, tzinfo=ZoneInfo("Europe/Tallinn"))
    inquiry = parse_restaurant_request("Laud neljaks oktoobriks kell seitse õhtul", now=now)
    assert inquiry == {"date": "2026-10-04", "start_time": "19:00"}
    assert parse_restaurant_request("Tegelikult viis", {**inquiry, "party_size": 4})["party_size"] == 5


@pytest.mark.parametrize("repair", ["Korda palun", "Ei saanud aru", "See on segane"])
def test_repair_repeats_the_actual_question(make_state, repair):
    state = make_state()
    state.observe_user_text("Soovin lauda broneerida")
    assert state.guard_reply("", []) == COPY["et"]["date"]
    state.observe_user_text(repair)
    assert trusted_booking_response(state) == {"content": COPY["et"]["date"]}
    assert state.pending is None


def test_unclear_clock_cannot_be_planned_by_model(make_state):
    async def run():
        state = make_state()
        state.observe_user_text("Soovin homme lauda neljale kell seitse")
        assert trusted_booking_response(state) == {"content": COPY["et"]["ambiguous_time"]}
        result = await state.dispatch("plan_restaurant_reservation", {
            "date": tomorrow(), "start_time": "19:00", "party_size": 4,
        })
        assert result == {"error": "clarification_required"}
        assert state.guard_reply("Laud on broneeritud", [result]) == COPY["et"]["ambiguous_time"]
        assert state.pending is None and state.bookings == set()
    asyncio.run(run())


def test_decline_discards_inquiry_without_creating_or_cancelling_booking(make_state):
    state = make_state()
    state.observe_user_text("Soovin homme kell 19 lauda neljale")
    assert state.booking_inquiry["party_size"] == 4
    state.observe_user_text("Ei, aitäh")
    assert state.booking_inquiry is None
    assert state.bookings == set()
    state.observe_user_text("Viis")
    assert trusted_booking_response(state) == {"content": COPY["et"]["information_unknown"]}


def test_natural_correction_requires_new_recap_before_confirmation(make_state):
    async def run():
        state = make_state()
        state.observe_user_text("Soovin homme kell 14 lauda, meid on neli")
        response = trusted_booking_response(state)
        result = await state.dispatch(response["name"], response["arguments"])
        assert state.mark_recap_delivered(result["hold_id"])
        state.observe_user_text("Tegelikult viis")
        assert state.pending is None and state.bookings == set()
        response = trusted_booking_response(state)
        assert response["arguments"]["party_size"] == 5
        result = await state.dispatch(response["name"], response["arguments"])
        recap = state.guard_reply("", [result])
        assert "5 inimesele" in recap
        assert "minutit ja on nimele" in recap
        state.observe_user_text("Jah, kinnitan")
        assert not state.pending or not state.pending["approved"]
        assert state.bookings == set()
    asyncio.run(run())
