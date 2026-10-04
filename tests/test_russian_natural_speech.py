"""Russian spoken delivery with local HTTP/media fixtures, never live audio."""

import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace as NS
from xml.etree import ElementTree as ET

import httpx
import pytest

from app.booking.tools import Dispatcher
from app.languages import CONSENT
from app.providers.azure_tts import AzureTtsClient, ssml
from app.providers.russian_speech import duration, guest_count, spoken_date, spoken_time
from app.providers.speech_delivery import SpeechDelivery
from app.restaurant_answers import format_schedule, match_question
from app.restaurant_call import COPY, RestaurantCallTools
from app.restaurant_data import load_restaurant_data
from tests.test_restaurant_http import start, tomorrow, turn

pytest_plugins = ["tests.test_restaurant_http"]

SSML = "{http://www.w3.org/2001/10/synthesis}"
MSTTS = "{http://www.w3.org/2001/mstts}"


@pytest.mark.parametrize(
    "hour,minute,expected",
    [
        (0, 0, "двенадцать ночи"),
        (1, 0, "час ночи"),
        (6, 5, "шесть ноль пять утра"),
        (12, 0, "двенадцать дня"),
        (13, 0, "час дня"),
        (14, 15, "два пятнадцать дня"),
        (18, 30, "шесть тридцать вечера"),
        (21, 0, "девять вечера"),
        (23, 59, "одиннадцать пятьдесят девять вечера"),
    ],
)
def test_clock_has_a_clear_time_of_day_without_zero_minutes(hour, minute, expected):
    assert spoken_time(hour, minute) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("2026-10-04", "четвёртого октября две тысячи двадцать шестого года"),
        ("2026-10-23", "двадцать третьего октября две тысячи двадцать шестого года"),
        ("2000-02-29", "двадцать девятого февраля двухтысячного года"),
        ("2030-12-31", "тридцать первого декабря две тысячи тридцатого года"),
    ],
)
def test_dates_use_ordinals_and_a_spoken_year(value, expected):
    assert spoken_date(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (1, "одного гостя"),
        (2, "двух гостей"),
        (3, "трёх гостей"),
        (4, "четырёх гостей"),
        (5, "пять гостей"),
        (6, "шесть гостей"),
        (11, "одиннадцать гостей"),
        (20, "двадцать гостей"),
    ],
)
def test_booking_guest_count_agrees_with_na(value, expected):
    assert guest_count(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (31, "тридцать одну минуту"),
        (32, "тридцать две минуты"),
        (45, "сорок пять минут"),
        (60, "час"),
        (90, "полтора часа"),
        (120, "два часа"),
        (240, "четыре часа"),
    ],
)
def test_duration_is_short_and_grammatical(value, expected):
    assert duration(value) == expected


@pytest.mark.parametrize("value", [0, -1, 21, True, 1.5])
def test_invalid_guest_count_is_rejected(value):
    with pytest.raises(ValueError):
        guest_count(value)


@pytest.mark.parametrize(
    "hour,minute", [(24, 0), (-1, 0), (18, 60), (True, 0), (18, 1.5)]
)
def test_invalid_clock_is_rejected(hour, minute):
    with pytest.raises(ValueError):
        spoken_time(hour, minute)


def test_all_supported_guest_counts_and_duration_bounds_are_spoken():
    assert all(
        guest_count(value).endswith(("гостя", "гостей")) for value in range(1, 21)
    )
    assert all(duration(value) for value in range(30, 241))
    assert all(spoken_time(hour, minute) for hour in range(24) for minute in range(60))


@pytest.mark.parametrize(
    "text,aliases",
    [
        ("Приходите в 18:30.", ["в шесть тридцать вечера"]),
        ("Открыты с 12 до 21.", ["с двенадцати дня до девяти вечера"]),
        ("Кухня с 12:00 до 20:30.", ["с двенадцати дня до восьми тридцати вечера"]),
        ("С 01:00 до 06:05.", ["с часа ночи до шести ноль пяти утра"]),
        (
            "2026-10-04 18:30",
            [
                "четвёртого октября две тысячи двадцать шестого года в шесть тридцать вечера"
            ],
        ),
        (
            "4 октября 2026 в 18:30",
            [
                "четвёртого октября две тысячи двадцать шестого года",
                "в шесть тридцать вечера",
            ],
        ),
        ("На 23 октября.", ["двадцать третье октября"]),
        (
            "Meretuule Demo Restaurant, Europe/Tallinn",
            ["деморесторан Меретууле", "по времени Таллина"],
        ),
    ],
)
def test_pronunciation_preserves_canonical_text_and_native_sentence_timing(
    text, aliases
):
    document = ET.fromstring(ssml(text, "ru-RU-SvetlanaNeural", "ru-RU"))
    assert [node.get("alias") for node in document.iter(SSML + "sub")] == aliases
    assert "".join(document.itertext()) == text
    assert not list(document.iter(MSTTS + "silence"))
    assert not list(document.iter(MSTTS + "express-as"))
    assert document.find(".//" + SSML + "prosody").get("rate") == "1.12"


@pytest.mark.parametrize(
    "text",
    [
        "31 февраля 2026",
        "2026-02-30",
        "в 24:00",
        "в 18:60",
        "в 6:3",
        "в 118:30",
        "в 18:30:15",
        "в 6:00 вечера",
        "с 12 до 21 евро",
        "с 1 до 4 гостей",
        "с 1 до 4 октября",
        "с 12 до 21 минут",
        "с 12 до 21 дней",
        "с 12 до 21 кг",
        "с 1 до 4 часов",
        "с 1 до 4 недель",
        "с 12 до 21 вечера",
        "с 12 до 24",
        "соотношение 1:30",
        "номер 12345",
        "10–20%",
    ],
)
def test_invalid_or_non_time_numbers_are_left_literal(text):
    document = ET.fromstring(ssml(text, "ru-RU-SvetlanaNeural", "ru-RU"))
    assert not list(document.iter(SSML + "sub"))
    assert "".join(document.itertext()) == text


def test_payload_cannot_introduce_ssml_and_neutral_mode_remains_literal():
    text = '<audio src="https://example.invalid"/> & 4 октября 2026 в 18:30'
    natural = ET.fromstring(ssml(text, "ru-RU-SvetlanaNeural", "ru-RU"))
    assert not list(natural.iter(SSML + "audio"))
    assert "".join(natural.itertext()) == text
    neutral = ET.fromstring(
        ssml(text, "ru-RU-SvetlanaNeural", "ru-RU", SpeechDelivery(mode="neutral"))
    )
    assert "".join(neutral.itertext()) == text
    assert not list(neutral.iter(SSML + "sub"))
    assert not list(neutral.iter(SSML + "prosody"))


def test_actual_russian_recap_introduction_preserves_venue_alias_and_canonical_text(
    client,
):
    session = start(client, "ru")["session_id"]
    result = turn(client, session, "Столик на четверых завтра в 18:00", language="ru")
    text = result["reply"]
    assert text.startswith("Могу предложить столик: ")
    markup = ET.fromstring(ssml(text, "ru-RU-SvetlanaNeural", "ru-RU"))
    assert "Меретууле" in [node.get("alias") for node in markup.iter(SSML + "sub")]
    assert "".join(markup.itertext()) == text
    state = client.app.state.demo_sessions.sessions[session].tools
    assert state.pending["recap"]["party_size"] == 4
    assert state.pending["recap"]["duration_minutes"] == 90
    assert state.pending["recap"]["date"] == tomorrow()
    assert result["booking_changes"] == []


@pytest.mark.parametrize("voice", ["ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural"])
def test_weekly_schedule_is_short_sentences_and_spoken_clock_ranges(voice):
    schedule = format_schedule(load_restaurant_data(), "ru") + "."
    document = ET.fromstring(ssml(schedule, voice, "ru-RU"))
    assert schedule.count(".") == 3
    assert [node.get("alias") for node in document.iter(SSML + "sub")] == [
        "с двенадцати дня до девяти вечера",
        "с двенадцати дня до одиннадцати вечера",
        "с двенадцати дня до восьми вечера",
    ]
    assert not list(document.iter(MSTTS + "silence"))


def test_alternative_times_are_clear_but_not_a_booking_confirmation():
    state = RestaurantCallTools(
        Dispatcher(business_type="restaurant", restaurant_data=load_restaurant_data()),
        language="ru",
    )
    reply = state.guard_reply(
        "",
        [
            {
                "restaurant_unavailable": True,
                "alternatives": ["18:00", "18:30"],
            }
        ],
    )
    assert (
        reply
        == "На это время столика нет. В тот же день есть шесть вечера и шесть тридцать вечера. Что вам удобнее?"
    )
    assert state.pending is None and not state.bookings


@pytest.mark.parametrize(
    "text,topic",
    [
        ("Сколько стоит суп?", "price"),
        ("Сколько он стоит?", "price"),
        ("Сколько будет стоить ужин?", "price"),
        ("Сколько стоят блюда?", "price"),
        ("Стоит ли прийти с собакой?", "pets"),
        ("Где стоит столик?", "location"),
    ],
)
def test_cost_questions_are_distinct_from_advice_or_location(text, topic):
    question = match_question(text, has_dish="суп" in text)
    assert question and question.topics[0] == topic
    if topic != "price":
        assert "price" not in question.topics


def test_russian_http_replies_recap_audio_and_booking_approval(client):
    requests = []

    def respond(request):
        if request.url.path.endswith("issueToken"):
            return httpx.Response(200, text="fixture-token")
        requests.append(ET.fromstring(request.content))
        return httpx.Response(200, content=b"fixture-mp3")

    speaker = AzureTtsClient(
        "fixture",
        "fixture",
        "ru-RU-SvetlanaNeural",
        "ru-RU",
        languages={"ru": ("ru-RU-SvetlanaNeural", "ru-RU")},
        transport=httpx.MockTransport(respond),
    )
    client.app.state.stack["tts"] = speaker
    try:
        session = start(client, "ru")
        assert session["greeting"] == COPY["ru"]["greeting"]
        identifier = session["session_id"]
        for question, expected in [
            (
                "Можно прийти с собакой?",
                "Можно прийти с собакой. О других питомцах спросите сотрудника ресторана.",
            ),
            (
                "Стоит ли прийти с собакой?",
                "Можно прийти с собакой. О других питомцах спросите сотрудника ресторана.",
            ),
            (
                "На сколько времени можно забронировать столик?",
                "Столик будет за вами на полтора часа.",
            ),
            ("Где находится ресторан?", "Адреса ресторана у меня пока нет."),
            ("Сколько стоит суп?", COPY["ru"]["price"]),
            ("Сколько стоят блюда?", COPY["ru"]["price"]),
        ]:
            answer = turn(client, identifier, question, language="ru")
            assert answer["reply"] == expected
            assert "".join(requests[-1].itertext()) == expected
            assert answer["booking_changes"] == []
        proposal = turn(
            client,
            identifier,
            f"Столик на одного гостя {tomorrow()} в 18:30",
            language="ru",
        )
        assert "на одного гостя" in proposal["reply"]
        assert "на полтора часа" in proposal["reply"]
        assert proposal["reply"].endswith(COPY["ru"]["confirmation_question"])
        assert "Скажите" not in proposal["reply"]
        assert "в шесть тридцать вечера" in [
            node.get("alias") for node in requests[-1].iter(SSML + "sub")
        ]
        assert requests[-1].find(".//" + SSML + "prosody").get("rate") == "1.00"
        state = client.app.state.demo_sessions.sessions[identifier].tools
        assert not state.pending["delivery"] and not state.pending["approved"]
        early = turn(client, identifier, CONSENT["ru"], language="ru")
        assert early["booking_changes"] == []
        assert not state.bookings
        proposal = turn(
            client,
            identifier,
            f"Столик на одного гостя {tomorrow()} в 18:30",
            language="ru",
        )
        confirmed = turn(
            client,
            identifier,
            CONSENT["ru"],
            language="ru",
            receipt=proposal["recap_delivery_id"],
        )
        assert confirmed["reply"] == COPY["ru"]["confirmed"]
        assert len(confirmed["booking_changes"]) == 1
        assert all(not list(document.iter(MSTTS + "silence")) for document in requests)
    finally:
        speaker.close()


def test_native_provider_uses_the_same_russian_markup_and_language_reset():
    pytest.importorskip("livekit.agents")
    from app.providers.telephone_tts import TelephoneTTS

    async def run():
        requests = []

        async def chunks():
            yield b"\0\0" * 2400, False

        @asynccontextmanager
        async def post(**kwargs):
            requests.append(ET.fromstring(kwargs["data"]))
            yield NS(raise_for_status=lambda: None, content=NS(iter_chunks=chunks))

        provider = TelephoneTTS(
            voice="ru-RU-SvetlanaNeural",
            language="ru-RU",
            delivery=SpeechDelivery(),
            speech_key="fixture",
            speech_region="fixture",
            http_session=NS(post=post),
        )
        try:
            async with provider.synthesize("Приходите в 18:30.") as stream:
                assert [event async for event in stream]
            provider.set_recap_delivery(True)
            async with provider.synthesize("4 октября 2026 в 18:30") as stream:
                assert [event async for event in stream]
            provider.set_recap_delivery(False)
            provider.update_options(voice="et-EE-AnuNeural", language="et-EE")
            async with provider.synthesize("Tere!") as stream:
                assert [event async for event in stream]
        finally:
            await provider.aclose()
        assert (
            requests[0].find(".//" + SSML + "sub").get("alias")
            == "в шесть тридцать вечера"
        )
        assert requests[1].find(".//" + SSML + "prosody").get("rate") == "1.00"
        assert all(not list(doc.iter(MSTTS + "silence")) for doc in requests[:2])
        assert requests[2].find(".//" + MSTTS + "silence") is None

    asyncio.run(run())
