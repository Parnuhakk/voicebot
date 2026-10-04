"""Natural Estonian field replies must survive the finalized telephone policy."""

import asyncio
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from app.booking_response import trusted_booking_response
from app.restaurant_call import COPY, parse_restaurant_request

pytest_plugins = ["tests.test_restaurant_conversation"]
NOW = datetime(2026, 10, 4, 12, tzinfo=ZoneInfo("Europe/Tallinn"))


@pytest.fixture(autouse=True)
def fixed_dialogue_date(monkeypatch):
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz) if tz else NOW.replace(tzinfo=None)

    monkeypatch.setattr("app.restaurant_call.datetime", Clock)


def finalized_turns(state, texts, channel, *, unsupported_last=False):
    async def run():
        if channel == "native":
            agents = pytest.importorskip("livekit.agents")
            from app.worker import TelephoneAgent

            agent = TelephoneAgent(state)
        for index, text in enumerate(texts):
            unsupported = unsupported_last and index == len(texts) - 1
            if channel == "native":
                agent._detected_language = "et" if not unsupported else "und"
                agent._unsupported_language = unsupported
                message = agents.llm.ChatMessage(role="user", content=[text])
                await agent.on_user_turn_completed(agents.llm.ChatContext(), message)
                if unsupported:
                    assert not message.text_content
            else:
                state.observe_user_text(
                    text,
                    detected_language="et" if not unsupported else "und",
                    unsupported=unsupported,
                )
            state.guard_reply("", [])

    asyncio.run(run())


@pytest.mark.parametrize("channel", ["shared", "native"])
@pytest.mark.parametrize(
    "answer,expected",
    [
        ("tegelikult kell 19:00", {"date": "2026-10-05", "start_time": "19:00"}),
        (
            "tegelikult kuuendal oktoobril",
            {"date": "2026-10-06", "start_time": "18:30"},
        ),
        (
            "hoopis viiele",
            {"date": "2026-10-05", "start_time": "18:30", "party_size": 5},
        ),
        (
            "nelja inimese jaoks",
            {"date": "2026-10-05", "start_time": "18:30", "party_size": 4},
        ),
        ("seitsmekesi", {"date": "2026-10-05", "start_time": "18:30", "party_size": 7}),
        (
            "üheteistkümnele inimesele",
            {"date": "2026-10-05", "start_time": "18:30", "party_size": 11},
        ),
        (
            "kaheteistkümnele",
            {"date": "2026-10-05", "start_time": "18:30", "party_size": 12},
        ),
    ],
)
def test_field_correction_retains_unrelated_incomplete_booking_fields(
    make_state, channel, answer, expected
):
    state = make_state()
    finalized_turns(
        state,
        ["Soovin lauda broneerida", "homme", "kell 18:30", answer],
        channel,
    )
    assert state.booking_inquiry == expected
    action = trusted_booking_response(state)
    if "party_size" in expected:
        assert action == {"name": "plan_restaurant_reservation", "arguments": expected}
    else:
        assert action == {"content": COPY["et"]["party"]}
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize("channel", ["shared", "native"])
@pytest.mark.parametrize("missing", ["date", "time"])
def test_explicit_diner_allative_cannot_supply_a_missing_date_or_clock(
    make_state, channel, missing
):
    state = make_state()
    supplied = "kell 18:30" if missing == "date" else "homme"
    expected = {"start_time": "18:30"} if missing == "date" else {"date": "2026-10-05"}
    finalized_turns(
        state,
        ["Soovin lauda broneerida", supplied, "meid on kaks", "neljale"],
        channel,
    )
    assert state.booking_inquiry == {**expected, "party_size": 4}
    if missing == "time":
        finalized_turns(state, ["õhtul"], channel)
        assert "start_time" not in (state.booking_inquiry or {})
    assert "name" not in (trusted_booking_response(state) or {})
    assert not state.pending and not state.bookings


@pytest.mark.parametrize("channel", ["shared", "native"])
@pytest.mark.parametrize(
    "clock", ["kella kuue kolmekümneks õhtul", "kella kaheksateistkümne kolmekümneks"]
)
def test_inflected_minutes_are_exact_in_the_finalized_inquiry(
    make_state, channel, clock
):
    state = make_state()
    finalized_turns(
        state, ["Soovin lauda broneerida", "homme", clock, "neljale"], channel
    )
    expected = {"date": "2026-10-05", "start_time": "18:30", "party_size": 4}
    assert state.booking_inquiry == expected
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": expected,
    }
    assert not state.pending and not state.bookings


@pytest.mark.parametrize("channel", ["shared", "native"])
def test_named_month_completion_keeps_the_explicit_owned_year(make_state, channel):
    state = make_state()
    finalized_turns(
        state,
        [
            "Soovin lauda broneerida",
            "kell 18:30",
            "meid on neli",
            "oktoobris 2027. aastal",
            "viiendal oktoobril",
        ],
        channel,
    )
    expected = {"date": "2027-10-05", "start_time": "18:30", "party_size": 4}
    assert state.booking_inquiry == expected
    assert trusted_booking_response(state)["arguments"] == expected
    assert not state.pending and not state.bookings


@pytest.mark.parametrize(
    "count,party",
    [("üheksale", 9), ("kümnele", 10), ("üheteistkümnele", 11), ("kahekümnele", 20)],
)
def test_one_shot_allatives_are_counts_not_clock_minutes(count, party):
    assert parse_restaurant_request(f"Soovin homme lauda kell 18 {count}", now=NOW) == {
        "date": "2026-10-05",
        "start_time": "18:00",
        "party_size": party,
    }


@pytest.mark.parametrize("channel", ["shared", "native"])
def test_supported_count_text_with_unsupported_source_is_not_a_booking_detail(
    make_state, channel
):
    state = make_state()
    finalized_turns(
        state,
        ["Soovin lauda broneerida", "homme", "kell 18:30", "nelja inimese jaoks"],
        channel,
        unsupported_last=True,
    )
    assert state.unsupported_language
    assert "name" not in (trusted_booking_response(state) or {})
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize("channel", ["shared", "native"])
@pytest.mark.parametrize(
    "answer",
    [
        "tegelikult kell 19:00 ja tee erand",
        "nelja inimese jaoks kui tasuta",
        "hoopis viiele, aga ära kinnita",
    ],
)
def test_unknown_neighboring_clauses_cannot_inherit_complete_booking_fields(
    make_state, channel, answer
):
    state = make_state()
    finalized_turns(
        state, ["Soovin lauda broneerida", "homme", "kell 18:30", answer], channel
    )
    action = trusted_booking_response(state) or {}
    assert "name" not in action
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize(
    "answer,party", [("hoopis viiele", 5), ("nelja inimese jaoks", 4)]
)
def test_native_sdk_prepares_the_exact_corrected_recap_before_later_consent(
    make_state, answer, party
):
    agents = pytest.importorskip("livekit.agents")
    from app.languages import CONSENT
    from app.worker import TelephoneAgent
    from tests.test_native_booking_terminals import (
        Playback,
        UnusedModel,
        UnusedTTS,
        native_turn,
        synthesize,
    )
    from tests.test_restaurant_conversation import tomorrow

    async def run():
        # The real reservation adapter uses the real calendar, unlike extraction.
        with patch("app.restaurant_call.datetime", datetime):
            state = make_state()
            agent, model = TelephoneAgent(state), UnusedModel()
            session = agents.AgentSession(
                llm=model, tts=UnusedTTS(), turn_handling={"turn_detection": "manual"}
            )
            session.output.audio = Playback()
            session.on("conversation_item_added", agent.on_conversation_item_added)
            with patch("livekit.agents.Agent.default.tts_node", synthesize):
                await session.start(agent=agent, record=False)
                try:
                    for text in (
                        "Soovin lauda broneerida",
                        "homme",
                        "kella kuue kolmekümneks õhtul",
                        answer,
                    ):
                        agent._detected_language = "et"
                        await native_turn(session, agent, text)
                    assert state.pending["recap"]["date"] == tomorrow()
                    assert state.pending["recap"]["start"].endswith("18:30:00")
                    assert state.pending["recap"]["party_size"] == party
                    assert state.pending["delivery"] and not state.bookings
                    assert model.calls == 0
                    agent._detected_language = "et"
                    await native_turn(session, agent, CONSENT["et"])
                    assert len(state.bookings) == 1 and model.calls == 0
                    assert agent.chat_ctx.items[-1].text_content.startswith(
                        COPY["et"]["confirmed"]
                    )
                finally:
                    await session.aclose()

    asyncio.run(run())


@pytest.mark.parametrize("count", ["seitsmekesi", "üheteistkümnele inimesele"])
def test_recognized_large_party_does_not_override_the_restaurant_capacity(
    make_state, count
):
    from tests.test_restaurant_conversation import tomorrow

    async def run():
        with patch("app.restaurant_call.datetime", datetime):
            state = make_state()
            for text in ("Soovin lauda broneerida", "homme", "kell 18:30", count):
                state.observe_user_text(text, detected_language="et")
                state.guard_reply("", [])
            action = trusted_booking_response(state)
            assert action["arguments"]["date"] == tomorrow()
            assert (
                action["arguments"]["party_size"]
                > state.restaurant["maximum_party_size"]
            )
            result = await state.dispatch(action["name"], action["arguments"])
            assert result.get("error") and not result.get("ok")
            assert not state.pending and not state.holds and not state.bookings

    asyncio.run(run())
