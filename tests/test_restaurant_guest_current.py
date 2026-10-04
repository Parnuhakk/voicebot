"""Current restaurant reads keep preferences, never stale corrections or consent."""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.booking_response import trusted_booking_response
from app.languages import CONSENT, requested_language, spoken_date
from app.restaurant_call import COPY, parse_restaurant_request
from app.restaurant_data import load_restaurant_data, restaurant_demo_profile
from tests.test_restaurant_conversation import make_state, prepare, tomorrow
from tests.test_restaurant_http import AUTH, client, start, turn


APPROVED_RESTAURANT = load_restaurant_data()
REQUESTS = {
    "et": "Soovin lauda {day} neljale.",
    "en": "A table on {day} for four.",
    "ru": "Столик на {day} для четверых.",
}
READS = [
    ("et", "Milline on menüü?", "Köögiviljasupp"),
    ("en", "What is on the menu?", "Vegetable soup"),
    ("ru", "Что есть в меню?", "Овощной суп"),
    ("et", "Millal restoran avatud on?", "12–21"),
    ("en", "What are your opening hours?", "12–21"),
    ("ru", "Когда ресторан открыт?", "с 12 до 21"),
    ("et", "Millal restoran lahti on?", "12–21"),
    ("et", "Millal restoran sulgub?", "21"),
    ("et", "Millal restoran avaneb?", "12"),
    ("ru", "Какие часы работы ресторана?", "с 12 до 21"),
    ("en", "Does the salmon contain allergens?", "fish, milk"),
    ("et", "Mul on raske pähkliallergia", "ristkontakti"),
    ("en", "I have a severe peanut allergy", "cross-contact"),
    (
        "ru",
        "У меня сильная аллергия на орехи",
        APPROVED_RESTAURANT["allergy_notice"]["ru"],
    ),
    ("et", "Kas see on päris restoran?", "fiktiivne"),
    ("en", "Is this a real restaurant?", "fictional"),
    (
        "ru",
        "Это настоящий ресторан?",
        restaurant_demo_profile(APPROVED_RESTAURANT)["faq"][0]["answer_ru"],
    ),
    (
        "et",
        "Kus restoran asub?",
        restaurant_demo_profile(APPROVED_RESTAURANT)["faq"][1]["answer_et"],
    ),
    (
        "en",
        "Where is the restaurant?",
        restaurant_demo_profile(APPROVED_RESTAURANT)["faq"][1]["answer_en"],
    ),
    (
        "ru",
        "Где находится ресторан?",
        restaurant_demo_profile(APPROVED_RESTAURANT)["faq"][1]["answer_ru"],
    ),
    ("en", "Can I speak to a person?", "can't transfer calls"),
]
MIXED = [
    ("en", "Actually we are five; what is on the menu?"),
    ("et", "Meid on nüüd viis; mis on menüüs?"),
    ("ru", "Нас теперь пятеро; что в меню?"),
    ("en", "Show the menu; for five or six people."),
    ("en", "We will come next Friday; show the menu."),
    ("en", "Book another table and show the menu."),
    ("en", "Cancel my booking; what's on the menu?"),
    ("en", "Confirm it and tell me the opening hours."),
    ("en", "Forget the date, what is on the menu?"),
    ("en", "Show the menu, tomorrow instead."),
    ("et", "Ei, näita menüüd."),
    ("ru", "Нет, расскажите о меню."),
    ("en", "Actually we are five."),
    ("et", "Tegelikult on meid viis."),
    ("ru", "Теперь нас пятеро."),
    ("en", "Where is the restaurant, actually we are five?"),
    ("en", "Is the soup gluten5free?"),
    ("en", "For five or six people."),
    ("et", "Viiele või kuuele inimesele."),
    ("ru", "Для пятерых или шестерых."),
]


@pytest.mark.parametrize("language,question,fact", READS)
def test_pure_information_interlude_keeps_true_count_and_date(
    make_state, language, question, fact
):
    state = make_state(language)
    day = tomorrow()
    state.observe_user_text(REQUESTS[language].format(day=day), language=language)
    state.observe_user_text(question, language=language)
    response = trusted_booking_response(state)
    assert response is not None and fact in response.get("content", "")
    assert state.pending is None and not state.bookings
    state.observe_user_text("14:00", language=language)
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": {"date": day, "party_size": 4, "start_time": "14:00"},
    }


@pytest.mark.parametrize("language,text", MIXED)
def test_mixed_correction_cannot_reuse_stale_four_diner_preferences(
    make_state, language, text
):
    state = make_state(language)
    state.observe_user_text(
        REQUESTS[language].format(day=tomorrow()), language=language
    )
    state.observe_user_text(text, language=language)
    assert (state.booking_inquiry or {}).get("party_size") != 4
    assert "name" not in (trusted_booking_response(state) or {})
    state.observe_user_text("14:00", language=language)
    assert (state.booking_inquiry or {}).get("party_size") != 4
    assert "name" not in (trusted_booking_response(state) or {})
    assert state.pending is None and not state.bookings


@pytest.mark.parametrize(
    "language,text,fresh_count",
    [
        ("en", "Actually we are five, at 14:00.", 5),
        ("et", "Tegelikult on meid viis, kell 14:00.", None),
        ("ru", "Теперь нас пятеро, в 14:00.", 5),
        ("en", "Actually next Friday at 14:00.", None),
        ("en", "Two fewer people, at 14:00.", None),
    ],
)
def test_partly_parsed_correction_never_inherits_old_date_or_diner_count(
    make_state, language, text, fresh_count
):
    state = make_state(language)
    state.observe_user_text(
        REQUESTS[language].format(day=tomorrow()), language=language
    )
    state.observe_user_text(text, language=language)
    inquiry = state.booking_inquiry or {}
    assert inquiry.get("party_size") == fresh_count
    assert inquiry.get("party_size") != 4
    assert inquiry.get("date") != tomorrow()
    assert "name" not in (trusted_booking_response(state) or {})
    assert state.pending is None and not state.bookings


@pytest.mark.parametrize(
    "language,text,fresh_count",
    [
        ("en", "Actually we are five, at 14:00.", 5),
        ("et", "Tegelikult on meid viis, kell 14:00.", None),
        ("ru", "Теперь нас пятеро, в 14:00.", 5),
    ],
)
def test_http_partly_parsed_correction_cannot_prepare_four_diner_recap(
    client, language, text, fresh_count
):
    session = start(client, language)["session_id"]
    turn(client, session, REQUESTS[language].format(day=tomorrow()), language=language)
    answer = turn(client, session, text, language=language)
    assert answer["recap_delivery_id"] is None
    assert answer["booking_changes"] == []
    tools = client.app.state.demo_sessions.sessions[session].tools
    assert tools.pending is None
    inquiry = tools.booking_inquiry or {}
    assert inquiry.get("party_size") == fresh_count
    assert inquiry.get("party_size") != 4 and "date" not in inquiry
    assert not tools.holds and not tools.bookings


@pytest.mark.parametrize(
    "language,text,want",
    [
        ("en", "For five.", 5),
        ("en", "For five persons.", 5),
        ("en", "For one person.", 1),
        ("en", "Five.", 5),
        ("et", "Viiele.", 5),
        ("ru", "Для пятерых.", 5),
    ],
)
def test_whole_exact_headcount_followup_updates_count_without_losing_date(
    make_state, language, text, want
):
    state = make_state(language)
    day = tomorrow()
    state.observe_user_text(REQUESTS[language].format(day=day), language=language)
    state.observe_user_text("16:00", language=language)
    state.observe_user_text(text, language=language)
    assert state.booking_inquiry == {
        "date": day,
        "start_time": "16:00",
        "party_size": want,
    }


@pytest.mark.parametrize(
    "language,text",
    [
        ("en", "For two adults and two children."),
        ("et", "Kaks täiskasvanut ja kaks last."),
        ("ru", "Два взрослых и два ребёнка."),
    ],
)
def test_exact_adult_child_total_keeps_requested_date_and_time(
    make_state, language, text
):
    state = make_state(language)
    day = tomorrow()
    state.observe_user_text(REQUESTS[language].format(day=day), language=language)
    state.observe_user_text("16:00", language=language)
    state.observe_user_text(text, language=language)
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": {"date": day, "party_size": 4, "start_time": "16:00"},
    }


@pytest.mark.parametrize("description,count", [("five persons", 5), ("one person", 1)])
def test_person_count_is_not_a_staff_request(make_state, description, count):
    state = make_state("en")
    day = tomorrow()
    state.observe_user_text(
        f"A table on {day} at 14:00 for {description}.", language="en"
    )
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": {"date": day, "party_size": count, "start_time": "14:00"},
    }


@pytest.mark.parametrize("description,count", [("five persons", 5), ("one person", 1)])
def test_http_person_count_gets_an_owned_recap(client, description, count):
    session = start(client, "en")["session_id"]
    answer = turn(
        client,
        session,
        f"A table on {tomorrow()} at 14:00 for {description}.",
        language="en",
    )
    assert answer["recap_delivery_id"]
    assert f"{count} guests" in answer["reply"]
    assert answer["booking_changes"] == []
    tools = client.app.state.demo_sessions.sessions[session].tools
    assert tools.pending["recap"]["party_size"] == count
    assert not tools.bookings


@pytest.mark.parametrize(
    "language,question",
    [
        ("et", "Kas saan ootenimekirja?"),
        ("en", "Can you add me to a waitlist?"),
        ("ru", "Можно записаться в лист ожидания?"),
    ],
)
def test_waitlist_cannot_enroll_promise_callback_or_reduce_actual_headcount(
    make_state, language, question
):
    state = make_state(language)
    day = tomorrow()
    state.observe_user_text(REQUESTS[language].format(day=day), language=language)
    state.observe_user_text(question, language=language)
    answer = trusted_booking_response(state)
    assert answer and set(answer) == {"content"}
    assert not any(
        term in answer["content"].casefold()
        for term in ("demo", "test", "демо", "демонстрац", "тест")
    )
    for fragment in {
        "et": (
            "ei paku ootenimekirja",
            "tagasihelistamist",
            "tegeliku inimeste arvuga",
        ),
        "en": ("no waitlist", "callback", "actual diner count"),
        "ru": ("нет листа ожидания", "обратного звонка", "фактическим числом гостей"),
    }[language]:
        assert fragment in answer["content"]
    assert state.pending is None and not state.bookings
    state.observe_user_text("14:00", language=language)
    assert trusted_booking_response(state)["arguments"]["party_size"] == 4


@pytest.mark.parametrize(
    "question", ["Is this a real restaurant?", "Can you add me to a waitlist?"]
)
def test_repeat_replays_current_capability_answer_not_unrelated_generic_prompt(
    make_state, question
):
    state = make_state("en")
    state.observe_user_text(question, language="en")
    original = state.guard_reply("", [])
    state.observe_user_text("Could you repeat that?", language="en")
    assert state.guard_reply("", []) == original


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_read_interlude_does_not_keep_delivered_recap_authority(make_state, language):
    async def run():
        state = make_state(language)
        result = await prepare(state)
        hold = result["hold_id"]
        previous = state.pending
        assert state.mark_recap_delivered(hold)
        question = next(
            question for selected, question, _ in READS if selected == language
        )
        state.observe_user_text(question, language=language)
        assert await state.dispatch("confirm_slot_booking", {"hold_id": hold}) == {
            "error": "consent_required"
        }
        assert not state.bookings
        assert state.pending is not previous and state.pending["hold_id"] == hold
        assert state.pending["expires_at"] == previous["expires_at"]
        assert not state.pending["delivery"] and not state.pending["approved"]
        assert set(state.holds) == {hold}
        assert state.booking_inquiry == {
            "date": tomorrow(),
            "start_time": "14:00",
            "party_size": 4,
        }

    asyncio.run(run())


ALLERGY_REVIEW_CASES = [
    (
        "et",
        "Mul on raske piimaallergia. Kas supp on ohutu?",
        "Supp sobib teie raskele piimaallergiale.",
        "Meid on nüüd viis; ",
    ),
    (
        "en",
        "I have a serious milk allergy. Is the soup safe?",
        "The soup is suitable for your serious milk allergy.",
        "Actually we are five; ",
    ),
    (
        "ru",
        "У меня сильная аллергия на молоко. Суп безопасен?",
        "Суп подходит при вашей сильной аллергии на молоко.",
        "Нас теперь пятеро; ",
    ),
]


@pytest.mark.parametrize(
    "language,question,permission,correction", ALLERGY_REVIEW_CASES
)
@pytest.mark.parametrize(
    "stage", ["direct", "incomplete", "pending", "mixed", "mixed_waitlist"]
)
def test_review_r1_allergy_classification_never_reaches_an_approving_model(
    make_state, language, question, permission, correction, stage
):
    from app.hackathon import _TrustedLlm
    from tests.test_restaurant_reasoning import Model

    async def run():
        state = make_state(language)
        if stage != "direct":
            state.observe_user_text(
                REQUESTS[language].format(day=tomorrow()), language=language
            )
        previous = None
        if stage == "pending":
            state.observe_user_text("14:00", language=language)
            action = trusted_booking_response(state)
            proposal = await state.dispatch(action["name"], action["arguments"])
            previous = state.pending
            assert state.mark_recap_delivered(proposal["hold_id"])
        text = correction + question if stage.startswith("mixed") else question
        if stage == "mixed_waitlist":
            text += " waitlist"
        state.observe_user_text(text, language=language)
        model = Model(permission, language, approved=True)
        model.candidate["fact_ids"] = ["policy.allergens"]
        reply = _TrustedLlm(model, SimpleNamespace(tools=state)).chat(
            [{"role": "user", "content": text}]
        )["content"]
        assert (
            state._restaurant_question
            and "allergens" in state._restaurant_question.topics
        )
        assert not state.reasoning_allowed and model.calls == []
        assert state.restaurant["allergy_notice"][language] in reply
        assert state.restaurant["menu"][0]["name"][language] in reply
        assert reply != permission and not state.bookings
        if stage.startswith("mixed"):
            assert state.booking_inquiry is None and state.pending is None
        elif previous:
            assert state.pending is not previous
            assert state.pending["hold_id"] == previous["hold_id"]
            assert state.pending["expires_at"] == previous["expires_at"]
            assert not state.pending["delivery"] and not state.pending["approved"]
            assert await state.dispatch(
                "confirm_slot_booking", {"hold_id": previous["hold_id"]}
            ) == {"error": "consent_required"}
        else:
            assert state.pending is None and not state.holds
        assert not (await state.dispatcher._slot.get_operator_bookings(tomorrow()))[
            "items"
        ]

    asyncio.run(run())


@pytest.mark.parametrize(
    "language,question,permission,correction", ALLERGY_REVIEW_CASES
)
@pytest.mark.parametrize(
    "stage", ["direct", "incomplete", "pending", "mixed", "mixed_waitlist"]
)
def test_review_r1_http_allergy_warning_is_spoken_without_model_or_consent(
    client, language, question, permission, correction, stage
):
    from tests.test_restaurant_reasoning import Model

    session = start(client, language)["session_id"]
    receipt = None
    if stage != "direct":
        turn(
            client,
            session,
            REQUESTS[language].format(day=tomorrow()),
            language=language,
        )
    state = client.app.state.demo_sessions.sessions[session].tools
    previous = None
    if stage == "pending":
        receipt = turn(client, session, "14:00", language=language)["recap_delivery_id"]
        assert receipt
        previous = state.pending
    model = Model(permission, language, approved=True)
    model.candidate["fact_ids"] = ["policy.allergens"]
    client.app.state.stack["llm_primary"] = model
    text = correction + question if stage.startswith("mixed") else question
    if stage == "mixed_waitlist":
        text += " waitlist"
    answer = turn(client, session, text, language=language, receipt=receipt)
    assert (
        state._restaurant_question and "allergens" in state._restaurant_question.topics
    )
    assert model.calls == [] and not state.reasoning_allowed
    assert state.restaurant["allergy_notice"][language] in answer["reply"]
    assert state.restaurant["menu"][0]["name"][language] in answer["reply"]
    assert answer["reply"] == client.provider.spoken[-1] != permission
    assert answer["booking_changes"] == [] and not state.bookings
    if previous:
        assert state.pending is not previous
        assert state.pending["hold_id"] == previous["hold_id"]
        assert state.pending["expires_at"] == previous["expires_at"]
        assert not state.pending["delivery"] and not state.pending["approved"]
        assert answer["recap_delivery_id"] and answer["recap_delivery_id"] != receipt
        stale = client.post(
            "/api/turn",
            headers=AUTH,
            json={
                "session_id": session,
                "text": CONSENT[language],
                "language": language,
                "recap_delivery_id": receipt,
            },
        )
        assert stale.status_code == 409 and not state.bookings
    else:
        assert (
            answer["recap_delivery_id"] is None
            and state.pending is None
            and not state.holds
        )
        if stage.startswith("mixed"):
            assert state.booking_inquiry is None
    assert not client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()[
        "items"
    ]


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_review_r2_exact_visible_food_example_retains_date_diners_and_diet(
    make_state, language
):
    from tests.test_restaurant_reasoning import QUESTIONS

    question = QUESTIONS[language]
    ui = Path(__file__).resolve().parents[1] / "app/restaurant/static/restaurant.js"
    assert question in ui.read_text()
    state = make_state(language)
    day = tomorrow()
    state.observe_user_text(REQUESTS[language].format(day=day), language=language)
    state.guard_reply("", [])
    state.observe_user_text(question, language=language)
    reply = state.guard_reply("", [])
    assert state.booking_inquiry == {"date": day, "party_size": 4}
    assert state._restaurant_diet == "vegan"
    assert state._restaurant_question.recommendation
    assert state.restaurant["menu"][0]["name"][language] in reply
    assert reply.endswith(COPY[language]["time"])
    assert state.pending is None and not state.holds and not state.bookings
    state.observe_user_text("14:00", language=language)
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": {"date": day, "party_size": 4, "start_time": "14:00"},
    }


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_review_r2_http_exact_visible_food_example_resumes_four_guest_plan(
    client, language
):
    from tests.test_restaurant_reasoning import QUESTIONS, REPLIES, Model

    session = start(client, language)["session_id"]
    day = tomorrow()
    turn(client, session, REQUESTS[language].format(day=day), language=language)
    model = Model(REPLIES[language], language, approved=True)
    client.app.state.stack["llm_primary"] = model
    answer = turn(client, session, QUESTIONS[language], language=language)
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.booking_inquiry == {"date": day, "party_size": 4}
    assert (
        state._restaurant_diet == "vegan" and state._restaurant_question.recommendation
    )
    assert (
        answer["reply"]
        == (
            REPLIES[language]
            + " "
            + COPY[language]["resume_booking"]
            + " "
            + COPY[language]["time"]
        )
        == client.provider.spoken[-1]
    )
    assert len(model.calls) == 2
    assert answer["recap_delivery_id"] is None and answer["booking_changes"] == []
    assert state.pending is None and not state.holds and not state.bookings
    proposal = turn(client, session, "14:00", language=language)
    assert proposal["recap_delivery_id"] and proposal["booking_changes"] == []
    assert (
        state.pending["recap"]["date"] == day
        and state.pending["recap"]["party_size"] == 4
    )
    assert not state.pending["approved"] and not state.pending["delivery"]
    assert not client.get("/api/bookings?date=" + day, headers=AUTH).json()["items"]


def test_native_russian_parking_question_keeps_requested_date_and_clock(make_state):
    state = make_state("ru")
    day = tomorrow()
    state.observe_user_text(f"Хочу столик {day} в 14:00.")
    state.guard_reply("", [])
    state.observe_user_text("Где парковка?")
    assert state.booking_inquiry == {"date": day, "start_time": "14:00"}
    assert state.guard_reply("", []).endswith(COPY["ru"]["party"])
    assert state.pending is None and not state.bookings
    state.observe_user_text("4")
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": {"date": day, "start_time": "14:00", "party_size": 4},
    }


def test_http_native_russian_parking_question_keeps_owned_four_guest_recap(client):
    session = start(client, "ru")["session_id"]
    day = tomorrow()
    turn(client, session, f"Хочу столик {day} в 14:00.", language="ru")
    answer = turn(client, session, "Где парковка?", language="ru")
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.booking_inquiry == {"date": day, "start_time": "14:00"}
    assert answer["reply"].endswith(COPY["ru"]["party"])
    assert answer["recap_delivery_id"] is None and answer["booking_changes"] == []
    proposal = turn(client, session, "4", language="ru")
    assert proposal["recap_delivery_id"] and proposal["booking_changes"] == []
    assert state.pending["recap"]["date"] == day
    assert state.pending["recap"]["start"] == day + "T14:00:00"
    assert state.pending["recap"]["party_size"] == 4
    assert not state.pending["approved"] and not state.pending["delivery"]
    assert not client.get("/api/bookings?date=" + day, headers=AUTH).json()["items"]


def test_russian_parking_with_unknown_correction_cannot_inherit_date_or_clock(
    make_state,
):
    state = make_state("ru")
    day = tomorrow()
    state.observe_user_text(f"Хочу столик {day} в 14:00.")
    state.guard_reply("", [])
    state.observe_user_text("Где парковка? Давайте изменим число гостей.")
    assert "date" not in (state.booking_inquiry or {})
    assert "start_time" not in (state.booking_inquiry or {})
    assert state.pending is None and not state.bookings


@pytest.mark.parametrize(
    "language,opener,question",
    [
        ("et", "Soovin lauda.", "Mis kellani te lahti olete?"),
        ("en", "I'd like a table.", "What are your opening hours?"),
        ("ru", "Хочу забронировать столик.", "До скольки вы работаете?"),
    ],
)
def test_browser_opening_hours_question_keeps_current_booking_prompt(
    make_state, language, opener, question
):
    state = make_state(language)
    state.observe_user_text(opener)
    state.guard_reply("", [])
    state.observe_user_text(question)
    assert state.booking_inquiry == {}
    assert state.guard_reply("", []).endswith(COPY[language]["date"])
    assert state.pending is None and not state.bookings


@pytest.mark.parametrize(
    "language,opener,question",
    [
        ("et", "Soovin lauda.", "Mis kellani te lahti olete?"),
        ("en", "I'd like a table.", "What are your opening hours?"),
        ("ru", "Хочу забронировать столик.", "До скольки вы работаете?"),
    ],
)
def test_http_browser_opening_hours_question_keeps_current_booking_prompt(
    client, language, opener, question
):
    session = start(client, language)["session_id"]
    turn(client, session, opener, language=language)
    answer = turn(client, session, question, language=language)
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.booking_inquiry == {}
    assert answer["reply"].endswith(COPY[language]["date"])
    assert answer["recap_delivery_id"] is None and answer["booking_changes"] == []
    assert state.pending is None and not state.bookings


@pytest.mark.parametrize(
    "language,question",
    [
        ("et", "Mis kellani te lahti olete? Vahetame külaliste arvu."),
        ("ru", "До скольки вы работаете? Давайте изменим число гостей."),
    ],
)
def test_browser_hours_with_unknown_correction_cannot_inherit_requested_fields(
    make_state, language, question
):
    state = make_state(language)
    state.observe_user_text(
        REQUESTS[language].format(day=tomorrow()), language=language
    )
    state.guard_reply("", [])
    state.observe_user_text(question, language=language)
    assert state.booking_inquiry is None
    assert state.pending is None and not state.bookings


PERIOD_COUNT_REVIEW_CASES = [
    ("en", "at six in the evening for five people."),
    ("en", "for five people at six in the evening."),
    ("en", "at six pm for five people."),
    ("et", "kell kuus õhtul viiele inimesele."),
    ("ru", "в шесть вечера для пятерых человек."),
]


@pytest.mark.parametrize("language,text", PERIOD_COUNT_REVIEW_CASES)
def test_review_r3_whole_period_and_count_keeps_only_owned_date(
    make_state, language, text
):
    state = make_state(language)
    day = tomorrow()
    state.observe_user_text(REQUESTS[language].format(day=day), language=language)
    state.observe_user_text(text, language=language)
    assert state.booking_inquiry == {
        "date": day,
        "start_time": "18:00",
        "party_size": 5,
    }
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": state.booking_inquiry,
    }
    assert state.pending is None and not state.holds and not state.bookings


@pytest.mark.parametrize("language,text", PERIOD_COUNT_REVIEW_CASES)
def test_review_r3_http_period_and_count_gets_fresh_five_guest_recap(
    client, language, text
):
    session = start(client, language)["session_id"]
    day = tomorrow()
    turn(client, session, REQUESTS[language].format(day=day), language=language)
    answer = turn(client, session, text, language=language)
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.booking_inquiry == {
        "date": day,
        "start_time": "18:00",
        "party_size": 5,
    }
    assert answer["recap_delivery_id"] and answer["booking_changes"] == []
    assert (
        state.pending["recap"]["date"] == day
        and state.pending["recap"]["party_size"] == 5
    )
    assert state.pending["recap"]["start"].endswith("18:00:00")
    assert not state.pending["delivery"] and not state.pending["approved"]
    assert not client.get("/api/bookings?date=" + day, headers=AUTH).json()["items"]


@pytest.mark.parametrize(
    "text",
    [
        "at six in the evening for five people, but we might be fewer.",
        "for five people at six in the evening; confirm it.",
        "at six in the evening for five people in the banquet hall.",
    ],
)
def test_review_r3_unknown_clause_beside_period_cannot_inherit_date_or_consent(
    make_state, text
):
    state = make_state("en")
    state.observe_user_text(REQUESTS["en"].format(day=tomorrow()), language="en")
    state.observe_user_text(text, language="en")
    assert state.booking_inquiry == parse_restaurant_request(text, {})
    assert (
        "date" not in state.booking_inquiry and state.booking_inquiry["party_size"] == 5
    )
    assert "name" not in (trusted_booking_response(state) or {})
    assert state.pending is None and not state.holds and not state.bookings


UNSUPPORTED_REVIEW_WORDING = [
    ("en", "We can add you to the waiting list and notify you when a table opens."),
    ("en", "A place on the waiting list is arranged."),
    ("en", "Someone will call you back when a table opens."),
    ("et", "Helistan teile tagasi, kui laud vabaneb."),
    ("ru", "Я внесу вас в лист ожидания и перезвоню."),
    ("ru", "Позвоню вам, когда появится столик."),
]


@pytest.mark.parametrize("language,promise", UNSUPPORTED_REVIEW_WORDING)
def test_review_r4_unsupported_wording_fails_generation_and_final_boundary(
    make_state, language, promise
):
    from app.restaurant_reasoning import (
        facts_digest,
        reasoned_reply,
        restaurant_facts,
        safe_wording,
    )
    from tests.test_restaurant_reasoning import Model, QUESTIONS

    state = make_state(language)
    state.observe_user_text(QUESTIONS[language], language=language)
    model = Model(promise, language, approved=True)
    model.candidate["fact_ids"] = ["policy.staff"]
    assert (
        reasoned_reply(state, [{"role": "user", "content": QUESTIONS[language]}], model)
        is None
    )
    assert len(model.calls) == 1 and state._reasoned_reply is None
    assert not safe_wording(promise, language)
    state._reasoned_reply = (
        state._turn_serial,
        language,
        promise,
        facts_digest(restaurant_facts(state)),
    )
    assert state.guard_reply(promise, []) == state.inquiry_reply() != promise
    assert state.pending is None and not state.holds and not state.bookings


@pytest.mark.parametrize(
    "language,text,promise",
    [
        (
            "en",
            "Actually we are five; can you add me to the waiting list?",
            UNSUPPORTED_REVIEW_WORDING[0][1],
        ),
        ("en", MIXED[0][1], UNSUPPORTED_REVIEW_WORDING[1][1]),
        ("en", MIXED[0][1], UNSUPPORTED_REVIEW_WORDING[2][1]),
        ("et", MIXED[1][1], UNSUPPORTED_REVIEW_WORDING[3][1]),
        ("ru", MIXED[2][1], UNSUPPORTED_REVIEW_WORDING[4][1]),
        ("ru", MIXED[2][1], UNSUPPORTED_REVIEW_WORDING[5][1]),
    ],
)
def test_review_r4_http_mixed_question_cannot_speak_unsupported_waiting_list_or_callback(
    client, language, text, promise
):
    from tests.test_restaurant_reasoning import Model

    session = start(client, language)["session_id"]
    turn(client, session, REQUESTS[language].format(day=tomorrow()), language=language)
    model = Model(promise, language, approved=True)
    model.candidate["fact_ids"] = ["policy.staff"]
    client.app.state.stack["llm_primary"] = model
    answer = turn(client, session, text, language=language)
    state = client.app.state.demo_sessions.sessions[session].tools
    assert (
        answer["reply"]
        == COPY[language]["information_unknown"]
        == client.provider.spoken[-1]
    )
    assert answer["reply"] != promise and len(model.calls) == 1
    assert answer["booking_changes"] == [] and answer["recap_delivery_id"] is None
    assert state.booking_inquiry is None and state.pending is None
    assert not state.holds and not state.bookings
    assert not client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()[
        "items"
    ]


@pytest.mark.parametrize("language,question,fact", READS)
def test_http_interlude_is_grounded_without_model_or_booking(
    client, language, question, fact
):
    session = start(client, language)["session_id"]
    turn(client, session, REQUESTS[language].format(day=tomorrow()), language=language)
    response = turn(client, session, question, language=language)
    assert fact in response["reply"]
    assert response["booking_changes"] == []
    assert client.app.state.demo_sessions.sessions[session].tools.pending is None


def test_visible_russian_hours_example_keeps_date_and_actual_diners(make_state):
    state = make_state("ru")
    day = tomorrow()
    state.observe_user_text(REQUESTS["ru"].format(day=day), language="ru")
    state.observe_user_text("Какие у вас часы работы?", language="ru")
    assert state.booking_inquiry == {"date": day, "party_size": 4}
    assert "с 12 до 21" in trusted_booking_response(state)["content"]
    assert state.pending is None and not state.holds and not state.bookings
    state.observe_user_text("14:00", language="ru")
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": {"date": day, "party_size": 4, "start_time": "14:00"},
    }


def test_http_visible_russian_hours_example_keeps_owned_four_guest_recap(client):
    session = start(client, "ru")["session_id"]
    day = tomorrow()
    turn(client, session, REQUESTS["ru"].format(day=day), language="ru")
    answer = turn(client, session, "Какие у вас часы работы?", language="ru")
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.booking_inquiry == {"date": day, "party_size": 4}
    assert "с 12 до 21" in answer["reply"]
    assert answer["booking_changes"] == [] and answer["recap_delivery_id"] is None
    assert state.pending is None and not state.holds and not state.bookings
    proposal = turn(client, session, "14:00", language="ru")
    assert proposal["recap_delivery_id"] and proposal["booking_changes"] == []
    assert state.pending["recap"]["date"] == day
    assert state.pending["recap"]["party_size"] == 4
    assert not client.get("/api/bookings?date=" + day, headers=AUTH).json()["items"]


RECOMMENDATION_READS = [
    ("et", "Mida soovitad?", "Räägi sellest lähemalt"),
    ("en", "What do you recommend?", "Tell me more about it"),
    ("ru", "Что посоветуете?", "Расскажите об этом подробнее"),
    ("et", "Olen vegan, mida soovitad?", "Palun täpsusta"),
    ("en", "I'm vegan. What do you recommend?", "Please tell me more"),
    ("ru", "Я веган, что посоветуете?", "Можно подробнее"),
]


@pytest.mark.parametrize("language,recommendation,followup", RECOMMENDATION_READS)
def test_whole_recommendation_and_detail_reads_keep_active_inquiry_and_diet(
    make_state, language, recommendation, followup
):
    state = make_state(language)
    day = tomorrow()
    state.observe_user_text(REQUESTS[language].format(day=day), language=language)
    diet_question = {
        "et": "Milliseid vegan toite menüüs on?",
        "en": "What vegan dishes are on the menu?",
        "ru": "Есть ли веганское меню?",
    }[language]
    for text in (diet_question, recommendation, followup):
        state.observe_user_text(text, language=language)
        reply = state.guard_reply("", [])
        assert state.booking_inquiry == {"date": day, "party_size": 4}
        assert state.restaurant["menu"][0]["name"][language] in reply
        assert state.restaurant["menu"][1]["name"][language] not in reply
        assert state._restaurant_diet == "vegan"
        assert state.pending is None and not state.holds and not state.bookings
    state.observe_user_text("14:00", language=language)
    assert trusted_booking_response(state)["arguments"] == {
        "date": day,
        "party_size": 4,
        "start_time": "14:00",
    }


@pytest.mark.parametrize("language,recommendation,followup", RECOMMENDATION_READS[:3])
def test_http_whole_recommendation_and_detail_reads_keep_active_inquiry(
    client, language, recommendation, followup
):
    session = start(client, language)["session_id"]
    day = tomorrow()
    turn(client, session, REQUESTS[language].format(day=day), language=language)
    turn(
        client,
        session,
        next(text for lang, text, _ in READS if lang == language),
        language=language,
    )
    state = client.app.state.demo_sessions.sessions[session].tools
    for text in (recommendation, followup):
        answer = turn(client, session, text, language=language)
        assert state.booking_inquiry == {"date": day, "party_size": 4}
        assert state.restaurant["menu"][0]["name"][language] in answer["reply"]
        assert answer["booking_changes"] == [] and answer["recap_delivery_id"] is None
        assert state.pending is None and not state.holds and not state.bookings
    proposal = turn(client, session, "14:00", language=language)
    assert proposal["recap_delivery_id"] and proposal["booking_changes"] == []
    assert state.pending["recap"]["date"] == day
    assert state.pending["recap"]["party_size"] == 4
    assert not client.get("/api/bookings?date=" + day, headers=AUTH).json()["items"]


WHOLE_DETAIL_REPLIES = [
    ("en", "on {named_day} for five.", "date"),
    ("en", "on {day} for five.", "date"),
    ("en", "at 14:00 for five guests, please.", "time"),
    ("et", "kell 14:00 viiele inimesele, palun.", "time"),
    ("ru", "в 14:00 для пятерых человек, пожалуйста.", "time"),
]


def detail_correction(template, changed):
    day = (datetime.fromisoformat(tomorrow()) + timedelta(days=1)).date().isoformat()
    return template.format(day=day, named_day=spoken_date(day).partition(", ")[2]), {
        "date": day if changed == "date" else tomorrow(),
        "start_time": "16:00" if changed == "date" else "14:00",
        "party_size": 5,
    }


@pytest.mark.parametrize("language,template,changed", WHOLE_DETAIL_REPLIES)
def test_whole_date_count_or_polite_clock_count_retains_other_known_details(
    make_state, language, template, changed
):
    state = make_state(language)
    state.observe_user_text(
        f"A table on {tomorrow()} at 16:00 for four.", language=language
    )
    reply, expected = detail_correction(template, changed)
    state.observe_user_text(reply, language=language)
    assert state.booking_inquiry == expected
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": expected,
    }
    assert state.pending is None and not state.holds and not state.bookings


@pytest.mark.parametrize("language,template,changed", WHOLE_DETAIL_REPLIES)
def test_http_whole_detail_correction_prepares_fresh_five_guest_recap(
    client, language, template, changed
):
    session = start(client, language)["session_id"]
    original = turn(
        client,
        session,
        f"A table on {tomorrow()} at 16:00 for four.",
        language=language,
    )
    assert original["recap_delivery_id"]
    reply, expected = detail_correction(template, changed)
    answer = turn(
        client, session, reply, language=language, receipt=original["recap_delivery_id"]
    )
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.booking_inquiry == expected
    assert (
        answer["recap_delivery_id"]
        and answer["recap_delivery_id"] != original["recap_delivery_id"]
    )
    assert answer["booking_changes"] == [] and not state.bookings
    assert state.pending["recap"]["date"] == expected["date"]
    assert state.pending["recap"]["party_size"] == 5
    assert (
        datetime.fromisoformat(state.pending["recap"]["start"]).strftime("%H:%M")
        == expected["start_time"]
    )
    expired = client.post(
        "/api/turn",
        json={
            "session_id": session,
            "text": CONSENT[language],
            "language": language,
            "recap_delivery_id": original["recap_delivery_id"],
        },
        headers=AUTH,
    )
    assert expired.status_code == 409
    assert expired.json()["detail"] == "recap_delivery_expired_or_unknown"
    for day in {tomorrow(), expected["date"]}:
        assert not client.get("/api/bookings?date=" + day, headers=AUTH).json()["items"]


UNKNOWN_DETAIL_REPLIES = [
    "on for five.",
    "on actually {named_day} for five.",
    "on actually at 14:00 for five guests.",
    "at 14:00 for five guests, but we might be fewer.",
    "at 14:00 for five guests, please actually.",
]


@pytest.mark.parametrize("template", UNKNOWN_DETAIL_REPLIES)
def test_unknown_detail_clause_cannot_inherit_date_clock_or_delivered_consent(
    make_state, template
):
    async def run():
        state = make_state("en")
        state.observe_user_text(
            f"A table on {tomorrow()} at 16:00 for four.", language="en"
        )
        action = trusted_booking_response(state)
        proposal = await state.dispatch(action["name"], action["arguments"])
        assert state.mark_recap_delivered(proposal["hold_id"])
        reply, _ = detail_correction(template, "date")
        state.observe_user_text(reply, language="en")
        assert state.booking_inquiry == parse_restaurant_request(reply, {})
        assert state.booking_inquiry.get("party_size") != 4
        assert state.booking_inquiry.get("date") != tomorrow()
        assert state.booking_inquiry.get("start_time") != "16:00"
        assert state.pending is None
        assert await state.dispatch(
            "confirm_slot_booking", {"hold_id": proposal["hold_id"]}
        ) == {"error": "consent_required"}
        state.observe_user_text("Yes, that works.", language="en")
        assert "name" not in (trusted_booking_response(state) or {})
        assert not state.bookings
        assert not (await state.dispatcher._slot.get_operator_bookings(tomorrow()))[
            "items"
        ]

    asyncio.run(run())


@pytest.mark.parametrize("template", UNKNOWN_DETAIL_REPLIES)
def test_http_unknown_detail_clause_cannot_reuse_old_recap_or_preferences(
    client, template
):
    session = start(client, "en")["session_id"]
    proposal = turn(client, session, f"A table on {tomorrow()} at 16:00 for four.")
    assert proposal["recap_delivery_id"]
    reply, _ = detail_correction(template, "date")
    answer = turn(client, session, reply, receipt=proposal["recap_delivery_id"])
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.booking_inquiry == parse_restaurant_request(reply, {})
    assert state.booking_inquiry.get("party_size") != 4
    assert state.booking_inquiry.get("date") != tomorrow()
    assert state.booking_inquiry.get("start_time") != "16:00"
    assert answer["recap_delivery_id"] is None and answer["booking_changes"] == []
    assert state.pending is None and not state.bookings
    rejected = client.post(
        "/api/turn",
        json={
            "session_id": session,
            "text": "Yes, that works.",
            "language": "en",
            "recap_delivery_id": proposal["recap_delivery_id"],
        },
        headers=AUTH,
    )
    assert rejected.status_code == 409
    assert rejected.json()["detail"] == "recap_delivery_expired_or_unknown"
    assert turn(client, session, "Yes, that works.")["booking_changes"] == []
    assert not client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()[
        "items"
    ]


@pytest.mark.parametrize(
    "language,text",
    [
        ("en", "What do you recommend to eat? Actually we are five."),
        ("en", "Recommend vegan food, but we are five and want more food"),
        ("en", "Tell me more about the menu; actually we are five."),
        ("et", "Mida soovitad süüa? Tegelikult on meid viis."),
        ("ru", "Что посоветуете поесть? Теперь нас пятеро."),
        ("ru", "Какие у вас часы работы, но нас пятеро?"),
    ],
)
def test_mixed_recommendation_detail_or_hours_clause_cannot_keep_four(
    make_state, language, text
):
    state = make_state(language)
    state.observe_user_text(
        REQUESTS[language].format(day=tomorrow()), language=language
    )
    state.observe_user_text(
        next(question for selected, question, _ in READS if selected == language),
        language=language,
    )
    state.guard_reply("", [])
    state.observe_user_text(text, language=language)
    assert state.booking_inquiry is None
    assert "name" not in (trusted_booking_response(state) or {})
    state.observe_user_text("14:00", language=language)
    assert (state.booking_inquiry or {}).get("party_size") != 4
    assert "name" not in (trusted_booking_response(state) or {})
    assert state.pending is None and not state.holds and not state.bookings


LANGUAGE_SWITCHES = [
    ("en", "et", "Palun räägi eesti keeles."),
    ("et", "ru", "Говорите по-русски, пожалуйста."),
    ("ru", "en", "Please speak English."),
]


@pytest.mark.parametrize("language,selected,switch", LANGUAGE_SWITCHES)
def test_pure_language_switch_keeps_actual_requested_date_and_diners(
    make_state, language, selected, switch
):
    state = make_state(language)
    day = tomorrow()
    state.observe_user_text(REQUESTS[language].format(day=day), language=language)
    state.observe_user_text(switch, language=language)
    assert state.language == selected
    assert state.booking_inquiry == {"date": day, "party_size": 4}
    state.observe_user_text("14:00", language=selected)
    assert trusted_booking_response(state)["arguments"] == {
        "date": day,
        "party_size": 4,
        "start_time": "14:00",
    }


@pytest.mark.parametrize("language,selected,switch", LANGUAGE_SWITCHES)
def test_unknown_snapshot_expires_before_pure_language_switch(
    make_state, language, selected, switch
):
    state = make_state(language)
    state.observe_user_text(
        f"A table on {tomorrow()} at 16:00 for four.", language=language
    )
    state.observe_user_text("What is the Wi-Fi password?", language=language)
    assert state.booking_inquiry and state._restaurant_unmatched
    state.observe_user_text(switch, language=language)
    assert state.language == selected and state.booking_inquiry is None
    state.observe_user_text("14:00", language=selected)
    assert "name" not in (trusted_booking_response(state) or {})
    assert (state.booking_inquiry or {}).get("party_size") != 4
    assert state.pending is None and not state.holds and not state.bookings


@pytest.mark.parametrize("language,selected,switch", LANGUAGE_SWITCHES)
def test_http_unknown_snapshot_expires_before_pure_language_switch(
    client, language, selected, switch
):
    session = start(client, language)["session_id"]
    turn(client, session, REQUESTS[language].format(day=tomorrow()), language=language)
    turn(client, session, "What is the Wi-Fi password?", language=language)
    answer = turn(client, session, switch, language=language)
    state = client.app.state.demo_sessions.sessions[session].tools
    assert answer["language"] == selected and state.booking_inquiry is None
    assert answer["recap_delivery_id"] is None and answer["booking_changes"] == []
    next_answer = turn(client, session, "14:00", language=selected)
    assert (
        next_answer["recap_delivery_id"] is None
        and next_answer["booking_changes"] == []
    )
    assert state.pending is None and not state.holds and not state.bookings


@pytest.mark.parametrize("language,selected,switch", LANGUAGE_SWITCHES)
def test_mixed_count_and_language_request_is_not_a_pure_switch(
    make_state, language, selected, switch
):
    state = make_state(language)
    state.observe_user_text(
        REQUESTS[language].format(day=tomorrow()), language=language
    )
    mixed = f"Actually we are five; {switch}"
    assert requested_language(mixed) is None
    state.observe_user_text(mixed, language=selected)
    assert state.booking_inquiry == {"party_size": 5}
    assert state.booking_inquiry.get("date") != tomorrow()
    assert state.pending is None and not state.holds and not state.bookings


@pytest.mark.parametrize(
    "language,question,promise",
    [
        (
            "et",
            "Kas saan ootenimekirja?",
            "Panen teid ootenimekirja ja helistan tagasi.",
        ),
        (
            "en",
            "Can you add me to a waitlist?",
            "We can add you to the waitlist and call you back.",
        ),
        (
            "ru",
            "Можно записаться в лист ожидания?",
            "Я внесу вас в лист ожидания и перезвоню.",
        ),
    ],
)
def test_waitlist_reply_cannot_be_replaced_by_generated_callback_promise(
    client, language, question, promise
):
    from tests.test_restaurant_reasoning import Model

    model = Model(promise, language, approved=True)
    model.candidate["fact_ids"] = ["current_question_facts"]
    client.app.state.stack["llm_primary"] = model
    session = start(client, language)["session_id"]
    result = turn(client, session, question, language=language)
    assert result["reply"] == COPY[language]["waitlist"]
    assert model.calls == []
    assert result["booking_changes"] == [] and result["recap_delivery_id"] is None
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.pending is None and not state.holds and not state.bookings


@pytest.mark.parametrize("language,text", MIXED[:3])
def test_mixed_waitlist_correction_cannot_gain_a_generated_callback_promise(
    client, language, text
):
    from tests.test_restaurant_reasoning import Model

    promises = {
        "et": "Panen teid ootenimekirja ja helistan tagasi.",
        "en": "We can add you to the waitlist and call you back.",
        "ru": "Я внесу вас в лист ожидания и перезвоню.",
    }
    model = Model(promises[language], language, approved=True)
    client.app.state.stack["llm_primary"] = model
    session = start(client, language)["session_id"]
    turn(client, session, REQUESTS[language].format(day=tomorrow()), language=language)
    result = turn(client, session, text + " waitlist", language=language)
    assert result["reply"] != promises[language]
    assert result["booking_changes"] == [] and result["recap_delivery_id"] is None
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.booking_inquiry is None and state.pending is None
    assert not state.holds and not state.bookings


@pytest.mark.parametrize("language,text", MIXED[:3])
def test_http_mixed_correction_uses_controlled_clarification_without_stale_inquiry(
    client, language, text
):
    class Planner:
        calls = 0

        def chat(self, messages, tools=None):
            self.calls += 1
            return {"content": "Please clarify the reservation details."}

    planner = Planner()
    client.app.state.stack["llm_primary"] = planner
    session = start(client, language)["session_id"]
    turn(client, session, REQUESTS[language].format(day=tomorrow()), language=language)
    response = turn(client, session, text, language=language)
    assert planner.calls == 0
    assert response["booking_changes"] == []
    tools = client.app.state.demo_sessions.sessions[session].tools
    assert tools.booking_inquiry is None and tools.pending is None
    assert not tools.holds and not tools.bookings
    followup = turn(client, session, "14:00", language=language)
    assert followup["recap_delivery_id"] is None and followup["booking_changes"] == []
    assert not tools.holds and not tools.bookings


@pytest.mark.parametrize(
    "language,date_reply,time_reply,party_reply",
    [
        ("et", "homseks", "kell kuus", "nelja inimesega"),
        ("en", "tomorrow", "at six o clock", "for four people"),
        ("ru", "завтра", "в шесть", "для четырех человек"),
    ],
)
def test_whole_resolver_details_keep_pending_time_context(
    make_state, language, date_reply, time_reply, party_reply
):
    state = make_state(language)
    state.observe_user_text("table", language=language)
    state.guard_reply("", [])
    for text, key in [(date_reply, "time"), (time_reply, "ambiguous_time")]:
        state.observe_user_text(text, language=language)
        assert state.guard_reply("", []) == COPY[language][key]
    state.observe_user_text("pm", language=language)
    assert state.guard_reply("", []) == COPY[language]["party"]
    state.observe_user_text(party_reply, language=language)
    assert trusted_booking_response(state)["arguments"] == {
        "date": tomorrow(),
        "start_time": "18:00",
        "party_size": 4,
    }


@pytest.mark.parametrize(
    "reply", ["homseks", "neljas oktoober", "4 October", "четвертого октября"]
)
def test_whole_date_repair_keeps_known_time_and_diners(make_state, reply):
    state = make_state("et")
    state.observe_user_text("table 31 February at 16:00 for four", language="et")
    assert state.guard_reply("", []) == COPY["et"]["date_invalid"]
    state.observe_user_text(reply, language="et")
    assert state.booking_inquiry["party_size"] == 4
    assert state.booking_inquiry["start_time"] == "16:00"
    assert "date_issue" not in state.booking_inquiry


@pytest.mark.parametrize(
    "language,reply",
    [
        ("en", "at 16:00 for five people"),
        ("et", "kell 16:00 viiele inimesele"),
        ("ru", "в 16:00 для пятерых человек"),
    ],
)
def test_whole_combined_count_and_clock_followup_keeps_requested_date(
    make_state, language, reply
):
    state = make_state(language)
    state.observe_user_text(
        REQUESTS[language].format(day=tomorrow()), language=language
    )
    state.observe_user_text(reply, language=language)
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": {"date": tomorrow(), "start_time": "16:00", "party_size": 5},
    }


def test_unknown_question_snapshot_cannot_restore_old_details_on_next_turn(make_state):
    state = make_state("en")
    state.observe_user_text(f"table on {tomorrow()} at 16:00 for four", language="en")
    state.observe_user_text("What is the Wi-Fi password?", language="en")
    assert trusted_booking_response(state) == {
        "content": COPY["en"]["information_unknown"]
        + " "
        + COPY["en"]["resume_booking"]
        + " "
        + COPY["en"]["resume_check"]
    }
    state.observe_user_text("14:00", language="en")
    assert state.booking_inquiry == {"start_time": "14:00"}
    assert "name" not in trusted_booking_response(state)


@pytest.mark.parametrize(
    "language,correction",
    [
        ("en", "Two fewer people, at 14:00."),
        ("et", "Tegelikult on meid viis, kell 14:00."),
    ],
)
def test_unparsed_count_after_delivered_recap_cannot_reuse_native_consent(
    make_state, language, correction
):
    async def run():
        state = make_state(language)
        state.observe_user_text(
            f"table on {tomorrow()} at 16:00 for four", language=language
        )
        action = trusted_booking_response(state)
        proposal = await state.dispatch(action["name"], action["arguments"])
        hold = proposal["hold_id"]
        assert state.mark_recap_delivered(hold)
        state.observe_user_text(correction, language=language)
        assert state.pending is None and "party_size" not in state.booking_inquiry
        assert await state.dispatch("confirm_slot_booking", {"hold_id": hold}) == {
            "error": "consent_required"
        }
        state.observe_user_text(CONSENT[language], language=language)
        assert "name" not in (trusted_booking_response(state) or {})
        assert not state.bookings
        assert not (await state.dispatcher._slot.get_operator_bookings(tomorrow()))[
            "items"
        ]

    asyncio.run(run())


@pytest.mark.parametrize(
    "language,correction",
    [
        ("en", "Two fewer people, at 14:00."),
        ("et", "Tegelikult on meid viis, kell 14:00."),
    ],
)
def test_http_unparsed_count_revokes_recap_receipt_and_cannot_book_stale_four(
    client, language, correction
):
    session = start(client, language)["session_id"]
    proposal = turn(
        client, session, f"table on {tomorrow()} at 16:00 for four", language=language
    )
    assert proposal["recap_delivery_id"]
    changed = turn(
        client,
        session,
        correction,
        language=language,
        receipt=proposal["recap_delivery_id"],
    )
    assert changed["recap_delivery_id"] is None and changed["booking_changes"] == []
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.pending is None and "party_size" not in state.booking_inquiry
    rejected = client.post(
        "/api/turn",
        json={
            "session_id": session,
            "text": CONSENT[language],
            "language": language,
            "recap_delivery_id": proposal["recap_delivery_id"],
        },
        headers=AUTH,
    )
    assert rejected.status_code == 409
    assert rejected.json()["detail"] == "recap_delivery_expired_or_unknown"
    confirmed = turn(client, session, CONSENT[language], language=language)
    assert (
        confirmed["booking_changes"] == []
        and state.pending is None
        and not state.bookings
    )
    assert not asyncio.run(state.dispatcher._slot.get_operator_bookings(tomorrow()))[
        "items"
    ]


@pytest.mark.parametrize(
    "language,correction",
    [
        ("en", "Two fewer people, at 14:00."),
        ("et", "Tegelikult on meid viis, kell 14:00."),
    ],
)
def test_native_sdk_unparsed_count_cannot_restore_delivered_recap(
    tmp_path, language, correction
):
    pytest.importorskip("livekit.agents")
    from unittest.mock import patch

    from livekit.agents import AgentSession
    from app import worker
    from app.booking.restaurant import RestaurantAdapter
    from app.business import restaurant_dispatcher
    from app.call_factory import make_call_tools
    from app.restaurant_data import load_restaurant_data
    from tests.test_native_booking_terminals import (
        Playback,
        UnusedModel,
        UnusedTTS,
        native_turn,
        synthesize,
    )

    async def run():
        data = load_restaurant_data()
        adapter = RestaurantAdapter(
            str(tmp_path / "guest-native.db"), data=data, allow_writes=True
        )
        state = make_call_tools(restaurant_dispatcher(adapter, data), language=language)
        agent = worker.TelephoneAgent(state)
        model = UnusedModel()
        session = AgentSession(
            llm=model, tts=UnusedTTS(), turn_handling={"turn_detection": "manual"}
        )
        session.output.audio = Playback()
        session.on("conversation_item_added", agent.on_conversation_item_added)
        request = {
            "en": f"A table on {tomorrow()} at 16:00 for four",
            "et": f"Soovin lauda {tomorrow()} kell 16:00 neljale",
        }[language]
        with patch("livekit.agents.Agent.default.tts_node", synthesize):
            await session.start(agent=agent, record=False)
            try:
                await native_turn(session, agent, request)
                assert state.pending and state.pending["delivery"]
                assert state.pending["recap"]["party_size"] == 4
                await native_turn(session, agent, correction)
                assert state.pending is None
                assert state.booking_inquiry == {"start_time": "14:00"}
                await native_turn(session, agent, CONSENT[language])
                assert state.pending is None and not state.bookings
                assert model.calls == 0
                assert not (await adapter.get_operator_bookings(tomorrow()))["items"]
            finally:
                await session.aclose()

    asyncio.run(run())


MEDICAL_HISTORY = {
    "en": (
        "I have celiac disease. What can I eat from your menu?",
        "What would you recommend?",
        "Vegetable soup is safe for you.",
    ),
    "et": (
        "Mul on tsöliaakia. Mida saan menüüst süüa?",
        "Mida soovitad süüa?",
        "Köögiviljasupp on teile ohutu.",
    ),
    "ru": (
        "У меня целиакия. Что можно есть из вашего меню?",
        "Что посоветуете поесть?",
        "Овощной суп для вас безопасен.",
    ),
}


@pytest.mark.parametrize("language", ["et", "en", "ru"])
@pytest.mark.parametrize("switch_language", [False, True])
def test_medical_food_history_survives_unknown_interlude_and_language_switch(
    client, language, switch_language
):
    from tests.test_restaurant_reasoning import Model

    disclosure, recommendation, _ = MEDICAL_HISTORY[language]
    selected, switch = (
        next(
            (selected, switch)
            for original, selected, switch in LANGUAGE_SWITCHES
            if original == language
        )
        if switch_language
        else (language, None)
    )
    unsafe = MEDICAL_HISTORY[selected][2]
    model = Model(unsafe, selected)
    client.app.state.stack["llm_primary"] = model
    session = start(client, language)["session_id"]
    turn(client, session, REQUESTS[language].format(day=tomorrow()), language=language)
    turn(client, session, disclosure, language=language)
    turn(client, session, recommendation, language=language)
    interlude = turn(client, session, "Who won Wimbledon?", language=language)
    assert interlude["booking_changes"] == []
    assert unsafe not in interlude["reply"] and not model.calls
    if switch:
        switched = turn(client, session, switch, language=language)
        assert unsafe not in switched["reply"] and switched["booking_changes"] == []
    before = len(model.calls)
    answer = turn(client, session, MEDICAL_HISTORY[selected][1], language=selected)
    state = client.app.state.demo_sessions.sessions[session].tools
    assert len(model.calls) == before
    assert state._restaurant_focus == "allergens"
    assert state.information_reply("allergens") in answer["reply"]
    assert unsafe not in answer["reply"]
    assert answer["booking_changes"] == [] and answer["recap_delivery_id"] is None
    assert state.pending is None and not state.holds and not state.bookings
    assert not client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()[
        "items"
    ]


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_medical_history_does_not_reclassify_hours_or_leak_to_new_session(
    client, language
):
    from tests.test_restaurant_reasoning import Model, REPLIES

    session = start(client, language)["session_id"]
    turn(client, session, MEDICAL_HISTORY[language][0], language=language)
    hours, hours_fact = {
        "et": ("Millal restoran avatud on?", "12–21"),
        "en": ("What are your opening hours?", "12–21"),
        "ru": ("Когда ресторан открыт?", "с 12 до 21"),
    }[language]
    answer = turn(client, session, hours, language=language)
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state._restaurant_focus == "hours" and hours_fact in answer["reply"]
    assert answer["booking_changes"] == []
    model = Model(REPLIES[language], language)
    client.app.state.stack["llm_primary"] = model
    fresh = start(client, language)["session_id"]
    answer = turn(client, fresh, MEDICAL_HISTORY[language][1], language=language)
    assert len(model.calls) == 2 and REPLIES[language] in answer["reply"]
    assert answer["booking_changes"] == []
