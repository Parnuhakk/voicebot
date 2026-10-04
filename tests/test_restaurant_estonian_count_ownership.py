"""Clock/date numbers and partial compounds cannot masquerade as diner totals."""

import pytest

from app.booking_response import trusted_booking_response
from app.restaurant_call import parse_restaurant_request
from tests.test_restaurant_estonian_field_turns import (
    NOW,
    finalized_turns,
    fixed_dialogue_date,  # noqa: F401 - shared autouse pytest fixture
)

pytest_plugins = ["tests.test_restaurant_conversation"]


CLOCK_REQUESTS = [
    ("Soovin homme lauda, tuleme 6:30 õhtul", "18:30"),
    ("Soovin homme lauda, tuleme kuue ajal õhtul", "18:00"),
    ("Soovin homme lauda, meid on 6:30 õhtul", "18:30"),
    ("Soovin homme lauda, tuleme 6:30 õhtul ja tuleme 6:30 õhtul", "18:30"),
]


@pytest.mark.parametrize("text,clock", CLOCK_REQUESTS)
def test_clock_span_is_owned_before_any_diner_candidate(text, clock):
    assert parse_restaurant_request(text, now=NOW) == {
        "date": "2026-10-05",
        "start_time": clock,
    }


@pytest.mark.parametrize("channel", ["shared", "native"])
@pytest.mark.parametrize("text,clock", CLOCK_REQUESTS)
def test_finalized_clock_reply_cannot_complete_an_unspoken_party(
    make_state, channel, text, clock
):
    state = make_state()
    finalized_turns(state, [text], channel)
    assert state.booking_inquiry == {"date": "2026-10-05", "start_time": clock}
    assert "name" not in (trusted_booking_response(state) or {})
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize("channel", ["shared", "native"])
@pytest.mark.parametrize("text,clock", CLOCK_REQUESTS)
def test_count_beside_a_clock_is_not_lost_with_the_owned_temporal_span(
    make_state, channel, text, clock
):
    state = make_state()
    finalized_turns(state, [text + " neljale"], channel)
    expected = {"date": "2026-10-05", "start_time": clock, "party_size": 4}
    assert state.booking_inquiry == expected
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": expected,
    }
    assert not state.pending and not state.bookings


COMPOUNDS = [
    "kahekümne ühele inimesele",
    "kahekümne kolmele",
    "kolmekümne neljale inimesele",
    "saja ühele inimesele",
    "meid on kahekümne ühele inimesele",
]


@pytest.mark.parametrize("count", COMPOUNDS)
def test_partial_compound_cannot_be_reserved_for_its_final_unit(count):
    inquiry = parse_restaurant_request(
        f"Soovin homme lauda {count} kell 18:30", now=NOW
    )
    assert "party_size" not in inquiry
    assert inquiry.get("party_invalid")


@pytest.mark.parametrize("channel", ["shared", "native"])
@pytest.mark.parametrize("count", COMPOUNDS)
def test_native_and_shared_partial_compound_never_plan_a_smaller_party(
    make_state, channel, count
):
    state = make_state()
    finalized_turns(state, [f"Soovin homme lauda {count} kell 18:30"], channel)
    assert "party_size" not in (state.booking_inquiry or {})
    assert "name" not in (trusted_booking_response(state) or {})
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize("channel", ["shared", "native"])
@pytest.mark.parametrize("count", COMPOUNDS)
def test_partial_compound_correction_cannot_reuse_an_old_diner_total(
    make_state, channel, count
):
    state = make_state()
    finalized_turns(
        state, ["Soovin homme lauda kell 18:30 neljale", "tegelikult " + count], channel
    )
    assert "party_size" not in (state.booking_inquiry or {})
    assert "name" not in (trusted_booking_response(state) or {})
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize(
    "count", ["neljale või viiele", "neljale kuni viiele", "neljakesi või viiekesi"]
)
def test_explicit_diner_case_forms_own_their_alternative_range(count):
    inquiry = parse_restaurant_request(
        f"Soovin homme lauda kell 18:30 {count}", now=NOW
    )
    assert "party_size" not in inquiry
    assert inquiry.get("party_invalid")


@pytest.mark.parametrize("channel", ["shared", "native"])
def test_unrecognized_adjacent_clock_numbers_are_not_a_diner_total(make_state, channel):
    state = make_state()
    finalized_turns(
        state,
        ["Soovin homme lauda, meid tuleb kuue kolmekümneks õhtul", "kell 18:30"],
        channel,
    )
    assert "party_size" not in (state.booking_inquiry or {})
    assert "name" not in (trusted_booking_response(state) or {})
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize("channel", ["shared", "native"])
@pytest.mark.parametrize(
    "clock",
    [
        "6:30 või 7:30",
        "6:30-7:30",
        "mitte 6:30",
        "6:99",
        "6:30 kolmekümneks või tuleme 5:30",
        "6:30 kolmekümneks või tuleme 5:30 kolmekümneks",
        "umbes kell 18:00 ja tuleme 6:30",
        "kell 1800-1900 ja tuleme 6:30",
    ],
)
def test_invalid_clock_then_valid_clock_still_requires_a_real_diner_count(
    make_state, channel, clock
):
    state = make_state()
    finalized_turns(
        state,
        [f"Soovin homme lauda, tuleme {clock} õhtul", "kell 18:30"],
        channel,
    )
    assert "party_size" not in (state.booking_inquiry or {})
    assert "name" not in (trusted_booking_response(state) or {})
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize("channel", ["shared", "native"])
@pytest.mark.parametrize(
    "utterance",
    [
        "Soovin homme lauda neljale, tuleme 6:30 või 7:30 õhtul",
        "Soovin homme lauda, tuleme 6:30 neljale või 7:30 õhtul",
        "Soovin homme lauda, tuleme 6:30 või 7:30 õhtul neljale",
        "Soovin homme lauda, tuleme 6:30 neljale ja tuleme 6:30 õhtul",
    ],
)
def test_conflicting_temporal_spans_do_not_hide_an_unrelated_explicit_diner_count(
    make_state, channel, utterance
):
    state = make_state()
    finalized_turns(state, [utterance, "kell 18:30"], channel)
    expected = {"date": "2026-10-05", "start_time": "18:30", "party_size": 4}
    assert state.booking_inquiry == expected
    assert trusted_booking_response(state)["arguments"] == expected
    assert not state.pending and not state.holds and not state.bookings


COMPONENT_COMPOUNDS = [
    "kahekümne ühe täiskasvanu ja kaks last",
    "kaks täiskasvanut ja kahekümne ühe last",
    "kahekümne ühe täiskasvanu ja kaks last, kokku kolm inimest",
    "meid on neli, neist kahekümne ühele last",
    "kaks täiskasvanut ja kaks last, kokku kahekümne ühele",
]


@pytest.mark.parametrize("count", COMPONENT_COMPOUNDS)
def test_component_and_total_compounds_cannot_be_cherry_picked(count):
    inquiry = parse_restaurant_request(
        f"Soovin homme lauda {count} kell 18:30", now=NOW
    )
    assert "party_size" not in inquiry
    assert inquiry.get("party_invalid")


@pytest.mark.parametrize("channel", ["shared", "native"])
@pytest.mark.parametrize("count", COMPONENT_COMPOUNDS)
def test_finalized_component_compounds_never_plan_for_their_smaller_sum(
    make_state, channel, count
):
    state = make_state()
    finalized_turns(state, [f"Soovin homme lauda {count} kell 18:30"], channel)
    assert "party_size" not in (state.booking_inquiry or {})
    assert "name" not in (trusted_booking_response(state) or {})
    assert not state.pending and not state.holds and not state.bookings


@pytest.mark.parametrize("channel", ["shared", "native"])
@pytest.mark.parametrize(
    "count",
    [
        "kaks täiskasvanut ja kaks last",
        "meid on neli, neist kaks last",
        "kaks täiskasvanut ja kaks last, kokku neli inimest",
    ],
)
def test_real_component_counts_are_not_temporal_or_compound_prefixes(
    make_state, channel, count
):
    state = make_state()
    finalized_turns(state, [f"Soovin homme lauda {count} kell 18:30"], channel)
    expected = {"date": "2026-10-05", "start_time": "18:30", "party_size": 4}
    assert state.booking_inquiry == expected
    assert trusted_booking_response(state)["arguments"] == expected
    assert not state.pending and not state.holds and not state.bookings
