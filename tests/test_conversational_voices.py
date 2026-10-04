"""Conversational voice selection and real SDK requests with offline audio."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import replace
from types import SimpleNamespace as NS
from unittest.mock import Mock
from xml.etree import ElementTree as ET

import httpx
import pytest

from app.providers.azure_tts import ssml
from app.providers.azure_voices import validated_voice
from app.providers.demo_voices import DemoVoices
from app.providers.speech_delivery import SpeechDelivery
from app.providers.voice_config import SpeechConfig
from tests.test_azure_voice_profiles import MP3, MSTTS, SSML, voice
from tests import test_azure_voice_profiles
from tests.test_restaurant_http import AUTH

XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
PROFILES = ["azure-conversational", "azure-conversational-male"]
azure = test_azure_voice_profiles.azure
client = test_azure_voice_profiles.client


def expected_voice(profile, language):
    if language == "et":
        return "et-EE-AnuNeural" if profile == PROFILES[0] else "et-EE-KertNeural"
    return (
        "en-US-EmmaMultilingualNeural"
        if profile == PROFILES[0]
        else "en-US-AndrewMultilingualNeural"
    )


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_session_keeps_conversational_voice_for_greeting_and_followup(
    client, azure, profile, language
):
    speaker, requests = azure
    started = client.post(
        "/api/demo/session",
        headers=AUTH,
        json={
            "language": language,
            "voice": profile,
        },
    )
    assert started.status_code == 200, started.text
    data = started.json()
    assert data["voice"]["effective"] == profile
    reply = client.post(
        "/api/turn",
        headers=AUTH,
        json={
            "session_id": data["session_id"],
            "voice": "azure",
            "language": language,
            "text": {
                "et": "Kas koeraga võib tulla?",
                "en": "Can I bring my dog?",
                "ru": "Можно с собакой?",
            }[language],
        },
    )
    assert reply.status_code == 200, reply.text
    assert reply.json()["voice"]["effective"] == profile
    assert all(voice(doc) == expected_voice(profile, language) for doc in requests)
    assert all(doc.find(".//" + MSTTS + "silence") is None for doc in requests)
    for doc in requests:
        lang = doc.find(".//" + SSML + "lang")
        if language == "et":
            assert lang is None
        else:
            assert lang.get(XML_LANG) == {"en": "en-US", "ru": "ru-RU"}[language]
    assert speaker._voice == "et-EE-AnuNeural"
    assert speaker._delivery == SpeechDelivery()


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_preview_uses_new_voice_without_model_or_booking(
    client, azure, profile, language
):
    _, requests = azure
    model_call = Mock(side_effect=AssertionError("Preview must not call a model"))
    client.app.state.stack["llm_primary"] = NS(chat=model_call)
    response = client.post(
        "/api/demo/voices/preview",
        headers=AUTH,
        json={
            "voice": profile,
            "language": language,
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["voice"]["effective"] == profile
    assert voice(requests[-1]) == expected_voice(profile, language)
    assert not client.app.state.demo_sessions.sessions
    model_call.assert_not_called()


@pytest.mark.parametrize("speaker", ["Emma", "Andrew"])
@pytest.mark.parametrize("mode", ["natural", "neutral"])
def test_explicit_russian_locale_safe_literal_text_and_recap_pronunciation(
    speaker, mode
):
    text = '4 октября 2026 в 18:30. <voice name="bad"> & Вам подходит?'
    doc = ET.fromstring(
        ssml(
            text,
            f"en-US-{speaker}MultilingualNeural",
            "ru-RU",
            SpeechDelivery(mode=mode),
        )
    )
    assert "".join(doc.itertext()) == text
    assert len(list(doc.iter(SSML + "voice"))) == 1
    assert doc.find(".//" + SSML + "lang").get(XML_LANG) == "ru-RU"
    assert doc.find(".//" + MSTTS + "silence") is None
    assert doc.find(".//" + MSTTS + "express-as") is None
    if mode == "natural":
        assert doc.find(".//" + SSML + "prosody").get("rate") == "1.00"
        assert (
            doc.find(".//" + SSML + "sub").get("alias").startswith("четвёртого октября")
        )
    else:
        assert doc.find(".//" + SSML + "prosody") is None
        assert doc.find(".//" + SSML + "sub") is None


@pytest.mark.parametrize("speaker", ["Emma", "Andrew"])
def test_telephone_settings_accept_only_documented_multilingual_locale_pairs(speaker):
    name = f"en-US-{speaker}MultilingualNeural"
    config = SpeechConfig.from_env({"AZURE_EN_VOICE": name, "AZURE_RU_VOICE": name})
    assert config.voice_for("ru") == (name, "ru-RU")
    assert config.voice_for("en") == (name, "en-US")
    assert config.voice_for("et") == ("et-EE-AnuNeural", "et-EE")


@pytest.mark.parametrize(
    "name,locale",
    [
        ("en-US-JennyNeural", "ru-RU"),
        ("en-US-EmmaMultilingualNeural", "en-GB"),
        ("en-US-AndrewMultilingualNeural", "et-EE"),
        ("en-US-UnknownMultilingualNeural", "en-US"),
        ("ru-RU-EmmaMultilingualNeural", "ru-RU"),
        ('en-US-EmmaMultilingualNeural"><voice', "ru-RU"),
    ],
)
def test_unsupported_or_injected_voice_is_rejected(name, locale):
    with pytest.raises(ValueError):
        validated_voice(name, locale)
    with pytest.raises(ValueError):
        SpeechConfig.from_env({"AZURE_RU_VOICE": name, "AZURE_RU_LANG": locale})


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize("streaming", [False, True])
def test_rejected_conversational_voice_uses_native_fallback_before_audio(
    azure, profile, streaming
):
    speaker, requests = azure
    speaker._http.close()

    def respond(request):
        if request.url.path.endswith("issueToken"):
            return httpx.Response(200, text="fixture-token")
        doc = ET.fromstring(request.content)
        requests.append(doc)
        return httpx.Response(400 if "Multilingual" in voice(doc) else 200, content=MP3)

    speaker._http = httpx.Client(transport=httpx.MockTransport(respond))
    choice = DemoVoices.from_env({}).choose(profile, azure=speaker).for_language("ru")
    assert (
        b"".join(choice.stream("Здравствуйте!"))
        if streaming
        else choice.synthesize("Здравствуйте!")
    ) == MP3
    assert [voice(doc) for doc in requests] == [
        expected_voice(profile, "ru"),
        "ru-RU-SvetlanaNeural",
    ]
    assert choice.voice_info["effective"] == "azure"
    assert choice.voice_info["reason"] == "provider_failure"


def test_parallel_languages_profiles_and_timing_do_not_mutate_shared_client(azure):
    speaker, requests = azure
    delivery = SpeechDelivery(rate=1.04, recap_rate=0.96)
    speaker._delivery = delivery
    registry = DemoVoices.from_env({})
    selections = [
        (profile, lang)
        for profile in [*PROFILES, "azure"]
        for lang in ["et", "ru", "en"]
    ]

    def synthesize(selection):
        profile, lang = selection
        return (
            registry.choose(profile, azure=speaker)
            .for_language(lang)
            .synthesize(f"{profile}|{lang}")
        )

    with ThreadPoolExecutor(max_workers=3) as pool:
        assert list(pool.map(synthesize, selections)) == [MP3] * len(selections)
    for doc in requests:
        profile, lang = "".join(doc.itertext()).split("|")
        if profile in PROFILES:
            assert voice(doc) == expected_voice(profile, lang)
            assert doc.find(".//" + MSTTS + "silence") is None
        assert doc.find(".//" + SSML + "prosody").get("rate") == "1.04"
    assert speaker._delivery is delivery
    assert not delivery.native_timing


def test_native_timing_option_requires_boolean():
    with pytest.raises(ValueError):
        replace(SpeechDelivery(), native_timing="yes")


def test_native_sdk_russian_multilingual_locale_and_switch_use_complete_markup():
    pytest.importorskip("livekit.agents")
    from app.providers.telephone_tts import TelephoneTTS

    async def run():
        requests = []

        async def chunks():
            yield b"\0\0" * 2400, False

        @asynccontextmanager
        async def post(**kwargs):
            requests.append(ET.fromstring(kwargs["data"]))
            yield NS(raise_for_status=lambda: None, content=NS(iter_chunks=chunks))

        provider = TelephoneTTS(
            voice="en-US-EmmaMultilingualNeural",
            language="ru-RU",
            delivery=SpeechDelivery(),
            speech_key="fixture",
            speech_region="fixture",
            http_session=NS(post=post),
        )
        try:
            async with provider.synthesize("Приходите в 18:30.") as stream:
                assert [event async for event in stream]
            provider.update_options(
                voice="en-US-AndrewMultilingualNeural", language="en-US"
            )
            async with provider.synthesize("Would six thirty work for you?") as stream:
                assert [event async for event in stream]
            provider.update_options(voice="et-EE-AnuNeural", language="et-EE")
            async with provider.synthesize("Kas kell kuus sobib?") as stream:
                assert [event async for event in stream]
        finally:
            await provider.aclose()
        assert requests[0].find(".//" + SSML + "lang").get(XML_LANG) == "ru-RU"
        assert (
            requests[0].find(".//" + SSML + "sub").get("alias")
            == "в шесть тридцать вечера"
        )
        assert requests[1].find(".//" + SSML + "lang").get(XML_LANG) == "en-US"
        assert all(doc.find(".//" + MSTTS + "silence") is None for doc in requests[:2])
        assert requests[2].find(".//" + SSML + "lang") is None
        assert requests[2].find(".//" + MSTTS + "silence").get("value") == "120ms"

    asyncio.run(run())
