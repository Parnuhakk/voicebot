"""Natural standalone English requests change the shared conversation policy."""

import asyncio
import base64

import pytest

from app.booking_response import trusted_booking_response
from app.languages import CONSENT, requested_language
from app.providers.transcription import Transcription, parse_transcription
from app.restaurant_call import COPY
from tests.test_restaurant_conversation import prepare
from tests.test_restaurant_http import AUTH, start

pytest_plugins = ["tests.test_restaurant_http", "tests.test_restaurant_conversation"]


@pytest.mark.parametrize(
    "utterance",
    [
        "English, please.",
        "Speak English, please.",
        "Can you please speak English?",
        "Do you speak English?",
        "Hello, can we speak English?",
        "Hello! Can we speak English?",
        "Hello. Can we speak English?",
        "Hi! Speak English, please.",
        "Please answer in English, please.",
    ],
)
@pytest.mark.parametrize("audio", [False, True])
def test_english_switch_is_acknowledged_without_model_or_booking(
    client, utterance, audio
):
    session = start(client, "auto")["session_id"]
    first = client.post(
        "/api/turn",
        json={"session_id": session, "text": "Tere! Soovin menüüd."},
        headers=AUTH,
    ).json()
    assert first["language"] == "et"
    body = {"session_id": session, "language": "auto"}
    if audio:
        client.provider.transcribe_with_metadata = lambda *args, **kwargs: (
            Transcription(utterance, "en")
        )
        body["audio_b64"] = base64.b64encode(b"synthetic audio").decode()
    else:
        body["text"] = utterance
    response = client.post("/api/turn", json=body, headers=AUTH)
    assert response.status_code == 200
    answer = response.json()
    assert answer["language"] == "en"
    assert answer["input_status"] == ("recognized" if audio else "typed")
    assert answer["outcome"] == "ok"
    assert not answer["fallback_used"]
    assert "English" in answer["reply"]
    assert answer["tools_used"] == 0 and answer["booking_changes"] == []


@pytest.mark.parametrize(
    "utterance",
    [
        "Do you serve English breakfast?",
        "Speak English, please, and confirm the booking.",
        "Can you please speak English and change the time?",
        "Hello! Speak English, please, and confirm the booking.",
        "Do you speak French?",
    ],
)
def test_english_switch_never_accepts_neighbouring_requests(make_state, utterance):
    assert requested_language(utterance) is None
    state = make_state("et")
    state.observe_user_text("Tere! Soovin lauda.", detected_language="et")
    state.observe_user_text(utterance, detected_language="en")
    assert state.language == "et" and state.language_locked
    assert not state.bookings


def test_unsupported_source_cannot_become_an_english_language_switch(client):
    session = start(client, "et")["session_id"]
    client.provider.transcribe_with_metadata = lambda *args, **kwargs: (
        parse_transcription({"text": "Speak English, please.", "language": "finnish"})
    )
    response = client.post(
        "/api/turn",
        json={
            "session_id": session,
            "audio_b64": base64.b64encode(b"synthetic audio").decode(),
        },
        headers=AUTH,
    )
    assert response.status_code == 200
    answer = response.json()
    assert answer["input_status"] == "unsupported_language"
    assert answer["language"] == "et" and answer["text_heard"] == ""
    assert "English" not in answer["reply"]
    assert answer["tools_used"] == 0 and answer["booking_changes"] == []


@pytest.mark.parametrize(
    "utterance,language,acknowledgement",
    [
        ("Russian, please.", "ru", "по-русски"),
        ("Eesti keeles palun.", "et", "eesti keeles"),
    ],
)
def test_other_supported_language_switches_remain_available(
    client, utterance, language, acknowledgement
):
    session = start(client, "en")["session_id"]
    client.post(
        "/api/turn", json={"session_id": session, "text": "Hello!"}, headers=AUTH
    )
    response = client.post(
        "/api/turn", json={"session_id": session, "text": utterance}, headers=AUTH
    )
    assert response.status_code == 200
    answer = response.json()
    assert answer["language"] == language and answer["outcome"] == "ok"
    assert acknowledgement in answer["reply"]
    assert answer["tools_used"] == 0 and answer["booking_changes"] == []


def test_english_switch_keeps_incomplete_reservation_prompt(make_state):
    state = make_state("et")
    state.observe_user_text("Soovin homme lauda kell 14.")
    previous = state.booking_inquiry
    state.observe_user_text("Can you please speak English?")
    assert state.language == "en" and state.booking_inquiry == previous
    assert trusted_booking_response(state) == {"content": COPY["en"]["party"]}
    assert not state.bookings


def test_english_switch_repeats_held_recap_without_model_or_old_consent(make_state):
    async def run():
        state = make_state("et")
        proposal = await prepare(state)
        assert state.mark_recap_delivered(proposal["hold_id"])
        state.observe_user_text("Speak English, please.", detected_language="en")
        assert state.language == "en"
        reply = trusted_booking_response(state)
        assert reply and "content" in reply
        assert reply["content"].endswith(COPY["en"]["confirmation_question"])
        assert state.pending["hold_id"] == proposal["hold_id"]
        assert not state.pending["delivery"] and not state.pending["approved"]
        state.observe_user_text(CONSENT["en"])
        denied = await state.dispatch(
            "confirm_slot_booking", {"hold_id": proposal["hold_id"]}
        )
        assert denied["error"] == "consent_required" and not state.bookings

    asyncio.run(run())
