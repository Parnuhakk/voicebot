"""Spoken ET/EN/RU clock selections, without assuming AM/PM or availability."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .restaurant_dates import ESTONIAN_COUNTS


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
NUMBERS.update(ESTONIAN_COUNTS)
MINUTES = {
    **NUMBERS,
    **{f"null {word}": digit for digit, word in enumerate(("üks", "kaks", "kolm", "neli", "viis", "kuus", "seitse", "kaheksa", "üheksa"), 1)},
}
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
for hour, stem in enumerate((
    "nulli", "ühe", "kahe", "kolme", "nelja", "viie", "kuue", "seitsme", "kaheksa", "üheksa", "kümne",
    "üheteistkümne", "kaheteistkümne", "kolmeteistkümne", "neljateistkümne", "viieteistkümne",
    "kuueteistkümne", "seitsmeteistkümne", "kaheksateistkümne", "üheksateistkümne", "kahekümne",
    "kahekümne ühe", "kahekümne kahe", "kahekümne kolme",
)):
    HOURS.update({stem + ending: hour for ending in ("", "ks", "le", "l")})


def _pattern(words: dict[str, int]) -> str:
    # Long compound numbers must precede their shorter prefixes.
    return r"(?:-?\d{1,3}|" + "|".join(re.escape(word) for word in sorted(words, key=len, reverse=True)) + ")"


HOUR = _pattern(HOURS)
MINUTE = _pattern(MINUTES)
GUEST_NOUN = r"(?:people|persons|guests|adults?|children|kids?|inimes\w*|külalis\w*|täiskasvan\w*|last|lapse\w*|человек\w*|гост\w*|взросл\w*|дет\w*|ребен\w*)"
MINUTE_NOT_GUEST = r"(?!\s+" + GUEST_NOUN + r"\b)"
APPROXIMATE_COUNT = re.compile(r"\b(?:around|about|approximately|between|umbes|около|примерно|между)\s+" + HOUR + r"(?:\s+(?:and|to|ja|kuni|и|до)\s+" + HOUR + r")?\s+" + GUEST_NOUN + r"\b")
PERIODS = {
    "am": re.compile(r"(?<![a-z])a\.?\s*m\.?(?![a-z])|\b(?:morning|hommik\w*|утр\w*)\b"),
    "pm": re.compile(r"(?<![a-z])p\.?\s*m\.?(?![a-z])|\b(?:afternoon|evening|õhtu\w*|pärastlõuna\w*|päeval|вечер\w*|дня|днем)\b"),
    "night": re.compile(r"\b(?:night|öösel|ööl|ночи|ночью)\b"),
}
SPECIAL = re.compile(r"\b(?P<noon>noon|midday|keskpäev\w*|полдень|полудень)|\b(?P<midnight>midnight|kesköö\w*|полночь|полночи)")
NAMED_CLOCK = r"(?:noon|midday|midnight|keskpäev\w*|kesköö\w*|полдень|полудень|полночь|полночи)"
NAMED_FRACTIONS = (
    (re.compile(r"\b(?:a\s+)?(?P<m>half|quarter|" + MINUTE + r")(?:\s+minutes?)?\s+(?P<direction>past|after|to|before)\s+(?P<h>" + NAMED_CLOCK + r")\b"), "en"),
    (re.compile(r"\b(?P<m>" + MINUTE + r")\s+minut\w*\s+(?P<direction>enne|üle)\s+(?P<h>" + NAMED_CLOCK + r")\b"), "et"),
    (re.compile(r"\bбез\s+(?P<m>четверти|" + MINUTE + r")(?:\s+минут\w*)?\s+(?P<h>" + NAMED_CLOCK + r")\b"), "ru"),
)
DIGITAL = re.compile(r"(?<![\w:.])(?P<h>\d{1,2})[:.](?P<m>\d{2})(?![\d:]|\.\d)")
MALFORMED_DIGITAL = re.compile(r"(?<![\w:.])\d{1,3}[:.]\d+(?!\w)")
FRACTIONS = (
    (re.compile(r"\b(?P<h>" + HOUR + r")\s+(?:and\s+(?:a\s+)?half|ja\s+pool|с\s+половиной)\b"), "after_half"),
    (re.compile(r"\b(?:a\s+)?(?P<m>half|quarter|" + MINUTE + r")(?:\s+minutes?)?\s+(?P<direction>past|to|after|before)\s+(?P<h>" + HOUR + r")\b"), "en"),
    (re.compile(r"\b(?P<h>" + HOUR + r")\s+läbi\s+(?P<m>" + MINUTE + r")(?:\s+minut\w*)?\b"), "et_past"),
    (re.compile(r"\b(?P<m>" + MINUTE + r")\s+minut\w*\s+(?P<direction>enne|üle)\s+(?P<h>" + HOUR + r")\b"), "et_minutes"),
    (re.compile(r"\bhalf\s+(?P<h>" + HOUR + r")\b"), "en_half"),
    (re.compile(r"\b(?P<m>kolmveerand|veerand|pool)\s+(?P<h>" + HOUR + r")\b"), "et"),
    (re.compile(r"\b(?:пол\s*|половин[аеуы]\s+)(?P<h>" + HOUR + r")\b"), "ru_half"),
    (re.compile(r"\bчетверть\s+(?P<h>" + HOUR + r")\b"), "ru_quarter"),
    (re.compile(r"\bбез\s+(?P<m>четверти|" + MINUTE + r")(?:\s+минут\w*)?\s+(?P<h>" + HOUR + r")\b"), "ru_to"),
)
PREFIX = re.compile(r"\b(?:at|kell|kella|в|к|около)\s+(?P<h>" + HOUR + r")(?:\s+(?:час(?:а|ов)?|hours?))?(?:\s+(?:(?:ja|and|и)\s+)?(?P<m>" + MINUTE + r")\b" + MINUTE_NOT_GUEST + r")?(?:\s+(?:минут\w*|minutes?|minut\w*))?(?:\s+ajal)?(?![\w:.])")
SUFFIX = re.compile(r"(?<!\w)(?P<h>" + HOUR + r")(?:\s+(?P<m>" + MINUTE + r"))?\s*(?:o'clock|час(?:а|ов)?|[ap]\.?\s*m\.?|ajal)(?!\w)")
BARE = re.compile(r"(?P<h>" + HOUR + r")(?:\s+(?P<m>" + MINUTE + r"))?")
CLOCK_TAIL = re.compile(r"^\s+(?:(?:ja|and|и)\s+)?(?P<n>-?\d+|" + MINUTE + r"|half|quarter|pool|poolteist|veerand|kolmveerand|läbi|с\s+половиной|четверт[ьи]|половин\w*)\b")
ALTERNATIVE = re.compile(r"\b(?:or|või|или|kuni|до|to)\s+" + HOUR + r"\b")
TIME_RANGE = re.compile(r"\b(?:between|vahemikus|между)\s+" + HOUR + r"\b|\b(?:с|from)\s+" + HOUR + r"\s+(?:до|to)\s+" + HOUR + r"\b")
APPROXIMATE_TIME = re.compile(r"\b(?:around|about|approximately|около|примерно|umbes)\s+(?:(?:at|kell|kella|в)\s+)?" + HOUR + r"\b|\b" + HOUR + r"\s+paiku\b")
MERIDIEM = re.compile(r"(?<![a-z])[ap]\.?\s*m\.?(?![a-z])")
NEGATED_TIME = re.compile(r"\b(?:not|mitte|ei|ära|не)(?:\s+\w+){0,2}\s*$")


def _number(value: str, *, hour=False) -> int:
    return int(value) if value.lstrip("-").isdigit() else (HOURS if hour else MINUTES)[value]


def _period(text: str) -> str | None:
    values = [period for period, pattern in PERIODS.items() if pattern.search(text)]
    return values[0] if len(values) == 1 else "conflict" if values else None


def _selection(hour: int, minute: int, period: str | None, *, explicit=False, meridiem=False, span=None) -> RequestedTime:
    if not 0 <= hour <= 23 or not 0 <= minute <= 59 or period == "conflict":
        return RequestedTime(invalid=True, span=span)
    if meridiem and (hour > 12 or hour == 0 and explicit):
        return RequestedTime(invalid=True, span=span)
    if period:
        if hour > 12 or (hour in {0, 12} and explicit):
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
    text = " ".join(unicodedata.normalize("NFC", text.casefold()).replace("ё", "е").replace("’", "'").replace("‘", "'").split())
    text = re.sub(r"\bo\s*'?\s*clock\b", "o'clock", text)
    text = re.sub(r"(?<=[a-z])-(?=[a-z])", " ", text)
    # Dates must never become clock times. Spaces preserve overlap positions.
    text = re.sub(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[./]\d{1,2}[./]\d{2,4})\b", lambda match: " " * len(match[0]), text)
    text = APPROXIMATE_COUNT.sub(lambda match: " " * len(match[0]), text)
    period = _period(text)
    meridiem = bool(MERIDIEM.search(text))
    found: list[RequestedTime] = []
    occupied: list[tuple[int, int]] = []

    def add(match, hour, minute=0, explicit=False):
        start, end = match.span()
        if any(start < high and end > low for low, high in occupied):
            return
        occupied.append((start, end))
        found.append(_selection(hour, minute, period, explicit=explicit, meridiem=meridiem, span=(start, end)))

    approximate = APPROXIMATE_TIME.search(text)
    if approximate:
        return RequestedTime(invalid=True, span=approximate.span())

    for pattern, kind in NAMED_FRACTIONS:
        for match in pattern.finditer(text):
            target = 12 if re.fullmatch(r"noon|midday|keskpäev\w*|полдень|полудень", match["h"]) else 0
            word = match["m"]
            minute = {"half": 30, "quarter": 15, "четверти": 15}.get(word)
            minute = _number(word) if minute is None else minute
            before = kind == "ru" or match["direction"] in {"to", "before", "enne"}
            total = (target * 60 + (-minute if before else minute)) % (24 * 60)
            hour, minute_of_hour = divmod(total, 60)
            compatible = period is None or period == "am" and hour < 12 or period == "pm" and hour >= 12 or period == "night" and (hour < 6 or hour >= 18)
            occupied.append(match.span())
            found.append(RequestedTime(f"{hour:02d}:{minute_of_hour:02d}", span=match.span()) if 1 <= minute <= 59 and compatible else RequestedTime(invalid=True, span=match.span()))
    for match in SPECIAL.finditer(text):
        # Noon/midnight name an exact time, even without a period suffix.
        start, end = match.span()
        if any(start < high and end > low for low, high in occupied):
            continue
        occupied.append((start, end))
        found.append(_selection(12 if match["noon"] else 0, 0, period, explicit=True, span=(start, end)))
    for pattern, kind in FRACTIONS:
        for match in pattern.finditer(text):
            target = _number(match["h"], hour=True)
            if not 1 <= target <= 23 or meridiem and target > 12:
                add(match, 24)
                continue
            if kind in {"en_half", "after_half", "ru_half", "ru_quarter"}:
                hour = target if kind in {"en_half", "after_half"} else (target - 1) % 12 if target <= 12 else target - 1
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
                before = kind == "ru_to" or kind in {"en", "et_minutes"} and match["direction"] in {"to", "before", "enne"}
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
    bare = None
    if not found and allow_bare:
        bare = text
        for pattern in PERIODS.values():
            bare = pattern.sub(" ", bare)
        bare = re.sub(r"\b(?:in the|in|the|please|palun|пожалуйста)\b", " ", bare)
        bare = " ".join(bare.strip(" .,!?").split())
        match = BARE.fullmatch(bare)
        if match:
            hour = _number(match["h"], hour=True)
            found.append(_selection(hour, _number(match["m"]) if match["m"] else 0, period, explicit=hour == 0 or hour > 12, meridiem=meridiem))
    if not found and pending and period:
        if any(
            NEGATED_TIME.search(text[:match.start()])
            for pattern in PERIODS.values() for match in pattern.finditer(text)
        ):
            return RequestedTime(candidates=pending, invalid=True)
        hour, minute = map(int, pending[0].split(":"))
        return _selection(hour, minute, period, meridiem=meridiem)
    if not found and period and bare == "":
        return RequestedTime(invalid=True)
    if not found:
        return RequestedTime(invalid=True) if TIME_RANGE.search(text) else None
    # An adjacent unconsumed clock fragment is not permission to use its prefix.
    # Explicit guest nouns and Estonian party case forms are separate selectors.
    for start, end in occupied:
        tail = CLOCK_TAIL.match(text[end:])
        if tail and tail["n"] not in {"ühele", "kahele", "kolmele", "neljale", "viiele", "kuuele", "seitsmele", "kaheksale"} and not re.match(
            r"\s+" + GUEST_NOUN + r"\b", text[end + tail.end():],
        ):
            return RequestedTime(invalid=True, span=(start, end + tail.end()))
    if any(NEGATED_TIME.search(text[:start]) for start, _ in occupied):
        return RequestedTime(invalid=True)
    # A date/guest alternative elsewhere in the request is not a clock choice.
    alternative_time = bool(TIME_RANGE.search(text))
    for alternative in ALTERNATIVE.finditer(text):
        for _, end in occupied:
            if alternative.start() < end:
                continue
            gap = text[end:alternative.start()]
            for pattern in PERIODS.values():
                gap = pattern.sub(" ", gap)
            gap = re.sub(r"\b(?:in the|in|the)\b", " ", gap)
            alternative_time |= not gap.strip(" ,.!?")
    # Two different offered times are a choice, never authority to pick one.
    if len({(selection.value, selection.candidates, selection.invalid) for selection in found}) > 1 or alternative_time:
        return RequestedTime(invalid=True)
    return found[0]
