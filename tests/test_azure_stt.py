"""Actual recognition/HTTP policy with documented synthetic provider responses."""

import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from app.server import create_app
from app.turn import recognize_audio_result


def test_restaurant_uses_recognizer_that_preserves_short_estonian(
    monkeypatch, tmp_path
):
    # Reverting the runtime to unrestricted Whisper loses this actual short ET
    # response at the source-language gate, even with an Estonian UI preference.
    monkeypatch.setenv("VOICEBOT_BUSINESS_TYPE", "restaurant")
    monkeypatch.setenv("GROQ_API_KEY", "fixture")
    monkeypatch.setenv("AZURE_SPEECH_KEY", "fixture")
    monkeypatch.setenv("AZURE_REGION", "northeurope")
    monkeypatch.delenv("VOICEBOT_STT_PROVIDER", raising=False)
    monkeypatch.setenv("RESTAURANT_STATE_DB", str(tmp_path / "restaurant.db"))
    monkeypatch.setenv("CALLS_DB", str(tmp_path / "calls.db"))

    original_send = httpx.Client.send

    def send(client, request, **kwargs):
        if request.url.host == "testserver":
            return original_send(client, request, **kwargs)
        if request.url.host == "api.groq.com":
            payload = {"text": "Ja kinnittan.", "language": "Finnish"}
        else:
            assert request.url.host == "northeurope.api.cognitive.microsoft.com"
            payload = {
                "durationMilliseconds": 1862,
                "combinedPhrases": [{"text": "Jah, kinnitan."}],
                "phrases": [
                    {
                        "text": "Jah, kinnitan.",
                        "locale": "et",
                        "confidence": 0,
                        "offsetMilliseconds": 0,
                        "durationMilliseconds": 1862,
                    }
                ],
            }
        return httpx.Response(200, json=payload, request=request)

    monkeypatch.setattr(httpx.Client, "send", send)
    with TestClient(create_app()) as client:
        result = asyncio.run(
            recognize_audio_result(
                client.app.state.stack["stt"], b"authored-audio", "et"
            )
        )
        assert result.status == "recognized"
        assert result.detected_language == "et"
        assert result.text == "Jah, kinnitan."
        status = client.get("/api/status").json()["models"]["stt"]
        assert status["provider"] == "azure"
        assert status["model"] == "MAI-Transcribe-2"
        assert status["preview"] is True
        assert status["reject_unsupported_languages"] is True


def response_payload(text, locale):
    return {
        "durationMilliseconds": 2000,
        "combinedPhrases": [{"text": text}],
        "phrases": [
            {
                "text": text,
                "locale": locale,
                "confidence": 0,
                "offsetMilliseconds": 0,
                "durationMilliseconds": 2000,
            }
        ],
    }


@pytest.mark.parametrize(
    "text,locale",
    [
        ("Meid on neli.", "et"),
        ("Jah, sobib.", "et"),
        ("Jah, kinnitan.", "et"),
        ("Homme kell 6 õhtul.", "et-EE"),
        ("Soovin oma broneeringu tühistada.", "et"),
        ("Yes, I confirm.", "en"),
        ("Да, подтверждаю.", "ru"),
    ],
)
def test_recognition_uses_unconstrained_source_metadata(text, locale):
    from app.providers.azure_stt import AzureSttClient

    def respond(request):
        assert request.url.path == "/speechtotext/transcriptions:transcribe"
        assert request.url.params["api-version"] == "2025-10-15"
        assert request.headers["Ocp-Apim-Subscription-Key"] == "fixture"
        assert b"MAI-Transcribe-2" in request.content
        assert b'name="audio"' in request.content
        assert b"locales" not in request.content
        assert b"prompt" not in request.content
        assert text.encode() not in request.content
        return httpx.Response(200, json=response_payload(text, locale))

    provider = AzureSttClient(
        "fixture", "northeurope", transport=httpx.MockTransport(respond)
    )
    try:
        result = asyncio.run(recognize_audio_result(provider, b"authored-audio", "et"))
        assert result.status == "recognized"
        assert result.text == text
        assert result.detected_language == locale.split("-")[0]
    finally:
        provider.close()
    assert provider._http.is_closed


@pytest.mark.parametrize("source", ["fi", "de", "es", "id", "und"])
def test_foreign_metadata_cannot_authorize_estonian_consent(source):
    from app.providers.azure_stt import AzureSttClient

    provider = AzureSttClient(
        "fixture",
        "northeurope",
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                200, json=response_payload("Jah, kinnitan.", source)
            )
        ),
    )
    try:
        result = asyncio.run(recognize_audio_result(provider, b"authored-audio", "et"))
        assert result.status == "unsupported_language"
        assert result.text == "" and result.detected_language is None
    finally:
        provider.close()


def test_foreign_phrase_is_not_hidden_by_supported_combined_transcript():
    from app.providers.azure_stt import parse_azure_transcription

    payload = response_payload("Jah, kinnitan.", "et")
    payload["phrases"].append(
        {
            "text": "Kyllä.",
            "locale": "fi",
            "confidence": 0,
            "offsetMilliseconds": 1500,
            "durationMilliseconds": 500,
        }
    )
    assert parse_azure_transcription(payload).unsupported


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"phrases": None},
        {"phrases": ["private"]},
        {"phrases": [{"text": "Jah, kinnitan."}]},
        {"phrases": [{"text": "Jah, kinnitan.", "locale": ""}]},
        {"phrases": [{"text": 42, "locale": "et"}]},
    ],
)
def test_malformed_source_evidence_fails_closed(payload):
    from app.providers.azure_stt import AzureSttClient

    provider = AzureSttClient(
        "fixture",
        "northeurope",
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json=payload)),
    )
    try:
        result = asyncio.run(recognize_audio_result(provider, b"authored-audio", "et"))
        assert result.status == "stt_unavailable" and result.text == ""
    finally:
        provider.close()


def test_silence_stays_no_speech():
    from app.providers.azure_stt import parse_azure_transcription

    result = parse_azure_transcription(
        {"durationMilliseconds": 2000, "combinedPhrases": [], "phrases": []}
    )
    assert result.text == ""


@pytest.mark.parametrize(
    "locale",
    ["et-!", "en-", "ru--RU", "et-EE-extra!", "et_!", "et-EE trailing", "unknown"],
)
def test_malformed_locale_cannot_be_recognized_as_supported_consent(locale):
    from app.providers.azure_stt import AzureSttClient

    provider = AzureSttClient(
        "fixture",
        "northeurope",
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                200, json=response_payload("Jah, kinnitan.", locale)
            )
        ),
    )
    try:
        result = asyncio.run(recognize_audio_result(provider, b"authored-audio", "et"))
        assert result.status == "stt_unavailable" and result.text == ""
        assert result.detected_language is None
    finally:
        provider.close()


@pytest.mark.parametrize(
    "locale,language",
    [
        ("et", "et"),
        ("et-EE", "et"),
        ("en-GB", "en"),
        ("en-Latn-US", "en"),
        ("ru-RU", "ru"),
    ],
)
def test_well_formed_azure_locale_keeps_supported_source_language(locale, language):
    from app.providers.azure_stt import parse_azure_transcription

    result = parse_azure_transcription(response_payload("authored fixture", locale))
    assert result.language == language and not result.unsupported


@pytest.mark.parametrize("status", [401, 429, 503])
def test_provider_outage_does_not_become_a_recognized_turn(status):
    from app.providers.azure_stt import AzureSttClient

    provider = AzureSttClient(
        "fixture",
        "northeurope",
        transport=httpx.MockTransport(
            lambda _: httpx.Response(status, json={"code": "fixture"})
        ),
    )
    try:
        result = asyncio.run(recognize_audio_result(provider, b"authored-audio", "et"))
        assert result.status == "stt_unavailable" and result.text == ""
    finally:
        provider.close()


def test_transport_failure_is_bounded_and_safe():
    from app.providers.azure_stt import AzureSttClient

    def fail(request):
        raise httpx.ReadTimeout("fixture", request=request)

    provider = AzureSttClient(
        "fixture", "northeurope", transport=httpx.MockTransport(fail)
    )
    try:
        result = asyncio.run(recognize_audio_result(provider, b"authored-audio", "et"))
        assert result.status == "stt_unavailable" and result.text == ""
    finally:
        provider.close()


@pytest.mark.parametrize(
    "settings,want",
    [
        ({"AZURE_SPEECH_KEY": "fixture", "AZURE_REGION": "northeurope"}, "azure"),
        ({}, "groq"),
        (
            {
                "VOICEBOT_STT_PROVIDER": "groq",
                "AZURE_SPEECH_KEY": "fixture",
                "AZURE_REGION": "northeurope",
            },
            "groq",
        ),
        (
            {
                "VOICEBOT_BUSINESS_TYPE": "hotel_spa",
                "AZURE_SPEECH_KEY": "fixture",
                "AZURE_REGION": "northeurope",
            },
            "groq",
        ),
    ],
)
def test_provider_selection_preserves_rollback_and_unconfigured_instances(
    settings, want
):
    from app.providers.azure_stt import stt_provider_from_env

    assert stt_provider_from_env(settings) == want


@pytest.mark.parametrize(
    "settings",
    [
        {"VOICEBOT_STT_PROVIDER": "invalid"},
        {"VOICEBOT_STT_PROVIDER": "azure"},
    ],
)
def test_invalid_explicit_selection_fails_configuration(settings):
    from app.providers.azure_stt import stt_provider_from_env

    with pytest.raises(ValueError):
        stt_provider_from_env(settings)


@pytest.mark.parametrize(
    "region", ["https://example.com", "x.invalid", "", "north/europe"]
)
def test_subscription_credential_cannot_be_routed_to_an_arbitrary_host(region):
    from app.providers.azure_stt import AzureSttClient

    with pytest.raises(ValueError):
        AzureSttClient("fixture", region)
