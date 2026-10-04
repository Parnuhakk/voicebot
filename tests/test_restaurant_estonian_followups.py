"""Bounded Estonian followups reuse owned booking and read-only venue policy."""

import asyncio

import pytest

from app.booking_response import trusted_booking_response
from app.restaurant_call import COPY, parse_restaurant_request
from app.restaurant_consent import is_restaurant_confirmation
from tests import test_restaurant_conversation
from tests.test_restaurant_conversation import prepare, tomorrow

make_state = test_restaurant_conversation.make_state


async def turn(state, text):
    state.observe_user_text(text, language="et")
    action = trusted_booking_response(state)
    if action and "name" in action:
        result = await state.dispatch(action["name"], action["arguments"])
        assert not result.get("error"), result
        reply = state.guard_reply("", [result])
    else:
        reply = state.guard_reply(action.get("content", "") if action else "", [])
    return action, reply


async def confirmed(state):
    proposal = await prepare(state)
    assert state.mark_recap_delivered(proposal["hold_id"])
    await turn(state, "Jah, kinnitan")
    assert len(state.bookings) == 1
    return state.last_booking


@pytest.mark.parametrize(
    "detail",
    [
        "Neli palun",
        "Neli, palun",
        "Palun neli",
        "Meid oleks neli",
        "Meid on neli, neist kaks last",
        "Meid oleks 4, neist 2 last",
    ],
)
def test_polite_party_followups_keep_exact_requested_fields(make_state, detail):
    async def run():
        state = make_state()
        for text in ("Soovin lauda broneerida", "Homme", "Kell 14"):
            await turn(state, text)
        action, reply = await turn(state, detail)
        assert action == {
            "name": "plan_restaurant_reservation",
            "arguments": {"date": tomorrow(), "start_time": "14:00", "party_size": 4},
        }
        assert state.pending["recap"]["party_size"] == 4
        assert "4 inimesele" in reply and not state.bookings

    asyncio.run(run())


@pytest.mark.parametrize(
    "detail",
    [
        "Meid on neli, neist viis last",
        "Meid oleks 4, neist 5 last",
    ],
)
def test_child_subset_cannot_exceed_total_or_leave_old_party(make_state, detail):
    prior = {"date": tomorrow(), "start_time": "14:00", "party_size": 4}
    parsed = parse_restaurant_request(detail, prior, expected_field="party")
    assert parsed == {"date": tomorrow(), "start_time": "14:00", "party_invalid": True}
    state = make_state()
    state.observe_user_text("Soovin homme lauda neljale kell 14", language="et")
    state.guard_reply("", [])
    state.observe_user_text(detail, language="et")
    assert state.booking_inquiry == parsed
    assert trusted_booking_response(state) == {"content": COPY["et"]["party"]}
    result = asyncio.run(state.dispatch("plan_restaurant_reservation", prior))
    assert result == {"error": "clarification_required"}
    assert not state.pending and not state.bookings


@pytest.mark.parametrize(
    "detail", ["Neli palun ja kinnita kohe", "Neli palun kui saab"]
)
def test_unparsed_words_are_not_a_whole_party_followup(make_state, detail):
    state = make_state()
    state.observe_user_text("Soovin homme lauda kell 14", language="et")
    state.guard_reply("", [])
    state.observe_user_text(detail, language="et")
    action = trusted_booking_response(state)
    assert not action or "name" not in action
    assert not state.pending and not state.bookings


@pytest.mark.parametrize("detail", ["Viis", "5"])
def test_bare_count_replacement_already_requires_new_delivery(make_state, detail):
    async def run():
        state = make_state()
        first = await prepare(state)
        state.guard_reply("", [first])
        assert state.mark_recap_delivered(first["hold_id"])
        action, reply = await turn(state, detail)
        assert action["arguments"] == {
            "date": tomorrow(),
            "start_time": "14:00",
            "party_size": 5,
        }
        assert "5 inimesele" in reply and not state.bookings
        assert not state.mark_recap_delivered(first["hold_id"])
        state.observe_user_text("Jah, kinnitan", language="et")
        assert not (state.pending and state.pending["approved"])
        assert not state.bookings

    asyncio.run(run())


AGREEMENTS = ("Jah nii sobib", "Täitsa sobib", "Kõlab hästi")


@pytest.mark.parametrize("text", AGREEMENTS)
def test_bounded_affirmative_saves_one_owned_delivered_booking(make_state, text):
    assert is_restaurant_confirmation(text, "et")

    async def run():
        state = make_state()
        proposal = await prepare(state)
        assert state.mark_recap_delivered(proposal["hold_id"])
        action, reply = await turn(state, text)
        assert action["name"] == "confirm_slot_booking"
        assert reply.startswith(COPY["et"]["confirmed"]) and len(state.bookings) == 1

    asyncio.run(run())


@pytest.mark.parametrize("text", AGREEMENTS)
@pytest.mark.parametrize("boundary", ["undelivered", "expired", "partial", "foreign"])
def test_new_affirmatives_do_not_bypass_delivery_or_ownership(
    make_state, text, boundary
):
    async def run():
        owner = make_state()
        proposal = await prepare(owner)
        if boundary != "undelivered":
            assert owner.mark_recap_delivered(proposal["hold_id"])
        state = make_state() if boundary == "foreign" else owner
        if boundary == "expired":
            state.pending["expires_at"] = 0
        state.observe_user_text(text, language="et", is_final=boundary != "partial")
        action = trusted_booking_response(state)
        assert not action or action.get("name") != "confirm_slot_booking"
        rejected = await state.dispatch(
            "confirm_slot_booking", {"hold_id": proposal["hold_id"]}
        )
        assert rejected.get("error") and not state.bookings

    asyncio.run(run())


@pytest.mark.parametrize(
    "text",
    [
        "Ei, nii sobib",
        "Ei, täitsa sobib",
        "Täitsa sobib?",
        "Kõlab hästi?",
        "Kas kõlab hästi",
        "Kas nii sobib",
        "Jah nii sobib kui hind sobib",
        "Kõlab hästi, aga viiele",
        "Täitsa sobib homme kell 18",
        '"Kõlab hästi"',
    ],
)
def test_affirmative_modifiers_cannot_hide_negatives_conditions_or_questions(
    make_state, text
):
    assert not is_restaurant_confirmation(text, "et")

    async def run():
        state = make_state()
        proposal = await prepare(state)
        assert state.mark_recap_delivered(proposal["hold_id"])
        state.observe_user_text(text, language="et")
        result = await state.dispatch(
            "confirm_slot_booking", {"hold_id": proposal["hold_id"]}
        )
        assert result.get("error") and not state.bookings

    asyncio.run(run())


def test_polite_recommendation_retains_vegan_preference(make_state):
    async def run():
        state = make_state()
        await turn(state, "Olen vegan")
        action, reply = await turn(state, "Mida soovitaksite?")
        assert action and "content" in action
        assert state._restaurant_question.recommendation
        assert state._restaurant_diet == "vegan"
        assert "Köögiviljasupp" in reply
        assert "Ahjulõhe" not in reply and "Seenerisoto" not in reply
        assert not state.holds and not state.bookings

    asyncio.run(run())


@pytest.mark.parametrize(
    "question", ["Kas selles on piima?", "Kas see sisaldab piima?"]
)
def test_price_interlude_preserves_exact_food_dish_and_literal_safety_notice(
    make_state, question
):
    async def run():
        state = make_state()
        await turn(state, "Kas teil suppi on?")
        await turn(state, "Mis see maksab?")
        action, reply = await turn(state, question)
        expected = "Köögiviljasupp: seller. " + state.restaurant["allergy_notice"]["et"]
        assert action == {"content": expected} and reply == expected
        assert state._restaurant_dish == "vegetable-soup"
        assert not state.holds and not state.bookings

    asyncio.run(run())


@pytest.mark.parametrize("interlude", [None, "Kas koeraga võib tulla?"])
def test_ingredient_pronoun_cannot_inherit_nonfood_or_expired_topic(
    make_state, interlude
):
    async def run():
        state = make_state()
        if interlude:
            await turn(state, "Kas teil suppi on?")
            await turn(state, interlude)
        _, reply = await turn(state, "Kas selles on piima?")
        assert reply == COPY["et"]["information_unknown"]
        assert state._restaurant_dish is None and not state.bookings

    asyncio.run(run())


@pytest.mark.parametrize(
    "utterance",
    [
        "Kas koeraga võib tulla? Broneeri laud homme kell 14:00 neljale.",
        "Broneeri laud homme kell 14:00 neljale. Kas koeraga võib tulla?",
        "Soovin homme kell 14:00 lauda neljale. Kas koeraga võib tulla?",
        "Broneeri laud homme kell 14:00 neljale ja kas koeraga võib tulla?",
    ],
)
def test_bounded_mixed_pet_request_prepares_only_exact_owned_table(
    make_state, utterance
):
    async def run():
        state = make_state()
        action, reply = await turn(state, utterance)
        assert action == {
            "name": "plan_restaurant_reservation",
            "arguments": {
                "date": tomorrow(),
                "start_time": "14:00",
                "party_size": 4,
            },
        }
        pet = state.restaurant["pet_policy"]["et"]
        assert reply.startswith(pet + " ") and reply.count(pet) == 1
        assert reply == state.render_recap()
        assert "4 inimesele" in reply and "90 minutit" in reply
        assert reply.endswith(COPY["et"]["confirmation_question"])
        assert not state.pending["approved"] and not state.pending["delivery"]
        assert not state.bookings

    asyncio.run(run())


@pytest.mark.parametrize(
    "utterance",
    [
        "Kas koeraga võib tulla? Ära broneeri lauda homme kell 14 neljale.",
        'Kas koeraga võib tulla? Näide: "Broneeri laud homme kell 14 neljale."',
        "Kas koeraga võib tulla? Broneeri laud homme kell 14 neljale. Tühista see.",
        "Broneeri laud homme kell 14 neljale. Kas koeraga võib tulla? Tegelikult kell 15.",
    ],
)
def test_unbounded_mixed_pet_text_cannot_discard_negation_or_later_clauses(
    make_state, utterance
):
    async def run():
        state = make_state()
        action, _ = await turn(state, utterance)
        assert not action or "name" not in action
        assert not state.holds and not state.pending and not state.bookings

    asyncio.run(run())


def test_partial_mixed_pet_request_retains_disclosure_through_followups(make_state):
    async def run():
        state = make_state()
        _, reply = await turn(state, "Kas koeraga võib tulla? Broneeri laud.")
        pet = state.restaurant["pet_policy"]["et"]
        assert reply.startswith(pet + " ") and reply.endswith(COPY["et"]["date"])
        assert state.booking_inquiry == {}
        for text in ("Homme", "Kell 14"):
            await turn(state, text)
        _, reply = await turn(state, "Neli palun")
        assert state.pending["recap"]["party_size"] == 4
        assert reply.startswith(pet + " ") and reply.count(pet) == 1
        assert not state.bookings

    asyncio.run(run())


@pytest.mark.parametrize(
    "steps,key",
    [
        (("Soovin lauda",), "date"),
        (("Soovin lauda", "Homme"), "time"),
        (("Soovin lauda", "Homme", "Kell 14"), "party"),
    ],
)
def test_pet_interlude_keeps_missing_booking_question(make_state, steps, key):
    async def run():
        state = make_state()
        for text in steps:
            await turn(state, text)
        before = state.booking_inquiry
        _, reply = await turn(state, "Kas koeraga võib tulla?")
        assert reply.startswith(state.restaurant["pet_policy"]["et"])
        assert reply.endswith(COPY["et"][key])
        assert state.booking_inquiry == before and not state.bookings

    asyncio.run(run())


def test_pet_interlude_keeps_hold_but_revokes_delivered_consent(make_state):
    async def run():
        state = make_state()
        proposal = await prepare(state)
        original, recap = state.pending, state.render_recap()
        assert state.mark_recap_delivered(proposal["hold_id"])
        _, reply = await turn(state, "Kas koeraga võib tulla?")
        assert reply.startswith(state.restaurant["pet_policy"]["et"])
        assert reply.endswith(recap)
        assert state.pending is not original
        assert state.pending["hold_id"] == original["hold_id"]
        assert state.pending["expires_at"] == original["expires_at"]
        assert not state.pending["delivery"] and not state.pending["approved"]
        rejected = await state.dispatch(
            "confirm_slot_booking", {"hold_id": proposal["hold_id"]}
        )
        assert rejected.get("error") and not state.bookings

    asyncio.run(run())


NO_BOOKING = "Selles vestluses pole kinnitatud lauabroneeringut."


@pytest.mark.parametrize("stage", ["none", "held", "confirmed", "cancelled", "foreign"])
def test_exact_status_reads_only_this_calls_owned_result(make_state, stage):
    async def run():
        state = make_state()
        expected = NO_BOOKING
        original = None
        if stage == "held":
            proposal = await prepare(state)
            assert state.mark_recap_delivered(proposal["hold_id"])
            original = state.pending
        elif stage in {"confirmed", "cancelled", "foreign"}:
            owner = make_state() if stage == "foreign" else state
            identifier = await confirmed(owner)
            expected = COPY["et"]["confirmed"] if stage != "foreign" else NO_BOOKING
            if stage == "cancelled":
                await turn(state, "Jah, tühista")
                expected = COPY["et"]["cancelled"]
            elif stage == "foreign":
                state.last_booking = identifier
                state.booking_receipts = list(owner.booking_receipts)
        action, reply = await turn(state, "Kas broneering on tehtud?")
        assert action is None or "name" not in action
        assert not state.reasoning_allowed
        if stage == "held":
            assert reply.startswith(expected + " ")
            assert state.pending is not original
            assert state.pending["hold_id"] == original["hold_id"]
            assert not state.pending["delivery"] and not state.pending["approved"]
            assert not state.bookings
        else:
            assert reply == expected
            assert state.booking_inquiry is None

    asyncio.run(run())


def test_status_cannot_override_unknown_write_result(make_state):
    async def run():
        state = make_state()
        await confirmed(state)
        state.mutation_uncertain = True
        action, reply = await turn(state, "Kas broneering on tehtud?")
        assert action == {"content": COPY["et"]["unknown"]}
        assert reply == COPY["et"]["unknown"]
        assert not state.reasoning_allowed

    asyncio.run(run())


CANCEL_ALIASES = (
    "Palun tühista minu broneering",
    "Palun tühista",
    "Tühista broneering palun",
)


@pytest.mark.parametrize("text", CANCEL_ALIASES)
def test_closed_cancellation_aliases_cancel_same_owned_booking(make_state, text):
    async def run():
        state = make_state()
        identifier = await confirmed(state)
        await turn(state, "Kas broneering on tehtud?")
        action, reply = await turn(state, text)
        assert action == {
            "name": "cancel_slot_booking",
            "arguments": {"booking_id": identifier},
        }
        assert reply == COPY["et"]["cancelled"]
        assert state.cancelled_bookings == {identifier}
        _, reply = await turn(state, "Kas broneering on tehtud?")
        assert reply == COPY["et"]["cancelled"]

    asyncio.run(run())


@pytest.mark.parametrize("text", CANCEL_ALIASES)
@pytest.mark.parametrize("foreign", [False, True])
def test_cancel_alias_cannot_create_inquiry_or_cancel_foreign_receipt(
    make_state, text, foreign
):
    async def run():
        state = make_state()
        if foreign:
            owner = make_state()
            state.last_booking = await confirmed(owner)
        action, _ = await turn(state, text)
        assert not action or "name" not in action
        assert state.cancel_approval is None and state.booking_inquiry is None
        assert not state.holds and not state.bookings and not state.cancelled_bookings

    asyncio.run(run())


@pytest.mark.parametrize(
    "text",
    [
        "Ära tühista minu broneeringut",
        "Kas palun tühista minu broneering?",
        "Palun tühista kui võimalik",
        '"Palun tühista"',
        "Palun tühista ja broneeri uuesti",
    ],
)
def test_cancel_aliases_remain_whole_explicit_final_intent(make_state, text):
    async def run():
        state = make_state()
        await confirmed(state)
        state.observe_user_text(text, language="et")
        action = trusted_booking_response(state)
        assert not action or action.get("name") != "cancel_slot_booking"
        assert state.cancel_approval is None and not state.cancelled_bookings

    asyncio.run(run())


@pytest.mark.parametrize(
    "language,key,maximum",
    [
        ("et", "party", 65),
        ("et", "information_unknown", 85),
        ("et", "domain", 85),
        ("et", "resume_booking", 12),
        ("et", "resume_check", 70),
        ("en", "information_unknown", 100),
    ],
)
def test_ordinary_copy_is_short_without_truncating_consequential_details(
    language, key, maximum
):
    assert len(COPY[language][key]) <= maximum
    if key == "party":
        assert "lapsed" in COPY[language][key] and COPY[language][key].count("?") == 1
    assert "ärge korrake" in COPY["et"]["unknown"].lower()
    assert all(
        "{" + field + "}" in COPY["et"]["recap"]
        for field in (
            "date",
            "time",
            "party",
            "name",
            "duration",
            "guest",
            "question",
        )
    )


def test_prompt_requests_short_natural_ordinary_answers_not_truncated_safety(
    make_state,
):
    prompt = make_state().conversation_instructions
    assert "Ordinary answers use one or two short spoken sentences" in prompt
    assert "Avoid repeated verification jargon" in prompt
    assert "Read the exact server recap" in prompt
    assert "Menu allergens are declarations, not allergy safety guarantees" in prompt
    assert "Do not invent menu items" in prompt
