"""Day-part counterquestions explain a clock, never replace details or consent."""

import asyncio
from unittest.mock import patch

import pytest

from app.restaurant_call import COPY
from tests.test_restaurant_http import AUTH, start, turn

pytest_plugins = ["tests.test_restaurant_http", "tests.test_restaurant_conversation"]


@pytest.mark.parametrize(
    "context,question,expected",
    [
        ("fresh", "hommikul või õhtul?", "Millist kellaaega mõtlete?"),
        (
            "ambiguous",
            "hommikul või õhtul?",
            "06:00 tähendab kell kuus hommikul. 18:00 tähendab kell kuus õhtul.",
        ),
        (
            "ambiguous",
            "Kas mõtlete hommikul või õhtul?",
            "06:00 tähendab kell kuus hommikul. 18:00 tähendab kell kuus õhtul.",
        ),
        ("recap", "hommikul või õhtul?", "18:00 tähendab kell kuus õhtul."),
        ("recap", "Kas see on hommikul või õhtul?", "18:00 tähendab kell kuus õhtul."),
        (
            "recap",
            "Kas 18:00 on hommikul või õhtul?",
            "18:00 tähendab kell kuus õhtul.",
        ),
        (
            "recap",
            "Kas kell kuus on hommikul või õhtul?",
            "06:00 tähendab kell kuus hommikul. 18:00 tähendab kell kuus õhtul.",
        ),
    ],
)
def test_http_daypart_question_explains_without_losing_booking(
    client, context, question, expected
):
    session = start(client, "et")["session_id"]
    if context != "fresh":
        clock = "kuus" if context == "ambiguous" else "18:00"
        response = turn(
            client, session, "Soovin homme lauda neljale kell " + clock, language="et"
        )
        if context == "ambiguous":
            assert response["reply"] == COPY["et"]["ambiguous_time"]
        else:
            assert response.get("recap_delivery_id")
    state = client.app.state.demo_sessions.sessions[session].tools
    before, old_pending = state.booking_inquiry, state.pending
    old_receipt = response.get("recap_delivery_id") if old_pending else None
    response = turn(client, session, question, language="et")
    assert response["reply"].startswith(expected)
    assert state.booking_inquiry == before
    assert state.language == "et" and not state.bookings
    assert response["booking_changes"] == []
    if context == "ambiguous":
        assert state.pending is None
        assert response["reply"].endswith(COPY["et"]["ambiguous_time"])
        resolved = turn(client, session, "õhtul", language="et")
        assert (
            resolved.get("recap_delivery_id")
            and state.pending["recap"]["party_size"] == 4
        )
        assert state.booking_inquiry["start_time"] == "18:00"
        assert not state.bookings
    if old_pending:
        assert state.pending is not old_pending
        assert state.pending["hold_id"] == old_pending["hold_id"]
        assert state.pending["expires_at"] == old_pending["expires_at"]
        assert not state.pending["delivery"] and not state.pending["approved"]
        assert response.get("recap_delivery_id")
        stale = client.post(
            "/api/turn",
            json={
                "session_id": session,
                "language": "et",
                "text": "jah",
                "recap_delivery_id": old_receipt,
            },
            headers=AUTH,
        )
        assert stale.status_code == 409 and not state.bookings


@pytest.mark.parametrize(
    "question,expected",
    [
        (
            "Kas 06:30 on hommikul või õhtul?",
            "06:30 tähendab kell kuus kolmkümmend hommikul.",
        ),
        ("Kas 14:00 on hommikul või õhtul?", "14:00 tähendab kell kaks päeval."),
        ("Kas 12:00 on hommikul või õhtul?", "12:00 tähendab kell kaksteist päeval."),
        (
            "Kas kell 12:00 on hommikul või õhtul?",
            "12:00 tähendab kell kaksteist päeval.",
        ),
        ("Kas 00:00 on hommikul või õhtul?", "00:00 tähendab kell kaksteist öösel."),
        ("Kas 25:00 on hommikul või õhtul?", "Millist kellaaega mõtlete?"),
    ],
)
def test_explicit_clock_question_is_read_only_not_a_booking_request(
    client, question, expected
):
    session = start(client, "et")["session_id"]
    response = turn(client, session, question, language="et")
    assert response["reply"] == expected
    state = client.app.state.demo_sessions.sessions[session].tools
    assert (
        state.booking_inquiry is None and state.pending is None and not state.bookings
    )


@pytest.mark.parametrize("clock", ["kuus", "18:00"])
def test_daypart_opening_hours_question_preserves_booking(client, clock):
    session = start(client, "et")["session_id"]
    turn(client, session, "Soovin homme lauda neljale kell " + clock, language="et")
    state = client.app.state.demo_sessions.sessions[session].tools
    before = state.booking_inquiry
    response = turn(
        client, session, "Kas olete hommikul või õhtul avatud?", language="et"
    )
    assert response["reply"].startswith(
        "Esmaspäevast neljapäevani kell 12–21, reedel ja laupäeval kell 12–23 ning pühapäeval kell 12–20."
    )
    assert state.booking_inquiry == before and not state.bookings


def test_counterquestion_revokes_earlier_recap_delivery(make_state):
    from app.booking_response import trusted_booking_response
    from tests.test_restaurant_conversation import prepare

    async def run():
        state = make_state("et")
        await prepare(state, time="18:00")
        original = state.pending
        assert state.mark_recap_delivered(original["hold_id"])
        state.observe_user_text("Hommikul või õhtul?", language="et")
        assert state.guard_reply("invented", []).startswith(
            "18:00 tähendab kell kuus õhtul."
        )
        assert state.pending is not original
        assert original["delivery"]
        assert not state.pending["delivery"] and not state.pending["approved"]
        state.observe_user_text("jah", language="et")
        action = trusted_booking_response(state)
        assert action.get("name") != "confirm_slot_booking" and not state.bookings
        assert action["name"] == "plan_restaurant_reservation"
        assert action["arguments"]["start_time"] == "18:00"

    asyncio.run(run())


@pytest.mark.parametrize("asked_question", [False, True])
@pytest.mark.parametrize(
    "language,booking_request,question,daypart",
    [
        (
            "et",
            "Soovin homme lauda neljale kell 18:00",
            "Hommikul või õhtul?",
            "Õhtul.",
        ),
        (
            "et",
            "Soovin homme lauda neljale kell 18:00",
            "Hommikul või õhtul?",
            "Jah, õhtul.",
        ),
        (
            "en",
            "I'd like a table tomorrow at 18:00 for four people",
            "AM or PM?",
            "PM.",
        ),
        (
            "ru",
            "Хочу столик завтра в 18:00 для четырёх гостей",
            "Утром или вечером?",
            "Вечером.",
        ),
    ],
)
def test_exact_recap_accepts_same_daypart_without_discarding_clock(
    client, asked_question, language, booking_request, question, daypart
):
    session = start(client, language)["session_id"]
    response = turn(client, session, booking_request, language=language)
    assert response["recap_delivery_id"]
    state = client.app.state.demo_sessions.sessions[session].tools
    before = state.booking_inquiry
    if asked_question:
        turn(client, session, question, language=language)
    response = turn(client, session, daypart, language=language)
    assert state.booking_inquiry == before
    assert response["recap_delivery_id"] and not state.bookings
    assert not state.pending["approved"] and not state.pending["delivery"]


def test_conflicting_daypart_after_exact_recap_requires_new_clock(client):
    session = start(client, "et")["session_id"]
    turn(client, session, "Soovin homme lauda neljale kell 18:00", language="et")
    state = client.app.state.demo_sessions.sessions[session].tools
    before = state.booking_inquiry
    turn(client, session, "Hommikul või õhtul?", language="et")
    response = turn(client, session, "Hommikul.", language="et")
    assert state.booking_inquiry["date"] == before["date"]
    assert state.booking_inquiry["party_size"] == 4
    assert state.booking_inquiry.get("time_invalid") and not state.booking_inquiry.get(
        "start_time"
    )
    assert not state.pending and not state.bookings
    assert response["reply"] == COPY["et"]["invalid_time"]


@pytest.mark.parametrize(
    "daypart",
    ["Õhtul.", "Jah, õhtul.", "Hommikul.", "Mitte õhtul.", "Hommikul või õhtul sobib."],
)
def test_daypart_reply_never_confirms_a_delivered_exact_recap(make_state, daypart):
    from app.booking_response import trusted_booking_response
    from tests.test_restaurant_conversation import prepare

    async def run():
        state = make_state("et")
        await prepare(state, time="18:00")
        assert state.mark_recap_delivered(state.pending["hold_id"])
        state.observe_user_text(daypart, language="et")
        response = trusted_booking_response(state)
        assert response is None or response.get("name") != "confirm_slot_booking"
        assert not state.bookings

    asyncio.run(run())


@pytest.mark.parametrize(
    "anchor,answer,expected",
    [
        ("18:00", "PM", "18:00"),
        ("18:00", "AM", None),
        ("06:00", "PM", None),
        ("06:00", "AM", "06:00"),
        ("12:00", "PM", "12:00"),
        ("12:00", "AM", None),
        ("00:00", "PM", None),
        ("00:00", "AM", "00:00"),
        ("18:30", "õhtul", "18:30"),
        ("18:30", "hommikul", None),
        ("18:00", "18:00 PM", None),
        ("18:00", "AM or PM", None),
        ("18:00", "с шести до семи вечера", None),
        ("18:00", "not PM", None),
        ("18:00", "mitte õhtul", None),
        ("18:00", "At night.", "18:00"),
        ("06:00", "At night.", None),
    ],
)
def test_daypart_must_agree_with_a_single_exact_clock_anchor(anchor, answer, expected):
    from app.restaurant_times import parse_spoken_time

    result = parse_spoken_time(answer, pending=(anchor,))
    assert result is not None
    assert result.value == expected
    assert result.invalid is (expected is None)
    if expected is None:
        assert not result.candidates


@pytest.mark.parametrize(
    "language,booking_request,answer",
    [
        ("et", "Soovin homme lauda neljale kell 18:00", "Õhtul viiele."),
        ("et", "Soovin homme lauda neljale kell 18:00", "Hommikul viiele."),
        (
            "en",
            "I'd like a table tomorrow at 18:00 for four people",
            "PM for five people.",
        ),
        (
            "en",
            "I'd like a table tomorrow at 18:00 for four people",
            "AM for five people.",
        ),
        (
            "ru",
            "Хочу столик завтра в 18:00 для четырёх гостей",
            "Вечером для пяти гостей.",
        ),
        (
            "ru",
            "Хочу столик завтра в 18:00 для четырёх гостей",
            "Утром для пяти гостей.",
        ),
    ],
)
def test_mixed_daypart_and_count_cannot_turn_exact_clock_into_fake_choice(
    client, language, booking_request, answer
):
    session = start(client, language)["session_id"]
    turn(client, session, booking_request, language=language)
    state = client.app.state.demo_sessions.sessions[session].tools
    previous = state.booking_inquiry
    result = turn(client, session, answer, language=language)
    assert state.booking_inquiry["date"] == previous["date"]
    assert state.booking_inquiry["party_size"] == 5
    assert state.booking_inquiry["time_invalid"] and not state.booking_inquiry.get(
        "time_candidates"
    )
    assert result["reply"] == COPY[language]["invalid_time"]
    assert not state.pending and not state.bookings


@pytest.mark.parametrize(
    "question",
    [
        "Kas 18:00 on hommikul või õhtul? Muuda inimeste arv viieks.",
        "Hommikul või õhtul sobib.",
        "Mitte õhtul.",
        "Jah, aga hommikul või õhtul?",
        "Kas 18:00 ja kuus inimest on hommikul või õhtul?",
        "Kas kell 18:00 tühista broneering on hommikul või õhtul?",
    ],
)
def test_mixed_or_negated_daypart_wording_cannot_authorize_booking(
    make_state, question
):
    from app.booking_response import trusted_booking_response
    from tests.test_restaurant_conversation import prepare

    async def run():
        state = make_state("et")
        await prepare(state, time="18:00")
        assert state.mark_recap_delivered(state.pending["hold_id"])
        state.observe_user_text(question, language="et")
        response = trusted_booking_response(state)
        assert response is None or response.get("name") != "confirm_slot_booking"
        assert not state.bookings
        assert not (state.pending and state.pending["approved"])
        assert state._restaurant_focus != "time_meaning"

    asyncio.run(run())


@pytest.mark.parametrize(
    "language,booking_request,question,expected",
    [
        (
            "et",
            "Soovin homme lauda neljale kell 18:00",
            "Hommikul või õhtul?",
            "18:00 tähendab kell kuus õhtul.",
        ),
        (
            "en",
            "I'd like a table tomorrow at 18:00 for four people",
            "AM or PM?",
            "18:00 means 6:00 PM.",
        ),
        (
            "ru",
            "Хочу столик завтра в 18:00 для четырёх гостей",
            "Утром или вечером?",
            "18:00 — это шесть вечера.",
        ),
    ],
)
def test_native_daypart_counterquestion_reissues_owned_recap_without_model(
    make_state, language, booking_request, question, expected
):
    pytest.importorskip("livekit.agents")
    from livekit.agents import AgentSession
    from app import worker
    from tests.test_native_booking_terminals import (
        Playback,
        UnusedModel,
        UnusedTTS,
        native_turn,
        synthesize,
    )

    async def run():
        state = make_state(language)
        agent, model = worker.TelephoneAgent(state), UnusedModel()
        session = AgentSession(
            llm=model, tts=UnusedTTS(), turn_handling={"turn_detection": "manual"}
        )
        session.output.audio = Playback()
        session.on("conversation_item_added", agent.on_conversation_item_added)
        with patch("livekit.agents.Agent.default.tts_node", synthesize):
            await session.start(agent=agent, record=False)
            try:
                await native_turn(session, agent, booking_request)
                original, before = state.pending, state.booking_inquiry
                assert original and original["delivery"]
                await native_turn(session, agent, question)
                assert agent.chat_ctx.items[-1].text_content.startswith(expected)
                assert state.booking_inquiry == before
                assert (
                    state.pending is not original
                    and state.pending["hold_id"] == original["hold_id"]
                )
                assert state.pending["delivery"] and not state.pending["approved"]
                assert not state.bookings and model.calls == 0
                await native_turn(
                    session,
                    agent,
                    {"et": "Õhtul.", "en": "PM.", "ru": "Вечером."}[language],
                )
                assert state.booking_inquiry == before
                assert (
                    state.pending
                    and agent.chat_ctx.items[-1].text_content == state.render_recap()
                )
                assert state.pending["delivery"] and not state.pending["approved"]
                assert not state.bookings and model.calls == 0
            finally:
                await session.aclose()

    asyncio.run(run())
