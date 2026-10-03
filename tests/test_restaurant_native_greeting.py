"""Actual SDK startup speech preserves the approved bilingual greeting."""

import asyncio
from unittest.mock import patch

import pytest

pytest.importorskip("livekit.agents")

from livekit.agents import AgentSession  # noqa: E402
from app import worker  # noqa: E402
from app.booking.restaurant import RestaurantAdapter  # noqa: E402
from app.business import restaurant_dispatcher  # noqa: E402
from app.call_factory import make_call_tools  # noqa: E402
from app.languages import ENGLISH_INVITATION  # noqa: E402
from app.restaurant_data import load_restaurant_data  # noqa: E402
from tests.test_native_booking_terminals import (  # noqa: E402
    Playback,
    UnusedModel,
    UnusedTTS,
    synthesize,
)


def test_actual_sdk_auto_greeting_speaks_the_checked_english_invitation(tmp_path):
    async def run():
        data = load_restaurant_data()
        adapter = RestaurantAdapter(
            str(tmp_path / "restaurant.db"), data=data, allow_writes=True
        )
        state = make_call_tools(restaurant_dispatcher(adapter, data), language="et")
        agent, model = worker.TelephoneAgent(state), UnusedModel()
        session = AgentSession(
            llm=model, tts=UnusedTTS(), turn_handling={"turn_detection": "manual"}
        )
        session.output.audio = Playback()
        with patch("livekit.agents.Agent.default.tts_node", synthesize):
            await session.start(agent=agent, record=False)
            try:
                await session.say(state.greeting)
                assert agent.chat_ctx.items[-1].text_content == state.greeting
                await session.say(ENGLISH_INVITATION)
                assert agent.chat_ctx.items[-1].text_content == ENGLISH_INVITATION
                assert state.language == "et"
                assert state.pending is None and not state.bookings
                assert model.calls == 0
            finally:
                await session.aclose()
        await adapter.close()

    asyncio.run(run())
