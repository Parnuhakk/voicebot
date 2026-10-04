"""Real installed media SDK wiring with local provider/session doubles."""

import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, Mock, patch
from zoneinfo import ZoneInfo

import pytest

pytest.importorskip("livekit.agents")

from app import worker  # noqa: E402
from app.restaurant_call import RestaurantCallTools  # noqa: E402
from app.restaurant_call import COPY  # noqa: E402
from app.booking.restaurant import RestaurantAdapter  # noqa: E402
from app.business import restaurant_dispatcher  # noqa: E402
from app.call_factory import make_call_tools  # noqa: E402
from app.restaurant_data import load_restaurant_data  # noqa: E402
from app.input_recovery import REPEAT_PROMPT, WRITE_LANGUAGE_PROMPT  # noqa: E402
from livekit.agents import AgentSession  # noqa: E402
from tests.test_native_booking_terminals import (  # noqa: E402
    Playback,
    UnusedModel,
    UnusedTTS,
    native_turn,
    synthesize,
)


@pytest.mark.parametrize(
    "language,steps,questions",
    [
        (
            "et",
            ["Soovin lauda", "Homme", "14:00", "4"],
            ["Mis kell te avatud olete?", "Milline on menüü?", "Kus saab parkida?"],
        ),
        (
            "en",
            ["I'd like a table", "Tomorrow", "2 pm", "4"],
            [
                "What are your opening hours?",
                "What is on the menu?",
                "Where can I park?",
            ],
        ),
        (
            "ru",
            ["Хочу забронировать столик", "Завтра", "14:00", "4"],
            ["Какие у вас часы работы?", "Что есть в меню?", "Где парковка?"],
        ),
    ],
)
def test_native_booking_resumes_after_information_questions(
    tmp_path, language, steps, questions
):
    from app.languages import CONSENT

    async def run():
        data = load_restaurant_data()
        adapter = RestaurantAdapter(
            str(tmp_path / "interruptions.db"), data=data, allow_writes=True
        )
        state = make_call_tools(restaurant_dispatcher(adapter, data), language=language)
        agent, model = worker.TelephoneAgent(state), UnusedModel()
        session = AgentSession(
            llm=model, tts=UnusedTTS(), turn_handling={"turn_detection": "manual"}
        )
        session.output.audio = Playback()
        session.on("conversation_item_added", agent.on_conversation_item_added)
        with patch("livekit.agents.Agent.default.tts_node", synthesize):
            await session.start(agent=agent, record=False)
            try:
                for text, question, key in zip(
                    steps, questions, ["date", "time", "party"]
                ):
                    await native_turn(session, agent, text)
                    before = state.booking_inquiry
                    await native_turn(session, agent, question)
                    assert agent.chat_ctx.items[-1].text_content.endswith(
                        COPY[language][key]
                    )
                    assert state.booking_inquiry == before
                await native_turn(session, agent, steps[3])
                original, recap = state.pending, state.render_recap()
                assert original["delivery"] and not state.bookings
                await native_turn(session, agent, questions[1])
                assert state.pending is not original
                assert state.pending["hold_id"] == original["hold_id"]
                assert state.pending["delivery"] and not state.pending["approved"]
                assert agent.chat_ctx.items[-1].text_content.endswith(recap)
                await native_turn(session, agent, CONSENT[language])
                assert len(state.bookings) == 1 and model.calls == 0
                assert (
                    agent.chat_ctx.items[-1].text_content == COPY[language]["confirmed"]
                )
            finally:
                await session.aclose()

    asyncio.run(run())


@pytest.mark.parametrize("initial", ["et", "en", "ru"])
@pytest.mark.parametrize(
    "selected,utterances",
    [
        ("et", ["Tere! Soovin lauda broneerida.", "Homme", "Kell 14", "Meid on neli"]),
        ("en", ["Hi! I would like to book a table.", "Tomorrow", "2 pm", "Four"]),
        (
            "ru",
            [
                "Здравствуйте! Я хочу забронировать столик.",
                "Завтра",
                "В 14:00",
                "Нас будет четверо",
            ],
        ),
    ],
)
def test_native_session_keeps_first_caller_language_and_voice(
    tmp_path, initial, selected, utterances
):
    from app.languages import CONSENT
    from app.providers.voice_config import SpeechConfig

    async def run():
        data = load_restaurant_data()
        adapter = RestaurantAdapter(
            str(tmp_path / "language.db"), data=data, allow_writes=True
        )
        state = make_call_tools(restaurant_dispatcher(adapter, data), language=initial)
        updates = []
        config = SpeechConfig(mode=initial)
        provider = NS(update_options=lambda **options: updates.append(options))
        agent = worker.TelephoneAgent(
            state, speech_config=config, speech_provider=provider
        )
        model = UnusedModel()
        session = AgentSession(
            llm=model, tts=UnusedTTS(), turn_handling={"turn_detection": "manual"}
        )
        session.output.audio = Playback()
        session.on("conversation_item_added", agent.on_conversation_item_added)
        with patch("livekit.agents.Agent.default.tts_node", synthesize):
            await session.start(agent=agent, record=False)
            try:
                for text, metadata in zip(utterances, [initial, "ru", "en", "et"]):
                    agent._detected_language = metadata
                    await native_turn(session, agent, text)
                    assert state.language == selected and state.language_locked
                    assert f"Reply only in {selected}" in agent.instructions
                    voice, locale = config.voice_for(selected)
                    assert updates[-1] == {"voice": voice, "language": locale}
                assert state.pending["recap"]["party_size"] == 4
                assert state.booking_inquiry["start_time"] == "14:00"
                assert state.pending["delivery"] and not state.bookings
                agent._detected_language = "et" if selected != "et" else "en"
                await native_turn(session, agent, CONSENT[selected])
                assert state.language == selected and len(state.bookings) == 1
                assert (
                    agent.chat_ctx.items[-1].text_content == COPY[selected]["confirmed"]
                )
                assert model.calls == 0
            finally:
                await session.aclose()

    asyncio.run(run())


@pytest.mark.parametrize("weak", ["Yeah.", "Yep!"])
def test_native_short_acknowledgement_keeps_language_unselected(tmp_path, weak):
    async def run():
        data = load_restaurant_data()
        adapter = RestaurantAdapter(
            str(tmp_path / "weak-input.db"), data=data, allow_writes=True
        )
        state = make_call_tools(restaurant_dispatcher(adapter, data), language="et")
        agent, model = worker.TelephoneAgent(state), UnusedModel()
        session = AgentSession(
            llm=model, tts=UnusedTTS(), turn_handling={"turn_detection": "manual"}
        )
        session.output.audio = Playback()
        session.on("conversation_item_added", agent.on_conversation_item_added)
        with patch("livekit.agents.Agent.default.tts_node", synthesize):
            await session.start(agent=agent, record=False)
            try:
                agent._detected_language = "en"
                await native_turn(session, agent, weak)
                assert state.language == "et" and not state.language_locked
                assert not state.pending and not state.bookings
                agent._detected_language = "et"
                await native_turn(
                    session,
                    agent,
                    "Soovin homme lauda neljale inimesele kell kuus õhtul.",
                )
                assert state.language == "et" and state.language_locked
                assert state.pending["recap"]["party_size"] == 4
                assert state.pending["recap"]["start"].endswith("18:00:00")
                assert state.pending["delivery"] and not state.pending["approved"]
                assert not state.bookings and model.calls == 0
                assert agent.chat_ctx.items[-1].text_content.endswith(
                    COPY["et"]["confirmation_question"]
                )
            finally:
                await session.aclose()

    asyncio.run(run())


@pytest.mark.parametrize("initial_language", ["et", "en", "ru"])
@pytest.mark.parametrize(
    "language,utterance,confirmation",
    [
        ("et", "Soovin homme lauda neljale kell 14.00", "ja kinnitää"),
        ("et", "Soovin lauaks homseks kell 14.00 nelja inimesega", "ja kinnitää"),
        ("et", "Soovin homme lauda, meid on neli, kell kaks päeval", "ja kinnitää"),
        ("et", "Soovin homme lauda, tuleme neljakesi, pool kolm päeval", "ja kinnitää"),
        ("et", "named-date", "ja kinnitää"),
        ("en", "A table for four tomorrow at 2 pm", "Yes, please confirm."),
        ("et", "Soovin homme lauda neljale kell 14.00", "jah"),
        ("et", "Soovin homme lauda neljale kell 14.00", "sobib"),
        ("et", "Soovin homme lauda neljale kell 14.00", "Jah, super!"),
        (
            "et",
            "Soovin homme lauda neljale kell 14.00",
            "See sobib mulle väga hästi, aitäh!",
        ),
        ("en", "A table for four tomorrow at 2 pm", "yes"),
        ("en", "A table for four tomorrow at 2 pm", "That works for me, thank you!"),
        ("ru", "Столик на четверых завтра в 14:00", "да"),
        (
            "ru",
            "Столик на четверых завтра в 14:00",
            "Да, всё отлично, спасибо большое!",
        ),
        ("en", "named-date", "Yes, please confirm."),
        ("ru", "Столик на четверых завтра в 14:00", "Да, подтверждаю."),
        (
            "en",
            "A table for four tomorrow at six o'clock in the evening",
            "Yes, please confirm.",
        ),
        (
            "en",
            "Please reserve a table tomorrow at 1800 for four guests total.",
            "Yes, please confirm.",
        ),
        ("et", "Soovin homme lauda neljale kell 1800", "ja kinnitää"),
        ("et", "Soovin homme lauda neljale pool seitse õhtul", "ja kinnitää"),
        ("ru", "Столик на четверых завтра в шесть тридцать вечера", "Да, подтверждаю."),
        (
            "en",
            ("A table for four tomorrow at 6 o clock", "in the evening"),
            "Yes, please confirm.",
        ),
        ("et", ("Soovin homme lauda neljale pool seitse", "õhtul"), "ja kinnitää"),
        (
            "ru",
            ("Столик на четверых завтра полседьмого", "вечером"),
            "Да, подтверждаю.",
        ),
        ("ru", "named-date", "Да, подтверждаю."),
        ("ru", "mixed-date", "Да, подтверждаю."),
        (
            "et",
            ("Soovin lauda neljale", "kahe päeva pärast", "kell kuueks õhtul"),
            "ja kinnitää",
        ),
        (
            "en",
            ("A table for four", "in two days", "at six and a half PM"),
            "Yes, please confirm.",
        ),
        (
            "ru",
            ("Столик на четверых", "через два дня", "в половине седьмого вечера"),
            "Да, подтверждаю.",
        ),
    ],
)
def test_native_sdk_confirmation_is_visible_in_the_restaurant_database(
    tmp_path, language, utterance, confirmation, initial_language
):
    async def run():
        request_text = utterance
        if request_text in {"named-date", "mixed-date"}:
            from tests.test_restaurant_http import spoken_tomorrow

            day = spoken_tomorrow(language, mixed_case=request_text == "mixed-date")
            request_text = {
                "et": f"Soovin lauda {day} kell 14 nelja külalisega",
                "en": f"I'd like a table {day} at 2 pm for four",
                "ru": f"Забронируйте столик {day} в 14:00 для четырёх гостей",
            }[language]
        data = load_restaurant_data()
        path = str(tmp_path / "shared-restaurant.db")
        adapter = RestaurantAdapter(path, data=data, allow_writes=True)
        state = make_call_tools(
            restaurant_dispatcher(adapter, data), language=initial_language
        )
        agent = worker.TelephoneAgent(state)
        model = UnusedModel()
        session = AgentSession(
            llm=model, tts=UnusedTTS(), turn_handling={"turn_detection": "manual"}
        )
        session.output.audio = Playback()
        session.on("conversation_item_added", agent.on_conversation_item_added)
        with patch("livekit.agents.Agent.default.tts_node", synthesize):
            await session.start(agent=agent, record=False)
            try:
                requests = (
                    request_text if isinstance(request_text, tuple) else (request_text,)
                )
                for index, request_text in enumerate(requests):
                    await native_turn(session, agent, request_text)
                    if index < len(requests) - 1:
                        assert state.pending is None and not state.bookings
                        question = (
                            ("date", "time")[index]
                            if len(requests) == 3
                            else "ambiguous_time"
                        )
                        assert (
                            agent.chat_ctx.items[-1].text_content
                            == COPY[language][question]
                        )
                assert state.language == language
                assert state.pending["delivery"] and not state.pending["approved"]
                if len(requests) == 3:
                    assert datetime.fromisoformat(
                        state.pending["recap"]["start"]
                    ).strftime("%H:%M") == ("18:00" if language == "et" else "18:30")
                await native_turn(session, agent, confirmation)
                assert len(state.bookings) == 1
                assert (
                    agent.chat_ctx.items[-1].text_content == COPY[language]["confirmed"]
                )
                assert model.calls == 0
            finally:
                await session.aclose()
        # This is the same scoped reader used by the website, with a fresh
        # connection to the durable database rather than the call's memory.
        reader = RestaurantAdapter(path, data=data, allow_writes=False)
        day = (
            datetime.now(ZoneInfo("Europe/Tallinn")).date()
            + timedelta(days=2 if len(requests) == 3 else 1)
        ).isoformat()
        rows = (await reader.get_operator_bookings(day))["items"]
        assert len(rows) == 1 and rows[0]["status"] == "confirmed"
        assert rows[0]["service_id"] == 4
        assert str(rows[0]["id"]) in state.bookings

    asyncio.run(run())


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_native_sdk_repeats_once_then_requests_writing_and_resets(tmp_path, language):
    async def run():
        data = load_restaurant_data()
        adapter = RestaurantAdapter(
            str(tmp_path / "recovery.db"), data=data, allow_writes=True
        )
        state = make_call_tools(restaurant_dispatcher(adapter, data), language=language)
        agent = worker.TelephoneAgent(state)
        model = UnusedModel()
        session = AgentSession(
            llm=model, tts=UnusedTTS(), turn_handling={"turn_detection": "manual"}
        )
        session.output.audio = Playback()
        with patch("livekit.agents.Agent.default.tts_node", synthesize):
            await session.start(agent=agent, record=False)
            try:
                for expected in (
                    REPEAT_PROMPT[language],
                    WRITE_LANGUAGE_PROMPT[language],
                ):
                    agent._unsupported_language = True
                    await native_turn(
                        session, agent, "private-rejected-language-fixture"
                    )
                    assert agent.chat_ctx.items[-1].text_content == expected
                    assert not state.bookings and state.pending is None
                greeting = {"et": "Tere", "en": "Hello", "ru": "Здравствуйте"}[language]
                await native_turn(session, agent, greeting)
                assert state.input_recovery_reply is None
                agent._unsupported_language = True
                await native_turn(session, agent, "private-rejected-language-fixture")
                assert agent.chat_ctx.items[-1].text_content == REPEAT_PROMPT[language]
                assert model.calls == 0
                assert not any(
                    "private-rejected" in (item.text_content or "")
                    for item in agent.chat_ctx.items
                    if getattr(item, "role", None) == "user"
                )
            finally:
                await session.aclose()

    asyncio.run(run())


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_native_startup_uses_restaurant_policy_and_shared_database(tmp_path, language):
    async def run():
        callbacks = {}
        session = NS(
            on=lambda name, fn: callbacks.update({name: fn}),
            aclose=AsyncMock(),
            say=Mock(),
        )

        async def start(**kwargs):
            callbacks["close"](None)

        session.start = start
        ctx = NS(
            proc=NS(userdata={"vad": object()}),
            room=NS(
                on=Mock(),
                name="restaurant-fixture",
                local_participant=NS(set_attributes=AsyncMock()),
            ),
            connect=AsyncMock(),
            wait_for_participant=AsyncMock(),
            api=NS(room=NS(delete_room=AsyncMock())),
            shutdown=Mock(),
        )
        env = {
            "VOICEBOT_BUSINESS_TYPE": "restaurant",
            "RESTAURANT_DEMO_WRITES": "1",
            "RESTAURANT_STATE_DB": str(tmp_path / "restaurant.db"),
            "CALLS_DB": str(tmp_path / "calls.db"),
            "VOICEBOT_TELEPHONE_LANGUAGE": language,
            "VOICEBOT_TELEPHONE_DEMO": "1",
            "LIVEKIT_URL": "ws://localhost:7880",
            "LIVEKIT_API_KEY": "fixture",
            "LIVEKIT_API_SECRET": "fixture",
            "GROQ_API_KEY": "fixture",
            "AZURE_SPEECH_KEY": "fixture",
            "AZURE_REGION": "fixture",
        }
        with (
            patch.dict("os.environ", env, clear=True),
            patch.object(worker, "protect_logs"),
            patch.object(worker, "EasyAppointmentsAdapter") as legacy,
            patch.object(worker, "DemoStayAdapter") as rooms,
            patch.object(worker, "AgentSession", return_value=session),
            patch.object(
                worker, "TelephoneAgent", wraps=worker.TelephoneAgent
            ) as agent,
            patch.object(worker.callslog, "log_call"),
            patch.object(worker.callslog, "history_safe"),
            patch.object(
                worker.TelephoneSTT, "from_env", return_value=NS(aclose=AsyncMock())
            ),
            patch.object(worker.groq, "LLM"),
            patch.object(worker, "TelephoneTTS"),
            patch.object(worker, "play_failure", new_callable=AsyncMock) as failure,
        ):
            await worker.entrypoint(ctx)
        legacy.assert_not_called()
        rooms.assert_not_called()
        failure.assert_not_called()
        state = agent.call_args.args[0]
        assert isinstance(state, RestaurantCallTools)
        assert state.language == language
        assert state.dispatcher._slot.state_db == env["RESTAURANT_STATE_DB"]
        names = {tool["function"]["name"] for tool in state.conversation_tools()}
        assert names == {
            "get_restaurant_information",
            "plan_restaurant_reservation",
            "confirm_slot_booking",
            "cancel_slot_booking",
        }
        session.say.assert_called_once_with(state.greeting)
        ctx.shutdown.assert_called_once()

    asyncio.run(run())
