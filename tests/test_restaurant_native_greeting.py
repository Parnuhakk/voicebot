"""Actual SDK startup speech preserves the approved bilingual greeting."""

import asyncio
import re
from unittest.mock import patch

import pytest

pytest.importorskip("livekit.agents")

from livekit.agents import AgentSession  # noqa: E402
from livekit import rtc  # noqa: E402
from app import worker  # noqa: E402
from app.booking.restaurant import RestaurantAdapter  # noqa: E402
from app.business import restaurant_dispatcher  # noqa: E402
from app.call_factory import make_call_tools  # noqa: E402
from app.languages import ENGLISH_INVITATION  # noqa: E402
from app.restaurant_data import load_restaurant_data  # noqa: E402
from app.providers.speech_text import normalize_estonian_speech  # noqa: E402
from tests.test_native_booking_terminals import (  # noqa: E402
    Playback,
    UnusedModel,
    UnusedTTS,
)


@pytest.mark.parametrize("language", ["auto", "et", "en", "ru"])
def test_actual_sdk_greeting_speaks_without_test_framing(tmp_path, language):
    async def run():
        data = load_restaurant_data()
        adapter = RestaurantAdapter(
            str(tmp_path / "restaurant.db"), data=data, allow_writes=True
        )
        selected = "et" if language == "auto" else language
        state = make_call_tools(restaurant_dispatcher(adapter, data), language=selected)
        spoken = []

        async def capture_speech(agent, text, settings):
            spoken.append("".join([part async for part in text]))
            yield rtc.AudioFrame(b"\x01\x00" * 240, 24000, 1, 240)

        agent, model = worker.TelephoneAgent(state), UnusedModel()
        session = AgentSession(
            llm=model, tts=UnusedTTS(), turn_handling={"turn_detection": "manual"}
        )
        session.output.audio = Playback()
        with patch("livekit.agents.Agent.default.tts_node", capture_speech):
            await session.start(agent=agent, record=False)
            try:
                await session.say(state.greeting)
                assert agent.chat_ctx.items[-1].text_content == state.greeting
                assert spoken == [normalize_estonian_speech(state.greeting, selected)]
                assert not re.search(
                    r"demo|testbroneering|test reservation|тестов|демо",
                    spoken[0],
                    re.I,
                )
                if language == "auto":
                    await session.say(ENGLISH_INVITATION)
                    assert agent.chat_ctx.items[-1].text_content == ENGLISH_INVITATION
                    assert spoken[-1] == ENGLISH_INVITATION
                assert state.language == selected
                assert state.pending is None and not state.bookings
                assert model.calls == 0
            finally:
                await session.aclose()
        await adapter.close()

    asyncio.run(run())
