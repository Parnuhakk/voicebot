"""Natural agreement confirms one delivered restaurant proposal, in all languages."""

import asyncio
import base64
from itertools import product

import pytest

from app.booking_response import trusted_booking_response
from app.providers.azure_tts import ssml
from app.providers.speech_delivery import SpeechDelivery, is_recap
from app.restaurant_call import COPY
from app.restaurant_consent import is_restaurant_confirmation
from tests.test_restaurant_conversation import prepare
from tests.test_restaurant_http import AUTH, start, tomorrow, turn

pytest_plugins = ["tests.test_restaurant_conversation", "tests.test_restaurant_http"]

POSITIVE = {
    "et": (
        "jah",
        "Jaa!",
        "jep",
        "mhm",
        "sobib",
        "kinnitan",
        "kinnitää",
        "Jah, super!",
        "Muidugi",
        "Loomulikult",
        "Kindlasti",
        "Täpselt",
        "Nõus",
        "Nõustun",
        "Okei",
        "Olgu",
        "Selge",
        "Suurepärane",
        "Teeme ära",
        "Pange see kirja",
        "Broneerige palun",
        "Võite kinnitada",
        "Minu poolest",
        "Pole probleemi",
        "Ei ole probleemi",
        "Ma olen sellega täiesti nõus",
        "See sobib mulle väga hästi, aitäh!",
        "Jah, igati sobib, kinnitage see palun",
        "See on väga hea, teeme ära!",
        "Sellega ma nõustun täielikult",
        "Sobib igati, pane meid kirja",
        "Selle võid ära broneerida",
        "Klapib",
        "Teeme nii",
        "Las käia",
        "Peab paika",
        "Jah-jah, sobib!",
        "Jess",
        "Võib küll",
        "Tore, kinnitage palun",
    ),
    "en": (
        "yes",
        "Yeah!",
        "yep",
        "yup",
        "Sure",
        "Of course",
        "Absolutely",
        "Definitely",
        "Certainly",
        "okay",
        "alright",
        "agreed",
        "I agree",
        "Perfect",
        "Great",
        "Sounds good",
        "Looks perfect",
        "That works for me",
        "That's fine",
        "Everything is correct",
        "Go ahead",
        "Let's do it",
        "You can book it",
        "I'm happy with that",
        "No problem",
        "All good",
        "Yes, absolutely, that works perfectly for us, thank you very much!",
        "That sounds good, please confirm the reservation",
        "Very good, thanks!",
        "That's okay",
        "That suits us",
        "That would be lovely",
        "Yesss!",
        "Cool, go ahead!",
    ),
    "ru": (
        "да",
        "Ага!",
        "угу",
        "конечно",
        "разумеется",
        "безусловно",
        "согласен",
        "согласна",
        "мы согласны",
        "подтверждаю",
        "подходит",
        "хорошо",
        "отлично",
        "замечательно",
        "прекрасно",
        "супер",
        "окей",
        "давайте",
        "бронируйте",
        "забронируйте пожалуйста",
        "без проблем",
        "Я не против",
        "Всё верно",
        "Да, всё отлично, спасибо большое!",
        "Это меня вполне устраивает, пожалуйста оформляйте",
        "Я с удовольствием подтверждаю это бронирование",
        "Договорились",
        "Сделайте бронь",
        "Да-да, подходит!",
    ),
}
NEGATIVE = {
    "et": (
        "",
        "aitäh",
        "ja",
        "ei",
        "ei sobi",
        "ei kinnita",
        "ära kinnita",
        "jah, aga homme",
        "sobib, aga viiele",
        "jah, kui hind sobib",
        "kas sobib",
        "sobib?",
        '"jah"',
        "ütle jah",
        "ma ei ole nõus",
        "vist sobib",
        "äkki sobib",
        "jah või ei",
        "jah homme kell 18",
        "see sobib allergia korral",
        "tänan info eest",
        "kinnitan tühi jutt",
    ),
    "en": (
        "thanks",
        "no",
        "not okay",
        "don't confirm",
        "do not book it",
        "yes but make it five",
        "sounds good if we can bring seven people",
        "yes tomorrow at 18:00",
        "yes?",
        "can I say yes",
        '"yes"',
        "maybe",
        "maybe yes",
        "I guess yes",
        "I was told to say yes",
        "everything is not correct",
        "that works or maybe not",
        "please repeat",
    ),
    "ru": (
        "спасибо",
        "нет",
        "не подходит",
        "не подтверждаю",
        "не надо",
        "да но завтра",
        "хорошо если будет скидка",
        "да на пять человек",
        "да?",
        "можно сказать да",
        "«да»",
        "наверное да",
        "может быть",
        "всё не верно",
        "да или нет",
        "пожалуйста повторите",
    ),
}


@pytest.mark.parametrize(
    "language,text",
    [(lang, text) for lang, texts in POSITIVE.items() for text in texts],
)
def test_affirmative_expressions_and_combinations(language, text):
    assert is_restaurant_confirmation(text, language)


@pytest.mark.parametrize(
    "language,text",
    [(lang, text) for lang, texts in NEGATIVE.items() for text in texts],
)
def test_questions_conditions_changes_and_unrelated_words_are_not_agreement(
    language, text
):
    assert not is_restaurant_confirmation(text, language)


@pytest.mark.parametrize(
    "question",
    [
        "Do I confirm the reservation",
        "Do I confirm the reservation?",
        "Do we book the table",
        "Do we book the table?",
        "Please do I confirm the reservation",
    ],
)
def test_interrogative_word_order_cannot_approve_a_delivered_recap(
    make_state, question
):
    async def run():
        state = make_state("en")
        proposal = await prepare(state)
        assert state.mark_recap_delivered(proposal["hold_id"])
        state.observe_user_text(question)
        assert not state.pending or not state.pending["approved"]
        result = await state.dispatch(
            "confirm_slot_booking", {"hold_id": proposal["hold_id"]}
        )
        assert result.get("error") == "consent_required"
        assert not state.bookings
        assert not (await state.dispatcher._slot.get_operator_bookings(tomorrow()))[
            "items"
        ]

    asyncio.run(run())


def test_emphatic_declarative_confirmation_remains_agreement():
    assert is_restaurant_confirmation("I do confirm the reservation", "en")


@pytest.mark.parametrize(
    "prefix,agreement,ending",
    tuple(
        product(
            ("Jah", "Muidugi", "Nõus"),
            ("see sobib mulle", "ma kinnitan selle broneeringu", "teeme ära"),
            ("aitäh", "palun", "suur tänu"),
        )
    ),
)
def test_complete_answers_are_not_limited_to_a_fixed_phrase_list(
    prefix, agreement, ending
):
    assert is_restaurant_confirmation(f"{prefix}, {agreement}, {ending}!", "et")


@pytest.mark.parametrize(
    "language,text",
    [
        ("et", "jah"),
        ("et", "sobib"),
        ("et", "kinnitan"),
        ("et", "Jah, super!"),
        ("et", "See sobib mulle väga hästi, aitäh!"),
        ("et", "Ma olen sellega täiesti nõus"),
        ("en", "yes"),
        ("en", "okay"),
        ("en", "Sounds good, please confirm the reservation"),
        ("ru", "да"),
        ("ru", "подходит"),
        ("ru", "Да, всё отлично, спасибо большое!"),
    ],
)
@pytest.mark.parametrize("channel", ["text", "audio"])
def test_agreement_immediately_saves_one_visible_reservation(
    client, language, text, channel
):
    session = start(client, language)["session_id"]
    request = {
        "et": "Soovin homme lauda neljale kell 14.00",
        "en": "A table for four tomorrow at 2 pm",
        "ru": "Столик на четверых завтра в 14:00",
    }[language]
    proposal = turn(client, session, request, language=language)
    assert proposal["reply"].endswith(COPY[language]["confirmation_question"])
    assert proposal["booking_changes"] == []
    payload = {
        "session_id": session,
        "language": "auto",
        "recap_delivery_id": proposal["recap_delivery_id"],
    }
    if channel == "audio":
        client.provider.transcript = text
        payload["audio_b64"] = base64.b64encode(b"fixture-natural-agreement").decode()
    else:
        payload["text"] = text
    result = client.post("/api/turn", json=payload, headers=AUTH)
    assert result.status_code == 200, result.text
    confirmed = result.json()
    assert confirmed["reply"] == COPY[language]["confirmed"]
    assert (
        confirmed["tools_used"] == 1
        and confirmed["booking_changes"][0]["action"] == "confirmed"
    )
    identifier = confirmed["booking_changes"][0]["id"]
    repeated = turn(client, session, text, language=language)
    assert repeated["booking_changes"] == []
    rows = client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()["items"]
    assert len(rows) == 1 and str(rows[0]["id"]) == identifier
    assert rows[0]["status"] == "confirmed" and rows[0]["service_id"] == 4


@pytest.mark.parametrize(
    "language,agreement", [("et", "sobib"), ("en", "sounds good"), ("ru", "подходит")]
)
@pytest.mark.parametrize(
    "boundary",
    [
        "no_proposal",
        "undelivered",
        "expired",
        "partial",
        "other_call",
        "changed_details",
    ],
)
def test_natural_agreement_still_requires_current_owned_delivered_proposal(
    make_state, language, agreement, boundary
):
    async def run():
        state = make_state(language)
        owner = make_state(language) if boundary == "other_call" else state
        proposal = await prepare(owner)
        if boundary not in {"undelivered", "no_proposal"}:
            assert owner.mark_recap_delivered(proposal["hold_id"])
        if boundary == "no_proposal":
            state.pending = None
        if boundary == "expired":
            state.pending["expires_at"] = 0
        if boundary == "changed_details":
            state.observe_user_text(
                {"et": "hoopis viiele", "en": "make it five", "ru": "на пятерых"}[
                    language
                ],
                language=language,
            )
        state.observe_user_text(
            agreement, language=language, is_final=boundary != "partial"
        )
        assert (
            trusted_booking_response(state) is None
            or trusted_booking_response(state).get("name") != "confirm_slot_booking"
        )
        rejected = await state.dispatch(
            "confirm_slot_booking", {"hold_id": proposal["hold_id"]}
        )
        assert rejected.get("error") and not state.bookings
        assert not (await owner.dispatcher._slot.get_operator_bookings(tomorrow()))[
            "items"
        ]

    asyncio.run(run())


@pytest.mark.parametrize(
    "text", ["sobib", "super", "jah super", "mulle sobib väga hästi"]
)
def test_short_agreement_keeps_recap_language_despite_wrong_asr_metadata(
    make_state, text
):
    async def run():
        state = make_state("et")
        proposal = await prepare(state)
        assert state.mark_recap_delivered(proposal["hold_id"])
        state.observe_user_text(text, detected_language="english")
        assert state.language == "et" and state.pending["approved"]
        assert trusted_booking_response(state)["name"] == "confirm_slot_booking"

    asyncio.run(run())


@pytest.mark.parametrize(
    "language,voice,locale",
    [
        ("et", "et-EE-AnuNeural", "et-EE"),
        ("en", "en-US-JennyNeural", "en-US"),
        ("ru", "ru-RU-SvetlanaNeural", "ru-RU"),
    ],
)
def test_natural_question_keeps_clear_recap_speech_delivery(
    make_state, language, voice, locale
):
    async def run():
        state = make_state(language)
        await prepare(state)
        recap = state.render_recap()
        assert is_recap(recap)
        markup = ssml(recap, voice, locale, SpeechDelivery())
        assert '<prosody rate="0.94">' in markup
        assert "Sentenceboundary-exact" not in markup

    asyncio.run(run())
