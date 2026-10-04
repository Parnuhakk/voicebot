"""Native utterance grouping, not synthetic audio recognition-quality claims."""

import asyncio
from array import array
from io import BytesIO
from itertools import groupby
from types import SimpleNamespace as NS
from unittest.mock import patch
import wave

import httpx
import pytest

pytest.importorskip("livekit.agents")
from livekit import rtc  # noqa: E402
from livekit.agents import APIConnectOptions, stt, vad  # noqa: E402
from livekit.plugins.silero import onnx_model  # noqa: E402

from app import worker  # noqa: E402
from app.providers.telephone_stt import TelephoneSTT  # noqa: E402


@pytest.fixture
def detector(monkeypatch):
    # Only inference is deterministic: real Silero buffering/threshold events,
    # native StreamAdapter and TelephoneSTT still execute. No recordings/provider.
    monkeypatch.setattr(worker, "protect_logs", lambda: None)
    monkeypatch.setattr(
        onnx_model.OnnxModel, "__call__", lambda self, x: float(x.max() > 0.1)
    )

    def create(business):
        monkeypatch.setenv("VOICEBOT_BUSINESS_TYPE", business)
        proc = NS(userdata={})
        worker.prewarm(proc)
        return proc.userdata["vad"]

    return create


def feed(stream, pause):
    # 32ms windows: 384ms speech, chosen internal pause, 704ms speech, 2s silence.
    for windows, data in (
        (12, b"\x00\x40"),
        (pause, b"\x00\x00"),
        (22, b"\x00\x40"),
        (64, b"\x00\x00"),
    ):
        for _ in range(windows):
            stream.push_frame(rtc.AudioFrame(data * 512, 16000, 1, 512))
    stream.end_input()


@pytest.mark.parametrize(
    "business,pause,segments",
    [("restaurant", 22, 1), ("restaurant", 38, 2), ("hotel_spa", 22, 2)],
)
def test_native_vad_groups_only_restaurant_short_pauses(
    detector, business, pause, segments
):
    async def run():
        stream = detector(business).stream()
        try:
            feed(stream, pause)
            events = [event async for event in stream]
        finally:
            await stream.aclose()
        starts = [e for e in events if e.type == vad.VADEventType.START_OF_SPEECH]
        ends = [e for e in events if e.type == vad.VADEventType.END_OF_SPEECH]
        assert len(ends) == segments
        assert len(starts) == segments and starts[0].timestamp < 0.1
        assert all(e.frames for e in ends)

    asyncio.run(run())


@pytest.mark.parametrize(
    "locales", [("et",), ("en",), ("ru",), ("fi",), ("et", "fi"), ("fi", "et")]
)
def test_grouped_native_stt_preserves_unrestricted_source_policy(detector, locales):
    async def run():
        requests = []

        def respond(request):
            requests.append(request)
            assert b"MAI-Transcribe-2" in request.content and b"RIFF" in request.content
            assert (
                b"locales" not in request.content and b"prompt" not in request.content
            )
            start = request.content.index(b"RIFF")
            size = int.from_bytes(request.content[start + 4 : start + 8], "little") + 8
            with wave.open(BytesIO(request.content[start : start + size]), "rb") as wav:
                assert wav.getframerate() == 16000 and wav.getnchannels() == 1
                samples = array("h", wav.readframes(wav.getnframes()))
            runs = [
                (bool(value), len(list(items))) for value, items in groupby(samples)
            ]
            if runs and not runs[0][0]:
                runs.pop(0)
            if runs and not runs[-1][0]:
                runs.pop()
            assert runs == [(True, 6144), (False, 11264), (True, 11264)]
            return httpx.Response(
                200,
                json={
                    "phrases": [
                        {"text": "Fixture speech.", "locale": locale}
                        for locale in locales
                    ]
                },
            )

        provider = TelephoneSTT.from_env(
            model="whisper-large-v3-turbo",
            env={"AZURE_SPEECH_KEY": "fixture", "AZURE_REGION": "northeurope"},
            transport=httpx.MockTransport(respond),
        )
        adapter = stt.StreamAdapter(stt=provider, vad=detector("restaurant"))
        stream = adapter.stream(conn_options=APIConnectOptions(max_retry=0))
        try:
            feed(stream, 22)
            events = [
                e
                async for e in stream
                if e.type == stt.SpeechEventType.FINAL_TRANSCRIPT
            ]
            assert len(requests) == 1 and len(events) == 1
            result = events[0].alternatives[0]
            unsupported = "fi" in locales
            assert str(result.language) == ("und" if unsupported else locales[0])
            assert result.metadata["unsupported_language"] is unsupported
        finally:
            await stream.aclose()
            await adapter.aclose()
            await provider.aclose()
        assert provider._http.is_closed

    asyncio.run(run())


def test_invalid_business_fails_before_loading_native_vad(monkeypatch):
    monkeypatch.setenv("VOICEBOT_BUSINESS_TYPE", "invalid")
    monkeypatch.setattr(worker, "protect_logs", lambda: None)
    with patch.object(worker.silero.VAD, "load") as load:
        with pytest.raises(ValueError, match="voicebot_business_type_invalid"):
            worker.prewarm(NS(userdata={}))
        load.assert_not_called()
