"""Regressions found by the ET/EN/RU customer-question research corpus."""

import asyncio

import pytest

from app.booking_response import trusted_booking_response
from app.restaurant_call import COPY
from app.restaurant_family import LABELS, family_reply
from app.restaurant_service_questions import general_reply, general_topic
from tests.test_restaurant_conversation import prepare
from tests.test_restaurant_http import start, turn

pytest_plugins = ["tests.test_restaurant_conversation", "tests.test_restaurant_http"]

CASES = {
    "payment_tax": [
        "Kas hinnad sisaldavad käibemaksu?",
        "Do prices include VAT?",
        "НДС включён в цены?",
    ],
    "family_certification": [
        "Kas teil on peresõbraliku restorani märgis?",
        "Do you have a family friendly restaurant certification?",
        "У вас есть официальная отметка семейного ресторана?",
    ],
    "play_hours": [
        "Mis kell mängunurk avatud on?",
        "What are the play corner's opening hours?",
        "В какие часы открыт игровой уголок?",
    ],
    "facility_safety": [
        "Kas mänguasjades on lateksit, lapsel on allergia?",
        "Are the toys safe for a child with a latex allergy?",
        "Игрушки безопасны для ребёнка с аллергией на латекс?",
    ],
    "food_stock": [
        "Kas lõhe on täna veel saadaval?",
        "Is the salmon still available today?",
        "Лосось сегодня ещё есть?",
    ],
    "family_serving": [
        "Kas lapse toit saab tulla enne meie toitu?",
        "Can my child's food come before ours?",
        "Можно принести еду ребёнку раньше нашей?",
    ],
    "last_order_help": [
        "Kui hilja saab viimase tellimuse teha?",
        "What is the latest time to place an order?",
        "До какого времени можно сделать последний заказ?",
    ],
    "dietary_certification": [
        "Kas liha on halal?",
        "Is the meat halal?",
        "Мясо халяльное?",
    ],
    "access_support": [
        "Kas kuulmisraskusega kliendile on abivahendeid?",
        "Do you offer support for guests with hearing difficulties?",
        "Есть помощь для гостей с нарушением слуха?",
    ],
    "food_order_help": [
        "Tellin ühe supi ja ühe mahla.",
        "I'd like to order a soup and a juice.",
        "Хочу заказать суп и сок.",
    ],
    "delivery_help": [
        "Kui palju kohaletoimetamine maksab?",
        "How much is delivery?",
        "Сколько стоит доставка?",
    ],
    "drinks_help": [
        "Kas saate roa juurde veini soovitada?",
        "Can you recommend a wine with my meal?",
        "Можете посоветовать вино к блюду?",
    ],
    "event_details": [
        "Kas aastavahetusel on erimenüü?",
        "Is there a special menu for New Year's Eve?",
        "В новогоднюю ночь есть специальное меню?",
    ],
    "contact_help": [
        "Mis on restorani telefoninumber?",
        "What is the restaurant's phone number?",
        "Какой номер телефона ресторана?",
    ],
    "children_services": [
        "Kas teil on mähkimislaud?",
        "Is there a baby changing table in the toilet?",
        "В туалете есть пеленальный столик?",
    ],
    "food_modifications": [
        "Kas saab ilma lisatud soolata?",
        "Can you prepare a dish without added salt?",
        "Можно приготовить без добавления соли?",
    ],
    "ingredient_details": [
        "Kas kastmes on seesamit?",
        "Does the sauce contain sesame?",
        "В соусе есть кунжут?",
    ],
    "other_pets": [
        "Kas kassiga võib tulla?",
        "Can I bring a cat?",
        "Можно прийти с кошкой?",
    ],
    "pet_details": [
        "Kas suur koer on lubatud?",
        "Are large dogs allowed?",
        "Можно с большой собакой?",
    ],
    "child_allergens": [
        "Millised allergeenid on lastemenüüs?",
        "What allergens are in the children's menu?",
        "Какие аллергены есть в детском меню?",
    ],
    "medical_food": [
        "Kas see roog sobib rasedale?",
        "Is this dish suitable during pregnancy?",
        "Это блюдо подходит при беременности?",
    ],
    "payment_secret": [
        "Kas annan pangakaardi numbri?",
        "Should I give you my card number?",
        "Мне назвать номер банковской карты?",
    ],
    "payment_help": [
        "Kas kaardiga saab maksta?",
        "Can I pay by card?",
        "Можно оплатить картой?",
    ],
    "privacy_help": [
        "Kas seda kõnet salvestatakse?",
        "Is this call being recorded?",
        "Этот звонок записывается?",
    ],
    "menu_formats": [
        "Kas menüü on suure kirjaga?",
        "Do you have a large print menu?",
        "Есть меню крупным шрифтом?",
    ],
    "amenities_help": ["Kas teil on WiFi?", "Do you have Wi-Fi?", "У вас есть Wi-Fi?"],
    "seating_help": [
        "Kas saan valida kindla lauanumbri?",
        "Can I choose a particular table number?",
        "Можно выбрать конкретный номер стола?",
    ],
    "complaints_help": [
        "Sain vale roa, kuhu kaebus esitada?",
        "I received the wrong dish. What should I do?",
        "Мне принесли не то блюдо. Что делать?",
    ],
    "language_help": [
        "Mis keeltes sa aru saad?",
        "Which languages do you understand?",
        "Какие языки ты понимаешь?",
    ],
    "booking_window": [
        "Kui kaugele ette saab broneerida?",
        "How far ahead can I book?",
        "Насколько заранее можно бронировать?",
    ],
    "emergency_help": [
        "Lapsel on raske hingata, mida teha?",
        "My child is struggling to breathe. What should I do?",
        "Ребёнку трудно дышать. Что делать?",
    ],
}


@pytest.mark.parametrize("language,index", [("et", 0), ("en", 1), ("ru", 2)])
@pytest.mark.parametrize("topic", CASES)
def test_service_questions_receive_reviewed_topic_without_booking(
    make_state, topic, language, index
):
    state = make_state(language)
    question = CASES[topic][index]
    assert general_topic(question) == topic
    state.observe_user_text(question, language=language)
    assert state._restaurant_question.topics[0] == topic
    assert trusted_booking_response(state) == {
        "content": general_reply(state.restaurant, topic, language)
    }
    assert not state.booking_inquiry and not state.pending and not state.bookings
    assert not state.reasoning_allowed


@pytest.mark.parametrize("language,index", [("et", 0), ("en", 1), ("ru", 2)])
def test_children_allergens_never_inherit_adult_dish_declarations(
    make_state, language, index
):
    state = make_state(language)
    state.observe_user_text(CASES["child_allergens"][index], language=language)
    reply = state.guard_reply("", [])
    assert all(item["name"][language] not in reply for item in state.restaurant["menu"])
    assert state.restaurant["allergy_notice"][language] in reply
    assert COPY[language]["party"] not in reply


@pytest.mark.parametrize("language,index", [("et", 0), ("en", 1), ("ru", 2)])
def test_other_pets_are_not_affirmed_by_the_dog_policy(make_state, language, index):
    state = make_state(language)
    state.observe_user_text(CASES["other_pets"][index], language=language)
    assert state.guard_reply("", []) != state.restaurant["pet_policy"][language]
    assert state._restaurant_question.topics == ("other_pets",)


@pytest.mark.parametrize(
    "language,question",
    [
        ("et", "Kas mangunurk on olemas?"),
        ("et", "Kas manguasjad on olemas?"),
        ("et", "Kas lastemenuu on olemas?"),
        ("et", "Mida laps saab lauda oodates teha?"),
        ("en", "Can my child draw while we visit?"),
        ("en", "Do you have a children’s menu?"),
        ("ru", "Чем дети могут заняться, пока ждут столик?"),
        ("ru", "Есть рисунки для детей?"),
    ],
)
def test_family_activity_forms_and_plain_keyboard_text(make_state, language, question):
    state = make_state(language)
    state.observe_user_text(question, language=language)
    assert state.guard_reply("", []) == family_reply(state.restaurant, language)
    assert all(label in state.guard_reply("", []) for label in LABELS[language])
    assert not state.booking_inquiry


@pytest.mark.parametrize("language,index", [("et", 0), ("en", 1), ("ru", 2)])
def test_urgent_question_precedes_recap_and_cannot_approve_booking(
    make_state, language, index
):
    async def run():
        state = make_state(language)
        proposal = await prepare(state)
        assert state.mark_recap_delivered(proposal["hold_id"])
        previous_hold = state.pending["hold_id"]
        state.observe_user_text(CASES["emergency_help"][index], language=language)
        reply = trusted_booking_response(state)["content"]
        assert "112" in reply and COPY[language]["confirmation_question"] not in reply
        assert COPY[language]["resume_booking"] not in reply
        assert state.pending["hold_id"] == previous_hold
        assert not state.pending["approved"] and not state.pending["delivery"]
        assert not state.bookings

    asyncio.run(run())


@pytest.mark.parametrize("context", ["fresh", "partial", "held"])
@pytest.mark.parametrize(
    "language,question",
    [
        ("et", "Lapsel on raske hingata!"),
        ("en", "I can't breathe!"),
        ("ru", "Мне трудно дышать!"),
        ("et", "Lapsel on raske hingata! Kas teil on ootenimekiri?"),
        ("en", "I can't breathe! Is there a waitlist?"),
        ("ru", "Мне трудно дышать! Есть лист ожидания?"),
    ],
)
def test_unlisted_emergency_cannot_be_erased_by_booking_or_waitlist(
    make_state, language, question, context
):
    from app.languages import CONSENT
    from tests.test_restaurant_conversation import tomorrow

    async def run():
        state = make_state(language)
        previous = None
        if context == "partial":
            state.observe_user_text(f"Book a table on {tomorrow()}", language=language)
            assert state.booking_inquiry
        elif context == "held":
            proposal = await prepare(state)
            assert state.mark_recap_delivered(proposal["hold_id"])
            state.observe_user_text(CONSENT[language], language=language)
            assert state.pending["approved"] and state.pending["delivery"]
            previous = dict(state.pending)

        state.observe_user_text(question, language=language)
        response = trusted_booking_response(state)
        assert response is not None and "112" in response["content"]
        assert COPY[language]["confirmation_question"] not in response["content"]
        assert COPY[language]["resume_booking"] not in response["content"]
        assert not state.booking_inquiry and not state.bookings
        if previous:
            assert state.pending["hold_id"] == previous["hold_id"]
            assert state.pending["expires_at"] == previous["expires_at"]
            assert not state.pending["approved"] and not state.pending["delivery"]
            assert (
                await state.dispatch(
                    "confirm_slot_booking", {"hold_id": previous["hold_id"]}
                )
            )["error"] == "consent_required"
        else:
            assert not state.pending

    asyncio.run(run())


@pytest.mark.parametrize(
    "language,question",
    [
        ("en", "Can you offer support?"),
        ("ru", "Есть рядом супермаркет?"),
        ("et", "Kas teil on suppression-süsteem?"),
    ],
)
def test_dish_aliases_do_not_match_inside_unrelated_words(
    make_state, language, question
):
    state = make_state(language)
    state.observe_user_text(question, language=language)
    assert state._restaurant_dish is None


@pytest.mark.parametrize(
    "language,question",
    [
        ("et", "Mis on supis?"),
        ("en", "What is in the soup?"),
        ("ru", "Что в супе?"),
        ("et", "Kas lõhes on allergeene?"),
        ("ru", "Какие аллергены в лососе?"),
    ],
)
def test_dish_aliases_preserve_normal_inflections(make_state, language, question):
    state = make_state(language)
    state.observe_user_text(question, language=language)
    assert state._restaurant_dish == (
        "salmon" if "lõhe" in question or "лосос" in question else "vegetable-soup"
    )


@pytest.mark.parametrize(
    "question",
    [
        "I am pregnant. Can I choose a particular table?",
        "I am pregnant and need support choosing a particular table.",
        "Olen rase, kas saan aknaaluse laua?",
        "Я беременна. Можно выбрать конкретный столик?",
    ],
)
def test_pregnancy_mention_does_not_turn_seating_into_medical_food_advice(question):
    assert general_topic(question) == "seating_help"


@pytest.mark.parametrize("language,index", [("et", 0), ("en", 1), ("ru", 2)])
@pytest.mark.parametrize(
    "topic", ["privacy_help", "family_certification", "food_stock", "child_allergens"]
)
def test_service_question_resumes_missing_booking_field_without_losing_date(
    make_state, language, index, topic
):
    from tests.test_restaurant_conversation import tomorrow

    state = make_state(language)
    state.observe_user_text(f"Book a table on {tomorrow()}", language=language)
    inquiry = dict(state.booking_inquiry)
    assert inquiry["date"] == tomorrow()
    state.observe_user_text(CASES[topic][index], language=language)
    reply = trusted_booking_response(state)["content"]
    assert general_reply(state.restaurant, topic, language) in reply
    assert state.booking_inquiry == inquiry
    assert not state.pending and not state.bookings


@pytest.mark.parametrize("language,index", [("et", 0), ("en", 1), ("ru", 2)])
@pytest.mark.parametrize(
    "first", ["Book a table", "Book a table tomorrow at 6 o clock"]
)
def test_urgent_question_precedes_missing_or_ambiguous_booking_prompt(
    make_state, language, index, first
):
    state = make_state(language)
    state.observe_user_text(first, language=language)
    retained = dict(state.booking_inquiry)
    state.observe_user_text(CASES["emergency_help"][index], language=language)
    assert trusted_booking_response(state) == {
        "content": general_reply(state.restaurant, "emergency_help", language)
    }
    assert state.booking_inquiry == retained
    assert not state.pending and not state.bookings


@pytest.mark.parametrize("language,index", [("et", 0), ("en", 1), ("ru", 2)])
@pytest.mark.parametrize("channel", ["text", "audio"])
def test_http_service_answers_resume_each_booking_step_with_synthetic_speech(
    client, language, index, channel
):
    from tests.test_restaurant_booking_interruptions import STEPS, speak, tomorrow

    session = start(client, language)["session_id"]
    state = client.app.state.demo_sessions.sessions[session].tools
    for step, key in enumerate(["date", "time", "party"]):
        prompt = speak(client, session, STEPS[language][step], language, channel)
        assert prompt["reply"] == COPY[language][key]
        retained = dict(state.booking_inquiry)
        topic = ["privacy_help", "food_stock", "child_allergens"][step]
        reply = speak(client, session, CASES[topic][index], language, channel)
        assert reply["reply"].startswith(
            general_reply(state.restaurant, topic, language)
        )
        assert reply["reply"].endswith(COPY[language][key])
        assert state.booking_inquiry == retained
        assert not reply["booking_changes"] and not reply["recap_delivery_id"]
    proposal = speak(client, session, STEPS[language][3], language, channel)
    assert state.booking_inquiry == {
        "date": tomorrow(),
        "start_time": "14:00",
        "party_size": 4,
    }
    assert proposal["recap_delivery_id"] and not proposal["booking_changes"]
    assert state.pending and not state.pending["approved"] and not state.bookings


@pytest.mark.parametrize(
    "language,index,followup",
    [("et", 0, "Aga piim?"), ("en", 1, "And milk?"), ("ru", 2, "А молоко?")],
)
def test_short_child_menu_allergen_followup_cannot_use_adult_menu(
    make_state, language, index, followup
):
    state = make_state(language)
    state.observe_user_text(CASES["child_allergens"][index], language=language)
    state.observe_user_text(followup, language=language)
    reply = state.guard_reply("", [])
    assert all(item["name"][language] not in reply for item in state.restaurant["menu"])
    assert state.restaurant["allergy_notice"][language] in reply


@pytest.mark.parametrize(
    "question",
    [
        "Is this call being recorded? Actually, book tomorrow at 2 pm for six.",
        "What is the Wi-Fi password? Cancel my booking.",
        "Do prices include VAT? Move the booking to 3 pm.",
    ],
)
def test_loose_service_topic_never_marks_a_mixed_correction_as_a_whole_read_question(
    question,
):
    from app.restaurant_service_questions import general_read_question

    assert not general_read_question(question)


@pytest.mark.parametrize("language,index", [("et", 0), ("en", 1), ("ru", 2)])
def test_real_http_uses_same_customer_question_policy(client, language, index):
    session = start(client, language)["session_id"]
    state = client.app.state.demo_sessions.sessions[session].tools
    for topic in [
        "other_pets",
        "child_allergens",
        "payment_secret",
        "privacy_help",
        "emergency_help",
    ]:
        response = turn(client, session, CASES[topic][index], language=language)
        assert response["reply"] == general_reply(state.restaurant, topic, language)
        assert not response["booking_changes"] and not response["recap_delivery_id"]


@pytest.mark.parametrize("language,index", [("et", 0), ("en", 1), ("ru", 2)])
def test_native_final_turn_routes_customer_question(make_state, language, index):
    agents = pytest.importorskip("livekit.agents")
    from app.worker import TelephoneAgent

    async def run():
        state = make_state(language)
        agent = TelephoneAgent(state)
        agent._detected_language = language
        message = agents.llm.ChatMessage(
            role="user", content=[CASES["child_allergens"][index]]
        )
        await agent.on_user_turn_completed(agents.llm.ChatContext(), message)
        assert state.guard_reply("", []) == general_reply(
            state.restaurant, "child_allergens", language
        )
        assert not state.bookings

    asyncio.run(run())
