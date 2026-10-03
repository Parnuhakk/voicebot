"""Owner-approved family facts reach typed, speech and native turns."""

import asyncio
import json

import pytest

from app.restaurant_answers import GUIDANCE, match_question
from app.restaurant_data import load_restaurant_data
from app.restaurant_family import FACILITIES, LABELS, family_reply, family_topic
from app.restaurant_reasoning import restaurant_facts
from tests.test_restaurant_http import start, turn

pytest_plugins = ["tests.test_restaurant_conversation", "tests.test_restaurant_http"]

QUESTIONS = {
    "et": [
        "Kas lastele on joonistamisvõimalus?",
        "Kas teil on mänguasju?",
        "Kas mängunurk on olemas?",
        "Kas lastemenüü on olemas?",
        "Kas lastega saab tulla?",
        "Kas lastele on midagi teha?",
    ],
    "en": [
        "Can children do some drawing?",
        "Do you have toys?",
        "Is there a play corner?",
        "Do you have a children's menu?",
        "Can we bring children?",
        "What can kids do while we wait?",
    ],
    "ru": [
        "Дети могут порисовать?",
        "Есть игрушки?",
        "Есть игровой уголок?",
        "Есть детское меню?",
        "Можно прийти с детьми?",
        "Есть чем заняться детям?",
    ],
}


@pytest.mark.parametrize("language", ["et", "en", "ru"])
@pytest.mark.parametrize("index", range(6))
def test_family_questions_use_only_owner_confirmed_facilities(
    make_state, language, index
):
    state = make_state(language)
    question = QUESTIONS[language][index]
    assert family_topic(question) == "family"
    state.observe_user_text(question, language=language)
    reply = state.guard_reply("", [])
    assert reply == family_reply(state.restaurant, language)
    assert all(label in reply for label in LABELS[language])
    assert state.pending is None and not state.bookings and not state.booking_inquiry
    assert restaurant_facts(state)["policy.family"] == reply


@pytest.mark.parametrize(
    "language,question",
    [
        ("et", "Mis road lastemenüüs on?"),
        ("en", "What dishes are on the kids menu?"),
        ("ru", "Какие блюда есть в детском меню?"),
        ("et", "Kas mängunurgas on järelevalve?"),
        ("en", "Is the play area supervised?"),
        ("ru", "В игровом уголке есть няня?"),
        ("et", "Kas mänguasjade kasutamine on tasuta?"),
        ("en", "Is the play corner free?"),
        ("ru", "Игровой уголок бесплатный?"),
    ],
)
def test_unconfirmed_family_details_are_not_assumed(make_state, language, question):
    state = make_state(language)
    assert family_topic(question) == "family_details"
    state.observe_user_text(question, language=language)
    reply = state.guard_reply("", [])
    assert reply == family_reply(state.restaurant, language, details=True)
    assert "family_details" in state._restaurant_question.topics
    assert all(item["name"][language] not in reply for item in state.restaurant["menu"])
    assert state.pending is None and not state.bookings


@pytest.mark.parametrize(
    "language,question",
    [
        ("et", "Kas lapsed lähevad inimeste arvu sisse?"),
        ("en", "Do children count in the total party size?"),
        ("ru", "Детей тоже учитывать в количестве гостей?"),
    ],
)
def test_guest_count_policy_remains_distinct(make_state, language, question):
    state = make_state(language)
    state.observe_user_text(question, language=language)
    assert state.guard_reply("", []) == GUIDANCE[language]["children"]
    assert family_topic(question) is None


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_absent_or_partial_facilities_cannot_inherit_demo_claims(language):
    data = load_restaurant_data()
    del data["family_facilities"]
    assert all(label not in family_reply(data, language) for label in LABELS[language])
    data["family_facilities"] = {"drawing": True, "toys": False, "play_corner": None}
    reply = family_reply(data, language)
    assert LABELS[language][0] in reply
    assert all(label not in reply for label in LABELS[language][1:])


@pytest.mark.parametrize(
    "invalid", [True, [], {"unknown": True}, {"toys": 1}, {"drawing": "yes"}]
)
def test_configuration_rejects_untrusted_facility_values(tmp_path, invalid):
    data = load_restaurant_data()
    data["family_facilities"] = invalid
    path = tmp_path / "family.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="restaurant_configuration_invalid"):
        load_restaurant_data(path)


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_public_facilities_match_real_http_conversation(client, language):
    public = client.get("/api/public/restaurant").json()
    assert public["restaurant"]["family_facilities"] == dict.fromkeys(FACILITIES, True)
    session = start(client, language)["session_id"]
    response = turn(client, session, QUESTIONS[language][0], language=language)
    assert response["reply"] == public["family_facilities_summary"][language]
    assert not response["booking_ids"] and response.get("recap_delivery_id") is None


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_native_final_turn_uses_the_same_confirmed_family_facts(make_state, language):
    agents = pytest.importorskip("livekit.agents")
    from app.worker import TelephoneAgent

    async def run():
        state = make_state(language)
        agent = TelephoneAgent(state)
        message = agents.llm.ChatMessage(role="user", content=[QUESTIONS[language][0]])
        agent._detected_language = language
        await agent.on_user_turn_completed(agents.llm.ChatContext(), message)
        assert state.guard_reply("", []) == family_reply(state.restaurant, language)
        assert not state.bookings

    asyncio.run(run())


def test_general_family_facilities_do_not_confirm_separate_accessibility_details():
    question = match_question("Kas lastega saab tulla ja kas teil on lastetool?")
    assert question and "highchair" in question.topics
    assert family_topic("Kas mängunurk on olemas?") == "family"


@pytest.mark.parametrize(
    "language,question",
    [
        ("et", "Milliseid allergeene on lastemenüüs?"),
        ("en", "What allergens are in your children's menu?"),
        ("ru", "Какие аллергены есть в детском меню?"),
    ],
)
def test_children_menu_allergens_never_inherit_ordinary_dish_declarations(
    client, language, question
):
    session = start(client, language)["session_id"]
    result = turn(client, session, question, language=language)
    state = client.app.state.demo_sessions.sessions[session].tools
    assert all(
        item["name"][language] not in result["reply"]
        for item in state.restaurant["menu"]
    )
    assert state.restaurant["allergy_notice"][language] in result["reply"]
    assert family_reply(state.restaurant, language, details=True) in result["reply"]
    assert result["reply"] == client.provider.spoken[-1]
    assert result["booking_changes"] == [] and result["recap_delivery_id"] is None
    assert not state.pending and not state.holds and not state.bookings


def test_children_allergen_scope_survives_two_prior_capability_topics(client):
    session = start(client, "en")["session_id"]
    result = turn(
        client,
        session,
        "Can I order takeaway? Can you record an allergy note? What allergens are in your children's menu?",
    )
    state = client.app.state.demo_sessions.sessions[session].tools
    assert all(
        item["name"]["en"] not in result["reply"] for item in state.restaurant["menu"]
    )
    assert state.restaurant["allergy_notice"]["en"] in result["reply"]
    assert (
        "confirmed list of dishes or ingredients for the children's menu"
        in result["reply"]
    )
    assert state.information_reply("food_orders") in result["reply"]
    assert state.information_reply("special_requests") in result["reply"]
    assert result["reply"] == client.provider.spoken[-1]
    assert result["booking_changes"] == [] and not state.pending and not state.holds


@pytest.mark.parametrize(
    "language,first,second",
    [
        (
            "en",
            "What allergens are in salmon?",
            "And what allergens are in your children's menu?",
        ),
        (
            "et",
            "Milliseid allergeene sisaldab lõhe?",
            "Aga milliseid allergeene on lastemenüüs?",
        ),
        ("ru", "Какие аллергены в лососе?", "А какие аллергены есть в детском меню?"),
    ],
)
def test_explicit_children_menu_scope_cannot_inherit_a_prior_dish(
    client, language, first, second
):
    session = start(client, language)["session_id"]
    initial = turn(client, session, first, language=language)
    state = client.app.state.demo_sessions.sessions[session].tools
    salmon = next(item for item in state.restaurant["menu"] if item["id"] == "salmon")
    assert salmon["name"][language] in initial["reply"]
    result = turn(client, session, second, language=language)
    assert all(
        item["name"][language] not in result["reply"]
        for item in state.restaurant["menu"]
    )
    assert state._restaurant_dish is None
    assert state.restaurant["allergy_notice"][language] in result["reply"]
    assert family_reply(state.restaurant, language, details=True) in result["reply"]
    assert result["reply"] == client.provider.spoken[-1]
    assert not result["booking_changes"] and not state.pending and not state.holds
