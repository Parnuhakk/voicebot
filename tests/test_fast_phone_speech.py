"""Fast speech settings reach real provider boundaries without changing facts."""

import asyncio
import xml.etree.ElementTree as ET
from unittest.mock import patch

import httpx
import pytest

from app.providers.azure_tts import AzureTtsClient, ssml
from app.providers.groq import GroqClient
from app.providers.speech_delivery import SpeechDelivery
from app.providers.voice_config import SpeechConfig, VoiceConfig

VOICE = "en-US-NovaTurboMultilingualNeural"
SSML = "{http://www.w3.org/2001/10/synthesis}"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


@pytest.mark.parametrize("profile", [None, "azure-conversational"])
def test_new_estonian_voice_reaches_the_synthesis_request_with_locale_and_aliases(
    profile,
):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(
            200,
            content=b"fixture" if request.url.path.endswith("issueToken") else b"audio",
        )

    config = SpeechConfig.from_env({"AZURE_VOICE": VOICE, "AZURE_LANG": "et-EE"})
    client = AzureTtsClient(
        "fixture",
        "fixture",
        *config.voice_for("et"),
        transport=httpx.MockTransport(respond),
    )
    text = "Laud kell 18:05 4 inimesele. Kas sobib?"
    try:
        speaker = client.for_profile(profile).for_language("et") if profile else client
        assert speaker.synthesize(text) == b"audio"
    finally:
        client.close()
    root = ET.fromstring(requests[-1].content)
    assert root.find(SSML + "voice").get("name") == VOICE
    assert root.find(".//" + SSML + "lang").get(XML_LANG) == "et-EE"
    assert "neljale inimesele" in [
        item.get("alias") for item in root.iter(SSML + "sub")
    ]
    assert "kell kaheksateist viis" in [
        item.get("alias") for item in root.iter(SSML + "sub")
    ]
    assert "".join(root.itertext()) == text


@pytest.mark.parametrize(
    "voice,locale",
    [
        ("et-EE-AnuNeural", "et-EE"),
        ("en-US-JennyNeural", "en-US"),
        ("ru-RU-SvetlanaNeural", "ru-RU"),
    ],
)
@pytest.mark.parametrize("env", [{}, {"VOICEBOT_SENTENCE_PAUSE_MS": "0"}])
def test_default_delivery_does_not_inject_fixed_sentence_silence(voice, locale, env):
    text = "First sentence. Second sentence?"
    rendered = ssml(text, voice, locale, SpeechDelivery.from_env(env))
    root = ET.fromstring(rendered)
    assert "".join(root.itertext()) == text
    assert "Sentenceboundary-exact" not in rendered
    assert not list(root.iter(SSML + "break"))


def test_default_turbo_transcription_is_unhinted_and_keeps_original_language_rejection():
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(
            200, json={"text": "Haluan pöydän.", "language": "finnish"}
        )

    client = GroqClient(
        "fixture",
        config=VoiceConfig.from_env({}),
        transport=httpx.MockTransport(respond),
    )
    try:
        result = client.transcribe_with_metadata(b"RIFF", language="et")
    finally:
        client.close()
    assert b"whisper-large-v3-turbo" in requests[0].content
    assert b'name="language"' not in requests[0].content
    assert b'name="prompt"' not in requests[0].content
    assert result.unsupported and result.language is None


def test_native_synthesis_keeps_the_new_voice_locale_and_literal_text():
    pytest.importorskip("livekit.agents")
    from livekit.plugins import azure

    from app.providers.telephone_tts import TelephoneTTS

    async def run():
        config = SpeechConfig.from_env({"AZURE_VOICE": VOICE})
        voice, locale = config.voice_for("et")
        provider = TelephoneTTS(
            voice=voice,
            language=locale,
            delivery=SpeechDelivery.from_env({}),
            speech_key="fixture",
            speech_region="fixture",
        )
        try:
            with patch.object(
                azure.TTS, "synthesize", return_value=object()
            ) as synthesize:
                provider.synthesize("Laud kell 18:05 4 inimesele.")
            root = ET.fromstring(
                '<speak xmlns="http://www.w3.org/2001/10/synthesis">'
                + synthesize.call_args.args[0]
                + "</speak>"
            )
            assert root.find(SSML + "lang").get(XML_LANG) == "et-EE"
            assert "".join(root.itertext()) == "Laud kell 18:05 4 inimesele."
            assert "neljale inimesele" in [
                item.get("alias") for item in root.iter(SSML + "sub")
            ]
        finally:
            await provider.aclose()

    asyncio.run(run())
