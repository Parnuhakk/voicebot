"""Repeat once, then ask for writing; real HTTP routes and call-owned guards."""

import asyncio
import base64

import httpx
import pytest

from app.input_recovery import InputRecovery, REPEAT_PROMPT, WRITE_LANGUAGE_PROMPT
from app.providers.groq import GroqClient
from app.restaurant_call import COPY
from tests.test_restaurant_http import AUTH, start, turn
from tests.test_restaurant_conversation import prepare

pytest_plugins = ["tests.test_restaurant_http", "tests.test_restaurant_conversation"]


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_closed_recovery_sequence_reset_and_provider_failure(language):
    recovery = InputRecovery()
    assert recovery.reply(language) is None
    recovery.observe("unsupported_language")
    assert recovery.reply(language) == REPEAT_PROMPT[language]
    recovery.observe("stt_unavailable")
    assert recovery.reply(language) is None and recovery.failures == 1
    recovery.observe("no_speech")
    assert recovery.reply(language) == WRITE_LANGUAGE_PROMPT[language]
    for _ in range(5):
        recovery.observe("unsupported_language")
        assert recovery.failures == 2 and recovery.reply(language) == WRITE_LANGUAGE_PROMPT[language]
    recovery.observe("recognized")
    assert recovery.reply(language) is None and recovery.failures == 0
    recovery.observe("no_speech")
    assert recovery.reply(language) == REPEAT_PROMPT[language]
    recovery.observe("typed")
    assert recovery.reply(language) is None and recovery.failures == 0


@pytest.mark.parametrize("language", ["et", "en", "ru"])
@pytest.mark.parametrize("first,second", [("finnish", "finnish"), ("finnish", "empty"), ("empty", "finnish"), ("empty", "empty")])
def test_http_retries_share_one_counter_and_recover_without_model_calls(client, language, first, second):
    selected = {"source": first}

    def response(_):
        source = selected["source"]
        if source == "empty":
            return httpx.Response(200, json={"text": "", "language": "estonian"})
        if source == "failure":
            return httpx.Response(503)
        return httpx.Response(200, json={"text": "private-foreign-fixture", "language": source})

    provider = GroqClient("fixture", transport=httpx.MockTransport(response))
    client.app.state.stack["stt"] = provider
    session_id = start(client, language)["session_id"]
    other_session = start(client, language)["session_id"]

    def unclear(session, source):
        selected["source"] = source
        result = client.post("/api/turn", headers=AUTH, json={
            "session_id": session, "language": language,
            "audio_b64": base64.b64encode(b"synthetic-recovery-fixture").decode(),
        })
        assert result.status_code == 200, result.text
        return result.json()

    try:
        first_answer = unclear(session_id, first)
        assert first_answer["reply"] == REPEAT_PROMPT[language]
        # Technical failures do not count as an unclear answer or expose text.
        failed = unclear(session_id, "failure")
        from app.turn import STT_UNAVAILABLE

        assert failed["reply"] == STT_UNAVAILABLE[language] and failed["fallback_used"]
        second_answer = unclear(session_id, second)
        assert second_answer["reply"] == WRITE_LANGUAGE_PROMPT[language]
        third_answer = unclear(session_id, second)
        assert third_answer["reply"] == WRITE_LANGUAGE_PROMPT[language]
        for answer in (first_answer, second_answer, third_answer):
            assert answer["tools_used"] == 0 and answer["booking_changes"] == []
            assert answer["text_heard"] == "" and answer["audio_b64"]
            assert not answer["fallback_used"] and answer["recap_delivery_id"] is None
        assert unclear(other_session, first)["reply"] == REPEAT_PROMPT[language]
        session = client.app.state.demo_sessions.sessions[session_id]
        assert not session.tools.holds and not session.tools.bookings
        assert all("private-foreign" not in entry["content"] for entry in session.history)
        greeting = {"et": "Tere", "en": "Hello", "ru": "Здравствуйте"}[language]
        recovered = turn(client, session_id, greeting, language=language)
        assert recovered["reply"] and not session.tools.input_recovery_reply
        assert unclear(session_id, first)["reply"] == REPEAT_PROMPT[language]
    finally:
        provider.close()


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_unclear_turn_revokes_consent_and_guard_reads_do_not_advance_retry(make_state, language):
    async def run():
        state = make_state(language)
        proposal = await prepare(state)
        assert state.mark_recap_delivered(proposal["hold_id"])
        state.observe_user_text("Yes, I confirm.", unsupported=True)
        for _ in range(3):
            assert state.direct_reply == REPEAT_PROMPT[language]
            assert state.guard_reply("arbitrary model output", []) == REPEAT_PROMPT[language]
        state.observe_user_text("", is_final=False, unsupported=True)
        assert state.direct_reply == REPEAT_PROMPT[language]
        assert state.pending is None
        state.observe_user_text("", unsupported=True)
        assert state.direct_reply == WRITE_LANGUAGE_PROMPT[language]
        rejected = await state.dispatch("confirm_slot_booking", {"hold_id": proposal["hold_id"]})
        assert rejected.get("error") and not state.bookings
        state.observe_user_text("", language=language)
        assert state.direct_reply == WRITE_LANGUAGE_PROMPT[language]
        assert (await state.dispatch("get_restaurant_information", {"topic": "hours"})).get("error")
        state.observe_user_text({"et": "Tere", "en": "Hello", "ru": "Здравствуйте"}[language], language=language)
        assert state.input_recovery_reply is None
        state.observe_user_text("", unsupported=True)
        assert state.direct_reply == REPEAT_PROMPT[language]

    asyncio.run(run())


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_unclear_followup_keeps_restaurant_preferences_for_correction(client, language):
    session_id = start(client, language)["session_id"]
    request = {"et": "Soovin lauda", "en": "I'd like a table", "ru": "Хочу забронировать столик"}[language]
    assert turn(client, session_id, request, language=language)["reply"] == COPY[language]["date"]
    tools = client.app.state.demo_sessions.sessions[session_id].tools
    tools.observe_user_text("", language=language)
    assert tools.direct_reply == REPEAT_PROMPT[language] and tools.booking_inquiry == {}
    tools.observe_user_text("", language=language)
    assert tools.direct_reply == WRITE_LANGUAGE_PROMPT[language] and tools.booking_inquiry == {}
    day = "завтра" if language == "ru" else "homseks" if language == "et" else "tomorrow"
    fixed = turn(client, session_id, day, language=language)
    assert fixed["reply"] == COPY[language]["time"]
    assert tools.input_recovery_reply is None
