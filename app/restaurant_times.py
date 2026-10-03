"""Spoken ET/EN/RU clock selections, without assuming AM/PM or availability."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestedTime:
    value: str | None = None
    candidates: tuple[str, str] | None = None
    invalid: bool = False
    span: tuple[int, int] | None = None


TIME_INPUT_EXAMPLES = {
    "et": ["kell kuus õhtul", "pool seitse õhtul", "kell kaheksateist kolmkümmend"],
    "en": ["at six o'clock in the evening", "half past six in the evening", "at six thirty PM"],
    "ru": ["в шесть вечера", "полседьмого вечера", "в восемнадцать тридцать"],
}


def _number_words() -> dict[str, int]:
    words: dict[str, int] = {}
    units = (
        ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"),
        ("null", "üks", "kaks", "kolm", "neli", "viis", "kuus", "seitse", "kaheksa", "üheksa"),
        ("ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"),
    )
    teens = (
        ("ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"),
        ("kümme", "üksteist", "kaksteist", "kolmteist", "neliteist", "viisteist", "kuusteist", "seitseteist", "kaheksateist", "üheksateist"),
        ("десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать", "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать"),
    )
    tens = (
        ("twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"),
        ("kakskümmend", "kolmkümmend", "nelikümmend", "viiskümmend", "kuuskümmend", "seitsekümmend", "kaheksakümmend", "üheksakümmend"),
        ("двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят", "девяносто"),
    )
    for language, singles in enumerate(units):
        words.update({word: number for number, word in enumerate(singles)})
        words.update({word: number for number, word in enumerate(teens[language], 10)})
        for ten, prefix in enumerate(tens[language], 2):
            words[prefix] = ten * 10
            for digit, suffix in enumerate(singles[1:], 1):
                words[prefix + " " + suffix] = ten * 10 + digit
                if language == 1:
                    words[prefix + suffix] = ten * 10 + digit
    words.update({"oh": 0, "две": 2, "одна": 1})
    for digit, word in enumerate(units[0][1:], 1):
        words["oh " + word] = digit
    russian_units = ("одной", "двух", "трех", "четырех", "пяти", "шести", "семи", "восьми", "девяти")
    words.update({word: value for value, word in enumerate(russian_units, 1)})
    words.update({word: value for value, word in enumerate(("десяти", "одиннадцати", "двенадцати", "тринадцати", "четырнадцати", "пятнадцати", "шестнадцати", "семнадцати", "восемнадцати", "девятнадцати"), 10)})
    for ten, prefix in enumerate(("двадцати", "тридцати", "сорока", "пятидесяти"), 2):
        words[prefix] = ten * 10
        for digit, suffix in enumerate(russian_units, 1):
            words[prefix + " " + suffix] = ten * 10 + digit
    return words


NUMBERS = _number_words()
HOURS = {
    **NUMBERS,
    "час": 1,
    "одного": 1, "двух": 2, "трех": 3, "четырех": 4, "пяти": 5,
    "шести": 6, "семи": 7, "восьми": 8, "девяти": 9,
    "десяти": 10, "одиннадцати": 11, "двенадцати": 12,
    "первого": 1, "второго": 2, "третьего": 3, "четвертого": 4,
    "пятого": 5, "шестого": 6, "седьмого": 7, "восьмого": 8,
    "девятого": 9, "десятого": 10, "одиннадцатого": 11, "двенадцатого": 12,
}


def _pattern(words: dict[str, int]) -> str:
    # Long compound numbers must precede their shorter prefixes.
    return r"(?:\d{1,2}|" + "|".join(re.escape(word) for word in sorted(words, key=len, reverse=True)) + ")"


HOUR = _pattern(HOURS)
MINUTE = _pattern(NUMBERS)
PERIODS = {
    "am": re.compile(r"(?<![a-z])a\.?\s*m\.?(?![a-z])|\b(?:morning|hommik\w*|утр\w*)\b"),
    "pm": re.compile(r"(?<![a-z])p\.?\s*m\.?(?![a-z])|\b(?:afternoon|evening|õhtu\w*|pärastlõuna\w*|päeval|вечер\w*|дня|днем)\b"),
    "night": re.compile(r"\b(?:night|öösel|ööl|ночи|ночью)\b"),
}
SPECIAL = re.compile(r"\b(?P<noon>noon|midday|keskpäev\w*|полдень|полудень)|\b(?P<midnight>midnight|kesköö\w*|полночь|полночи)")
DIGITAL = re.compile(r"(?<![\w:.])(?P<h>\d{1,2})[:.](?P<m>\d{2})(?![\d:.])")
MALFORMED_DIGITAL = re.compile(r"(?<![\w:.])\d{1,3}[:.]\d+(?!\w)")
FRACTIONS = (
    (re.compile(r"\b(?:a\s+)?(?P<m>half|quarter|" + MINUTE + r")\s+(?P<direction>past|to)\s+(?P<h>" + HOUR + r")\b"), "en"),
    (re.compile(r"\bhalf\s+(?P<h>" + HOUR + r")\b"), "en_half"),
    (re.compile(r"\b(?P<m>kolmveerand|veerand|pool)\s+(?P<h>" + HOUR + r")\b"), "et"),
    (re.compile(r"\b(?:пол\s*|половина\s+)(?P<h>" + HOUR + r")\b"), "ru_half"),
    (re.compile(r"\bчетверть\s+(?P<h>" + HOUR + r")\b"), "ru_quarter"),
    (re.compile(r"\bбез\s+(?P<m>четверти|" + MINUTE + r")(?:\s+минут\w*)?\s+(?P<h>" + HOUR + r")\b"), "ru_to"),
)
PREFIX = re.compile(r"\b(?:at|kell|kella|в|к|около)\s+(?P<h>" + HOUR + r")(?:\s+час(?:а|ов)?)?(?:\s+(?:(?:ja|and|и)\s+)?(?P<m>" + MINUTE + r"))?(?:\s+минут\w*)?(?![\w:.])")
SUFFIX = re.compile(r"(?<!\w)(?P<h>" + HOUR + r")(?:\s+(?P<m>" + MINUTE + r"))?\s*(?:o'clock|час(?:а|ов)?|[ap]\.?\s*m\.?)(?!\w)")
BARE = re.compile(r"(?P<h>" + HOUR + r")(?:\s+(?P<m>" + MINUTE + r"))?")
ALTERNATIVE = re.compile(r"\b(?:or|või|или|between|vahemikus|между)\b")


def _number(value: str, *, hour=False) -> int:
    return int(value) if value.isdigit() else (HOURS if hour else NUMBERS)[value]


def _period(text: str) -> str | None:
    values = [period for period, pattern in PERIODS.items() if pattern.search(text)]
    return values[0] if len(values) == 1 else "conflict" if values else None


def _selection(hour: int, minute: int, period: str | None, *, explicit=False, span=None) -> RequestedTime:
    if not 0 <= hour <= 23 or not 0 <= minute <= 59 or period == "conflict":
        return RequestedTime(invalid=True, span=span)
    if period:
        if hour > 12 or (hour == 0 and explicit):
            compatible = hour < 12 if period == "am" else hour >= 12 if period == "pm" else hour < 6 or hour >= 18
            if not compatible:
                return RequestedTime(invalid=True, span=span)
        else:
            hour %= 12
            if period == "pm" or (period == "night" and hour >= 6):
                hour += 12
        return RequestedTime(f"{hour:02d}:{minute:02d}", span=span)
    if explicit or hour > 12:
        return RequestedTime(f"{hour:02d}:{minute:02d}", span=span)
    return RequestedTime(candidates=(f"{hour % 12:02d}:{minute:02d}", f"{hour % 12 + 12:02d}:{minute:02d}"), span=span)


def parse_spoken_time(
    text: str, *, pending: tuple[str, str] | None = None, allow_bare: bool = False,
) -> RequestedTime | None:
    """Return only clock selectors. Bare numbers require an expected time reply."""
    if not isinstance(text, str) or len(text) > 2000:
        return None
    text = " ".join(text.casefold().replace("ё", "е").replace("’", "'").replace("‘", "'").split())
    text = re.sub(r"\bo\s*'?\s*clock\b", "o'clock", text)
    text = re.sub(r"(?<=[a-z])-(?=[a-z])", " ", text)
    # Dates must never become clock times. Spaces preserve overlap positions.
    text = re.sub(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[./]\d{1,2}[./]\d{2,4})\b", lambda match: " " * len(match[0]), text)
    period = _period(text)
    found: list[RequestedTime] = []
    occupied: list[tuple[int, int]] = []

    def add(match, hour, minute=0, explicit=False):
        start, end = match.span()
        if any(start < high and end > low for low, high in occupied):
            return
        occupied.append((start, end))
        found.append(_selection(hour, minute, period, explicit=explicit, span=(start, end)))

    for match in SPECIAL.finditer(text):
        # Noon/midnight name an exact time, even without a period suffix.
        start, end = match.span()
        occupied.append((start, end))
        found.append(RequestedTime("12:00" if match["noon"] else "00:00", span=(start, end)))
    for pattern, kind in FRACTIONS:
        for match in pattern.finditer(text):
            target = _number(match["h"], hour=True)
            if not 1 <= target <= 23:
                add(match, 24)
                continue
            if kind in {"en_half", "ru_half", "ru_quarter"}:
                hour = target if kind == "en_half" else (target - 1) % 12 if target <= 12 else target - 1
                minute = 15 if kind == "ru_quarter" else 30
            elif kind == "et":
                hour = (target - 1) % 12 if target <= 12 else target - 1
                minute = {"pool": 30, "veerand": 15, "kolmveerand": 45}[match["m"]]
            else:
                word = match["m"]
                minute = {"half": 30, "quarter": 15, "четверти": 15}.get(word)
                minute = _number(word) if minute is None else minute
                if not 1 <= minute <= 59:
                    add(match, 24)
                    continue
                before = kind == "ru_to" or match["direction"] == "to"
                hour = (target - 1) % 12 if before and target <= 12 else target - 1 if before else target
                minute = 60 - minute if before else minute
            add(match, hour, minute, explicit=target > 12)
    for match in DIGITAL.finditer(text):
        hour = int(match["h"])
        add(match, hour, int(match["m"]), explicit=hour == 0 or hour > 12 or match["h"].startswith("0"))
    for match in MALFORMED_DIGITAL.finditer(text):
        add(match, 24)
    for pattern in (PREFIX, SUFFIX):
        for match in pattern.finditer(text):
            hour = _number(match["h"], hour=True)
            minute = _number(match["m"]) if match["m"] else 0
            add(match, hour, minute, explicit=hour == 0 or hour > 12)
    if not found and allow_bare:
        bare = text
        for pattern in PERIODS.values():
            bare = pattern.sub(" ", bare)
        bare = re.sub(r"\b(?:in the|in|the|please|palun|пожалуйста)\b", " ", bare)
        bare = " ".join(bare.strip(" .,!?").split())
        match = BARE.fullmatch(bare)
        if match:
            hour = _number(match["h"], hour=True)
            found.append(_selection(hour, _number(match["m"]) if match["m"] else 0, period, explicit=hour == 0 or hour > 12))
    if not found and pending and period:
        hour, minute = map(int, pending[0].split(":"))
        return _selection(hour, minute, period)
    if not found:
        return None
    # Two different offered times are a choice, never authority to pick one.
    if len({(selection.value, selection.candidates, selection.invalid) for selection in found}) > 1 or ALTERNATIVE.search(text):
        return RequestedTime(invalid=True)
    return found[0]
