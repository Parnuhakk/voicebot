"""Russian spoken forms for trusted dates, clocks and reservation details."""

from __future__ import annotations

from datetime import datetime


MONTHS = (
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
)
_ONES = (
    "ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь",
    "восемь", "девять", "десять", "одиннадцать", "двенадцать",
    "тринадцать", "четырнадцать", "пятнадцать", "шестнадцать",
    "семнадцать", "восемнадцать", "девятнадцать",
)
_GENITIVE = (
    "нуля", "одного", "двух", "трёх", "четырёх", "пяти", "шести", "семи",
    "восьми", "девяти", "десяти", "одиннадцати", "двенадцати",
    "тринадцати", "четырнадцати", "пятнадцати", "шестнадцати",
    "семнадцати", "восемнадцати", "девятнадцати",
)
_TENS = (
    "", "", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят",
    "семьдесят", "восемьдесят", "девяносто",
)
_TENS_GENITIVE = (
    "", "", "двадцати", "тридцати", "сорока", "пятидесяти", "шестидесяти",
    "семидесяти", "восьмидесяти", "девяноста",
)
_HUNDREDS = (
    "", "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот",
    "семьсот", "восемьсот", "девятьсот",
)
_ORDINAL = (
    "", "первого", "второго", "третьего", "четвёртого", "пятого",
    "шестого", "седьмого", "восьмого", "девятого", "десятого",
    "одиннадцатого", "двенадцатого", "тринадцатого", "четырнадцатого",
    "пятнадцатого", "шестнадцатого", "семнадцатого", "восемнадцатого",
    "девятнадцатого",
)
_ROUND_ORDINAL = {
    20: "двадцатого", 30: "тридцатого", 40: "сорокового", 50: "пятидесятого",
    60: "шестидесятого", 70: "семидесятого", 80: "восьмидесятого", 90: "девяностого",
    100: "сотого", 200: "двухсотого", 300: "трёхсотого", 400: "четырёхсотого",
    500: "пятисотого", 600: "шестисотого", 700: "семисотого",
    800: "восьмисотого", 900: "девятисотого",
    1000: "тысячного", 2000: "двухтысячного", 3000: "трёхтысячного",
    4000: "четырёхтысячного", 5000: "пятитысячного", 6000: "шеститысячного",
    7000: "семитысячного", 8000: "восьмитысячного", 9000: "девятитысячного",
}


def spoken_number(value: int) -> str:
    if type(value) is not int or not 0 <= value <= 9999:
        raise ValueError("invalid Russian spoken number")
    if value < 20:
        return _ONES[value]
    if value < 100:
        return _TENS[value // 10] + (" " + _ONES[value % 10] if value % 10 else "")
    if value < 1000:
        return _HUNDREDS[value // 100] + (
            " " + spoken_number(value % 100) if value % 100 else ""
        )
    thousands, remainder = divmod(value, 1000)
    prefix = {
        1: "тысяча", 2: "две тысячи", 3: "три тысячи", 4: "четыре тысячи",
    }.get(thousands, _ONES[thousands] + " тысяч")
    return prefix + (" " + spoken_number(remainder) if remainder else "")


def _genitive_number(value: int) -> str:
    if not 0 <= value <= 59:
        raise ValueError("invalid Russian clock number")
    if value < 20:
        return _GENITIVE[value]
    return _TENS_GENITIVE[value // 10] + (" " + _GENITIVE[value % 10] if value % 10 else "")


def _ordinal(value: int) -> str:
    if not 1 <= value <= 9999:
        raise ValueError("invalid Russian ordinal")
    if value < 20:
        return _ORDINAL[value]
    if value in _ROUND_ORDINAL:
        return _ROUND_ORDINAL[value]
    unit = 10 if value < 100 else 100 if value < 1000 else 1000
    prefix, remainder = divmod(value, unit)
    return spoken_number(prefix * unit) + " " + _ordinal(remainder)


def spoken_date(
    value: str, *, accusative: bool = False, include_year: bool = True,
) -> str:
    day = datetime.fromisoformat(value)
    ordinal = _ordinal(day.day)
    if accusative:
        # A visit is "четвёртого октября"; a table is "на четвёртое октября".
        ordinal = (
            ordinal.removesuffix("третьего") + "третье"
            if ordinal.endswith("третьего") else ordinal.removesuffix("ого") + "ое"
        )
    result = ordinal + " " + MONTHS[day.month - 1]
    if include_year:
        result += " " + _ordinal(day.year) + " года"
    return result


def spoken_time(hour: int, minute: int, *, genitive: bool = False) -> str:
    if (
        type(hour) is not int or type(minute) is not int
        or not 0 <= hour <= 23 or not 0 <= minute <= 59
    ):
        raise ValueError("invalid Russian spoken time")
    period = (
        "ночи" if hour < 5 else "утра" if hour < 12
        else "дня" if hour < 17 else "вечера"
    )
    number = _genitive_number if genitive else spoken_number
    clock_hour = hour % 12 or 12
    value = (
        ("часа" if genitive else "час") if clock_hour == 1 else number(clock_hour)
    )
    if minute:
        value += " " + ("ноль " if minute < 10 else "") + number(minute)
    return value + " " + period


def guest_count(value: int) -> str:
    if type(value) is not int or not 1 <= value <= 20:
        raise ValueError("invalid Russian guest count")
    # Accusative animate numerals: "на одного гостя", "на двух гостей",
    # but "на пять гостей". This agrees with the reservation template.
    number = _GENITIVE[value] if value <= 4 else spoken_number(value)
    return number + (" гостя" if value == 1 else " гостей")


def _noun_form(value: int, one: str, few: str, many: str) -> str:
    if 11 <= value % 100 <= 14:
        return many
    return one if value % 10 == 1 else few if value % 10 in {2, 3, 4} else many


def duration(value: int) -> str:
    if type(value) is not int or not 1 <= value <= 9999:
        raise ValueError("invalid Russian reservation duration")
    if value == 60:
        return "час"
    if value == 90:
        return "полтора часа"
    if value % 60 == 0:
        hours = value // 60
        form = _noun_form(hours, "час", "часа", "часов")
        return spoken_number(hours) + " " + form
    form = _noun_form(value, "минуту", "минуты", "минут")
    number = spoken_number(value)
    if form == "минуту":
        number = number.removesuffix("один") + "одну"
    elif value % 10 == 2 and value % 100 != 12:
        number = number.removesuffix("два") + "две"
    return number + " " + form
