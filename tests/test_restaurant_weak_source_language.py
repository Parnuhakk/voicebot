"""Closed startup ACKs defer language selection, never source gates or consent."""

import asyncio
from unittest.mock import patch

import pytest

from app.booking_response import trusted_booking_response
from app.languages import select_language
from app.providers.transcription import parse_transcription
from app.restaurant_call import COPY
from tests.test_restaurant_conversation import tomorrow

pytest_plugins = ["tests.test_restaurant_conversation"]

WEAK = [
    "Ja.",
    "Jaa.",
    "Yah.",
    "Ya.",
    "Ah.",
    "Jah?",
    "Yeah?",
    "Yes?",
    "Да?",
    "Нет?",
    "Jah.",
    "Yes.",
    "Yeah.",
    "Yep!",
    "OK",
]
ET_BOOKING = "Soovin homme lauda neljale inimesele kell kuus õhtul."
CLEAR = [
    ("et", "Soovin lauda broneerida."),
    ("en", "Hi! I would like to book a table."),
    ("ru", "Здравствуйте! Я хочу забронировать столик."),
]
COMMITMENTS = [
    ("et", "Jah, kinnitan."),
    ("et", "Jah tühista."),
    ("en", "Yes, I confirm."),
    ("en", "Please cancel this test booking."),
    ("ru", "Да, подтверждаю."),
    ("ru", "Да отмените."),
]


@pytest.mark.parametrize("weak", WEAK)
@pytest.mark.parametrize("metadata", ["en", "ru"])
@pytest.mark.parametrize("current", ["", "et", "en", "ru"])
def test_closed_weak_turn_retains_only_current_language(weak, metadata, current):
    assert select_language(weak, metadata, current) == current
    assert select_language(ET_BOOKING, metadata, current) == "et"


@pytest.mark.parametrize("weak", WEAK)
@pytest.mark.parametrize("metadata", ["en", "ru"])
def test_shared_final_weak_turn_defers_lock_until_clear_et(make_state, weak, metadata):
    state = make_state()
    state.observe_user_text(weak, detected_language=metadata)
    assert state.language == "et" and not state.language_locked
    assert not state.pending and not state.bookings
    state.observe_user_text(ET_BOOKING, detected_language=metadata)
    assert state.language == "et" and state.language_locked
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": {"date": tomorrow(), "start_time": "18:00", "party_size": 4},
    }
    assert not state.bookings


@pytest.mark.parametrize("selected,text", CLEAR + COMMITMENTS)
@pytest.mark.parametrize("metadata", ["en", "ru"])
def test_clear_and_full_commitment_first_turns_still_select_language(
    make_state, selected, text, metadata
):
    assert select_language(text, metadata, "") == selected
    state = make_state()
    state.observe_user_text(text, detected_language=metadata)
    assert state.language == selected and state.language_locked
    assert not state.bookings and not state.pending


@pytest.mark.parametrize("metadata", ["en", "ru"])
def test_explicit_first_language_request_still_selects_et(make_state, metadata):
    state = make_state("en")
    state.observe_user_text("Palun eesti keeles", detected_language=metadata)
    assert state.language == "et" and state.language_locked


@pytest.mark.parametrize("weak", WEAK)
@pytest.mark.parametrize("metadata", ["en", "ru"])
def test_native_final_weak_turn_then_clear_et_booking(make_state, weak, metadata):
    pytest.importorskip("livekit.agents")
    from livekit.agents import AgentSession

    from app.worker import TelephoneAgent
    from tests.test_native_booking_terminals import (
        Playback,
        UnusedModel,
        UnusedTTS,
        native_turn,
        synthesize,
    )

    async def run():
        state = make_state()
        agent, model = TelephoneAgent(state), UnusedModel()
        session = AgentSession(
            llm=model, tts=UnusedTTS(), turn_handling={"turn_detection": "manual"}
        )
        session.output.audio = Playback()
        session.on("conversation_item_added", agent.on_conversation_item_added)
        with patch("livekit.agents.Agent.default.tts_node", synthesize):
            await session.start(agent=agent, record=False)
            try:
                agent._detected_language = metadata
                await native_turn(session, agent, weak)
                assert state.language == "et" and not state.language_locked
                assert not state.pending and not state.bookings
                assert agent._detected_language is None
                agent._detected_language = metadata
                await native_turn(session, agent, ET_BOOKING)
                assert state.language == "et" and state.language_locked
                assert state.pending["recap"]["party_size"] == 4
                assert state.pending["recap"]["start"].endswith("18:00:00")
                assert state.pending["delivery"] and not state.pending["approved"]
                assert agent.chat_ctx.items[-1].text_content.endswith(
                    COPY["et"]["confirmation_question"]
                )
                assert not state.bookings and model.calls == 0
            finally:
                await session.aclose()

    asyncio.run(run())


@pytest.mark.parametrize("source", ["finnish", "de"])
@pytest.mark.parametrize("text", ["Ja.", "Yes?", "Да?", ET_BOOKING, "Yes, I confirm."])
def test_unsupported_source_still_blocks_final_native_turn(make_state, source, text):
    pytest.importorskip("livekit.agents")
    from app.worker import TelephoneAgent
    from tests.test_native_booking_terminals import finalized

    async def run():
        transcription = parse_transcription({"text": text, "language": source})
        assert transcription.unsupported
        state = make_state()
        agent = TelephoneAgent(state)
        agent._detected_language = transcription.language
        agent._unsupported_language = transcription.unsupported
        message = await finalized(agent, transcription.text)
        assert message.content == []
        assert state.unsupported_language
        assert state.language == "et" and not state.language_locked
        assert not state.booking_inquiry and not state.pending and not state.bookings

    asyncio.run(run())
