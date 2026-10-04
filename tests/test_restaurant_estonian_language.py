"""Clear Estonian speech wins over metadata; explicit switches revoke consent."""

import asyncio

import pytest

from app.booking_response import trusted_booking_response
from app.languages import requested_language
from app.restaurant_call import COPY
from tests.test_restaurant_conversation import prepare

pytest_plugins = ["tests.test_restaurant_conversation"]


@pytest.mark.parametrize(
    "text",
    ["Sooviksin homseks lauda neljale", "Tahaksin homseks lauda", "Tervist", "Menüü"],
)
@pytest.mark.parametrize("metadata", ["english", "russian"])
def test_estonian_openers_cannot_lock_the_call_to_noisy_metadata(
    make_state, text, metadata
):
    state = make_state("en")
    state.observe_user_text(text, detected_language=metadata)
    assert state.language == "et" and state.language_locked
    assert not state.bookings


@pytest.mark.parametrize(
    "text,target",
    [
        ("Rääkige palun eesti keeles", "et"),
        ("Kas saaks eesti keeles?", "et"),
        ("Eesti keeles, palun", "et"),
        ("Palun rääkige eesti keeles", "et"),
        ("Kas saaksite rääkida eesti keeles?", "et"),
        ("Rääkige palun inglise keeles", "en"),
        ("Vene keeles, palun", "ru"),
    ],
)
def test_polite_explicit_switch_keeps_preferences_but_revokes_recap(
    make_state, text, target
):
    async def run():
        state = make_state("en" if target != "en" else "ru")
        proposal = await prepare(state)
        assert state.mark_recap_delivered(proposal["hold_id"])
        preferences = state.booking_inquiry
        state.observe_user_text(text)
        assert state.language == target and state.language_locked
        assert state.booking_inquiry == preferences
        assert (
            state.pending
            and not state.pending["delivery"]
            and not state.pending["approved"]
        )
        response = await state.dispatch(
            "confirm_slot_booking", {"hold_id": proposal["hold_id"]}
        )
        assert response["error"] == "consent_required" and not state.bookings

    asyncio.run(run())


@pytest.mark.parametrize(
    "text",
    [
        "Kas menüü on eesti keeles?",
        "Rääkige palun eesti keeles ja kinnitage broneering",
        "Inglise keeles menüü, palun",
        "Kas teil on inglise hommikusöök?",
    ],
)
def test_language_mentions_with_other_intents_are_not_explicit_switches(text):
    assert requested_language(text) is None


def test_native_estonian_opener_ignores_english_asr_metadata(make_state):
    pytest.importorskip("livekit.agents")
    from unittest.mock import patch

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
        state = make_state("en")
        agent = TelephoneAgent(state)
        model = UnusedModel()
        session = AgentSession(
            llm=model, tts=UnusedTTS(), turn_handling={"turn_detection": "manual"}
        )
        session.output.audio = Playback()
        session.on("conversation_item_added", agent.on_conversation_item_added)
        with patch("livekit.agents.Agent.default.tts_node", synthesize):
            await session.start(agent=agent, record=False)
            try:
                agent._detected_language = "english"
                await native_turn(session, agent, "Sooviksin homseks lauda neljale")
                assert state.language == "et" and state.language_locked
                assert trusted_booking_response(state) == {
                    "content": COPY["et"]["time"]
                }
                assert agent.chat_ctx.items[-1].text_content == COPY["et"]["time"]
                assert model.calls == 0 and not state.bookings
            finally:
                await session.aclose()

    asyncio.run(run())
