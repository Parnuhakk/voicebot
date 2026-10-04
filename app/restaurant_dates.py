"""Bounded date vocabulary for restaurant requests, never booking consent.

Estonian/Russian case endings, English date orders and clear spelling errors
are tolerated in calendar context. Stored caller text and consent stay unchanged.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from .restaurant_date_vocabulary import (
    ENGLISH_CARDINALS,
    ENGLISH_DAY_FORMS,
    ENGLISH_MONTH_FORMS,
    RUSSIAN_DAY_FORMS,
    RUSSIAN_MONTH_FORMS,
    RUSSIAN_COUNTS,
)
from .restaurant_date_spelling import CalendarSpelling
from .restaurant_date_years import THOUSAND as THOUSAND_YEAR, SpokenYears


CASE_ENDINGS = ("", "l", "le", "ks", "st", "ga", "ni", "s", "sse", "ta", "lt", "t", "na")
CARDINAL_BASES = (
    ("üks", "ühe", "üht", "ühte"),
    ("kaks", "kahe", "kaht", "kahte"),
    ("kolm", "kolme"),
    ("neli", "nelja"),
    ("viis", "viie", "viit"),
    ("kuus", "kuue", "kuut"),
    ("seitse", "seitsme", "seitset"),
    ("kaheksa",),
    ("üheksa",),
    ("kümme", "kümne", "kümmet"),
)
ORDINAL_BASES = (
    ("esimene", "esimese", "esimest"),
    ("teine", "teise", "teist"),
    ("kolmas", "kolmanda"),
    ("neljas", "neljanda"),
    ("viies", "viienda"),
    ("kuues", "kuuenda"),
    ("seitsmes", "seitsmenda"),
    ("kaheksas", "kaheksanda"),
    ("üheksas", "üheksanda"),
    ("kümnes", "kümnenda"),
)


def _forms(bases: tuple[str, ...]) -> set[str]:
    return {base + ending for base in bases for ending in CASE_ENDINGS}


ESTONIAN_COUNTS = {
    form: number
    for number, bases in enumerate(CARDINAL_BASES, 1)
    for form in _forms(bases)
}
DAY_FORMS = dict(ESTONIAN_COUNTS)
DAY_FORMS["null"] = 0
for number, bases in enumerate(ORDINAL_BASES, 1):
    DAY_FORMS.update(dict.fromkeys(_forms(bases), number))
for number, (cardinal, stem) in enumerate(
    zip(
        (
            "üksteist",
            "kaksteist",
            "kolmteist",
            "neliteist",
            "viisteist",
            "kuusteist",
            "seitseteist",
            "kaheksateist",
            "üheksateist",
        ),
        (
            "üheteist",
            "kaheteist",
            "kolmeteist",
            "neljateist",
            "viieteist",
            "kuueteist",
            "seitsmeteist",
            "kaheksateist",
            "üheksateist",
        ),
    ),
    11,
):
    DAY_FORMS.update(
        dict.fromkeys(
            _forms((cardinal, stem + "kümne", stem + "kümnes", stem + "kümnenda")),
            number,
        )
    )
for tens, cardinal, stem in ((20, "kakskümmend", "kahe"), (30, "kolmkümmend", "kolme")):
    DAY_FORMS.update(
        dict.fromkeys(
            _forms((cardinal, stem + "kümne", stem + "kümnes", stem + "kümnenda")), tens
        )
    )
    # Also recognize 32..39 so an impossible day cannot fall back to day 2..9.
    for form, units in list(DAY_FORMS.items()):
        if 1 <= units <= 9:
            for prefix in (cardinal, stem + "kümne"):
                for separator in (" ", "", "-"):
                    DAY_FORMS[prefix + separator + form] = tens + units

MONTH_BASES = (
    ("jaanuar", "jaanuari"),
    ("veebruar", "veebruari"),
    ("märts", "märtsi"),
    ("aprill", "aprilli"),
    ("mai",),
    ("juuni",),
    ("juuli",),
    ("august", "augusti"),
    ("september", "septembri"),
    ("oktoober", "oktoobri"),
    ("november", "novembri"),
    ("detsember", "detsembri"),
)
MONTH_FORMS = {
    base + ending: number
    for number, bases in enumerate(MONTH_BASES, 1)
    for base in bases
    for ending in CASE_ENDINGS + ("il", "ile", "iks", "ist", "iga", "ini")
}
DAY_FORMS.update(ENGLISH_DAY_FORMS)
DAY_FORMS.update(RUSSIAN_DAY_FORMS)
MONTH_FORMS.update(ENGLISH_MONTH_FORMS)
MONTH_FORMS.update(RUSSIAN_MONTH_FORMS)


def _alternatives(forms: dict[str, int]) -> str:
    return "|".join(
        re.escape(form)
        for form in sorted(forms, key=lambda value: (-len(value), value))
    )


DAY_PATTERN = r"(?:\d{1,2}(?:st|nd|rd|th|-(?:го|е|й|ое|ого|ому|ом))?\.?|" + _alternatives(DAY_FORMS) + ")"
MONTH_PATTERN = "(?:" + _alternatives(MONTH_FORMS) + ")"
NAMED_DATES = (
    re.compile(
        r"(?<!\w)(?P<day>"
        + DAY_PATTERN
        + r")(?:\s+(?:of(?:\s+the)?|day\s+of|числа))?\s*(?P<month>"
        + MONTH_PATTERN
        + r")\.?(?!\w)"
    ),
    re.compile(
        r"(?<!\w)(?P<month>"
        + MONTH_PATTERN
        + r")\.?\s+(?:the\s+)?(?P<day>"
        + DAY_PATTERN
        + r")(?!\w)"
    ),
)
MONTHS = re.compile(r"\b" + MONTH_PATTERN + r"\b")
ALTERNATIVE_DAY = re.compile(
    r"(?<!\w)" + DAY_PATTERN + r"\s*(?:või|ja|kuni|or|and|through|to|или|и|до|по|[-–])\s*(?:the\s+)?$"
)
TRAILING_ALTERNATIVE_DAY = re.compile(
    r"^\s*(?:või|ja|kuni|or|and|through|to|или|и|до|по|[-–])\s*(?:the\s+)?" + DAY_PATTERN + r"(?!\w)"
)
ISO_DATE = re.compile(r"\b(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\b")
YEAR_FIRST_DATE = re.compile(r"\b(?P<year>\d{4})(?P<sep>[./-])(?P<month>\d{1,2})(?P=sep)(?P<day>\d{1,2})\b")
LOCAL_DATE = re.compile(r"\b(?P<day>\d{1,2})\.(?P<month>\d{1,2})\.(?P<year>\d{4})\b")
AMBIGUOUS_NUMERIC_DATE = re.compile(r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b")
GUEST_NOUN = re.compile(
    r"\s+(?:inimes|külalis|külalist|täiskasvan|last|lapse|people|guests|adults|children|человек|гост|взросл|дет|реб[её]н)\w*\b"
)

TOMORROW_FORMS = {"homme", "hommele", "hommeks"} | {
    "homs" + ending
    for ending in ("e", "eks", "ele", "el", "est", "et", "esse", "eni", "ega")
}
RELATIVE_FORMS = {
    **dict.fromkeys(TOMORROW_FORMS, 1),
    **dict.fromkeys({"üle" + form for form in TOMORROW_FORMS}, 2),
    **dict.fromkeys(
        {"täna", "tänaks", "tänale"}
        | {
            "tänas" + ending
            for ending in ("e", "eks", "ele", "el", "est", "et", "esse", "eni", "ega")
        },
        0,
    ),
    "tomorrow": 1,
    "day after tomorrow": 2,
    "today": 0,
    "yesterday": -1,
    "day before yesterday": -2,
    "eile": -1,
    "eilseks": -1,
    "eilsele": -1,
    "eilsel": -1,
    "üleeile": -2,
    "tonight": 0,
    "завтра": 1,
    "послезавтра": 2,
    "сегодня": 0,
    "вчера": -1,
    "позавчера": -2,
    "завтрашний день": 1,
    "завтрашнего дня": 1,
    "завтрашнему дню": 1,
    "завтрашним днём": 1,
    "завтрашним днем": 1,
    "завтрашнем дне": 1,
    "сегодняшний день": 0,
    "сегодняшнего дня": 0,
    "сегодняшнему дню": 0,
    "сегодняшнем дне": 0,
    "послезавтрашний день": 2,
    "послезавтрашнего дня": 2,
    "послезавтрашнему дню": 2,
}
RELATIVE = re.compile(r"\b(?:" + _alternatives(RELATIVE_FORMS) + r")\b")
WEEKDAYS = {
    "monday": 0,
    "esmaspäev": 0,
    "понедельник": 0,
    "tuesday": 1,
    "teisipäev": 1,
    "вторник": 1,
    "wednesday": 2,
    "kolmapäev": 2,
    "сред": 2,
    "thursday": 3,
    "neljapäev": 3,
    "четверг": 3,
    "friday": 4,
    "reede": 4,
    "пятниц": 4,
    "saturday": 5,
    "laupäev": 5,
    "суббот": 5,
    "sunday": 6,
    "pühapäev": 6,
    "воскресенье": 6,
    "воскресенья": 6,
    "воскресенью": 6,
    "воскресеньем": 6,
    "воскресеньи": 6,
}
WEEKDAY = re.compile(r"\b(?P<base>" + _alternatives(WEEKDAYS) + r")\w*\b")

# A calendar week starts on Monday. Short "next Friday" keeps the existing
# next-occurrence meaning; "next week on Friday" names a particular week.
WEEK_QUALIFIERS = tuple(
    (re.compile(r"\b(?:" + pattern + r")\b"), offset)
    for pattern, offset in (
        (r"ülejärgmis\w*\s+nädal\w*|(?:the\s+)?week\s+after\s+next|через\s+(?:две|2)\s+недели", 2),
        (r"järgmis\w*\s+nädal\w*|next\s+week|следующ\w*\s+недел\w*|через\s+(?:одну\s+)?неделю", 1),
        (r"selle\s+nädal\w*|sel\s+nädal\w*|this\s+week(?:'s)?|эт\w*\s+недел\w*", 0),
        (r"this(?:\s+coming)?|sel|sellel|selle|эт(?:от|у|о|ой)", 0),
    )
)
WEEK_GAP = re.compile(r"[\s,]*(?:(?:on|the|in|at|в|на|этой)\s+)*$")
OFFSET_COUNTS = {"a": 1, "an": 1, "одну": 1, **RUSSIAN_COUNTS}
OFFSET_COUNTS.update({word: number for number, word in enumerate(ENGLISH_CARDINALS, 1)})
for number, word in enumerate((
    "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять", "десять",
    "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать", "шестнадцать",
    "семнадцать", "восемнадцать", "девятнадцать",
), 1):
    OFFSET_COUNTS[word] = number
for number, bases in enumerate(CARDINAL_BASES, 1):
    OFFSET_COUNTS.update(dict.fromkeys(bases, number))
for number, word in enumerate((
    "üksteist", "kaksteist", "kolmteist", "neliteist", "viisteist", "kuusteist", "seitseteist", "kaheksateist", "üheksateist",
), 11):
    OFFSET_COUNTS[word] = number
# Relative quantities need cardinal words, not the thousands of calendar-day
# declensions. Keeping this vocabulary separate also bounds regex startup cost.
for tens, prefixes, units in (
    (20, ("twenty",), tuple((word,) for word in ENGLISH_CARDINALS[:9])),
    (30, ("thirty",), tuple((word,) for word in ENGLISH_CARDINALS[:9])),
    (20, ("kakskümmend", "kahekümne"), CARDINAL_BASES[:9]),
    (30, ("kolmkümmend", "kolmekümne"), CARDINAL_BASES[:9]),
    (20, ("двадцать", "двадцати"), tuple((word,) for word in ("один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"))),
    (30, ("тридцать", "тридцати"), tuple((word,) for word in ("один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"))),
):
    for prefix in prefixes:
        OFFSET_COUNTS[prefix] = tens
        for digit, variants in enumerate(units, 1):
            for word in variants:
                OFFSET_COUNTS[prefix + " " + word] = tens + digit
OFFSET_NUMBER = r"(?:-?\d{1,4}|" + _alternatives(OFFSET_COUNTS) + ")"
OFFSETS = (
    re.compile(r"(?<![\w-])(?P<n>" + OFFSET_NUMBER + r")\s+(?P<unit>päeva|päev|nädala|nädalat|nädal)\s+pärast\b"),
    re.compile(r"\b(?P<unit>nädala)\s+pärast\b"),
    re.compile(r"\bin\s+(?P<n>" + OFFSET_NUMBER + r")\s+(?P<unit>days?|weeks?)\b"),
    re.compile(r"(?<![\w-])(?P<n>" + OFFSET_NUMBER + r")\s+(?P<unit>days?|weeks?)\s+from\s+(?:now|today)\b"),
    re.compile(r"\bчерез\s+(?P<n>" + OFFSET_NUMBER + r")\s+(?P<unit>день|дня|дней|неделю|недели|недель)\b"),
    re.compile(r"\bчерез\s+(?P<unit>неделю)\b"),
)
INCOMPLETE_PERIOD = re.compile(
    r"\b(?:järgmis\w*\s+kuu\w*|(?:this|next)\s+month|следующ\w*\s+месяц\w*|"
    r"in\s+" + OFFSET_NUMBER + r"\s+months?|" + OFFSET_NUMBER + r"\s+kuu\s+pärast|"
    r"через\s+(?:" + OFFSET_NUMBER + r"\s+)?месяц\w*)\b"
)
CALENDAR_SPELLING = CalendarSpelling(
    MONTH_FORMS, DAY_FORMS, RELATIVE_FORMS, WEEKDAYS,
    protected=(RELATIVE, WEEKDAY, INCOMPLETE_PERIOD, *OFFSETS, *(pattern for pattern, _ in WEEK_QUALIFIERS)),
)
SPOKEN_YEARS = SpokenYears(DAY_FORMS)


@dataclass(frozen=True)
class DateResolution:
    value: str | None
    issue: str | None
    remaining_text: str
    day: int | None = None
    month: int | None = None
    year: int | None = None


def resolve_restaurant_date(
    text: str, now: datetime, *, include_weekdays: bool = True,
    allow_bare_day: bool = False, pending_day: int | None = None,
    pending_month: int | None = None, pending_year: int | None = None,
) -> DateResolution:
    """Resolve one date, masking its words before time and party extraction.

    A missing year means the next occurrence of that calendar date. Explicit
    years are kept. The restaurant's existing advance window is enforced later.
    Conflicting, negated or impossible dates ask for clarification instead.
    """
    text = " ".join(unicodedata.normalize("NFC", text.casefold()).split())
    spelling = CALENDAR_SPELLING.normalize(text, date_reply=allow_bare_day)
    text = spelling.text
    spans: list[tuple[int, int]] = list(spelling.ambiguous_spans)
    values: set[str] = set()
    issue: str | None = None
    partial_day, partial_month, partial_year = None, None, None

    def record(
        start: int, end: int, value: date | None, error: str | None = None
    ) -> None:
        nonlocal issue
        if any(start < right and end > left for left, right in spans):
            return
        spans.append((start, end))
        # A declined date is not a booking request, even if only one was heard.
        if re.search(r"\b(?:mitte|ei|ära|not|не)(?:\s+\w+){0,2}\s*$", text[:start]):
            error = "date_ambiguous"
        if error:
            issue = error
        elif value:
            values.add(value.isoformat())

    def calendar(
        day: int, month: int, year: int | None
    ) -> tuple[date | None, str | None]:
        years = (year,) if year is not None else range(now.year, min(now.year + 9, 10000))
        for calendar_year in years:
            try:
                candidate = date(calendar_year, month, day)
            except ValueError:
                continue
            if year is not None or candidate >= now.date():
                return candidate, None
        return None, "date_invalid"

    for pattern in (ISO_DATE, LOCAL_DATE, YEAR_FIRST_DATE):
        for match in pattern.finditer(text):
            value, error = calendar(
                int(match["day"]), int(match["month"]), int(match["year"])
            )
            record(*match.span(), value, error)
    for match in AMBIGUOUS_NUMERIC_DATE.finditer(text):
        numbers = re.split(r"[/-]", match[0])
        year = int(numbers[2]) if len(numbers) == 3 and len(numbers[2]) == 4 else None
        if len(numbers) == 3 and year is None:
            record(*match.span(), None, "date_ambiguous")
            continue
        alternatives = {
            candidate for day, month in ((int(numbers[0]), int(numbers[1])), (int(numbers[1]), int(numbers[0])))
            if (candidate := calendar(day, month, year)[0]) is not None
        }
        record(*match.span(), next(iter(alternatives)) if len(alternatives) == 1 else None,
               "date_ambiguous" if len(alternatives) > 1 else "date_invalid" if not alternatives else None)
    for pattern in NAMED_DATES:
        for match in pattern.finditer(text):
            # In "October two thousand twenty-seven", "two" starts a year,
            # not the second day of October. Leave this for the partial-month
            # parser. "October twenty-first" still names a calendar day.
            if match.start("month") < match.start("day"):
                fragment = text[match.end("month"):]
                spoken_year = SPOKEN_YEARS.after(fragment)
                if spoken_year and (spoken_year.value is not None or THOUSAND_YEAR.match(fragment.lstrip(" ,"))):
                    continue
            raw_day = match["day"].rstrip(".")
            numeric_day = re.fullmatch(r"(\d{1,2})(?:st|nd|rd|th|-(?:го|е|й|ое|ого|ому|ом))?", raw_day)
            day = int(numeric_day[1]) if numeric_day else DAY_FORMS[raw_day]
            end = match.end()
            if text[end:end + 1] == ".":
                end += 1
            start = match.start()
            year = None
            error = None
            # Do not consume a neighbouring guest count as a year.
            year_match = re.match(r"(?:\s*,\s*|\s+)(\d{2,4})(?![\w:.])", text[end:])
            if year_match and not GUEST_NOUN.match(text[end + year_match.end() :]):
                end += year_match.end()
                if len(year_match[1]) != 4:
                    error = "date_ambiguous"
                else:
                    year = int(year_match[1])
            elif (spoken_year := SPOKEN_YEARS.after(text[end:])) is not None:
                end += spoken_year.end
                year, error = spoken_year.value, spoken_year.issue
            preceding_year = re.search(r"\b(\d{4})\.?\s+(?:aasta(?:l)?|года?|году|year)\s*[,.:]?\s*$", text[:start])
            if preceding_year:
                start = preceding_year.start()
                if year is not None and year != int(preceding_year[1]):
                    error = "date_ambiguous"
                else:
                    year = int(preceding_year[1])
            elif (spoken_before := SPOKEN_YEARS.before(text[:start])) is not None:
                start, spoken_year = spoken_before
                if spoken_year.issue or (year is not None and year != spoken_year.value):
                    error = "date_ambiguous"
                else:
                    year = spoken_year.value
            # Unsupported larger compound numbers must not become their units.
            if re.search(
                r"\b(?:\w*(?:kümmend|kümne|sada|saja)|hundred|thousand|сто|ста|тысяч\w*|\d+)(?:[ -]+(?:and|и))?[ -]+$", text[: match.start()]
            ):
                error = "date_invalid"
            trailing_alternative = TRAILING_ALTERNATIVE_DAY.match(text[end:])
            if ALTERNATIVE_DAY.search(text[: match.start()]) or (
                trailing_alternative and not GUEST_NOUN.match(text[end + trailing_alternative.end():])
            ):
                error = "date_ambiguous"
            value, invalid = calendar(day, MONTH_FORMS[match["month"]], year)
            record(start, end, value, error or invalid)
    qualifiers: list[tuple[re.Match[str], int, bool]] = []
    for pattern, weeks in WEEK_QUALIFIERS:
        for match in pattern.finditer(text):
            if not any(match.start() < previous.end() and match.end() > previous.start() for previous, _, _ in qualifiers):
                qualifiers.append((match, weeks, False))
    for match in WEEKDAY.finditer(text):
        qualified = None
        for index, (qualifier, weeks, used) in enumerate(qualifiers):
            if qualifier.end() <= match.start() and WEEK_GAP.fullmatch(text[qualifier.end():match.start()]):
                qualified = (index, weeks)
            elif qualifier.start() >= match.end() and WEEK_GAP.fullmatch(text[match.end():qualifier.start()]):
                qualified = (index, weeks)
        if qualified is not None:
            index, weeks = qualified
            qualifier, _, _ = qualifiers[index]
            qualifiers[index] = (qualifier, weeks, True)
            monday = now.date() - timedelta(days=now.weekday())
            declined = re.search(r"\b(?:mitte|ei|ära|not|не)(?:\s+\w+){0,2}\s*$", text[:qualifier.start()])
            record(*match.span(), monday + timedelta(days=weeks * 7 + WEEKDAYS[match["base"]]), "date_ambiguous" if declined else None)
        elif include_weekdays:
            offset = (WEEKDAYS[match["base"]] - now.weekday()) % 7 or 7
            record(*match.span(), now.date() + timedelta(days=offset))
    for qualifier, _, used in qualifiers:
        if used:
            spans.append(qualifier.span())
        elif re.search(r"week|nädal|недел", qualifier[0]) and not re.search(r"\bчерез\b", qualifier[0]):
            record(*qualifier.span(), None, "date_incomplete")
    for pattern in OFFSETS:
        for match in pattern.finditer(text):
            raw = match.groupdict().get("n")
            if raw is None and match["unit"] == "nädala" and re.search(
                r"\b(?:\d+|pool|poole|paar|paari|mõne|mitme|\w*(?:kümmend|kümne|sada|saja|tuhat|tuhande\w*))\s+$",
                text[:match.start()],
            ):
                record(*match.span(), None, "date_ambiguous")
                continue
            count = int(raw) if raw and raw.lstrip("-").isdigit() else OFFSET_COUNTS[raw] if raw else 1
            factor = 7 if re.search(r"week|nädal|недел", match["unit"]) else 1
            if 0 <= count * factor <= 3660:
                record(*match.span(), now.date() + timedelta(days=count * factor))
            else:
                record(*match.span(), None, "date_invalid")
    for match in INCOMPLETE_PERIOD.finditer(text):
        record(*match.span(), None, "date_incomplete")
    for match in RELATIVE.finditer(text):
        record(*match.span(), now.date() + timedelta(days=RELATIVE_FORMS[match[0]]))
    # A numeric dot date is not a clock when replying to a date question.
    # Month/day order remains uncertain without a named month.
    if allow_bare_day and re.fullmatch(r"\d{1,2}[./-]\d{1,2}\.?", text.strip(" !?,")):
        record(0, len(text), None, "date_ambiguous")
    if allow_bare_day and not spans:
        bare_day = re.fullmatch(r"(?:(?:on|the|na|на|kuupäeval|kuupäevaks)\s+)*(?P<day>" + DAY_PATTERN + r")[.!?,]*(?:\s+palun[.!?,]*)?", text)
        if bare_day:
            raw = bare_day["day"].rstrip(".")
            numeric = re.fullmatch(r"(\d{1,2})(?:st|nd|rd|th|-(?:го|е|й|ое|ого|ому|ом))?", raw)
            partial_day = int(numeric[1]) if numeric else DAY_FORMS[raw]
            if not 1 <= partial_day <= 31:
                record(0, len(text), None, "date_invalid")
            elif pending_month is not None:
                value, error = calendar(partial_day, pending_month, pending_year)
                record(0, len(text), value, error)
            else:
                record(0, len(text), None, "date_incomplete")
    partial_months: set[int] = set()
    for match in MONTHS.finditer(text):
        year_match = re.match(r"(?:\s*,\s*|\s+)(\d{4})(?![\w:.])", text[match.end():])
        spoken_year = SPOKEN_YEARS.after(text[match.end():]) if not year_match else None
        # English "may" is usually a modal, not a request for the month of May.
        # The short "mar" also means ordinary prose; accept these alone only
        # with a month preposition or as the entire answer to a date question.
        if match[0] in {"may", "mar"} and not (allow_bare_day and (year_match or spoken_year)) and text.strip(" .!?,") != match[0] and not re.search(
            r"\b(?:in|during|for|by|until|on)\s+$", text[:match.start()]
        ):
            continue
        if not any(
            match.start() < right and match.end() > left for left, right in spans
        ):
            partial_month = MONTH_FORMS[match[0]]
            partial_months.add(partial_month)
            partial_year = int(year_match[1]) if year_match else pending_year
            end = match.end() + (year_match.end() if year_match else 0)
            if spoken_year:
                partial_year = spoken_year.value
                end = match.end() + spoken_year.end
                if spoken_year.issue:
                    record(match.start(), end, None, spoken_year.issue)
                    continue
            if pending_day is not None and allow_bare_day:
                value, error = calendar(pending_day, partial_month, partial_year)
                record(match.start(), end, value, error)
            else:
                record(match.start(), end, None, "date_incomplete")
    if len(values) > 1 or len(partial_months) > 1:
        issue = "date_ambiguous"
    if spelling.ambiguous_spans:
        issue = "date_ambiguous"
    remaining = list(text)
    for left, right in spans:
        remaining[left:right] = " " * (right - left)
    return DateResolution(
        next(iter(values)) if len(values) == 1 and not issue else None,
        issue,
        "".join(remaining),
        partial_day if issue == "date_incomplete" else None,
        partial_month if issue == "date_incomplete" else None,
        partial_year if issue == "date_incomplete" else None,
    )
