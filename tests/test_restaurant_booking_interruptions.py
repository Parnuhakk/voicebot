"""Side questions resume restaurant booking using real routes and SQLite."""

import asyncio
import base64
import copy

import pytest

from app.booking_response import trusted_booking_response
from app.languages import CONSENT
from app.restaurant_call import COPY
from tests.test_restaurant_conversation import make_state as state_factory, prepare
from tests.test_restaurant_http import (
    AUTH,
    client as http_client,
    start,
    tomorrow,
    turn,
)
from tests.test_restaurant_reasoning import Model, QUESTIONS, REPLIES

client = http_client
make_state = state_factory

STEPS = {
    "et": ["Soovin lauda broneerida", "Homme", "14:00", "4"],
    "en": ["I'd like to book a table", "Tomorrow", "2 pm", "4"],
    "ru": ["Хочу забронировать столик", "Завтра", "14:00", "4"],
}
SIDE_QUESTIONS = {
    "et": ["Mis kell te avatud olete?", "Milline on menüü?", "Kus saab parkida?"],
    "en": ["What are your opening hours?", "What is on the menu?", "Where can I park?"],
    "ru": ["Какие у вас часы работы?", "Что есть в меню?", "Где можно припарковаться?"],
}
FULL_REQUEST = {
    "et": "Soovin homme lauda neljale kell 14.00",
    "en": "A table for four tomorrow at 2 pm",
    "ru": "Столик на четверых завтра в 14:00",
}


def speak(client, session, text, language, channel, receipt=None):
    body = {"session_id": session, "language": language}
    if channel == "audio":
        client.provider.transcript = text
        body["audio_b64"] = base64.b64encode(b"synthetic-microphone-input").decode()
    else:
        body["text"] = text
    if receipt:
        body["recap_delivery_id"] = receipt
    response = client.post("/api/turn", json=body, headers=AUTH)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["reply"] == client.provider.spoken[-1]
    return result


@pytest.mark.parametrize("language", ["et", "en", "ru"])
@pytest.mark.parametrize("channel", ["text", "audio"])
def test_answer_then_resume_each_missing_detail_without_restarting(
    client, language, channel
):
    session = start(client, language)["session_id"]
    state = client.app.state.demo_sessions.sessions[session].tools
    for index, key in enumerate(["date", "time", "party"]):
        prompt = speak(client, session, STEPS[language][index], language, channel)
        assert prompt["reply"] == COPY[language][key]
        retained = state.booking_inquiry
        side = speak(
            client, session, SIDE_QUESTIONS[language][index], language, channel
        )
        assert side["reply"].startswith(state.question_reply())
        assert side["reply"].endswith(COPY[language][key])
        assert state.booking_inquiry == retained
        assert side["booking_changes"] == [] and side["recap_delivery_id"] is None
    proposal = speak(client, session, STEPS[language][3], language, channel)
    assert state.booking_inquiry == {
        "date": tomorrow(),
        "start_time": "14:00",
        "party_size": 4,
    }
    assert proposal["recap_delivery_id"] and proposal["booking_changes"] == []
    saved = speak(
        client,
        session,
        CONSENT[language],
        language,
        channel,
        proposal["recap_delivery_id"],
    )
    assert saved["reply"] == COPY[language]["confirmed"]
    assert saved["booking_changes"][0]["party_size"] == 4
    assert saved["booking_changes"][0]["start_local"].startswith(tomorrow() + "T14:00")
    rows = client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()["items"]
    assert len(rows) == 1 and str(rows[0]["id"]) == saved["booking_changes"][0]["id"]


@pytest.mark.parametrize("language", ["et", "en", "ru"])
@pytest.mark.parametrize("channel", ["text", "audio"])
def test_questions_after_summary_keep_hold_and_require_new_delivery(
    client, language, channel
):
    session = start(client, language)["session_id"]
    proposal = speak(client, session, FULL_REQUEST[language], language, channel)
    state = client.app.state.demo_sessions.sessions[session].tools
    original_pending = state.pending
    held = set(state.holds)
    recap = proposal["reply"]
    receipt = proposal["recap_delivery_id"]
    for question in SIDE_QUESTIONS[language][:2]:
        before = state.pending
        side = speak(client, session, question, language, channel, receipt)
        assert state.pending is not before
        assert state.pending["hold_id"] == original_pending["hold_id"]
        assert state.pending["expires_at"] == original_pending["expires_at"]
        assert not state.pending["approved"] and not state.pending["delivery"]
        assert set(state.holds) == held
        assert side["reply"].startswith(state.question_reply())
        assert side["reply"].endswith(recap)
        assert side["recap_delivery_id"] and side["recap_delivery_id"] != receipt
        assert not state.results and not side["booking_changes"]
        receipt = side["recap_delivery_id"]
    stale = client.post(
        "/api/turn",
        json={
            "session_id": session,
            "text": CONSENT[language],
            "language": language,
            "recap_delivery_id": proposal["recap_delivery_id"],
        },
        headers=AUTH,
    )
    assert stale.status_code == 409 and not state.bookings
    # Rejected stale receipts consume the transport receipt: a new reading is
    # required, and it still reuses the same unexpired hold.
    repeated = speak(client, session, SIDE_QUESTIONS[language][1], language, channel)
    saved = speak(
        client,
        session,
        CONSENT[language],
        language,
        channel,
        repeated["recap_delivery_id"],
    )
    assert saved["reply"] == COPY[language]["confirmed"]
    assert len(state.bookings) == 1 and len(state.confirmed_holds) == 1


@pytest.mark.parametrize("stage", ["date", "ambiguous_time", "party"])
@pytest.mark.parametrize("provider_failure", [False, True])
def test_generated_side_answers_and_fallback_resume_authoritative_prompt(
    client, stage, provider_failure
):
    session = start(client, "en")["session_id"]
    initial = {
        "date": "Book a table",
        "ambiguous_time": "A table tomorrow at seven for four",
        "party": "A table tomorrow at 2 pm",
    }[stage]
    turn(client, session, initial)
    state = client.app.state.demo_sessions.sessions[session].tools
    retained = state.booking_inquiry
    model = Model()
    model.fail_at = 1 if provider_failure else None
    client.app.state.stack["llm_primary"] = model
    answer = turn(client, session, QUESTIONS["en"])
    assert answer["reply"].endswith(COPY["en"][stage])
    assert state.booking_inquiry == retained and answer["booking_changes"] == []
    assert answer["recap_delivery_id"] is None
    if provider_failure:
        assert answer["reply"].startswith(state.question_reply())
        assert {"stage": "llm", "code": "grounded_reply_unavailable"} in answer[
            "warnings"
        ]
    else:
        assert answer["reply"].startswith(REPLIES["en"]) and len(model.calls) == 2


def test_question_numbers_and_dates_do_not_change_pending_booking(client):
    session = start(client)["session_id"]
    proposal = turn(client, session, FULL_REQUEST["en"])
    state = client.app.state.demo_sessions.sessions[session].tools
    retained = state.booking_inquiry
    for question in [
        "Are you open on Sunday at 19:00?",
        "What is Wi-Fi for six devices?",
        "Can seven children use the terrace?",
    ]:
        side = turn(client, session, question)
        assert state.booking_inquiry == retained and side["reply"].endswith(
            proposal["reply"]
        )
        assert side["booking_changes"] == [] and not state.pending["approved"]


def test_late_native_playback_cannot_approve_new_side_question_recap(make_state):
    async def run():
        state = make_state("en")
        proposal = await prepare(state)
        previous = state.pending
        state.mark_recap_delivered(proposal["hold_id"])
        state.observe_user_text(SIDE_QUESTIONS["en"][1], language="en")
        assert state.pending is not previous and not state.pending["delivery"]
        previous["delivery"] = True  # stale native task holds the old object
        assert not state.pending["delivery"]
        assert (
            trusted_booking_response(state) is None
        )  # direct_reply supplies the owned recap
        assert state.guard_reply("invented", []).endswith(
            COPY["en"]["confirmation_question"]
        )
        assert (
            await state.dispatch(
                "confirm_slot_booking", {"hold_id": proposal["hold_id"]}
            )
        )["error"] == "consent_required"

    asyncio.run(run())


def test_expired_summary_answers_question_then_requires_new_check(make_state):
    async def run():
        state = make_state("en")
        await prepare(state)
        previous = state.pending
        previous["expires_at"] = 0
        state.observe_user_text(SIDE_QUESTIONS["en"][1], language="en")
        assert state.pending is None
        response = trusted_booking_response(state)
        assert response["content"].startswith(state.question_reply())
        assert response["content"].endswith(COPY["en"]["resume_check"])
        state.observe_user_text("yes", language="en")
        action = trusted_booking_response(state)
        assert action["name"] == "plan_restaurant_reservation"
        assert action["arguments"] == {
            "date": tomorrow(),
            "start_time": "14:00",
            "party_size": 4,
        }
        assert not state.bookings  # this yes authorizes rechecking, not a write

    asyncio.run(run())


@pytest.mark.parametrize(
    "question", ["What is on the menu?", "What is the Wi-Fi password?"]
)
def test_side_question_without_new_delivery_cannot_save_booking(client, question):
    session = start(client)["session_id"]
    turn(client, session, FULL_REQUEST["en"])
    turn(client, session, question)
    answer = turn(client, session, "yes")
    assert not answer["booking_changes"]
    assert (
        client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()["items"]
        == []
    )


@pytest.mark.parametrize(
    "text", ["Cancel. What is on the menu?", "Change the time. What is on the menu?"]
)
def test_explicit_change_or_cancellation_does_not_restore_old_proposal(
    make_state, text
):
    async def run():
        state = make_state("en")
        await prepare(state)
        state.observe_user_text(text, language="en")
        assert state.pending is None and state.booking_inquiry is None
        response = trusted_booking_response(state)
        assert response == {"content": state.question_reply()}

    asyncio.run(run())


def test_allergy_guard_remains_authoritative_while_booking(client):
    session = start(client)["session_id"]
    turn(client, session, "A table tomorrow at 2 pm")
    model = Model("The salmon is safe for all allergies.")
    client.app.state.stack["llm_primary"] = model
    answer = turn(client, session, "Is the salmon safe for a severe allergy?")
    assert model.calls == [] and answer["reply"].endswith(COPY["en"]["party"])
    assert "cannot guarantee" in answer["reply"]


def test_partial_transcript_does_not_pause_or_replace_booking(make_state):
    state = make_state("en")
    state.observe_user_text("A table tomorrow at 2 pm", language="en")
    retained = copy.deepcopy(state.booking_inquiry)
    state.observe_user_text(SIDE_QUESTIONS["en"][1], language="en", is_final=False)
    assert state.booking_inquiry == retained and not state._restaurant_booking_paused


def test_repeated_side_answer_keeps_the_same_missing_prompt(make_state):
    state = make_state("en")
    state.observe_user_text("A table tomorrow at 2 pm", language="en")
    state.guard_reply("", [])
    state.observe_user_text("What is on the menu?", language="en")
    answer = state.guard_reply("", [])
    state.observe_user_text("Please repeat that", language="en")
    assert state.guard_reply("", []) == answer


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_offered_alternative_times_survive_side_question(client, language):
    occupied = start(client, language)["session_id"]
    request = {
        "et": "Soovin homme lauda kuuele kell 14.00",
        "en": "A table for six tomorrow at 2 pm",
        "ru": "Столик на шестерых завтра в 14:00",
    }[language]
    proposal = turn(client, occupied, request, language=language)
    saved = turn(
        client,
        occupied,
        CONSENT[language],
        language=language,
        receipt=proposal["recap_delivery_id"],
    )
    assert len(saved["booking_changes"]) == 1
    session = start(client, language)["session_id"]
    unavailable = turn(client, session, request, language=language)
    state = client.app.state.demo_sessions.sessions[session].tools
    offered = list(state._restaurant_alternatives)
    assert offered and state.pending is None
    side = turn(client, session, SIDE_QUESTIONS[language][1], language=language)
    assert side["reply"].endswith(unavailable["reply"])
    assert state._restaurant_alternatives == offered
    alternative = turn(client, session, offered[0], language=language)
    assert (
        alternative["recap_delivery_id"] and state.booking_inquiry["party_size"] == 6
    ), (alternative, state.booking_inquiry, offered)
    assert state.booking_inquiry["start_time"] == offered[0]
    assert alternative["booking_changes"] == []


@pytest.mark.parametrize(
    "initial,expected,answer,resolved",
    [
        (
            "A table tomorrow at seven for four",
            "ambiguous_time",
            "in the evening",
            "19:00",
        ),
        ("A table tomorrow at 25:00 for four", "invalid_time", "14:00", "14:00"),
    ],
)
def test_clock_clarification_survives_multiple_side_questions(
    client, initial, expected, answer, resolved
):
    session = start(client)["session_id"]
    turn(client, session, initial)
    state = client.app.state.demo_sessions.sessions[session].tools
    retained = state.booking_inquiry
    for question in ["What is on the menu?", "What are your opening hours?"]:
        side = turn(client, session, question)
        assert side["reply"].endswith(COPY["en"][expected])
        assert state.booking_inquiry == retained
    recap = turn(client, session, answer)
    assert (
        recap["recap_delivery_id"] and state.booking_inquiry["start_time"] == resolved
    )
    assert state.booking_inquiry["party_size"] == 4


def test_speech_failure_after_side_question_cannot_authorize_write(client, monkeypatch):
    session = start(client)["session_id"]
    turn(client, session, FULL_REQUEST["en"])

    def fail_speech(text):
        raise TimeoutError("synthetic provider failure")

    monkeypatch.setattr(client.provider, "synthesize", fail_speech)
    side = turn(client, session, "What is on the menu?")
    # JSON still exposes readable canonical text for explicit UI acknowledgment;
    # synthesis failure itself does not establish delivery or consent.
    state = client.app.state.demo_sessions.sessions[session].tools
    assert side["tts_failed"] and side["recap_delivery_id"]
    assert not state.pending["delivery"] and not state.pending["approved"]
    assert not side["booking_changes"]
    again = turn(client, session, "yes")
    assert not again["booking_changes"]
    assert (
        client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()["items"]
        == []
    )
