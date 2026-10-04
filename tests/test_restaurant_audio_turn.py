"""Public audio/commit boundary with the installed SDK; no room or providers."""

import asyncio
from collections import deque
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

pytest.importorskip("livekit.agents")

from livekit import rtc  # noqa: E402
from livekit.agents import AgentSession, NOT_GIVEN, stt  # noqa: E402
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS  # noqa: E402
from livekit.agents.voice import io  # noqa: E402

from app.booking.restaurant import RestaurantAdapter  # noqa: E402
from app.business import restaurant_dispatcher  # noqa: E402
from app.call_factory import make_call_tools  # noqa: E402
from app.languages import CONSENT, ENGLISH_INVITATION  # noqa: E402
from app.restaurant_call import COPY  # noqa: E402
from app.restaurant_data import load_restaurant_data  # noqa: E402
from app.worker import TelephoneAgent  # noqa: E402
from tests.test_native_booking_terminals import (  # noqa: E402
    Playback,
    UnusedModel,
    UnusedTTS,
    synthesize,
)


class FixtureAudio(io.AudioInput):
    def __init__(self):
        super().__init__(label="fixture audio")
        self.frames = asyncio.Queue()

    async def __anext__(self):
        return await self.frames.get()


class FixtureSTT(stt.STT):
    def __init__(self, texts, language):
        super().__init__(
            capabilities=stt.STTCapabilities(streaming=True, interim_results=False)
        )
        self.texts = deque(texts)
        self.language = language

    async def _recognize_impl(self, *args, **kwargs):
        raise AssertionError("streaming fixture must not use batch recognition")

    def stream(self, *, language=NOT_GIVEN, conn_options=DEFAULT_API_CONNECT_OPTIONS):
        return FixtureSpeechStream(stt=self, conn_options=conn_options)


class FixtureSpeechStream(stt.SpeechStream):
    async def _run(self):
        async for frame in self._input_ch:
            if not isinstance(frame, rtc.AudioFrame) or not any(frame.data):
                continue
            assert self._stt.texts, "unexpected extra voiced fixture frame"
            self._event_ch.send_nowait(
                stt.SpeechEvent(
                    type=stt.SpeechEventType.FINAL_TRANSCRIPT,
                    alternatives=[
                        stt.SpeechData(
                            text=self._stt.texts.popleft(),
                            language=self._stt.language,
                            metadata={"unsupported_language": False},
                        )
                    ],
                )
            )


class ObservedAgent(TelephoneAgent):
    async def on_user_turn_completed(self, turn_ctx, new_message):
        self.finalized.append(new_message.text_content)
        await super().on_user_turn_completed(turn_ctx, new_message)


@pytest.mark.parametrize(
    "language,caller_text",
    [
        ("en", "I'd like to book a table tomorrow at six PM for two guests total."),
        ("et", "Soovin lauda homme kell 18 kahele külalisele."),
        ("en", "Please reserve a table tomorrow at 1800 hours for two guests total."),
        ("en", "Please reserve a table tomorrow at 18:00 hours for two guests total."),
    ],
)
def test_public_audio_commit_plans_recap_before_later_consent(
    tmp_path, monkeypatch, language, caller_text
):
    async def run():
        data = load_restaurant_data()
        adapter = RestaurantAdapter(
            str(tmp_path / "audio-turn.db"), data=data, allow_writes=True
        )
        state = make_call_tools(restaurant_dispatcher(adapter, data), language="et")
        agent, model = ObservedAgent(state), UnusedModel()
        agent.finalized = []
        recognizer = FixtureSTT([caller_text, CONSENT[language]], language)
        audio = FixtureAudio()
        session = AgentSession(
            stt=recognizer,
            llm=model,
            tts=UnusedTTS(),
            turn_handling={
                "turn_detection": "manual",
                "preemptive_generation": {"enabled": False},
            },
        )
        session.input.audio = audio
        session.output.audio = Playback()
        inputs, replies = asyncio.Queue(), asyncio.Queue()
        actions, errors, before_playback = [], [], []

        def observed_item(event):
            if getattr(event.item, "role", None) == "assistant":
                replies.put_nowait(event.item)

        session.on("conversation_item_added", agent.on_conversation_item_added)
        session.on("conversation_item_added", observed_item)
        session.on(
            "user_input_transcribed",
            lambda event: (
                inputs.put_nowait(event.transcript) if event.is_final else None
            ),
        )
        session.on("error", errors.append)
        session.on(
            "function_tools_executed",
            lambda event: actions.extend(call.name for call in event.function_calls),
        )

        async def fixture_synthesis(agent, text, model_settings):
            if state.pending:
                before_playback.append(
                    (
                        state.pending["delivery"],
                        state.pending["approved"],
                        len(state.bookings),
                    )
                )
            async for frame in synthesize(agent, text, model_settings):
                yield frame

        monkeypatch.setattr("livekit.agents.Agent.default.tts_node", fixture_synthesis)

        async def commit(expected):
            # The SDK, not the test, builds the finalized ChatMessage and invokes
            # the hook. The commit future is a transcript, not a reply handle.
            audio.frames.put_nowait(rtc.AudioFrame(b"\x01\x00" * 480, 24000, 1, 480))
            assert await asyncio.wait_for(inputs.get(), 3) == expected
            committed = session.commit_user_turn(
                transcript_timeout=1, stt_flush_duration=0
            )
            assert await asyncio.wait_for(committed, 3) == expected
            item = await asyncio.wait_for(replies.get(), 4)
            assert not errors
            assert model.calls == 0
            assert not item.interrupted
            return item.text_content

        await asyncio.wait_for(session.start(agent=agent, record=False), 4)
        try:
            if language == "en":
                for greeting in (state.greeting, ENGLISH_INVITATION):
                    await asyncio.wait_for(session.say(greeting), 4)
                    item = await asyncio.wait_for(replies.get(), 4)
                    assert item.text_content == greeting and not item.interrupted
                assert state.language == "et" and not state.booking_inquiry
            day = (
                datetime.now(ZoneInfo("Europe/Tallinn")).date() + timedelta(days=1)
            ).isoformat()
            reply = await commit(caller_text)
            assert agent.finalized == [caller_text]
            assert state.language == language
            assert state.booking_inquiry is not None
            assert state.booking_inquiry["date"] == day
            assert state.booking_inquiry["start_time"] == "18:00"
            assert state.booking_inquiry["party_size"] == 2
            assert actions == ["plan_restaurant_reservation"]
            assert state.pending is not None
            assert reply == state.render_recap()
            assert reply.endswith(COPY[language]["confirmation_question"])
            assert before_playback == [(False, False, 0)]
            assert state.pending["delivery"] and not state.pending["approved"]
            assert not state.bookings

            assert (await commit(CONSENT[language])).startswith(
                COPY[language]["confirmed"]
            )
            assert agent.finalized == [caller_text, CONSENT[language]]
            assert actions == ["plan_restaurant_reservation", "confirm_slot_booking"]
            assert len(state.bookings) == 1
            assert not recognizer.texts and not errors and model.calls == 0
        finally:
            await asyncio.wait_for(session.aclose(), 4)

    asyncio.run(asyncio.wait_for(run(), 18))
