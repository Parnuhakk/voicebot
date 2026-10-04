"""Natural approved call wording reaches speech without internal fixture labels."""

import re

import pytest

from app.demo import load_demo_data
from app.restaurant_answers import match_question
from app.restaurant_data import load_restaurant_data, restaurant_demo_profile
from tests.test_restaurant_http import start, turn
from app.languages import CONSENT

pytest_plugins = ["tests.test_restaurant_conversation", "tests.test_restaurant_http"]

INTERNAL_FRAMING = r"demo|testbroneering|test reservation|тестов|демо"
QUESTIONS = {
    "et": {
        "staff": "Kas saan restorani töötajaga rääkida?",
        "policies": "Millised on broneerimise tingimused?",
        "location": "Kus te asute?",
        "recap": "Soovin homme lauda neljale kell 14.00",
        "real": "Kas see on päris restoran?",
        "cancel": "Palun tühista broneering, mille just selles kõnes tegime",
        "special_requests": "Kas saate mu allergia broneeringule kirja panna?",
        "food_orders": "Kas saan toitu kaasa tellida?",
    },
    "en": {
        "staff": "Can I speak to a member of staff?",
        "policies": "What are your reservation policies?",
        "location": "Where are you?",
        "recap": "A table for four tomorrow at 14:00",
        "real": "Is this a real restaurant?",
        "cancel": "Please cancel the booking we just made in this call",
        "special_requests": "Can you record an allergy note?",
        "food_orders": "Can I order takeaway?",
    },
    "ru": {
        "staff": "Можно поговорить с сотрудником ресторана?",
        "policies": "Какие правила бронирования?",
        "location": "Где находится ресторан?",
        "recap": "Столик на четверых завтра в 14:00",
        "real": "Это настоящий ресторан?",
        "cancel": "Пожалуйста отмените бронирование которое мы только что сделали в этом звонке",
        "special_requests": "Можете записать мою аллергию в бронирование?",
        "food_orders": "Можно заказать еду навынос?",
    },
}


@pytest.mark.parametrize("language", ["et", "en", "ru"])
@pytest.mark.parametrize(
    "stage",
    [
        "greeting",
        "staff",
        "policies",
        "location",
        "recap",
        "cancelled",
        "special_requests",
        "food_orders",
    ],
)
def test_browser_call_speaks_no_internal_test_labels(client, language, stage):
    session = start(client, language)["session_id"]
    if stage != "greeting":
        question = "recap" if stage == "cancelled" else stage
        answer = turn(client, session, QUESTIONS[language][question], language=language)
        if stage == "cancelled":
            saved = turn(
                client,
                session,
                CONSENT[language],
                language=language,
                receipt=answer["recap_delivery_id"],
            )
            assert saved["booking_changes"][0]["action"] == "confirmed"
            answer = turn(
                client, session, QUESTIONS[language]["cancel"], language=language
            )
            assert answer["booking_changes"][0]["action"] == "cancelled"
        else:
            assert answer["booking_changes"] == []
        assert client.provider.spoken[-1] == answer["reply"]
    spoken = client.provider.spoken[-1]
    assert spoken and not re.search(INTERNAL_FRAMING, spoken, re.I), spoken
    if stage == "recap":
        details = (
            ("четырёх гостей", "полтора часа") if language == "ru" else ("4", "90")
        )
        assert all(value in spoken for value in ("Meretuule", "Külaline", *details))
        assert answer["recap_delivery_id"]
        assert client.app.state.demo_sessions.sessions[session].tools.bookings == set()


@pytest.mark.parametrize("language", ["et", "en", "ru"])
@pytest.mark.parametrize("capability", ["special_requests", "food_orders"])
def test_capability_booking_recap_has_no_testing_narration_and_requires_receipt(
    client, language, capability
):
    requests = {
        "et": "Broneeri laud homme kell 14:00 neljale.",
        "en": "Book a table tomorrow at 14:00 for four.",
        "ru": "Забронируйте столик завтра в 14:00 на четверых.",
    }
    session = start(client, language)["session_id"]
    answer = turn(
        client,
        session,
        QUESTIONS[language][capability] + " " + requests[language],
        language=language,
    )
    state = client.app.state.demo_sessions.sessions[session].tools
    assert answer["reply"] == client.provider.spoken[-1] == state.render_recap()
    assert state.pending and answer["recap_delivery_id"] and not state.bookings
    assert not re.search(INTERNAL_FRAMING, answer["reply"], re.I)
    denied = turn(client, session, CONSENT[language], language=language)
    assert denied["booking_changes"] == [] and not state.bookings


@pytest.mark.parametrize(
    "language,question,topic,expected",
    [
        (
            "et",
            "Kui kauaks saab lauda broneerida?",
            "duration",
            "Lauabroneering kestab 90 minutit.",
        ),
        (
            "et",
            "Kui kaua on laud meie päralt?",
            "duration",
            "Lauabroneering kestab 90 minutit.",
        ),
        (
            "et",
            "Kui palju toidud maksavad?",
            "price",
            "Mul pole praegu menüühindu. Täpse hinna ütleb restorani töötaja.",
        ),
        (
            "et",
            "Mis ahjulõhe maksma läheb?",
            "price",
            "Mul pole praegu menüühindu. Täpse hinna ütleb restorani töötaja.",
        ),
        (
            "et",
            "Kas saan restorani töötajaga rääkida?",
            "staff",
            "Seda palun küsige restorani töötajalt. Ma ei saa kõnet edasi suunata.",
        ),
        (
            "en",
            "How long can we keep the table?",
            "duration",
            "The table reservation lasts 90 minutes.",
        ),
        (
            "ru",
            "Как долго можно занимать столик?",
            "duration",
            "Столик будет за вами на полтора часа.",
        ),
    ],
)
def test_estonian_question_forms_select_the_requested_fact(
    make_state, language, question, topic, expected
):
    selection = match_question(question)
    assert selection is not None and selection.topics == (topic,)
    state = make_state(language)
    state.observe_user_text(question, language=language)
    assert state.guard_reply("Siin käib testimine", []) == expected
    assert (
        state.booking_inquiry is None and state.pending is None and not state.bookings
    )


def test_cat_answer_does_not_grant_dog_only_permission(make_state):
    from app.restaurant_service_questions import general_reply

    state = make_state()
    state.observe_user_text("Kas kassiga tohib tulla?", language="et")
    answer = state.guard_reply("Jah, loomulikult!", [])
    assert answer == general_reply(state.restaurant, "other_pets", "et")
    state.restaurant.pop("pet_policy")
    assert state.guard_reply("Jah", []) == general_reply(state.restaurant, "other_pets", "et")


@pytest.mark.parametrize(
    "stage,question,expected",
    [
        (
            "children",
            "Kas lapsed lähevad inimeste arvu sisse?",
            "Palun arvestage ka lapsed külaliste koguarvu hulka.",
        ),
        (
            "menu",
            "Olen vegan, mida soovitate?",
            "Menüüst võiksite valida: Köögiviljasupp. Mis teile meeldiks?",
        ),
        (
            "allergens",
            "Kas ahjulõhe sisaldab piima?",
            "Raske allergia korral palun rääkige enne tellimist restorani töötajaga.",
        ),
        ("hours", "Mis kell te lahti olete?", "Millist kuupäeva silmas peate?"),
    ],
)
def test_estonian_information_uses_consistent_polite_address(
    make_state, stage, question, expected
):
    state = make_state()
    if stage == "hours":
        state.restaurant["closures"] = {
            "2027-01-01": {"et": "Suletud", "en": "Closed", "ru": "Закрыто"}
        }
    state.observe_user_text(question, language="et")
    answer = state.guard_reply("", [])
    assert expected in answer
    if stage == "allergens":
        assert (
            "piim" in answer
            and "ristkontakti" in answer
            and "Ma ei saa lubada allergeenivaba toitu" in answer
        )


def test_restaurant_guest_aliases_preserve_reserved_contacts_and_shared_fixture():
    base = load_demo_data()
    profile = restaurant_demo_profile(load_restaurant_data())
    assert set(profile["guests"]) == set(base["guests"])
    for fixture_id, ordinal in [
        ("guest-001", "Esimene"),
        ("guest-002", "Teine"),
        ("guest-003", "Kolmas"),
    ]:
        guest = profile["guests"][fixture_id]
        assert (guest["firstName"], guest["lastName"]) == (ordinal, "Külaline")
        assert guest["email"] == base["guests"][fixture_id]["email"]
        assert guest["phone"] == base["guests"][fixture_id]["phone"]
    assert base["guests"]["guest-001"]["firstName"] == "Demo"
    assert load_restaurant_data()["restaurant_id"] == "meretuule-restaurant-demo"
    assert profile["synthetic"] is True


@pytest.mark.parametrize(
    "name", ["Esimene Külaline", "Teine Külaline", "Kolmas Külaline", "guest-002"]
)
def test_spoken_guest_alias_does_not_choose_session_language(make_state, name):
    state = make_state("et")
    state.observe_user_text(name, detected_language="english")
    assert state.language == "et" and not state.language_locked
    assert not state.bookings and state.pending is None


@pytest.mark.parametrize(
    "language,expected",
    [
        ("et", "Teie lauabroneering on kinnitatud."),
        ("en", "Your table reservation is confirmed."),
        ("ru", "Готово, бронь подтверждена."),
    ],
)
def test_confirmed_speech_reports_saved_state_without_browser_only_instructions(
    client, language, expected
):
    session = start(client, language)["session_id"]
    proposal = turn(client, session, QUESTIONS[language]["recap"], language=language)
    answer = turn(
        client,
        session,
        CONSENT[language],
        language=language,
        receipt=proposal["recap_delivery_id"],
    )
    assert answer["reply"] == expected == client.provider.spoken[-1]
    assert answer["booking_changes"][0]["action"] == "confirmed"


@pytest.mark.parametrize(
    "language,truth", [("et", "fiktiivne"), ("en", "fictional"), ("ru", "деморесторан")]
)
def test_explicit_reality_question_remains_truthful(client, language, truth):
    session = start(client, language)["session_id"]
    answer = turn(client, session, QUESTIONS[language]["real"], language=language)
    assert truth in answer["reply"] == client.provider.spoken[-1]
    assert not answer["booking_changes"]
    public = client.get("/api/public/restaurant").json()
    assert public["synthetic"] is True
    assert (
        "fictional" in client.get("/").text.lower()
        or "fiktiivne" in client.get("/").text.lower()
    )


@pytest.mark.parametrize(
    "language,expected",
    [
        (
            "et",
            "Ma ei saanud toimingu tulemust kinnitada. Palun ärge korrake seda; kontrollige broneeringu olekut.",
        ),
        (
            "en",
            "I couldn't confirm the result. Please don't repeat the action; check the reservation's status.",
        ),
        (
            "ru",
            "Не удалось подтвердить результат действия. Не повторяйте его; проверьте статус брони.",
        ),
    ],
)
def test_uncertain_write_is_honest_in_both_call_transports(
    make_state, language, expected
):
    state = make_state(language)
    reply = state.guard_reply(
        "Your reservation is confirmed.", [{"error": "write_outcome_unknown"}]
    )
    assert reply == expected
    assert state.mutation_uncertain and not state.bookings
