"""English reservation details retain trusted fields without granting consent."""

import asyncio
from datetime import date

import pytest

from app.booking_response import trusted_booking_response
from app.languages import CONSENT
from app.restaurant_call import COPY
from tests.test_restaurant_conversation import tomorrow
from tests.test_restaurant_http import start, turn

pytest_plugins = ["tests.test_restaurant_conversation", "tests.test_restaurant_http"]


@pytest.mark.parametrize("child_count", ["one", "1"])
def test_singular_child_is_included_in_the_total_party(make_state, child_count):
    state = make_state("en")
    state.observe_user_text(
        f"A table for two adults and {child_count} child tomorrow at 6 PM",
        language="en",
    )
    expected = {"date": tomorrow(), "start_time": "18:00", "party_size": 3}
    assert state.booking_inquiry == expected
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": expected,
    }
    assert not state.pending and not state.holds and not state.bookings


def test_singular_child_followup_keeps_the_requested_date_and_time(make_state):
    state = make_state("en")
    for text, question in [
        ("I'd like to reserve a table", "date"),
        ("Tomorrow", "time"),
        ("At 6 PM", "party"),
    ]:
        state.observe_user_text(text, language="en")
        assert state.guard_reply("", []) == COPY["en"][question]
    state.observe_user_text("Two adults and one child", language="en")
    assert state.booking_inquiry == {
        "date": tomorrow(),
        "start_time": "18:00",
        "party_size": 3,
    }
    assert trusted_booking_response(state)["arguments"] == state.booking_inquiry
    assert not state.pending and not state.bookings


@pytest.mark.parametrize("child", ["a child", "child"])
def test_child_without_a_numeric_count_requires_party_clarification(make_state, child):
    state = make_state("en")
    state.observe_user_text(
        f"A table for two adults and {child} tomorrow at 6 PM", language="en"
    )
    assert state.booking_inquiry == {"date": tomorrow(), "start_time": "18:00"}
    assert trusted_booking_response(state) == {"content": COPY["en"]["party"]}
    assert not state.pending and not state.holds and not state.bookings


UNACCOUNTED_COMPONENTS = [
    "two adults and one child plus two more children",
    "two adults and one child or two more children",
    "two adults and one child plus one more adult",
    "two adults and one child plus a child",
]


@pytest.mark.parametrize("components", UNACCOUNTED_COMPONENTS)
def test_unaccounted_guest_components_require_total_party_size(make_state, components):
    state = make_state("en")
    state.observe_user_text(f"A table for {components} tomorrow at 6 PM", language="en")
    assert state.booking_inquiry["date"] == tomorrow()
    assert state.booking_inquiry["start_time"] == "18:00"
    assert "party_size" not in state.booking_inquiry
    assert trusted_booking_response(state) == {"content": COPY["en"]["party"]}
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize("components", UNACCOUNTED_COMPONENTS)
def test_http_unaccounted_guests_never_prepare_an_undercounted_recap(
    client, components
):
    session = start(client, "en")["session_id"]
    answer = turn(client, session, f"A table for {components} tomorrow at 6 PM")
    assert answer["reply"] == COPY["en"]["party"]
    assert answer["recap_delivery_id"] is None
    assert answer["tools_used"] == 0 and answer["booking_changes"] == []
    state = client.app.state.demo_sessions.sessions[session].tools
    assert not state.pending and not state.holds and not state.bookings


def test_http_explicit_total_resolves_unaccounted_components(client):
    session = start(client, "en")["session_id"]
    clarification = turn(
        client,
        session,
        "A table for two adults and one child plus two more children tomorrow at 6 PM",
    )
    assert clarification["reply"] == COPY["en"]["party"]
    answer = turn(client, session, "Total five people.")
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.pending["recap"]["party_size"] == 5
    assert state.pending["recap"]["date"] == tomorrow()
    assert answer["recap_delivery_id"] and "for 5 guests" in answer["reply"]
    assert not state.pending["delivery"] and not state.pending["approved"]
    assert answer["booking_changes"] == [] and not state.bookings


def test_child_count_correction_revokes_the_previous_recap_approval(make_state):
    async def run():
        state = make_state("en")
        state.observe_user_text("A table for four tomorrow at 2 PM", language="en")
        action = trusted_booking_response(state)
        proposal = await state.dispatch(action["name"], action["arguments"])
        assert proposal.get("ok"), proposal
        assert state.mark_recap_delivered(proposal["hold_id"])
        state.observe_user_text(CONSENT["en"], language="en")
        assert state.pending["approved"]

        state.observe_user_text("Actually two adults and one child.", language="en")
        assert state.booking_inquiry == {
            "date": tomorrow(),
            "start_time": "14:00",
            "party_size": 3,
        }
        assert state.pending is None and state.render_recap() is None
        assert not state.mark_recap_delivered(proposal["hold_id"])
        result = await state.dispatch(
            "confirm_slot_booking", {"hold_id": proposal["hold_id"]}
        )
        assert result["error"] == "consent_required"
        assert not state.bookings
        assert not (await state.dispatcher._slot.get_operator_bookings(tomorrow()))[
            "items"
        ]

    asyncio.run(run())


@pytest.mark.parametrize(
    "correction", ["Actually seven PM", "Actually at seven PM instead"]
)
def test_english_time_correction_keeps_date_before_party_reply(make_state, correction):
    state = make_state("en")
    for text, question in [
        ("I'd like to reserve a table", "date"),
        ("Tomorrow", "time"),
        ("At 6 PM", "party"),
    ]:
        state.observe_user_text(text, language="en")
        assert state.guard_reply("", []) == COPY["en"][question]
    state.observe_user_text(correction, language="en")
    assert state.booking_inquiry == {"date": tomorrow(), "start_time": "19:00"}
    assert state.guard_reply("", []) == COPY["en"]["party"]
    state.observe_user_text("Four", language="en")
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": {
            "date": tomorrow(),
            "start_time": "19:00",
            "party_size": 4,
        },
    }
    assert not state.pending and not state.holds and not state.bookings


def test_ambiguous_english_time_correction_keeps_date_without_old_clock(make_state):
    state = make_state("en")
    for text in ["I'd like to reserve a table", "Tomorrow", "At 6 PM"]:
        state.observe_user_text(text, language="en")
        state.guard_reply("", [])
    state.observe_user_text("Actually at seven", language="en")
    assert state.booking_inquiry == {
        "date": tomorrow(),
        "time_candidates": ("07:00", "19:00"),
    }
    assert trusted_booking_response(state) == {"content": COPY["en"]["ambiguous_time"]}
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize("correction", ["Actually five.", "Actually 5."])
def test_bare_english_count_correction_replans_an_owned_recap(make_state, correction):
    async def run():
        state = make_state("en")
        state.observe_user_text("A table for four tomorrow at 2 PM", language="en")
        action = trusted_booking_response(state)
        original = await state.dispatch(action["name"], action["arguments"])
        assert original.get("ok"), original
        assert state.mark_recap_delivered(original["hold_id"])
        state.observe_user_text(CONSENT["en"], language="en")
        assert state.pending["approved"]

        state.observe_user_text(correction, language="en")
        expected = {"date": tomorrow(), "start_time": "14:00", "party_size": 5}
        assert state.booking_inquiry == expected
        assert state.pending is None and state.render_recap() is None
        assert not state.mark_recap_delivered(original["hold_id"])
        action = trusted_booking_response(state)
        assert action == {
            "name": "plan_restaurant_reservation",
            "arguments": expected,
        }
        updated = await state.dispatch(action["name"], action["arguments"])
        assert updated.get("ok"), updated
        assert updated["hold_id"] != original["hold_id"]
        assert state.pending["recap"] == updated["recap"]
        assert state.pending["recap"]["party_size"] == 5
        assert not state.pending["delivery"] and not state.pending["approved"]
        recap = state.render_recap()
        assert "for 5 guests" in recap and "2:00 PM" in recap
        assert COPY["en"]["confirmation_question"] in recap
        assert state.guard_reply("Your table for four is confirmed.", []) == recap
        assert not state.bookings
        assert not (await state.dispatcher._slot.get_operator_bookings(tomorrow()))[
            "items"
        ]

        assert state.mark_recap_delivered(updated["hold_id"])
        state.observe_user_text(CONSENT["en"], language="en")
        action = trusted_booking_response(state)
        assert action == {
            "name": "confirm_slot_booking",
            "arguments": {"hold_id": updated["hold_id"]},
        }
        confirmed = await state.dispatch(action["name"], action["arguments"])
        assert confirmed.get("ok"), confirmed
        assert confirmed["booking"]["party_size"] == 5
        rows = await state.dispatcher._slot.get_operator_bookings(tomorrow())
        assert len(rows["items"]) == 1 and rows["items"][0]["service_id"] == 5

    asyncio.run(run())


@pytest.mark.parametrize(
    "correction,clock",
    [
        ("Actually five PM.", {"start_time": "17:00"}),
        ("Actually at five.", {"time_candidates": ("05:00", "17:00")}),
    ],
)
def test_clock_markers_cannot_correct_the_party_count(make_state, correction, clock):
    state = make_state("en")
    state.observe_user_text("A table for four tomorrow at 2 PM", language="en")
    state.observe_user_text(correction, language="en")
    assert state.booking_inquiry == {"date": tomorrow(), "party_size": 4, **clock}
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize(
    "correction,fields",
    [
        ("Actually we are five.", {"party_size"}),
        ("Actually next Friday at 14:00.", {"date", "start_time"}),
    ],
)
def test_non_clock_correction_cannot_inherit_unspoken_booking_fields(
    make_state, correction, fields
):
    state = make_state("en")
    state.observe_user_text("A table for four tomorrow at 2 PM", language="en")
    state.observe_user_text(correction, language="en")
    assert set(state.booking_inquiry) == fields
    if "party_size" in fields:
        assert state.booking_inquiry["party_size"] == 5
    else:
        assert state.booking_inquiry["start_time"] == "14:00"
        assert date.fromisoformat(state.booking_inquiry["date"]).weekday() == 4
    assert "name" not in (trusted_booking_response(state) or {})
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize(
    "correction",
    [
        "Actually five and yes confirm",
        "Actually two adults and one child and yes confirm",
    ],
)
def test_mixed_correction_and_consent_never_confirms_a_proposal(make_state, correction):
    async def run():
        state = make_state("en")
        state.observe_user_text("A table for four tomorrow at 2 PM", language="en")
        action = trusted_booking_response(state)
        original = await state.dispatch(action["name"], action["arguments"])
        assert original.get("ok"), original
        assert state.mark_recap_delivered(original["hold_id"])
        state.observe_user_text(CONSENT["en"], language="en")
        assert state.pending["approved"]

        state.observe_user_text(correction, language="en")
        assert state.pending is None and state.render_recap() is None
        assert not state.mark_recap_delivered(original["hold_id"])
        assert "name" not in (trusted_booking_response(state) or {})
        rejected = await state.dispatch(
            "confirm_slot_booking", {"hold_id": original["hold_id"]}
        )
        assert rejected["error"] == "consent_required"

        state.observe_user_text("A table for five tomorrow at 2 PM", language="en")
        action = trusted_booking_response(state)
        prepared = await state.dispatch(action["name"], action["arguments"])
        assert prepared.get("ok"), prepared
        state.observe_user_text(CONSENT["en"], language="en")
        assert state.pending is None
        rejected = await state.dispatch(
            "confirm_slot_booking", {"hold_id": prepared["hold_id"]}
        )
        assert rejected["error"] == "consent_required"
        assert not state.bookings
        assert not (await state.dispatcher._slot.get_operator_bookings(tomorrow()))[
            "items"
        ]

        state.observe_user_text("A table for five tomorrow at 2 PM", language="en")
        action = trusted_booking_response(state)
        updated = await state.dispatch(action["name"], action["arguments"])
        assert updated.get("ok"), updated
        assert not state.pending["delivery"] and not state.pending["approved"]
        assert state.mark_recap_delivered(updated["hold_id"])
        state.observe_user_text(CONSENT["en"], language="en")
        action = trusted_booking_response(state)
        assert action["name"] == "confirm_slot_booking"
        confirmed = await state.dispatch(action["name"], action["arguments"])
        assert confirmed.get("ok"), confirmed
        assert confirmed["booking"]["party_size"] == 5
        rows = await state.dispatcher._slot.get_operator_bookings(tomorrow())
        assert len(rows["items"]) == 1

    asyncio.run(run())


@pytest.mark.parametrize(
    "components",
    ["two adults and one hundred child", "two adults and hundred one child"],
)
def test_malformed_child_count_never_uses_a_smaller_total(make_state, components):
    state = make_state("en")
    state.observe_user_text(f"A table for {components} tomorrow at 6 PM", language="en")
    assert "party_size" not in state.booking_inquiry
    assert trusted_booking_response(state) == {"content": COPY["en"]["party"]}
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize(
    "texts,party,clock",
    [
        (["A table for two adults and one child tomorrow at 6 PM"], 3, "6:00 PM"),
        (
            [
                "I'd like to reserve a table",
                "Tomorrow",
                "At 6 PM",
                "Actually seven PM",
                "Four",
            ],
            4,
            "7:00 PM",
        ),
        (["A table for four tomorrow at 2 PM", "Actually five."], 5, "2:00 PM"),
    ],
)
def test_http_english_details_reach_the_canonical_recap(client, texts, party, clock):
    session = start(client, "en")["session_id"]
    for text in texts:
        result = turn(client, session, text)
        assert result["language"] == "en"
        assert result["booking_changes"] == [] and result["booking_ids"] == []
        assert result["warnings"] == [] and not result["fallback_used"]
        assert result["reply"] == client.provider.spoken[-1]
    state = client.app.state.demo_sessions.sessions[session].tools
    assert result["recap_delivery_id"]
    assert result["reply"] == state.render_recap()
    assert f"for {party} guests" in result["reply"] and clock in result["reply"]
    assert state.pending["recap"]["party_size"] == party
    assert state.pending["recap"]["date"] == tomorrow()
    assert not state.pending["delivery"] and not state.pending["approved"]
    assert not state.bookings
