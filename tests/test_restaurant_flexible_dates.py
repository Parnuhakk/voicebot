"""Calendar spelling repair is contextual, bounded and separate from consent."""

import asyncio
import base64
from datetime import datetime
from itertools import product
from zoneinfo import ZoneInfo

import httpx
import pytest

from app.providers.groq import GroqClient
from app.restaurant_call import COPY, parse_restaurant_request
from app.restaurant_dates import CALENDAR_SPELLING, resolve_restaurant_date
from app.restaurant_date_spelling import _distance
from tests.test_restaurant_http import AUTH, start, tomorrow, turn

pytest_plugins = ["tests.test_restaurant_conversation", "tests.test_restaurant_http"]
NOW = datetime(2026, 10, 3, 12, tzinfo=ZoneInfo("Europe/Tallinn"))
TYPOS = {
    "et": "jaanar veebrur maerts april maai juunu juulu auguts septembr oktobte noveber detsembr".split(),
    "en": "Janury Februry Marhc Aprli Maay Juune Jully Augsut Septmber Octobre Novembr Decemeber".split(),
    "ru": "янврая феврля марат аперля маай июння июлля авгусат сентябаря октябиря ноябрья декабяря".split(),
}


def test_bounded_spelling_distance_matches_full_matrix_with_transpositions():
    def reference(left, right):
        rows = [list(range(len(right) + 1))]
        for i, letter in enumerate(left, 1):
            row = [i]
            for j, other in enumerate(right, 1):
                cost = min(
                    row[j - 1] + 1,
                    rows[i - 1][j] + 1,
                    rows[i - 1][j - 1] + (letter != other),
                )
                if i > 1 and j > 1 and letter == right[j - 2] and left[i - 2] == other:
                    cost = min(cost, rows[i - 2][j - 2] + 1)
                row.append(cost)
            rows.append(row)
        return rows[-1][-1]

    words = [
        "".join(chars) for size in range(4) for chars in product("ab", repeat=size)
    ]
    for left, right, limit in product(words, words, range(3)):
        expected = min(reference(left, right), limit + 1)
        assert min(_distance(left, right, limit), limit + 1) == expected


def typo_tomorrow(language):
    target = datetime.fromisoformat(tomorrow())
    return f"{target.day} {TYPOS[language][target.month - 1]}"


@pytest.mark.parametrize("language", ["et", "en", "ru"])
@pytest.mark.parametrize("month", range(1, 13))
def test_spelling_variants_for_every_month_in_each_supported_language(language, month):
    result = resolve_restaurant_date(f"4 {TYPOS[language][month - 1]} 2028", NOW)
    assert result.value == f"2028-{month:02d}-04" and result.issue is None


@pytest.mark.parametrize(
    "text",
    [
        "4 oktobte",
        "neljandal oktobte",
        "neljanadl oktoobrl",
        "4 oktober",
        "neljandana oktoobrina",
        "neljandal oktoobril",
        "4 oktoobrle",
        "4 oktobril",
        "neljas oktobri",
    ],
)
def test_estonian_month_errors_are_one_calendar_date(text):
    result = resolve_restaurant_date(text, NOW)
    assert result.value == "2026-10-04" and result.issue is None


@pytest.mark.parametrize(
    "text,expected",
    [
        ("fourth Octobre", "2026-10-04"),
        ("forth Octber", "2026-10-04"),
        ("kahekümne esimsesl oktoobril", "2026-10-21"),
        ("twenty frist October", "2026-10-21"),
        ("fivth Novembr", "2026-11-05"),
        ("4 октябиря", "2026-10-04"),
        ("четвретого октябра", "2026-10-04"),
        ("четвертому октбярю", "2026-10-04"),
        ("4 октябрём", "2026-10-04"),
        ("neljas veebrur", "2027-02-04"),
        ("4 maerts", "2027-03-04"),
        ("4 martsi", "2027-03-04"),
        ("4 detsembril", "2026-12-04"),
        ("4 Septmber", "2027-09-04"),
        ("4 Decemeber", "2026-12-04"),
    ],
)
def test_english_russian_and_diacritic_variants(text, expected):
    result = resolve_restaurant_date(text, NOW)
    assert result.value == expected and result.issue is None


@pytest.mark.parametrize(
    "text,expected",
    [
        ("homsesks", "2026-10-04"),
        ("ulehomseks", "2026-10-05"),
        ("tommorow", "2026-10-04"),
        ("завтрра", "2026-10-04"),
        ("thrusday", "2026-10-08"),
        ("teisipaeval", "2026-10-06"),
    ],
)
def test_spoken_relative_words_and_weekday_spelling(text, expected):
    result = resolve_restaurant_date(text, NOW, allow_bare_day=True)
    assert result.value == expected and result.issue is None


@pytest.mark.parametrize("text", ["kahe päeva pärast", "in two days", "через два дня"])
def test_known_calendar_grammar_is_never_repaired_into_month_words(text):
    assert CALENDAR_SPELLING.normalize(text, date_reply=True).text == text
    result = resolve_restaurant_date(text, NOW, allow_bare_day=True)
    assert result.value == "2026-10-05" and result.issue is None


@pytest.mark.parametrize(
    "text,expected",
    [
        ("2026/10/4", "2026-10-04"),
        ("2026.10.04", "2026-10-04"),
        ("2026-10-4", "2026-10-04"),
        ("13/10/2026", "2026-10-13"),
        ("10/13/2026", "2026-10-13"),
        ("10-13-2026", "2026-10-13"),
        ("10/10/2026", "2026-10-10"),
        ("13/10", "2026-10-13"),
        ("4 oktobte two thousand and twenty-six", "2026-10-04"),
        ("fourth October twenty twenty-seven", "2027-10-04"),
        ("4. oktoober kaks tuhat kakskümmend kuus", "2026-10-04"),
        ("neljandal oktoobril kahe tuhande kahekümne kuuendal aastal", "2026-10-04"),
        ("kahe tuhande kahekümne kuuendal aastal neljandal oktoobril", "2026-10-04"),
        ("4 октября две тысячи двадцать шестого года", "2026-10-04"),
        ("две тысячи двадцать шестого года четвертого октября", "2026-10-04"),
        ("October fourth nineteen ninety-nine", "1999-10-04"),
    ],
)
def test_unambiguous_numeric_orders_and_explicit_spoken_years(text, expected):
    result = resolve_restaurant_date(text, NOW)
    assert result.value == expected and result.issue is None


@pytest.mark.parametrize(
    "text",
    [
        "04/10/2026",
        "31/04/2026",
        "2026/13/4",
        "4th October twenty five",
        "4th October two thousand one hundred",
        "4 oktobte või 5 november",
    ],
)
def test_number_orders_impossible_dates_and_incomplete_spoken_years_need_clarification(
    text,
):
    result = resolve_restaurant_date(text, NOW)
    assert result.value is None and result.issue


@pytest.mark.parametrize(
    "year",
    [
        "two thousnad twenty-seven",
        "two thousnd twenty-seven",
        "two thosand twenty-seven",
    ],
)
def test_malformed_adjacent_spoken_year_clears_previous_date_without_guessing(year):
    previous = {"date": "2026-10-06", "party_size": 4, "start_time": "18:00"}
    text = "Book a table on 4 Octobre " + year
    resolved = resolve_restaurant_date(text, NOW)
    assert resolved.value is None and resolved.issue == "date_ambiguous"
    assert parse_restaurant_request(text, previous, now=NOW) == {
        "date_issue": "date_ambiguous",
        "party_size": 4,
        "start_time": "18:00",
    }
    assert previous == {"date": "2026-10-06", "party_size": 4, "start_time": "18:00"}


@pytest.mark.parametrize("scale", ["thousnad", "thousnd", "thosand"])
def test_partial_month_malformed_year_cannot_invent_a_day(scale):
    previous = {"date": "2026-10-06", "party_size": 4, "start_time": "18:00"}
    text = f"Book a table for November two {scale} twenty-seven"
    resolved = resolve_restaurant_date(text, NOW)
    assert resolved.value is None and resolved.issue == "date_ambiguous"
    assert parse_restaurant_request(text, previous, now=NOW) == {
        "date_issue": "date_ambiguous",
        "party_size": 4,
        "start_time": "18:00",
    }
    assert previous == {"date": "2026-10-06", "party_size": 4, "start_time": "18:00"}


@pytest.mark.parametrize("day", ["twenty-first", "twenty first"])
def test_month_first_ordinary_ordinal_remains_a_day(day):
    result = resolve_restaurant_date(f"Book a table for October {day}", NOW)
    assert result.value == "2026-10-21" and result.issue is None


@pytest.mark.parametrize(
    "numeric",
    [
        "2026/10/04/2027",
        "2026.10.04.2027",
        "04.10.2026.2027",
        "2026/10/04.2027",
        "2026//10/04",
        "2026/10/04/",
    ],
)
def test_malformed_whole_numeric_date_cannot_accept_a_valid_prefix(numeric):
    previous = {"date": "2026-10-06", "party_size": 4, "start_time": "18:00"}
    text = "A table on " + numeric
    resolved = resolve_restaurant_date(text, NOW)
    assert resolved.value is None and resolved.issue
    result = parse_restaurant_request(text, previous, now=NOW)
    assert "date" not in result and result["date_issue"]
    assert result["party_size"] == 4 and result["start_time"] == "18:00"
    assert previous["date"] == "2026-10-06"


def test_short_weekday_typo_conflicting_with_explicit_date_requires_clarification():
    text = "Book a table on 4 Octobre 2026, Frday"
    previous = {"date": "2026-10-06", "party_size": 4, "start_time": "18:00"}
    assert resolve_restaurant_date(text, NOW).issue == "date_ambiguous"
    assert parse_restaurant_request(text, previous, now=NOW) == {
        "date_issue": "date_ambiguous",
        "party_size": 4,
        "start_time": "18:00",
    }
    assert previous["date"] == "2026-10-06"


@pytest.mark.parametrize("count,number", [("nineteen", 19), ("twenty", 20)])
@pytest.mark.parametrize("noun", ["guests", "people"])
def test_adjacent_spoken_party_is_not_consumed_as_a_year(count, number, noun):
    text = f"A table on fourth October, {count} {noun} at 18:00"
    previous = {"date": "2026-10-06", "party_size": 4, "start_time": "17:00"}
    resolved = resolve_restaurant_date(text, NOW)
    assert resolved.value == "2026-10-04" and resolved.issue is None
    assert f"{count} {noun}" in resolved.remaining_text
    assert parse_restaurant_request(text, previous, now=NOW) == {
        "date": "2026-10-04",
        "party_size": number,
        "start_time": "18:00",
    }
    assert previous == {"date": "2026-10-06", "party_size": 4, "start_time": "17:00"}


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Book a table on 9 Octobre 2026, Frday", "2026-10-09"),
        ("Book a table on Frday, 9 Octobre 2026", "2026-10-09"),
        ("Book a table on 4 Octobre 2026, ready for dinner", "2026-10-04"),
        ("A table on 2026/10/04. at 18:00", "2026-10-04"),
    ],
)
def test_bounded_calendar_checks_preserve_valid_dates_and_ordinary_words(
    text, expected
):
    result = resolve_restaurant_date(text, NOW)
    assert result.value == expected and result.issue is None


def test_missing_year_means_the_next_actual_leap_day():
    assert resolve_restaurant_date("29 Februry", NOW).value == "2028-02-29"
    assert resolve_restaurant_date("29 Februry 2026", NOW).issue == "date_invalid"


def test_month_with_a_spoken_year_retains_the_year_for_the_later_day():
    first = parse_restaurant_request(
        "oktobte kaks tuhat kakskümmend seitse", {}, now=NOW, expected_field="date"
    )
    assert first == {
        "date_issue": "date_incomplete",
        "date_month": 10,
        "date_year": 2027,
    }
    result = parse_restaurant_request(
        "neljanadl", first, now=NOW, expected_field="date_incomplete"
    )
    assert result == {"date": "2027-10-04"}


@pytest.mark.parametrize("month", ["May", "October", "oktobte", "октябрь"])
def test_month_then_spoken_year_does_not_invent_a_day(month):
    result = resolve_restaurant_date(
        month + " two thousand twenty-seven", NOW, allow_bare_day=True
    )
    assert result.value is None and result.issue == "date_incomplete"
    assert result.year == 2027 and result.day is None


def test_date_repair_preserves_estonian_booking_words():
    text = "Soovin lauaks 5 oktobte kell 17.00 nelja inimesega"
    assert parse_restaurant_request(text, now=NOW) == {
        "date": "2026-10-05",
        "start_time": "17:00",
        "party_size": 4,
    }


def test_russian_evening_is_not_repaired_into_yesterday():
    text = "Столик на четверых завтра в шесть тридцать вечера"
    assert parse_restaurant_request(text, now=NOW) == {
        "date": "2026-10-04",
        "start_time": "18:30",
        "party_size": 4,
    }


@pytest.mark.parametrize(
    "first,second", [("neljanadl", "oktobte"), ("oktobte", "neljanadl")]
)
def test_imperfect_day_and_month_answers_combine_without_changing_guest_count(
    first, second
):
    previous = {"party_size": 4, "start_time": "18:00"}
    result = parse_restaurant_request(first, previous, now=NOW, expected_field="date")
    assert "date" not in result and result["date_issue"] == "date_incomplete"
    result = parse_restaurant_request(
        second, result, now=NOW, expected_field="date_incomplete"
    )
    assert result == {"date": "2026-10-04", "party_size": 4, "start_time": "18:00"}


@pytest.mark.parametrize(
    "text",
    [
        "4 juui",
        "4 marst",
        "31 Februr",
        "4 Octobre or 5 Novembre",
        "not 4 oktobte",
        "mitte neljanadl oktobte",
    ],
)
def test_uncertain_impossible_and_declined_dates_cannot_keep_previous_day(text):
    result = parse_restaurant_request(
        text, {"date": "2026-10-06", "party_size": 2, "start_time": "18:00"}, now=NOW
    )
    assert "date" not in result and result["date_issue"]
    assert result["party_size"] == 2 and result["start_time"] == "18:00"


@pytest.mark.parametrize(
    "text",
    [
        "May I book a table?",
        "We may need a table",
        "What is on the menu?",
        "My name is Augustus",
        "I'm at home",
        "four guests",
        "for two adults",
        "октябрьский",
        "septemberfest",
        "Octoberfest",
        "Can I bring my dog?",
    ],
)
def test_ordinary_business_words_and_names_do_not_gain_a_date(text):
    result = resolve_restaurant_date(text, NOW)
    assert result.value is None and result.issue is None


def test_parsing_copy_is_corrected_without_rewriting_caller_input():
    text = "Soovin lauda neljanadl oktobte kell 18:00 neljale"
    inquiry = parse_restaurant_request(text, now=NOW)
    assert inquiry == {"date": "2026-10-04", "start_time": "18:00", "party_size": 4}
    assert text == "Soovin lauda neljanadl oktobte kell 18:00 neljale"
    assert "oktoober" in CALENDAR_SPELLING.normalize(text.casefold()).text


@pytest.mark.parametrize("language", ["et", "en", "ru"])
@pytest.mark.parametrize("audio", [False, True])
def test_http_recognition_keeps_original_transcript_and_uses_repaired_date(
    client, language, audio
):
    assert client.get("/api/status").json()["capabilities"][
        "restaurant_flexible_dates_ready"
    ]
    session = start(client, language)["session_id"]
    initial = {
        "et": "Soovin lauda neljale",
        "en": "A table for four",
        "ru": "Столик на четверых",
    }[language]
    turn(client, session, initial, language=language)
    text = typo_tomorrow(language)
    provider = GroqClient(
        "fixture",
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                200,
                json={
                    "text": text,
                    "language": {"et": "estonian", "en": "english", "ru": "russian"}[
                        language
                    ],
                },
            )
        ),
    )
    try:
        if audio:
            client.app.state.stack["stt"] = provider
            result = client.post(
                "/api/turn",
                headers=AUTH,
                json={
                    "session_id": session,
                    "language": language,
                    "audio_b64": base64.b64encode(b"fixture").decode(),
                },
            ).json()
        else:
            result = turn(client, session, text, language=language)
        assert (
            result["text_heard"] == text and result["reply"] == COPY[language]["time"]
        )
        assert result["input_status"] == ("recognized" if audio else "typed")
        result = turn(client, session, "18:00", language=language)
        assert result["recap_delivery_id"] and not result["booking_ids"]
        state = client.app.state.demo_sessions.sessions[session].tools
        assert state.booking_inquiry["date"] == tomorrow()
        assert state.pending["recap"]["party_size"] == 4
    finally:
        provider.close()


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_native_final_turn_understands_the_same_imperfect_calendar_words(
    make_state, language
):
    agents = pytest.importorskip("livekit.agents")
    from app.worker import TelephoneAgent

    async def run():
        state = make_state(language)
        agent = TelephoneAgent(state)
        for text in ["table for four", typo_tomorrow(language), "18:00"]:
            message = agents.llm.ChatMessage(role="user", content=[text])
            agent._detected_language = language
            await agent.on_user_turn_completed(agents.llm.ChatContext(), message)
            state.guard_reply("", [])
            assert message.text_content == text
        assert state.booking_inquiry == {
            "date": tomorrow(),
            "start_time": "18:00",
            "party_size": 4,
        }
        assert not state.bookings

    asyncio.run(run())
