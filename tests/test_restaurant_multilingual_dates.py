"""Independent calendar fixtures for spoken English and Russian, not live ASR."""

from datetime import date

import pytest

from app.restaurant_call import parse_restaurant_request
from app.restaurant_dates import resolve_restaurant_date
from tests.test_restaurant_dates import NOW


ENGLISH_DAYS = (
    "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth",
    "ninth", "tenth", "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth",
    "sixteenth", "seventeenth", "eighteenth", "nineteenth", "twentieth",
    "twenty-first", "twenty-second", "twenty-third", "twenty-fourth", "twenty-fifth",
    "twenty-sixth", "twenty-seventh", "twenty-eighth", "twenty-ninth", "thirtieth",
    "thirty-first",
)
RUSSIAN_DAYS = (
    "первое", "второе", "третье", "четвёртое", "пятое", "шестое", "седьмое",
    "восьмое", "девятое", "десятое", "одиннадцатое", "двенадцатое", "тринадцатое",
    "четырнадцатое", "пятнадцатое", "шестнадцатое", "семнадцатое", "восемнадцатое",
    "девятнадцатое", "двадцатое", "двадцать первое", "двадцать второе",
    "двадцать третье", "двадцать четвёртое", "двадцать пятое", "двадцать шестое",
    "двадцать седьмое", "двадцать восьмое", "двадцать девятое", "тридцатое",
    "тридцать первое",
)
ENGLISH_MONTHS = (
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
)
RUSSIAN_MONTHS = (
    "января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа",
    "сентября", "октября", "ноября", "декабря",
)


@pytest.mark.parametrize("language", ["en", "ru"])
@pytest.mark.parametrize("day", range(1, 32))
@pytest.mark.parametrize("month", range(1, 13))
def test_every_calendar_day_in_every_month(language, day, month):
    if language == "en":
        text = f"the {ENGLISH_DAYS[day - 1]} of {ENGLISH_MONTHS[month - 1]} 2028"
    else:
        word = RUSSIAN_DAYS[day - 1]
        word = word[:-1] + "его" if word.endswith("тье") else word[:-2] + "ого"
        text = f"на {word} {RUSSIAN_MONTHS[month - 1]} 2028 года"
    result = resolve_restaurant_date(text, NOW)
    try:
        expected = date(2028, month, day).isoformat()
    except ValueError:
        assert result.value is None and result.issue == "date_invalid"
    else:
        assert result.value == expected and result.issue is None


@pytest.mark.parametrize(
    "text",
    [
        "October fourth", "the fourth of October", "fourth October", "four October",
        "October the fourth", "October 4th, 2026", "4th of October 2026",
        "4nd October", "4rd October", "Oct. 4th", "4th Oct.", "4 October 14:00",
        "fourth day of October", "fourth of the October", "October 4th 2026",
        "четвёртое октября", "четвертое октября", "четвёртого октября",
        "четвёртый октябрь", "четвёртая октябрю", "четвёртому октябрём",
        "четвертом октябре", "четвертым октября", "четвертой октября",
        "октября четвёртого", "октябрь четыре", "четырёх октября",
        "четыре октября", "четвёртого числа октября", "4-го октября", "4-ого октября",
        "4-е октября", "2026 года четвёртого октября", "October fourth, 2026",
    ],
)
def test_word_orders_declensions_numeric_suffixes_and_mixed_cases(text):
    result = resolve_restaurant_date(text, NOW)
    assert result.value == "2026-10-04" and result.issue is None


@pytest.mark.parametrize(
    "text,expected",
    [
        ("for tomorrow", "2026-10-04"), ("on the day after tomorrow", "2026-10-05"),
        ("на завтра", "2026-10-04"), ("к завтрашнему дню", "2026-10-04"),
        ("завтрашним днём", "2026-10-04"), ("завтрашнего дня", "2026-10-04"),
        ("на послезавтра", "2026-10-05"), ("к послезавтрашнему дню", "2026-10-05"),
        ("на сегодняшний день", "2026-10-03"), ("к сегодняшнему дню", "2026-10-03"),
        ("к воскресенью", "2026-10-04"), ("в воскресенье", "2026-10-04"),
        ("на воскресенья", "2026-10-04"), ("в понедельник", "2026-10-05"),
        ("в двадцать первом октябре", "2026-10-21"),
        ("двадцатьтретье ноября", "2026-11-23"),
        ("twentyfirst November", "2026-11-21"),
        ("twenty one November", "2026-11-21"),
        ("twentieth first November", "2026-11-21"),
        ("двадцатого первого ноября", "2026-11-21"),
        ("двадцатому четвёртому октябрю", "2026-10-24"),
        ("тридцати первому октябрю", "2026-10-31"),
        ("одиннадцать октября", "2026-10-11"),
        ("двенадцати октября", "2026-10-12"),
        ("thirty-first December", "2026-12-31"),
        ("January first", "2027-01-01"),
        ("первого января", "2027-01-01"),
    ],
)
def test_relative_cases_compound_days_and_year_rollover(text, expected):
    result = resolve_restaurant_date(text, NOW)
    assert result.value == expected and result.issue is None


@pytest.mark.parametrize("month", range(1, 13))
@pytest.mark.parametrize("ending", ["ый", "ое", "ого", "ому", "ым", "ом", "ая", "ую", "ой"])
def test_regular_russian_day_cases_with_every_month(month, ending):
    text = f"четвёрт{ending} {RUSSIAN_MONTHS[month - 1]} 2028"
    assert resolve_restaurant_date(text, NOW).value == f"2028-{month:02d}-04"


@pytest.mark.parametrize("day", range(1, 32))
@pytest.mark.parametrize("language", ["en", "ru"])
def test_all_ordinal_days_in_month_first_or_nominative_order(day, language):
    text = f"December the {ENGLISH_DAYS[day - 1]}" if language == "en" else f"{RUSSIAN_DAYS[day - 1]} декабря"
    assert resolve_restaurant_date(text, NOW).value == f"2026-12-{day:02d}"


@pytest.mark.parametrize("text", ["A table on October fourth and four guests at 14:00", "Столик на четвертое октября и четыре гостя в 14:00"])
def test_guest_nouns_after_month_are_not_a_date_range(text):
    assert parse_restaurant_request(text, now=NOW) == {"date": "2026-10-04", "start_time": "14:00", "party_size": 4}


@pytest.mark.parametrize(
    "text,issue",
    [
        ("thirty-first February", "date_invalid"),
        ("thirty-second October", "date_invalid"),
        ("forty fourth October", "date_invalid"),
        ("one hundred and fourth October", "date_invalid"),
        ("zero October", "date_invalid"),
        ("тридцать первое февраля", "date_invalid"),
        ("тридцать второй октябрь", "date_invalid"),
        ("сорок четвертого октября", "date_invalid"),
        ("сто четвертого октября", "date_invalid"),
        ("тридцатого второго октября", "date_invalid"),
        ("ноль октября", "date_invalid"),
        ("fourth or fifth October", "date_ambiguous"),
        ("October fourth or fifth", "date_ambiguous"),
        ("October fourth through fifth", "date_ambiguous"),
        ("the fourth and the fifth of October", "date_ambiguous"),
        ("4th-5th October", "date_ambiguous"),
        ("четвертого или пятого октября", "date_ambiguous"),
        ("октября четвертого или пятого", "date_ambiguous"),
        ("с четвертого до пятого октября", "date_ambiguous"),
        ("not on October fourth", "date_ambiguous"),
        ("не на четвёртое октября", "date_ambiguous"),
        ("for tomorrow or the day after tomorrow", "date_ambiguous"),
        ("на завтра или послезавтра", "date_ambiguous"),
        ("fourth October 26", "date_ambiguous"),
        ("4 октября 26", "date_ambiguous"),
        ("2027 года 4 октября 2026", "date_ambiguous"),
        ("October", "date_incomplete"), ("in May", "date_incomplete"),
        ("в октябре", "date_incomplete"),
        ("on 10/04/2026", "date_ambiguous"),
        ("на 04/10", "date_ambiguous"),
    ],
)
def test_invalid_unclear_and_negated_dates_remove_previous_date(text, issue):
    previous = {"date": "2026-10-06", "start_time": "14:00", "party_size": 4}
    result = parse_restaurant_request(text, previous, now=NOW)
    assert result == {"start_time": "14:00", "party_size": 4, "date_issue": issue}
    assert previous["date"] == "2026-10-06"


@pytest.mark.parametrize("text", ["May I book a table?", "We may need a table", "mayonnaise", "marching", "октябрьский", "четвертовать"])
def test_ordinary_words_are_not_month_requests(text):
    result = resolve_restaurant_date(text, NOW)
    assert result.value is None and result.issue is None


@pytest.mark.parametrize(
    "text",
    [
        "A table for four on October fourth at 2 pm",
        "A table on the fourth of October at 14:00 for four",
        "Столик на четверых четвёртого октября в 14:00",
        "Столик четвёртая октябрю в 14:00 для четырёх гостей",
        "Столик 4 октября в 14:00 с четырьмя гостями",
    ],
)
def test_dates_do_not_become_guest_counts_or_clock_times(text):
    result = parse_restaurant_request(text, now=NOW)
    assert result == {"date": "2026-10-04", "start_time": "14:00", "party_size": 4}


@pytest.mark.parametrize("text", ["Table for the fourth of October", "Столик на четыре октября", "Столик на четвёртого октября"])
def test_date_without_guest_count_still_asks_for_guests(text):
    result = parse_restaurant_request(text, now=NOW)
    assert result == {"date": "2026-10-04"}


@pytest.mark.parametrize("text", ["Are you open on October fourth?", "And the fourth of October?", "Вы открыты четвёртого октября?", "А на четвёртое октября?"])
def test_hours_questions_use_the_same_date_grammar(text):
    from app.restaurant_answers import RestaurantQuestion, match_question

    question = match_question(text, previous=RestaurantQuestion(("hours",)), now=NOW)
    assert question.date == "2026-10-04" and question.days == (6,)
    assert question.date_issue is None
