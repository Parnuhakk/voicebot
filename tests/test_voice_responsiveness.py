"""Faster delivery reaches real provider requests without weakening recaps."""

from xml.etree import ElementTree as ET

import httpx
import pytest

from app.languages import CONSENT
from app.providers.azure_tts import AzureTtsClient
from app.providers.speech_delivery import SpeechDelivery

SSML = "{http://www.w3.org/2001/10/synthesis}"
MSTTS = "{http://www.w3.org/2001/mstts}"


@pytest.mark.parametrize(
    "language,voice,locale,text",
    [
        ("et", "et-EE-AnuNeural", "et-EE", "Tere! Mis kell sulle sobiks?"),
        ("en", "en-US-JennyNeural", "en-US", "Hello! What time works for you?"),
        (
            "ru",
            "ru-RU-SvetlanaNeural",
            "ru-RU",
            "Здравствуйте! Какое время вам подходит?",
        ),
    ],
)
@pytest.mark.parametrize("from_env", [False, True])
def test_default_provider_delivery_is_brisk_but_recaps_keep_normal_speed(
    language, voice, locale, text, from_env
):
    requests = []

    def respond(request):
        if request.url.path.endswith("issueToken"):
            return httpx.Response(200, text="fixture")
        requests.append(ET.fromstring(request.content))
        return httpx.Response(200, content=b"synthetic-audio")

    provider = AzureTtsClient(
        "fixture",
        "fixture",
        voice,
        locale,
        delivery=SpeechDelivery.from_env({}) if from_env else None,
        transport=httpx.MockTransport(respond),
    )
    try:
        assert provider.synthesize(text) == b"synthetic-audio"
        assert provider.synthesize(CONSENT[language]) == b"synthetic-audio"
    finally:
        provider.close()
    ordinary, recap = requests
    assert "".join(ordinary.itertext()) == text
    assert ordinary.find(".//" + SSML + "prosody").get("rate") == "1.12"
    silence = ordinary.find(".//" + MSTTS + "silence")
    if language == "ru":
        assert silence is None
    else:
        assert silence.get("value") == "120ms"
    assert "".join(recap.itertext()) == CONSENT[language]
    assert recap.find(".//" + SSML + "prosody").get("rate") == "1.00"
    assert recap.find(".//" + MSTTS + "silence") is None


def test_operator_pace_override_is_not_overwritten_by_faster_defaults():
    requests = []

    def respond(request):
        if request.url.path.endswith("issueToken"):
            return httpx.Response(200, text="fixture")
        requests.append(ET.fromstring(request.content))
        return httpx.Response(200, content=b"synthetic-audio")

    provider = AzureTtsClient(
        "fixture",
        "fixture",
        "et-EE-AnuNeural",
        "et-EE",
        delivery=SpeechDelivery.from_env(
            {
                "VOICEBOT_SPEECH_RATE": "0.90",
                "VOICEBOT_RECAP_RATE": "0.88",
                "VOICEBOT_SENTENCE_PAUSE_MS": "300",
            }
        ),
        transport=httpx.MockTransport(respond),
    )
    try:
        provider.synthesize("Tere! Mis kell sobiks?")
        provider.synthesize(CONSENT["et"])
    finally:
        provider.close()
    assert requests[0].find(".//" + SSML + "prosody").get("rate") == "0.90"
    assert requests[0].find(".//" + MSTTS + "silence").get("value") == "300ms"
    assert requests[1].find(".//" + SSML + "prosody").get("rate") == "0.88"
