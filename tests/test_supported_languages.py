"""Source-language gates, real HTTP routes and owned consent; fixture providers."""

import asyncio
import base64
from unittest.mock import Mock

import httpx
import pytest

from app.languages import CONSENT, SUPPORTED_LANGUAGE_PROMPT
from app.providers.errors import ProviderError
from app.providers.groq import GroqClient
from app.providers.transcription import parse_transcription
from app.turn import run_turn
from tests.test_restaurant_conversation import prepare
from tests.test_restaurant_http import AUTH, start

pytest_plugins = ["tests.test_restaurant_http", "tests.test_restaurant_conversation"]


@pytest.mark.parametrize("language", ["et", "en", "ru", "auto"])
@pytest.mark.parametrize("source", ["finnish", "de", "french", "spanish", "ukrainian"])
def test_selected_reply_language_cannot_force_supported_recognition(language, source):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json={"text": "Yes, I confirm.", "language": source})

    provider = GroqClient("fixture", transport=httpx.MockTransport(respond))
    llm, tts, dispatcher = Mock(), Mock(), Mock()
    tts.synthesize.return_value = b"fixture-audio"
    try:
        result = asyncio.run(
            run_turn(b"fixture-audio", provider, llm, tts, dispatcher, language=language)
        )
    finally:
        provider.close()
    assert result["input_status"] == "unsupported_language"
    assert result["text_heard"] == "" and result["tool_results"] == []
    assert result["reply"] == SUPPORTED_LANGUAGE_PROMPT.get(language, SUPPORTED_LANGUAGE_PROMPT["et"])
    assert not result["fallback_used"]
    llm.chat.assert_not_called()
    dispatcher.available_tools.assert_not_called()
    assert b'name="language"' not in requests[0].content
    assert b'name="prompt"' not in requests[0].content
    assert b"verbose_json" in requests[0].content


@pytest.mark.parametrize("payload", [
    {"text": "Tere"},
    {"text": "Tere", "language": None},
    {"text": "Tere", "language": ""},
    {"text": "Tere", "language": "estonian", "segments": "private"},
])
def test_missing_language_metadata_is_provider_failure(payload):
    provider = GroqClient("fixture", transport=httpx.MockTransport(
        lambda _: httpx.Response(200, json=payload)
    ))
    try:
        with pytest.raises(ProviderError, match="invalid language metadata"):
            provider.transcribe_with_metadata(b"fixture-audio")
    finally:
        provider.close()


def test_silence_does_not_become_a_confirmation():
    result = parse_transcription({
        "text": "Jah, kinnitan.", "language": "estonian",
        "segments": [{"no_speech_prob": 0.99, "avg_logprob": -1.8}],
    })
    assert result.text == "" and result.language == "et"


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_http_rejects_finnish_without_model_tools_or_foreign_history(client, language):
    session_id = start(client, language)["session_id"]
    provider = GroqClient("fixture", transport=httpx.MockTransport(
        lambda _: httpx.Response(200, json={
            "text": "Haluan varata pöydän neljälle huomenna kello 14.",
            "language": "finnish",
        })
    ))
    client.app.state.stack["stt"] = provider
    try:
        response = client.post("/api/turn", headers=AUTH, json={
            "session_id": session_id, "language": language,
            "audio_b64": base64.b64encode(b"fixture-audio").decode(),
        })
    finally:
        provider.close()
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["input_status"] == "unsupported_language"
    assert result["reply"] == SUPPORTED_LANGUAGE_PROMPT[language]
    assert result["language"] == language
    assert result["text_heard"] == "" and result["tools_used"] == 0
    assert result["booking_changes"] == [] and result["booking_ids"] == []
    assert result["warnings"] == [] and result["audio_b64"]
    assert not result["fallback_used"]
    session = client.app.state.demo_sessions.sessions[session_id]
    assert session.tools.booking_inquiry is None
    assert all("Haluan" not in entry["content"] for entry in session.history)
    # The restriction belongs to this turn, and the same session can recover.
    recovered = client.post("/api/turn", headers=AUTH, json={
        "session_id": session_id, "language": language,
        "text": {"et": "Tere", "en": "Hello", "ru": "Здравствуйте"}[language],
    }).json()
    assert recovered["warnings"] == [] and not recovered["fallback_used"]
    assert not session.tools.unsupported_language


@pytest.mark.parametrize("source,text,expected", [
    ("estonian", "Mis kell te lahti olete?", "et"),
    ("russian", "Когда ресторан открыт?", "ru"),
    ("english", "What are your opening hours?", "en"),
])
def test_auto_http_uses_source_language_for_allowed_speech(client, source, text, expected):
    session_id = start(client, "auto")["session_id"]
    provider = GroqClient("fixture", transport=httpx.MockTransport(
        lambda _: httpx.Response(200, json={"text": text, "language": source})
    ))
    client.app.state.stack["stt"] = provider
    try:
        response = client.post("/api/turn", headers=AUTH, json={
            "session_id": session_id, "language": "auto",
            "audio_b64": base64.b64encode(b"fixture-audio").decode(),
        })
    finally:
        provider.close()
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["language"] == expected
    assert result["input_status"] == "recognized"
    assert result["text_heard"] == text and result["reply"]
    assert result["warnings"] == [] and not result["fallback_used"]


@pytest.mark.parametrize("language", ["et", "en", "ru"])
@pytest.mark.parametrize("text", ["English please", "Mari Näidis", "Jah, kinnitan."])
def test_unsupported_source_cannot_override_gate_or_delivered_consent(make_state, language, text):
    async def run():
        state = make_state(language)
        prepared = await prepare(state)
        assert state.mark_recap_delivered(prepared["hold_id"])
        state.observe_user_text(text, unsupported=True, detected_language="finnish")
        assert state.unsupported_language and state.pending is None
        assert state.language == language
        assert state.direct_reply == SUPPORTED_LANGUAGE_PROMPT[language]
        rejected = await state.dispatch("confirm_slot_booking", {"hold_id": prepared["hold_id"]})
        assert rejected.get("error") and not state.bookings
        state.observe_user_text(CONSENT[language], language=language)
        assert not state.unsupported_language
        rejected = await state.dispatch("confirm_slot_booking", {"hold_id": prepared["hold_id"]})
        assert rejected.get("error") and not state.bookings
    asyncio.run(run())


def test_status_exposes_language_restriction(client):
    stt = client.get("/api/status").json()["models"]["stt"]
    assert stt["languages"] == ["et", "en", "ru"]
    assert stt["reject_unsupported_languages"] is True
