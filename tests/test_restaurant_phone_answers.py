"""Reviewed capability disclosures, mixed planning and real consent boundaries."""

import asyncio
import json

import pytest

from app.booking_response import trusted_booking_response
from app.booking_faq import FAQ_PATH, load_faq
from app.restaurant_call import COPY
from tests.test_restaurant_conversation import make_state, prepare
from tests.test_restaurant_http import AUTH, client, start


CASES = [
    (
        "et",
        "Kas saate minu allergiast köögile teatada?",
        "Ma ei salvesta erisoove ega saada köögile teateid. Allergiaohutust ma kinnitada ei saa.",
    ),
    (
        "en",
        "Can you record an allergy note?",
        "I can't save special requests or notify the kitchen. I can't confirm allergy safety.",
    ),
    (
        "ru",
        "Можете записать мою аллергию в бронирование?",
        "Я не сохраняю особые пожелания и не уведомляю кухню. Я не могу подтвердить безопасность при аллергии.",
    ),
    (
        "et",
        "Kas saan toitu kaasa tellida?",
        "Ma ei võta vastu toidu-, kaasamüügi- ega kohaletoimetamise tellimusi. Saan aidata lauabroneeringuga.",
    ),
    (
        "en",
        "Can I order takeaway?",
        "I don't take food, takeaway or delivery orders. I can help with a table reservation.",
    ),
    (
        "ru",
        "Можно заказать еду навынос?",
        "Я не принимаю заказы еды, навынос или с доставкой. Могу помочь с бронированием столика.",
    ),
]


@pytest.mark.parametrize(
    "language,question,index",
    [
        (language, phrase, index)
        for index, entry in enumerate(
            load_faq(FAQ_PATH.with_name("restaurant-phone-faq.json"))
        )
        for language in ("et", "en", "ru")
        for phrase in (entry["question_" + language], *entry["variants_" + language])
    ],
)
def test_every_reviewed_alias_uses_the_same_capability_reply(
    make_state, language, question, index
):
    state = make_state(language)
    state.observe_user_text(question, language=language)
    expected = [case[2] for case in CASES if case[0] == language][index]
    assert trusted_booking_response(state) == {"content": expected}
    assert not state.holds and not state.bookings


@pytest.mark.parametrize("language,question,answer", CASES)
def test_unsupported_request_is_a_grounded_http_reply_without_model_or_write(
    client, language, question, answer
):
    session = start(client, "auto")["session_id"]
    response = client.post(
        "/api/turn", headers=AUTH, json={"session_id": session, "text": question}
    )
    assert response.status_code == 200
    assert response.json()["language"] == language
    assert response.json()["reply"] == answer
    state = client.app.state.demo_sessions.sessions[session].tools
    assert not state.holds and not state.bookings
    assert response.json()["booking_changes"] == []


@pytest.mark.parametrize("language,question,answer", CASES)
def test_capability_question_cannot_authorize_a_delivered_recap(
    make_state, language, question, answer
):
    async def run():
        state = make_state(language)
        proposal = await prepare(state)
        previous_pending = state.pending
        recap = state.render_recap()
        assert state.mark_recap_delivered(proposal["hold_id"])
        state.observe_user_text(question, language=language)
        # Published side-question handling retains the owned hold, not consent.
        assert trusted_booking_response(state) is None
        assert state.guard_reply("untrusted", []) == (
            answer + " " + COPY[language]["resume_booking"] + " " + recap
        )
        assert state.pending is not previous_pending
        assert state.pending["hold_id"] == proposal["hold_id"]
        assert state.pending["expires_at"] == previous_pending["expires_at"]
        assert not state.pending["delivery"] and not state.pending["approved"]
        assert not state.bookings
        assert (
            await state.dispatch(
                "confirm_slot_booking", {"hold_id": proposal["hold_id"]}
            )
        )["error"] == "consent_required"

    asyncio.run(run())


@pytest.mark.parametrize("language,question,answer", CASES)
def test_partial_capability_input_changes_neither_language_nor_booking(
    make_state, language, question, answer
):
    state = make_state("en")
    state.observe_user_text("Book a table tomorrow for four.", language="en")
    inquiry = state.booking_inquiry
    state.observe_user_text(question, detected_language=language, is_final=False)
    assert state.language == "en" and state.booking_inquiry == inquiry
    assert trusted_booking_response(state) == {"content": COPY["en"]["time"]}


def test_uncertain_write_and_tool_failure_take_priority_over_capability_facts(
    make_state,
):
    state = make_state("en")
    state.mutation_uncertain = True
    state.observe_user_text("Can I order takeaway?", language="en")
    assert state.guard_reply("untrusted", []) == COPY["en"]["unknown"]
    other = make_state("en")
    other.observe_user_text("Can I order takeaway?", language="en")
    assert (
        other.guard_reply("untrusted", [{"error": "slot_unavailable"}])
        == COPY["en"]["unavailable"]
    )


MIXED = [
    (
        "et",
        "Kas saate mu allergia broneeringule kirja panna?",
        "Broneeri laud",
        "homme kell 14:00 neljale",
    ),
    (
        "en",
        "Can you record an allergy note?",
        "Book a table",
        "tomorrow at 14:00 for four",
    ),
    (
        "ru",
        "Можете записать мою аллергию в бронирование?",
        "Забронируйте столик",
        "завтра в 14:00 на четверых",
    ),
]


@pytest.mark.parametrize("language,question,verb,details", MIXED)
def test_explicit_mixed_request_plans_exact_table_but_does_not_confirm(
    make_state, language, question, verb, details
):
    state = make_state(language)
    state.observe_user_text(f"{question} {verb} {details}.", language=language)
    response = trusted_booking_response(state)
    assert response["name"] == "plan_restaurant_reservation"
    assert response["arguments"]["party_size"] == 4
    assert response["arguments"]["start_time"] == "14:00"
    assert not state.pending and not state.bookings


@pytest.mark.parametrize("language,question,verb,details", MIXED)
def test_partial_mixed_booking_asks_missing_detail_instead_of_dropping_booking(
    make_state, language, question, verb, details
):
    state = make_state(language)
    state.observe_user_text(f"{question} {verb}.", language=language)
    assert state.booking_inquiry == {}
    disclosure = next(case[2] for case in CASES if case[0] == language)
    assert trusted_booking_response(state) == {
        "content": disclosure + " " + COPY[language]["date"]
    }


def test_real_mixed_http_request_creates_only_owned_unconfirmed_hold(client):
    session = start(client, "en")["session_id"]
    response = client.post(
        "/api/turn",
        headers=AUTH,
        json={
            "session_id": session,
            "text": "Can you record an allergy note? Book a table tomorrow at 14:00 for four.",
            "language": "en",
        },
    )
    assert response.status_code == 200 and response.json()["recap_delivery_id"]
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.pending["recap"]["party_size"] == 4
    assert state.pending["recap"]["start"].endswith("14:00:00")
    assert len(state.holds) == 1 and not state.bookings
    assert response.json()["reply"].startswith(CASES[1][2] + " ")
    assert state.render_recap() == response.json()["reply"]


@pytest.mark.parametrize(
    "language,repeat",
    [
        ("et", "Palun korda."),
        ("en", "Please repeat that."),
        ("ru", "Повторите, пожалуйста."),
    ],
)
@pytest.mark.parametrize("reverse", [False, True])
def test_combined_capabilities_repeat_in_caller_order(
    make_state, language, repeat, reverse
):
    items = [case for case in CASES if case[0] == language]
    if reverse:
        items.reverse()
    state = make_state(language)
    state.observe_user_text(" ".join(item[1] for item in items), language=language)
    answer = state.guard_reply("untrusted", [])
    assert answer == " ".join(item[2] for item in items)
    state.observe_user_text(repeat, language=language)
    assert state.guard_reply("untrusted", []) == answer


def test_allergen_information_is_not_an_allergy_note_or_new_booking(make_state):
    state = make_state("en")
    state.observe_user_text("Book a table tomorrow at 14:00 for four.", language="en")
    original = state.booking_inquiry
    state.observe_user_text("Does the salmon contain milk?", language="en")
    answer = state.guard_reply("untrusted", [])
    assert "Baked salmon" in answer and "milk" in answer
    assert "save special requests" not in answer
    assert state.booking_inquiry == original and not state.pending
    state.observe_user_text(
        "Where do four pilots meet tomorrow at 14:00?", language="en"
    )
    assert trusted_booking_response(state).get("name") is None
    assert state.booking_inquiry == original


def test_note_request_does_not_hide_a_separate_kitchen_hours_question(make_state):
    state = make_state("en")
    state.observe_user_text(
        "Can you tell the kitchen about my allergy? When does the kitchen close?",
        language="en",
    )
    answer = state.guard_reply("untrusted", [])
    assert answer.startswith(CASES[1][2])
    assert "The kitchen:" in answer and "20:30" in answer


@pytest.mark.parametrize(
    "extra",
    [
        "How do I book a table?",
        "Do not book a table tomorrow at 14:00 for four.",
        'The example says "Book a table tomorrow at 14:00 for four."',
    ],
)
def test_booking_examples_and_negatives_do_not_become_mixed_booking_intent(
    make_state, extra
):
    state = make_state("en")
    state.observe_user_text("Can you record an allergy note? " + extra, language="en")
    assert state.booking_inquiry is None
    assert trusted_booking_response(state).get("name") is None
    assert not state.holds and not state.bookings


@pytest.mark.parametrize(
    "extra",
    [
        'The instructions say: "First ask a question. Book a table tomorrow at 14:00 for four."',
        "How can I order food and book a table tomorrow at 14:00 for four?",
        "Do not order food and book a table tomorrow at 14:00 for four.",
    ],
)
def test_instructional_or_negated_conjunctions_never_create_a_hold(client, extra):
    session = start(client, "en")["session_id"]
    response = client.post(
        "/api/turn",
        headers=AUTH,
        json={
            "session_id": session,
            "language": "en",
            "text": "Can you record an allergy note? " + extra,
        },
    )
    assert response.status_code == 200
    state = client.app.state.demo_sessions.sessions[session].tools
    assert not state.holds and not state.bookings and state.booking_inquiry is None
    assert not response.json()["recap_delivery_id"]


@pytest.mark.parametrize(
    "language,question,want,details",
    [
        ("et", MIXED[0][1], "Ma soovin broneerida lauda", MIXED[0][3]),
        ("en", MIXED[1][1], "I want to book a table", MIXED[1][3]),
        ("ru", MIXED[2][1], "Я хочу забронировать столик", MIXED[2][3]),
    ],
)
@pytest.mark.parametrize("complete", [False, True])
def test_positive_mixed_desire_keeps_complete_and_partial_booking(
    make_state, language, question, want, details, complete
):
    state = make_state(language)
    state.observe_user_text(
        f"{question} {want} {details if complete else ''}.", language=language
    )
    action = trusted_booking_response(state)
    if complete:
        assert action["name"] == "plan_restaurant_reservation"
        assert action["arguments"]["party_size"] == 4
        assert action["arguments"]["start_time"] == "14:00"
    else:
        disclosure = next(case[2] for case in CASES if case[0] == language)
        assert action == {"content": disclosure + " " + COPY[language]["date"]}


def test_mixed_disclosure_survives_detail_followups_and_recap_receipt(client):
    session = start(client, "en")["session_id"]
    from tests.test_restaurant_http import turn

    first = turn(
        client, session, "Can you record an allergy note? I want to book a table."
    )
    assert first["reply"].startswith(CASES[1][2])
    turn(client, session, "Tomorrow.")
    turn(client, session, "14:00.")
    prepared = turn(client, session, "Four people.")
    state = client.app.state.demo_sessions.sessions[session].tools
    assert prepared["reply"].startswith(CASES[1][2]) and prepared["recap_delivery_id"]
    assert state.pending and not state.bookings
    assert state.render_recap() == prepared["reply"]


@pytest.mark.parametrize("language,question,verb,details", MIXED)
def test_mixed_capability_side_question_discloses_once_and_revokes_old_receipt(
    client, language, question, verb, details
):
    from app.languages import CONSENT
    from tests.test_restaurant_http import turn

    session = start(client, language)["session_id"]
    initial = turn(client, session, f"{question} {verb} {details}.", language=language)
    state = client.app.state.demo_sessions.sessions[session].tools
    previous = state.pending
    held = set(state.holds)
    reply = turn(
        client,
        session,
        question,
        language=language,
        receipt=initial["recap_delivery_id"],
    )
    disclosure = next(case[2] for case in CASES if case[0] == language)
    assert reply["reply"].startswith(disclosure + " ")
    assert reply["reply"].count(disclosure) == 1
    assert reply["reply"] == client.provider.spoken[-1]
    assert reply["recap_delivery_id"] != initial["recap_delivery_id"]
    assert state.pending is not previous and set(state.holds) == held
    assert state.pending["hold_id"] == previous["hold_id"]
    assert state.pending["expires_at"] == previous["expires_at"]
    assert not state.pending["approved"] and not state.pending["delivery"]
    assert reply["booking_changes"] == [] and not state.bookings
    stale = client.post(
        "/api/turn",
        headers=AUTH,
        json={
            "session_id": session,
            "language": language,
            "text": CONSENT[language],
            "recap_delivery_id": initial["recap_delivery_id"],
        },
    )
    assert stale.status_code == 409 and not state.bookings


@pytest.mark.parametrize(
    "language,question,verb,details,key",
    [
        ("et", MIXED[0][1], MIXED[0][2], "homme kell 7 neljale", "ambiguous_time"),
        ("en", MIXED[1][1], MIXED[1][2], "tomorrow at 7 for four", "ambiguous_time"),
        ("ru", MIXED[2][1], MIXED[2][2], "завтра в 7 на четверых", "ambiguous_time"),
        ("et", MIXED[0][1], MIXED[0][2], "homme kell 14:90 neljale", "invalid_time"),
        ("en", MIXED[1][1], MIXED[1][2], "tomorrow at 14:90 for four", "invalid_time"),
        ("ru", MIXED[2][1], MIXED[2][2], "завтра в 14:90 на четверых", "invalid_time"),
        (
            "et",
            MIXED[0][1],
            MIXED[0][2],
            "31. veebruaril kell 14:00 neljale",
            "date_invalid",
        ),
        (
            "en",
            MIXED[1][1],
            MIXED[1][2],
            "31 February at 14:00 for four",
            "date_invalid",
        ),
        (
            "ru",
            MIXED[2][1],
            MIXED[2][2],
            "31 февраля в 14:00 на четверых",
            "date_invalid",
        ),
    ],
)
def test_mixed_clarification_also_discloses_the_unsupported_action(
    make_state, language, question, verb, details, key
):
    state = make_state(language)
    state.observe_user_text(f"{question} {verb} {details}.", language=language)
    notice = next(case[2] for case in CASES if case[0] == language)
    assert trusted_booking_response(state) == {
        "content": notice + " " + COPY[language][key]
    }
    assert state.guard_reply("untrusted", []) == notice + " " + COPY[language][key]
    assert not state.holds and not state.bookings


@pytest.mark.parametrize(
    "question,topic,claim,expected",
    [
        (CASES[1][1], "special_requests", "I will inform the kitchen.", CASES[1][2]),
        (CASES[4][1], "food_orders", "I will take your food order.", CASES[4][2]),
    ],
)
def test_capability_disclosure_is_not_delegated_to_free_wording(
    client, question, topic, claim, expected
):
    class UntrustedReasoner:
        supports_restaurant_reasoning = True
        calls = 0

        def chat(self, messages, tools=None, **kwargs):
            self.calls += 1
            body = (
                {"reply": claim, "fact_ids": ["policy." + topic], "language": "en"}
                if self.calls == 1
                else {"approved": True, "language": "en"}
            )
            return {"content": json.dumps(body)}

    model = UntrustedReasoner()
    client.app.state.stack["llm_primary"] = model
    session = start(client, "en")["session_id"]
    response = client.post(
        "/api/turn", headers=AUTH, json={"session_id": session, "text": question}
    )
    assert response.status_code == 200
    assert response.json()["reply"] == expected and model.calls == 0
    state = client.app.state.demo_sessions.sessions[session].tools
    assert not state.holds and not state.bookings
