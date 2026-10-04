"""Validated telephone replies retain context in one real provider request."""

import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace as NS
from xml.etree import ElementTree as ET

import pytest

pytest.importorskip("livekit.agents")
import aiohttp  # noqa: E402
from livekit.agents import AgentSession, APIConnectOptions  # noqa: E402
from livekit.agents.voice.agent_session import SessionConnectOptions  # noqa: E402

from app.booking.restaurant import RestaurantAdapter  # noqa: E402
from app.business import restaurant_dispatcher  # noqa: E402
from app.call_factory import make_call_tools  # noqa: E402
from app.providers.speech_delivery import SpeechDelivery  # noqa: E402
from app.providers.telephone_tts import TelephoneTTS  # noqa: E402
from app.providers.voice_config import SpeechConfig  # noqa: E402
from app.restaurant_data import load_restaurant_data  # noqa: E402
from app.worker import TelephoneAgent  # noqa: E402
from app.telephone import FALLBACK  # noqa: E402
from tests.test_native_booking_terminals import (  # noqa: E402
    Playback,
    UnusedModel,
    finalized,
    native_turn,
)

SSML = "{http://www.w3.org/2001/10/synthesis}"


@asynccontextmanager
async def native_restaurant(tmp_path, language, post, playback=None):
    provider = TelephoneTTS(
        voice="en-US-JennyNeural",
        language="en-US",
        delivery=SpeechDelivery(),
        speech_key="fixture",
        speech_region="fixture",
        http_session=NS(post=post),
    )
    data = load_restaurant_data()
    adapter = RestaurantAdapter(
        str(tmp_path / "speech.db"), data=data, allow_writes=True
    )
    state = make_call_tools(restaurant_dispatcher(adapter, data), language=language)
    model = UnusedModel()
    agent = TelephoneAgent(
        state,
        speech_config=SpeechConfig(estonian_voice="en-US-NovaTurboMultilingualNeural"),
        speech_provider=provider,
    )
    session = AgentSession(
        llm=model,
        tts=provider,
        turn_handling={"turn_detection": "manual"},
        conn_options=SessionConnectOptions(
            tts_conn_options=APIConnectOptions(max_retry=0, timeout=7.0)
        ),
    )
    playback = playback if playback is not None else Playback()
    metrics = []
    session.output.audio = playback
    session.on("conversation_item_added", agent.on_conversation_item_added)
    session.on("metrics_collected", lambda event: metrics.append(event.metrics))
    await session.start(agent=agent, record=False)
    try:
        agent._detected_language = language
        yield NS(
            provider=provider,
            state=state,
            agent=agent,
            session=session,
            playback=playback,
            model=model,
            metrics=metrics,
        )
    finally:
        await session.aclose()
        await provider.aclose()
        await adapter.close()


@pytest.mark.parametrize(
    "language,question,expected,voice,locale",
    [
        (
            "et",
            "Kas saate minu allergiast köögile teatada?",
            "Ma ei salvesta erisoove ega saada köögile teateid. "
            "Allergiaohutust ma kinnitada ei saa.",
            "en-US-NovaTurboMultilingualNeural",
            "et-EE",
        ),
        (
            "en",
            "Can you record an allergy note?",
            "I can't save special requests or notify the kitchen. "
            "I can't confirm allergy safety.",
            "en-US-JennyNeural",
            "en-US",
        ),
        (
            "ru",
            "Можете записать мою аллергию в бронирование?",
            "Я не сохраняю особые пожелания и не уведомляю сотрудников кухни. "
            "Я не могу подтвердить безопасность при аллергии.",
            "ru-RU-SvetlanaNeural",
            "ru-RU",
        ),
    ],
)
def test_native_refusal_keeps_full_context_in_one_request(
    tmp_path, language, question, expected, voice, locale
):
    async def run():
        requests = []

        async def chunks():
            yield b"\x10\x01" * 4800, False

        @asynccontextmanager
        async def post(**kwargs):
            requests.append(ET.fromstring(kwargs["data"]))
            assert kwargs["timeout"].sock_connect == 7.0
            yield NS(raise_for_status=lambda: None, content=NS(iter_chunks=chunks))

        async with native_restaurant(tmp_path, language, post) as call:
            await native_turn(call.session, call.agent, question)
            assert len(requests) == 1, (
                "sentence splitting lost the validated reply context"
            )
            assert "".join(requests[0].itertext()) == expected
            assert requests[0].find(".//" + SSML + "voice").get("name") == voice
            assert (
                requests[0].get("{http://www.w3.org/XML/1998/namespace}lang") == locale
            )
            assert requests[0].find(".//" + SSML + "prosody").get("rate") == "1.12"
            assert call.session.history.items[-1].text_content == expected
            assert call.playback.duration > 0 and call.metrics
            assert (
                call.model.calls == 0
                and call.state.pending is None
                and not call.state.bookings
            )

    asyncio.run(run())


def test_whole_recap_still_requires_delivered_later_consent(tmp_path):
    async def run():
        requests = []

        async def chunks():
            yield b"\x10\x01" * 4800, False

        @asynccontextmanager
        async def post(**kwargs):
            requests.append(ET.fromstring(kwargs["data"]))
            yield NS(raise_for_status=lambda: None, content=NS(iter_chunks=chunks))

        async with native_restaurant(tmp_path, "et", post) as call:
            await native_turn(
                call.session, call.agent, "Soovin homme lauda neljale kell 18:00."
            )
            original = call.state.pending
            assert (
                original["delivery"]
                and not original["approved"]
                and not call.state.bookings
            )
            await native_turn(call.session, call.agent, "Hommikul või õhtul?")
            assert call.state.pending is not original
            assert call.state.pending["hold_id"] == original["hold_id"]
            assert call.state.pending["delivery"] and not call.state.pending["approved"]
            assert not call.state.bookings and len(requests) == 2
            assert [
                doc.find(".//" + SSML + "prosody").get("rate") for doc in requests
            ] == ["1.00", "1.00"]
            await native_turn(
                call.session,
                call.agent,
                "Jah, sobib.",
            )
            assert len(call.state.bookings) == 1 and call.model.calls == 0

    asyncio.run(run())


def test_whole_provider_failure_cannot_deliver_recap(tmp_path):
    async def run():
        requests = []

        @asynccontextmanager
        async def post(**kwargs):
            requests.append(kwargs["data"])
            raise aiohttp.ClientResponseError(None, (), status=503, message="fixture")
            yield

        async with native_restaurant(tmp_path, "et", post) as call:
            await native_turn(
                call.session, call.agent, "Soovin homme lauda neljale kell 18:00."
            )
            assert len(requests) == 1 and call.playback.duration > 0
            assert call.session.history.items[-1].text_content == FALLBACK
            assert call.state.pending is None and not call.state.bookings
            assert call.state.outcome == "provider_error" and call.model.calls == 0

    asyncio.run(run())


def test_interrupted_whole_provider_stream_closes_without_delivery(tmp_path):
    async def run():
        started, closed, blocked = asyncio.Event(), asyncio.Event(), asyncio.Event()

        async def chunks():
            yield b"\x10\x01" * 4800, False
            started.set()
            await blocked.wait()
            yield b"\x10\x01" * 4800, False

        @asynccontextmanager
        async def post(**kwargs):
            try:
                yield NS(raise_for_status=lambda: None, content=NS(iter_chunks=chunks))
            finally:
                closed.set()

        async with native_restaurant(tmp_path, "et", post) as call:
            handle = call.session.generate_reply(
                user_input=await finalized(
                    call.agent, "Soovin homme lauda neljale kell 18:00."
                )
            )
            await asyncio.wait_for(started.wait(), 2)
            assert call.state.pending and not call.state.pending["delivery"]
            original = call.state.pending
            await asyncio.wait_for(call.session.interrupt(), 2)
            await asyncio.wait_for(closed.wait(), 2)
            assert handle.interrupted and not call.agent._tts_voice_lock.locked()
            assert call.state.pending is None
            assert not original["delivery"] and not original["approved"]
            assert not call.state.bookings and call.model.calls == 0

    asyncio.run(run())


def test_partial_whole_provider_failure_cannot_deliver_recap(tmp_path):
    async def run():
        captured, closed = asyncio.Event(), asyncio.Event()

        class PartialPlayback(Playback):
            async def capture_frame(self, frame):
                await super().capture_frame(frame)
                captured.set()

        async def chunks():
            yield b"\x10\x01" * 9600, False
            await asyncio.wait_for(captured.wait(), 2)
            raise aiohttp.ClientPayloadError("fixture partial transport failure")

        @asynccontextmanager
        async def post(**kwargs):
            try:
                yield NS(raise_for_status=lambda: None, content=NS(iter_chunks=chunks))
            finally:
                closed.set()

        async with native_restaurant(tmp_path, "et", post, PartialPlayback()) as call:
            await native_turn(
                call.session, call.agent, "Soovin homme lauda neljale kell 18:00."
            )
            assert captured.is_set() and closed.is_set() and call.playback.duration > 0
            assert FALLBACK in call.session.history.items[-1].text_content
            assert not call.agent._tts_voice_lock.locked()
            assert call.state.pending is None and not call.state.bookings
            assert call.state.outcome == "provider_error" and call.model.calls == 0

    asyncio.run(run())


@pytest.mark.parametrize("change", ["expired", "replaced"])
def test_completed_whole_speech_cannot_deliver_changed_pending(tmp_path, change):
    async def run():
        closed = asyncio.Event()
        original = None

        class ChangedPlayback(Playback):
            def flush(self):
                nonlocal original
                original = call.state.pending
                assert original and not original["delivery"]
                if change == "expired":
                    original["expires_at"] = 0
                else:
                    call.state.pending = dict(original)
                super().flush()

        async def chunks():
            yield b"\x10\x01" * 4800, False

        @asynccontextmanager
        async def post(**kwargs):
            try:
                yield NS(raise_for_status=lambda: None, content=NS(iter_chunks=chunks))
            finally:
                closed.set()

        async with native_restaurant(tmp_path, "et", post, ChangedPlayback()) as call:
            await native_turn(
                call.session, call.agent, "Soovin homme lauda neljale kell 18:00."
            )
            assert closed.is_set() and call.playback.duration > 0
            assert not call.agent._tts_voice_lock.locked()
            assert original and not original["delivery"] and not original["approved"]
            assert call.state.pending is None or (
                call.state.pending is not original
                and not call.state.pending["delivery"]
                and not call.state.pending["approved"]
            )
            assert not call.state.bookings and call.model.calls == 0

    asyncio.run(run())
