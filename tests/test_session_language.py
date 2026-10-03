"""The first clear caller turn selects a language for the owned session."""

import asyncio
import base64

import pytest

from app.booking_response import trusted_booking_response
from app.languages import CONSENT
from app.providers.transcription import Transcription
from app.restaurant_call import COPY
from tests.test_restaurant_conversation import tomorrow
from tests.test_restaurant_http import AUTH, start

pytest_plugins = ["tests.test_restaurant_http", "tests.test_restaurant_conversation"]

OPENERS = {
    "et": "Tere! Soovin lauda broneerida.",
    "en": "Hi! I would like to book a table.",
    "ru": "Здравствуйте! Я хочу забронировать столик.",
}


@pytest.mark.parametrize("initial", ["et", "en", "ru"])
@pytest.mark.parametrize("selected", ["et", "en", "ru"])
def test_first_clear_turn_selects_language_despite_initial_voice(
    make_state, initial, selected
):
    state = make_state(initial)
    assert not state.language_locked
    state.observe_user_text(OPENERS[selected], detected_language=initial)
    assert state.language == selected and state.language_locked
    assert trusted_booking_response(state) == {"content": COPY[selected]["date"]}
    for text, metadata in [
        ("Mari Näidis", "et"),
        ("4", "ru"),
        ("OK", "en"),
        ("Tere", "et"),
    ]:
        state.observe_user_text(text, detected_language=metadata)
        assert state.language == selected
        assert f"Reply only in {selected}" in state.conversation_instructions


@pytest.mark.parametrize("weak", ["", "4", "14:00", "OK", "Demo Teine"])
def test_weak_or_rejected_first_input_does_not_choose_language(make_state, weak):
    state = make_state()
    state.observe_user_text(weak, detected_language="english")
    assert not state.language_locked and state.language == "et"
    state.observe_user_text("Hello", is_final=False, detected_language="english")
    assert not state.language_locked
    state.observe_user_text("Hello", unsupported=True, detected_language="finnish")
    assert not state.language_locked
    state.observe_user_text(OPENERS["ru"], detected_language="russian")
    assert state.language_locked and state.language == "ru"


def test_english_booking_details_keep_language_and_values(make_state):
    state = make_state()
    for text, metadata, question in [
        (OPENERS["en"], "et", "date"),
        ("Tomorrow", "ru", "time"),
        ("At six o'clock", "et", "ambiguous_time"),
        ("In the evening", "et", "party"),
    ]:
        state.observe_user_text(text, detected_language=metadata)
        assert state.language == "en"
        assert trusted_booking_response(state) == {"content": COPY["en"][question]}
        state.guard_reply("", [])
    state.observe_user_text("Four", detected_language="russian")
    result = trusted_booking_response(state)
    assert result["arguments"] == {
        "date": tomorrow(),
        "start_time": "18:00",
        "party_size": 4,
    }
    assert state.language == "en" and state.bookings == set()


def test_only_explicit_language_request_changes_a_selected_language(make_state):
    state = make_state()
    state.observe_user_text(OPENERS["en"])
    state.observe_user_text(
        "Milline on menüü?", detected_language="estonian", language="et"
    )
    assert state.language == "en"
    answer = trusted_booking_response(state)["content"]
    assert answer.startswith(state.information_reply("menu"))
    assert answer.endswith(COPY["en"]["date"])
    state.observe_user_text("Please speak Russian", detected_language="english")
    assert state.language_locked and state.language == "ru"
    state.observe_user_text("Thank you", detected_language="english")
    assert state.language == "ru"


def test_foreign_confirmation_does_not_switch_language_or_confirm(make_state):
    async def run():
        state = make_state()
        state.observe_user_text("Hi! Book a table tomorrow at 2 pm for four.")
        response = trusted_booking_response(state)
        held = await state.dispatch(response["name"], response["arguments"])
        assert state.mark_recap_delivered(held["hold_id"])
        state.observe_user_text(CONSENT["et"], detected_language="estonian")
        assert state.language == "en"
        result = await state.dispatch(
            "confirm_slot_booking", {"hold_id": held["hold_id"]}
        )
        assert result.get("error") and state.bookings == set()

    asyncio.run(run())


def test_explicit_switch_preserves_details_and_asks_next_question_in_new_language(
    make_state,
):
    state = make_state()
    state.observe_user_text("Hi! I'd like a table tomorrow at 2 pm.")
    previous = state.booking_inquiry
    state.observe_user_text("Please speak Russian")
    assert state.booking_inquiry == previous and state.language == "ru"
    assert trusted_booking_response(state) == {"content": COPY["ru"]["party"]}
    assert state.pending is None and not state.bookings


@pytest.mark.parametrize(
    "text", ["Hi", "I didn't understand", "Please repeat that", "This is confusing"]
)
def test_first_english_social_turn_can_select_english(make_state, text):
    state = make_state()
    state.observe_user_text(text)
    assert state.language == "en" and state.language_locked


@pytest.mark.parametrize(
    "text", ["Do the dishes contain nuts?", "Do the rooms have Wi-Fi? Two adults."]
)
def test_first_english_do_the_question_selects_language_without_a_hint(
    make_state, text
):
    state = make_state()
    assert state.language == "et" and not state.language_locked
    state.observe_user_text(text)
    assert state.language == "en" and state.language_locked
    state.observe_user_text("14:00", detected_language="estonian")
    assert state.language == "en" and state.pending is None and not state.bookings


@pytest.mark.parametrize(
    "text", ["Do the dishes contain nuts?", "Do the rooms have Wi-Fi? Two adults."]
)
def test_http_first_english_do_the_question_overrides_initial_estonian_voice(
    client, text
):
    identifier = start(client, "et")["session_id"]
    response = client.post(
        "/api/turn",
        headers=AUTH,
        json={
            "session_id": identifier,
            "language": "et",
            "text": text,
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["language"] == "en"
    assert response.json()["booking_changes"] == []
    state = client.app.state.demo_sessions.sessions[identifier].tools
    assert state.language_locked and state.pending is None and not state.bookings


class MetadataRecognition:
    def __init__(self):
        self.text = ""
        self.source = "en"
        self.hints = []

    def transcribe_with_metadata(self, audio, *, language):
        self.hints.append(language)
        return Transcription(self.text, self.source)


@pytest.mark.parametrize("initial", ["auto", "et", "en", "ru"])
@pytest.mark.parametrize("selected", ["et", "en", "ru"])
@pytest.mark.parametrize("channel", ["text", "audio"])
def test_http_uses_first_caller_language_not_repeated_ui_preference(
    client, initial, selected, channel
):
    identifier = start(client, initial)["session_id"]
    stt = MetadataRecognition()
    stt.text, stt.source = OPENERS[selected], selected
    client.app.state.stack["stt"] = stt
    body = {"session_id": identifier, "language": initial}
    if channel == "audio":
        body["audio_b64"] = base64.b64encode(b"synthetic-audio").decode()
    else:
        body["text"] = OPENERS[selected]
    response = client.post("/api/turn", headers=AUTH, json=body)
    assert response.status_code == 200, response.text
    assert response.json()["language"] == selected
    assert response.json()["reply"] == COPY[selected]["date"]
    stt.text, stt.source = "4", "et" if selected != "et" else "ru"
    body["language"] = stt.source
    if channel == "text":
        body["text"] = "4"
    response = client.post("/api/turn", headers=AUTH, json=body)
    assert response.status_code == 200, response.text
    assert response.json()["language"] == selected
    assert response.json()["reply"] == COPY[selected]["date_incomplete"]
    if channel == "audio":
        assert stt.hints == ["auto", selected]


def test_session_language_does_not_leak_to_another_booking(client):
    english = start(client)["session_id"]
    russian = start(client)["session_id"]
    for identifier, selected in [(english, "en"), (russian, "ru")]:
        result = client.post(
            "/api/turn",
            headers=AUTH,
            json={
                "session_id": identifier,
                "language": "et",
                "text": OPENERS[selected],
            },
        ).json()
        assert (
            result["language"] == selected and result["reply"] == COPY[selected]["date"]
        )
    result = client.post(
        "/api/turn",
        headers=AUTH,
        json={
            "session_id": english,
            "text": "4",
            "language": "ru",
        },
    ).json()
    assert result["language"] == "en"
