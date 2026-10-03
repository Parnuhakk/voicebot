"""Calendar preferences from finalized speech in ET/EN/RU, never write consent."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
import re
from functools import lru_cache
from zoneinfo import ZoneInfo

from .booking_dates import MONTHS, resolve_estonian_date


TALLINN = ZoneInfo("Europe/Tallinn")
_CASES = ("", "sse", "s", "st", "le", "l", "lt", "ks", "ni", "na", "ta", "ga")


def _alternatives(values):
    return _cached_alternatives(tuple(values))


@lru_cache(maxsize=128)
def _cached_alternatives(values):
    return "(?:" + "|".join(re.escape(v).replace(r"\ ", r"\s+") for v in sorted(values, key=len, reverse=True)) + ")"


def _normalized(text):
    text = text.casefold().replace("ё", "е").replace("’", "'")
    text = re.sub(r"(?<=[a-z])-(?=[a-z])", " ", text)
    text = re.sub(r"(?<!\d):(?=\w)", ": ", text)
    return " ".join(text.split())


def _et_cases(nominative, genitive, partitive):
    return {nominative, partitive, *(genitive + suffix for suffix in _CASES)}


ET_MONTHS = {}
for number, ((name, _), stem) in enumerate(zip(MONTHS, (
    "jaanuari", "veebruari", "märtsi", "aprilli", "mai", "juuni", "juuli",
    "augusti", "septembri", "oktoobri", "novembri", "detsembri",
)), 1):
    for form in _et_cases(name, stem, stem + "t") | {stem, "maid" if number == 5 else stem}:
        ET_MONTHS[form] = number
ET_MONTHS.update({word: n for n, word in enumerate(("jaan", "veebr", "märts", "apr", "mai", "juun", "juul", "aug", "sept", "okt", "nov", "dets"), 1)})

EN_MONTH_NAMES = ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december")
EN_MONTHS = {name: n for n, name in enumerate(EN_MONTH_NAMES, 1)}
EN_MONTHS.update({name[:3]: n for n, name in enumerate(EN_MONTH_NAMES, 1)})
EN_MONTHS["sept"] = 9
RU_MONTH_NAMES = ("января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря")
RU_MONTHS = {}
for number, stem in enumerate(("январ", "феврал", "март", "апрел", "ма", "июн", "июл", "август", "сентябр", "октябр", "ноябр", "декабр"), 1):
    endings = ("й", "я", "ю", "е", "ем") if number not in {3, 8} else ("", "а", "у", "е", "ом")
    if number == 5:
        endings = ("й", "я", "ю", "е", "ем")
    else:
        endings = tuple("ь" if x == "й" else x for x in endings)
    for ending in endings:
        RU_MONTHS[stem + ending] = number

ET_DAYS = {}
_ET_BASE_ORDINALS = (
    ("esimene", "esimese", "esimest"), ("teine", "teise", "teist"),
    ("kolmas", "kolmanda", "kolmandat"), ("neljas", "neljanda", "neljandat"),
    ("viies", "viienda", "viiendat"), ("kuues", "kuuenda", "kuuendat"),
    ("seitsmes", "seitsmenda", "seitsmendat"), ("kaheksas", "kaheksanda", "kaheksandat"),
    ("üheksas", "üheksanda", "üheksandat"), ("kümnes", "kümnenda", "kümnendat"),
)
for number, forms in enumerate(_ET_BASE_ORDINALS, 1):
    ET_DAYS.update(dict.fromkeys(_et_cases(*forms), number))
for number, prefix in enumerate(("ühe", "kahe", "kolme", "nelja", "viie", "kuue", "seitsme", "kaheksa", "üheksa"), 11):
    ET_DAYS.update(dict.fromkeys(_et_cases(prefix + "teistkümnes", prefix + "teistkümnenda", prefix + "teistkümnendat"), number))
for number, prefix in ((20, "kahe"), (30, "kolme")):
    ET_DAYS.update(dict.fromkeys(_et_cases(prefix + "kümnes", prefix + "kümnenda", prefix + "kümnendat"), number))
    for unit in range(1, min(9, 31 - number) + 1):
        for form in _et_cases(*_ET_BASE_ORDINALS[unit - 1]):
            ET_DAYS[prefix + "kümne " + form] = number + unit
            ET_DAYS[prefix + "kümne" + form] = number + unit

EN_DAYS = {}
_EN_ORDINALS = ("first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth", "twentieth")
EN_DAYS.update({word: n for n, word in enumerate(_EN_ORDINALS, 1)})
EN_DAYS.update({"twenty " + _EN_ORDINALS[n - 1]: 20 + n for n in range(1, 10)})
EN_DAYS.update({"thirtieth": 30, "thirty first": 31})
RU_DAYS = {}
_RU_STEMS = ("перв", "втор", "треть", "четверт", "пят", "шест", "седьм", "восьм", "девят", "десят", "одиннадцат", "двенадцат", "тринадцат", "четырнадцат", "пятнадцат", "шестнадцат", "семнадцат", "восемнадцат", "девятнадцат", "двадцат")
for n, stem in enumerate(_RU_STEMS, 1):
    endings = ("е", "его", "ему", "им", "ем") if n == 3 else ("ое", "ого", "ому", "ым", "ом")
    for suffix in endings:
        RU_DAYS[stem + suffix] = n
for base, prefix, units in ((20, "двадцать", range(1, 10)), (30, "тридцать", range(1, 2))):
    for word, n in list(RU_DAYS.items()):
        if n in units:
            RU_DAYS[prefix + " " + word] = base + n
for suffix in ("ое", "ого", "ому", "ым", "ом"):
    RU_DAYS["тридцат" + suffix] = 30

_ET_NUMBERS = ("null", "üks", "kaks", "kolm", "neli", "viis", "kuus", "seitse", "kaheksa", "üheksa", "kümme", "üksteist", "kaksteist", "kolmteist", "neliteist", "viisteist", "kuusteist", "seitseteist", "kaheksateist", "üheksateist")
_EN_NUMBERS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen")
_RU_NUMBERS = ("ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять", "десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать", "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать")
NUMBERS = {}
for lang, base, tens in (
    ("et", _ET_NUMBERS, ("kakskümmend", "kolmkümmend", "nelikümmend", "viiskümmend", "kuuskümmend", "seitsekümmend", "kaheksakümmend", "üheksakümmend")),
    ("en", _EN_NUMBERS, ("twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")),
    ("ru", _RU_NUMBERS, ("двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят", "девяносто")),
):
    numbers = {word: n for n, word in enumerate(base)}
    for decade, word in enumerate(tens, 2):
        numbers[word] = decade * 10
        for unit in range(1, 10):
            numbers[word + " " + base[unit]] = decade * 10 + unit
            if lang == "et":
                numbers[word + base[unit]] = decade * 10 + unit
    NUMBERS[lang] = numbers
NUMBERS["ru"].update({"одна": 1, "одну": 1, "два": 2, "две": 2, "двух": 2, "трех": 3, "четырех": 4})
NUMBERS["et"].update({"ühe": 1, "kahe": 2, "kolme": 3, "nelja": 4, "viie": 5, "kuue": 6, "seitsme": 7, "kaheksa": 8, "üheksa": 9, "kümne": 10})
for n, (nom, gen, part) in enumerate(zip(_ET_NUMBERS[1:11], ("ühe", "kahe", "kolme", "nelja", "viie", "kuue", "seitsme", "kaheksa", "üheksa", "kümne"), ("üht", "kaht", "kolme", "nelja", "viit", "kuut", "seitset", "kaheksat", "üheksat", "kümmet")), 1):
    NUMBERS["et"].update(dict.fromkeys(_et_cases(nom, gen, part), n))
for n, root in enumerate(("ühe", "kahe", "kolme", "nelja", "viie", "kuue", "seitsme", "kaheksa", "üheksa"), 11):
    NUMBERS["et"][root + "teistkümne"] = n
for decade, root in enumerate(("kahe", "kolme", "nelja", "viie", "kuue", "seitsme", "kaheksa", "üheksa"), 2):
    NUMBERS["et"][root + "kümne"] = decade * 10
    for unit, word in enumerate(("ühe", "kahe", "kolme", "nelja", "viie", "kuue", "seitsme", "kaheksa", "üheksa"), 1):
        for separator in ("", " "):
            NUMBERS["et"][root + "kümne" + separator + word] = decade * 10 + unit
# Compound cardinals take their case on the final component.
for word, n in list(NUMBERS["et"].items()):
    if n >= 11 and (word.endswith("kümne") or re.search(r"kümne ?(?:ühe|kahe|kolme|nelja|viie|kuue|seitsme|kaheksa|üheksa)$", word)):
        for suffix in _CASES:
            NUMBERS["et"][word + suffix] = n
for n, word in enumerate(("одной", "двух", "трех", "четырех", "пяти", "шести", "семи", "восьми", "девяти", "десяти", "одиннадцати", "двенадцати", "тринадцати", "четырнадцати", "пятнадцати", "шестнадцати", "семнадцати", "восемнадцати", "девятнадцати"), 1):
    NUMBERS["ru"][word] = n
_RU_CARDINAL_CASES = (
    ("одного", "одному", "одним", "одном"),
    ("двух", "двум", "двумя"), ("трех", "трем", "тремя"),
    ("четырех", "четырем", "четырьмя"),
    ("пяти", "пятью"), ("шести", "шестью"), ("семи", "семью"),
    ("восьми", "восемью", "восьмью"), ("девяти", "девятью"), ("десяти", "десятью"),
)
for n, forms in enumerate(_RU_CARDINAL_CASES, 1):
    NUMBERS["ru"].update(dict.fromkeys(forms, n))
for n, root in enumerate(_RU_NUMBERS[11:19], 11):
    NUMBERS["ru"].update({root[:-1] + "и": n, root + "ю": n})
for decade, forms in enumerate((
    ("двадцати", "двадцатью"), ("тридцати", "тридцатью"), ("сорока", "сорока"),
    ("пятидесяти", "пятьюдесятью"), ("шестидесяти", "шестьюдесятью"),
    ("семидесяти", "семьюдесятью"), ("восьмидесяти", "восемьюдесятью"),
    ("девяноста", "девяноста"),
), 2):
    NUMBERS["ru"].update(dict.fromkeys(forms, decade * 10))
    for unit, words in enumerate(_RU_CARDINAL_CASES[:9], 1):
        for prefix in forms:
            for word in words:
                NUMBERS["ru"][prefix + " " + word] = decade * 10 + unit
for lang, days in (("et", ET_DAYS), ("en", EN_DAYS), ("ru", RU_DAYS)):
    days.update({word: n for word, n in NUMBERS[lang].items() if 1 <= n <= 31})

YEARS = {"et": {"kaks tuhat": 2000}, "en": {"two thousand": 2000}, "ru": {"две тысячи": 2000, "двухтысячного": 2000}}
for lang, prefixes in (("et", ("kaks tuhat",)), ("en", ("two thousand", "two thousand and")), ("ru", ("две тысячи",))):
    for word, number in NUMBERS[lang].items():
        if number:
            for prefix in prefixes:
                YEARS[lang][prefix + " " + word] = 2000 + number
for word, number in NUMBERS["en"].items():
    if number >= 10:
        YEARS["en"]["twenty " + word] = 2000 + number
for word, number in ET_DAYS.items():
    YEARS["et"]["kahe tuhande " + word] = 2000 + number
for word, number in RU_DAYS.items():
    YEARS["ru"]["две тысячи " + word] = 2000 + number
    YEARS["ru"]["двух тысяч " + word] = 2000 + number
for decade, root in enumerate(("kahe", "kolme", "nelja", "viie", "kuue", "seitsme", "kaheksa", "üheksa"), 2):
    for form in _et_cases(root + "kümnes", root + "kümnenda", root + "kümnendat"):
        YEARS["et"]["kahe tuhande " + form] = 2000 + decade * 10
    for unit, forms in enumerate(_ET_BASE_ORDINALS[:9], 1):
        for form in _et_cases(*forms):
            YEARS["et"]["kahe tuhande " + root + "kümne " + form] = 2000 + decade * 10 + unit
            YEARS["et"]["kahe tuhande " + root + "kümne" + form] = 2000 + decade * 10 + unit
_RU_YEAR_UNITS = {}
for n, stem in enumerate(_RU_STEMS[:9], 1):
    nominative = "третий" if n == 3 else stem + ("ой" if n in {2, 6, 7, 8} else "ый")
    _RU_YEAR_UNITS[nominative] = n
    for suffix in (("его", "ему", "им", "ем") if n == 3 else ("ого", "ому", "ым", "ом")):
        _RU_YEAR_UNITS[stem + suffix] = n
for word, n in _RU_YEAR_UNITS.items():
    YEARS["ru"]["две тысячи " + word] = 2000 + n
for n, stem in [*enumerate(_RU_STEMS[9:], 10), (30, "тридцат"), (40, "сороков"), (50, "пятидесят"), (60, "шестидесят"), (70, "семидесят"), (80, "восьмидесят"), (90, "девяност")]:
    for suffix in ("ой" if n == 40 else "ый", "ого", "ому", "ым", "ом"):
        YEARS["ru"]["две тысячи " + stem + suffix] = 2000 + n
for decade, prefix in enumerate(("двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят", "девяносто"), 2):
    for word, n in _RU_YEAR_UNITS.items():
        YEARS["ru"]["две тысячи " + prefix + " " + word] = 2000 + decade * 10 + n

WEEKDAYS = {"et": {}, "en": {}, "ru": {}}
for n, name in enumerate(("esmaspäev", "teisipäev", "kolmapäev", "neljapäev", "reede", "laupäev", "pühapäev")):
    stem = "reede" if n == 4 else name + "a"
    WEEKDAYS["et"].update(dict.fromkeys(_et_cases(name, stem, stem + "t"), n))
for n, name in enumerate(("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")):
    WEEKDAYS["en"].update({name: n, name[:3]: n})
for n, forms in enumerate((
    ("понедельник", "понедельника", "понедельнику", "понедельником", "понедельнике"),
    ("вторник", "вторника", "вторнику", "вторником", "вторнике"),
    ("среда", "среды", "среду", "среде", "средой"),
    ("четверг", "четверга", "четвергу", "четвергом", "четверге"),
    ("пятница", "пятницы", "пятницу", "пятнице", "пятницей"),
    ("суббота", "субботы", "субботу", "субботе", "субботой"),
    ("воскресенье", "воскресенья", "воскресенью", "воскресеньем", "воскресеньи"),
)):
    WEEKDAYS["ru"].update(dict.fromkeys(forms, n))

RELATIVE = {
    "et": {"täna": 0, "homme": 1, "ülehomme": 2, "eile": -1},
    "en": {"today": 0, "tomorrow": 1, "the day after tomorrow": 2, "day after tomorrow": 2, "yesterday": -1},
    "ru": {"сегодня": 0, "завтра": 1, "послезавтра": 2, "вчера": -1},
}
RELATIVE["en"].update({"this morning": 0, "this afternoon": 0, "this evening": 0, "tonight": 0})
RELATIVE["ru"].update({"этим утром": 0, "этим вечером": 0, "сегодня ночью": 0})
for root, offset in (("tänase", 0), ("homse", 1), ("ülehomse", 2), ("eilse", -1)):
    RELATIVE["et"].update(dict.fromkeys((root + suffix for suffix in _CASES), offset))
RELATIVE["et"].update({"tänane": 0, "homseks": 1, "ülehomseks": 2, "homset": 1, "ülehomset": 2})


@dataclass
class TemporalInput:
    dates: list[dict[str, str]] = field(default_factory=list)
    times: list[dict[str, str]] = field(default_factory=list)
    issue: str | None = None
    is_answer: bool = False


def _number(value, language):
    return int(value) if value.isdigit() else NUMBERS[language][value]


def _calendar(day, month, year, today):
    return resolve_estonian_date(f"{day}. {MONTHS[month - 1][0]}" + (f" {year}" if year else ""), today)


def temporal_language(text: str) -> str | None:
    """Strong calendar words can identify the language of a short ASR answer."""
    value = _normalized(text)
    lexicons = {
        "et": (*ET_MONTHS, *ET_DAYS, *WEEKDAYS["et"], *RELATIVE["et"]),
        "en": (*EN_MONTHS, *EN_DAYS, *WEEKDAYS["en"], *RELATIVE["en"], "noon", "midnight"),
        "ru": (*RU_MONTHS, *RU_DAYS, *WEEKDAYS["ru"], *RELATIVE["ru"]),
    }
    candidates = [lang for lang, words in lexicons.items() if re.search(r"\b" + _alternatives(words) + r"\b", value)]
    return candidates[0] if len(candidates) == 1 else None


def validate_local_datetime(day: str, clock: str, now: datetime) -> str | None:
    """The current minute, nonexistent wall clocks and DST folds need clarification."""
    naive = datetime.fromisoformat(day + "T" + clock)
    local = naive.replace(tzinfo=TALLINN)
    if local.astimezone(timezone.utc).astimezone(TALLINN).replace(tzinfo=None) != naive:
        return "invalid_time"
    if local.utcoffset() != local.replace(fold=1).utcoffset():
        return "timezone"
    if now.tzinfo is None:
        now = now.replace(tzinfo=TALLINN)
    return "past" if local <= now.astimezone(TALLINN) else None


def interpret_temporal(text: str, language: str, now: datetime, reference_date: str | None = None, expected: str | None = None, reference_clock: str | None = None) -> TemporalInput:
    """Normalize exact dates/times; classify ambiguity instead of choosing for callers."""
    result = TemporalInput()
    if language not in NUMBERS or not isinstance(text, str) or len(text) > 2000:
        return result
    value = _normalized(text)
    if now.tzinfo is None:
        now = now.replace(tzinfo=TALLINN)
    today = now.astimezone(TALLINN).date()
    occupied = []

    def matches(pattern):
        for m in re.finditer(r"(?<![\w:-])" + pattern + r"(?![\w:-])", value):
            if not any(m.start() < end and m.end() > start for start, end in occupied):
                occupied.append(m.span())
                yield m

    def add_date(resolved):
        result.dates.append(resolved)
        if resolved["status"] != "resolved":
            result.issue = "past" if resolved["status"] == "past" else "invalid_date"

    def add_clock(hour, minute, period="", ambiguous=False):
        period = period.strip()
        if not 0 <= hour <= 23 or not 0 <= minute <= 59:
            result.issue = "invalid_time"
            return
        if period:
            if period in {"am", "a.m.", "pm", "p.m."} and hour > 12:
                result.issue = "invalid_time"
                return
            if hour == 12 and period in {"õhtul", "õhtuks", "õhtusel ajal", "evening", "in the evening", "tonight", "вечера", "вечером"}:
                hour = 0
            elif period in {"pm", "p.m.", "päeval", "pärastlõunal", "õhtul", "õhtuks", "õhtusel ajal", "evening", "afternoon", "in the evening", "in the afternoon", "tonight", "вечера", "вечером", "дня", "днем"}:
                if hour < 12:
                    hour += 12
            elif hour == 12 and period not in {"hommikul", "hommikuks", "morning", "in the morning", "утра", "утром"}:
                hour = 0
        elif ambiguous and 0 <= hour <= 12:
            result.times.append({"status": "ambiguous", "time": f"{hour % 12:02d}:{minute:02d}", "alternative": f"{hour % 12 + 12:02d}:{minute:02d}"})
            result.issue = "ambiguous_time"
            return
        result.times.append({"status": "resolved", "time": f"{hour:02d}:{minute:02d}"})

    # Explicit offset timestamps preserve the instant and its Tallinn date.
    for m in matches(r"\d{4}-\d{2}-\d{2}[t ]\d{2}:\d{2}(?::\d{2})?(?:z|[+-]\d{2}:\d{2})?"):
        try:
            stamp = datetime.fromisoformat(m[0].replace("z", "+00:00"))
            stamp = (stamp.replace(tzinfo=TALLINN) if stamp.tzinfo is None else stamp).astimezone(TALLINN)
            add_date({"status": "past" if stamp.date() < today else "resolved", "date": stamp.date().isoformat()})
            add_clock(stamp.hour, stamp.minute)
            if stamp.second:
                result.issue = "invalid_time"
        except ValueError:
            result.issue = "invalid_date"

    for m in matches(r"\d{4}-\d{2}-\d{2}"):
        add_date(resolve_estonian_date(m[0], today))

    months = {"et": ET_MONTHS, "en": EN_MONTHS, "ru": RU_MONTHS}[language]
    days = {"et": ET_DAYS, "en": EN_DAYS, "ru": RU_DAYS}[language]
    numeric_suffix = {"et": r"(?:-?(?:nda(?:sse|st|le|lt|ks|ni|na|ta|ga|s|l)?|ndat|se(?:le|l|ks)?))?", "en": r"(?:st|nd|rd|th)?", "ru": r"(?:-?(?:го|ого|ому|ым|ом|му|е|м))?"}[language]
    day_pattern = rf"(?:\d{{1,2}}{numeric_suffix}|{_alternatives(days)})"
    month_pattern = _alternatives(months)
    year_pattern = rf"(?:\d{{4}}|{_alternatives(YEARS[language])})"

    def year_value(match):
        year = match["year"]
        if year and re.search(r"järgmis|next|следующ", year):
            return str(today.year + 1)
        if year and re.search(r"eelmis|last|прошл", year):
            return str(today.year - 1)
        if year and re.search(r"this|selle|эт", year):
            return str(today.year)
        return str(YEARS[language][year]) if year and not year.isdigit() else year

    year_reference = {"et": r"(?:järgmis\w*|eelmis\w*|sellel) aasta(?:l)?", "en": r"(?:next|this|last) year", "ru": r"(?:в )?(?:следующ\w*|прошл\w*|эт\w*) год(?:а|у)?"}[language]
    year_pattern = rf"(?:{year_pattern}|{year_reference})"

    named = rf"(?P<day>{day_pattern})\.?\s+(?:of\s+)?(?P<month>{month_pattern})\.?(?:[,\s]+(?P<year>{year_pattern})(?:\.?\s+(?:aastal|aasta|года|году|год))?)?(?!\s+\d{{4,}})"
    for m in matches(named):
        word = m["day"]
        day = int(re.match(r"\d+", word)[0]) if word[0].isdigit() else days[word]
        add_date(_calendar(day, months[m["month"]], year_value(m), today))
    if language == "en":
        for m in matches(rf"(?P<month>{month_pattern})\.?\s+(?:the\s+)?(?P<day>{day_pattern})(?:,?\s+(?P<year>{year_pattern}))?(?!\s+\d{{4,}})"):
            word = m["day"]
            day = int(re.match(r"\d+", word)[0]) if word[0].isdigit() else days[word]
            add_date(_calendar(day, months[m["month"]], year_value(m), today))

    # A stated month relation gives an exact month, unlike a vague month alone.
    implicit_patterns = {
        "et": [rf"(?P<ref>sellel|selle|sel|järgmis\w*) ku(?:ul|u)\s+(?P<day>{day_pattern})", rf"(?P<day>{day_pattern})(?:\s+päeval)?\s+(?P<ref>sellel|selle|sel|järgmis\w*) ku(?:ul|u)"],
        "en": [rf"(?P<ref>this|next) month(?: on)?(?: the)?\s+(?P<day>{day_pattern})", rf"(?:the )?(?P<day>{day_pattern})(?: of)?\s+(?P<ref>this|next) month"],
        "ru": [rf"(?P<day>{day_pattern})(?: числа)?\s+(?:в )?(?P<ref>эт\w*|следующ\w*) месяц\w*", rf"(?:в )?(?P<ref>эт\w*|следующ\w*) месяц\w*\s+(?P<day>{day_pattern})(?: числа)?"],
    }[language]
    for pattern in implicit_patterns:
        for m in matches(pattern):
            word = m["day"]
            day = int(re.match(r"\d+", word)[0]) if word[0].isdigit() else days[word]
            shift = 1 if re.search(r"järgmis|next|следующ", m["ref"]) else 0
            year, month_index = divmod(today.year * 12 + today.month - 1 + shift, 12)
            add_date(_calendar(day, month_index + 1, str(year), today))

    # ET/RU use day-month. English slash dates need clarification when both
    # common orderings describe different valid dates.
    for m in matches(r"(?P<a>\d{1,2})(?P<sep>[/.\-])(?P<b>\d{1,2})(?:[/.\-](?P<year>\d{4}))?\.?"):
        if re.search(r"(?:kell|at|в)\s*$", value[:m.start()]) or (expected == "time" and not m["year"]):
            occupied.remove(m.span())
            continue
        a, b = int(m["a"]), int(m["b"])
        if language == "en" and 1 <= a <= 12 and 1 <= b <= 12 and a != b:
            result.issue = "ambiguous_date"
            result.dates.append({"status": "ambiguous"})
        elif language == "en" and m["sep"] == "/" and a <= 12:
            add_date(_calendar(b, a, m["year"], today))
        elif 1 <= b <= 12:
            add_date(_calendar(a, b, m["year"], today))
        else:
            # A dotted 10.30 following a clock marker is a time, not a date.
            if m["year"] or m["sep"] in {"/", "-"} or expected == "date":
                add_date({"status": "invalid"})
            else:
                occupied.remove(m.span())

    for m in matches(_alternatives(RELATIVE[language]) + (r"(?:\s+päev(?:al|aks|a)?)?" if language == "et" else "")):
        token = re.sub(r"\s+päev\w*$", "", m[0])
        try:
            requested = today + timedelta(days=RELATIVE[language][token])
            add_date({"status": "past" if requested < today else "resolved", "date": requested.isoformat()})
        except OverflowError:
            result.issue = "invalid_date"

    weekdays = WEEKDAYS[language]
    week_modifier = {"et": r"(?:järgmis\w*|eelmis\w*|ülejärgmis\w*)\s+nädal\w*", "en": r"(?:next week|last week|the week after next)(?: on)?", "ru": r"(?:на )?(?:следующ\w*|прошл\w*)\s+недел\w*(?: в)?"}[language]
    modifier = {"et": r"(?:järgmis\w*|eelmis\w*|ülejärgmis\w*|selle|sel|käesoleval)\s+", "en": r"(?:next|this|last|previous)\s+", "ru": r"(?:(?:на|в)\s+)?(?:следующ\w*|прошл\w*|предыдущ\w*|эт\w*)\s+"}[language]
    for m in matches(rf"(?P<modifier>(?:{week_modifier}\s+|{modifier}))?(?P<day>{_alternatives(weekdays)})(?P<week>\s+{week_modifier})?"):
        weekday = weekdays[m["day"]]
        requested = today + timedelta(days=(weekday - today.weekday()) % 7)
        prefix = (m["modifier"] or "") + (m["week"] or "")
        is_next = bool(re.search(r"järgmis|next|следующ", prefix))
        is_past = bool(re.search(r"eelmis|last|previous|прошл|предыдущ", prefix))
        is_this = bool(prefix and not is_next)
        if re.search(r"nädal|week|недел", prefix):
            shift = -7 if is_past else 14 if re.search(r"ülejärgmis|after next", prefix) else 7
            requested = today - timedelta(days=today.weekday()) + timedelta(days=shift + weekday)
        elif is_past:
            requested -= timedelta(days=7)
        elif re.search(r"ülejärgmis", prefix):
            result.issue = "ambiguous_date"
            result.dates.append({"status": "ambiguous"})
            continue
        elif is_this:
            requested = today - timedelta(days=today.weekday()) + timedelta(days=weekday)
        elif is_next and requested == today:
            requested += timedelta(days=7)
        elif is_next and weekday > today.weekday():
            result.issue = "ambiguous_date"
            result.dates.append({"status": "ambiguous", "date": requested.isoformat(), "alternative": (requested + timedelta(days=7)).isoformat()})
            continue
        add_date({"status": "past" if requested < today else "resolved", "date": requested.isoformat()})

    number_pattern = rf"(?:\d{{1,3}}|{_alternatives(NUMBERS[language])})"
    # Consume compound elapsed times as a whole before shorter duration forms.
    compound_duration = {
        "et": rf"(?P<h>{number_pattern}) tunni(?:\s+ja)?\s+(?P<m>{number_pattern}) minuti pärast",
        "en": rf"in (?P<h>{number_pattern}) hours?(?:\s+and)?\s+(?P<m>{number_pattern}) minutes?",
        "ru": rf"через (?P<h>{number_pattern}) час(?:а|ов)?(?:\s+и)?\s+(?P<m>{number_pattern}) минут(?:у|ы)?",
    }[language]
    for m in matches(compound_duration):
        stamp = (now.astimezone(timezone.utc) + timedelta(minutes=_number(m["h"], language) * 60 + _number(m["m"], language))).astimezone(TALLINN)
        add_date({"status": "resolved", "date": stamp.date().isoformat()})
        add_clock(stamp.hour, stamp.minute)
    relative_pattern = {
        "et": rf"(?P<n>{number_pattern})\s+(?P<unit>päeva|nädala|kuu|aasta|tunni|minuti)\s+pärast",
        "en": rf"in\s+(?P<n>{number_pattern})\s+(?P<unit>days?|weeks?|months?|years?|hours?|minutes?)",
        "ru": rf"через\s+(?P<n>{number_pattern})\s+(?P<unit>день|дня|дней|неделю|недели|недель|месяц|месяца|месяцев|год|года|лет|час|часа|часов|минуту|минуты|минут)",
    }[language]
    relative_aliases = {
        "et": {"nädala pärast": (7, "day"), "kuu aja pärast": (1, "month"), "aasta pärast": (12, "month"), "poole tunni pärast": (30, "minute"), "veerand tunni pärast": (15, "minute"), "pooleteise tunni pärast": (90, "minute")},
        "en": {"in a week": (7, "day"), "in a month": (1, "month"), "in a year": (12, "month"), "in an hour": (60, "minute"), "in half an hour": (30, "minute"), "in a quarter of an hour": (15, "minute"), "in a fortnight": (14, "day"), "in one and a half hours": (90, "minute"), "in an hour and a half": (90, "minute")},
        "ru": {"через неделю": (7, "day"), "через месяц": (1, "month"), "через год": (12, "month"), "через час": (60, "minute"), "через полчаса": (30, "minute"), "через четверть часа": (15, "minute"), "через полтора часа": (90, "minute")},
    }[language]
    for m in matches(_alternatives(relative_aliases)):
        if re.search(rf"{number_pattern}\s+$", value[:m.start()]):
            occupied.remove(m.span())
            continue
        n, unit = relative_aliases[m[0]]
        try:
            if unit == "minute":
                stamp = (now.astimezone(timezone.utc) + timedelta(minutes=n)).astimezone(TALLINN)
                add_date({"status": "resolved", "date": stamp.date().isoformat()})
                add_clock(stamp.hour, stamp.minute)
            elif unit == "month":
                year, month_index = divmod(today.year * 12 + today.month - 1 + n, 12)
                add_date(_calendar(today.day, month_index + 1, str(year), today))
            else:
                add_date({"status": "resolved", "date": (today + timedelta(days=n)).isoformat()})
        except (ValueError, OverflowError):
            result.issue = "invalid_date"
    for m in matches(relative_pattern):
        n, unit = _number(m["n"], language), m["unit"]
        try:
            if re.match(r"tunni|hour|час|minuti|minute|минут", unit):
                minutes = n if re.match(r"minuti|minute|минут", unit) else n * 60
                stamp = (now.astimezone(timezone.utc) + timedelta(minutes=minutes)).astimezone(TALLINN)
                add_date({"status": "resolved", "date": stamp.date().isoformat()})
                add_clock(stamp.hour, stamp.minute)
            elif re.match(r"kuu|month|месяц|aasta|year|год|лет", unit):
                count = n * 12 if re.match(r"aasta|year|год|лет", unit) else n
                year, month_index = divmod(today.year * 12 + today.month - 1 + count, 12)
                add_date(_calendar(today.day, month_index + 1, str(year), today))
            else:
                count = n * 7 if re.match(r"nädala|week|недел", unit) else n
                add_date({"status": "resolved", "date": (today + timedelta(days=count)).isoformat()})
        except (ValueError, OverflowError):
            result.issue = "invalid_date"

    next_day = {"et": r"järgmisel (?:päeval|hommikul)", "en": r"(?:the )?(?:next day|day after that|next morning|following morning)", "ru": r"(?:на )?следующий день|следующим утром"}[language]
    for m in matches(next_day):
        if reference_date:
            try:
                requested = date.fromisoformat(reference_date) + timedelta(days=1)
                add_date({"status": "past" if requested < today else "resolved", "date": requested.isoformat()})
            except (ValueError, OverflowError):
                result.issue = "invalid_date"
        else:
            result.issue = "ambiguous_date"

    period_pattern = r"(?:a\.?\s*m\.?|p\.?\s*m\.?|hommikul|hommikuks|päeval|pärastlõunal|õhtul|õhtuks|õhtusel ajal|öösel|in the morning|in the evening|in the afternoon|morning|evening|afternoon|tonight|утра|утром|вечера|вечером|дня|днем|ночи|ночью)"
    prefix = {"et": r"(?:(?:kell|kella|kellaks)\s+)?", "en": r"(?:at\s+)?", "ru": r"(?:(?:в|к|на)\s*)?"}[language]

    def period_for(match):
        if match["period"]:
            period = match["period"]
            return re.sub(r"[.\s]", "", period) if re.fullmatch(r"[ap]\.?(?:\s*)m\.?", period) else period
        preceding = re.search(rf"(?P<period>{period_pattern})\s*$", value[:match.start()])
        if preceding:
            if not any(preceding.start() < end and preceding.end() > start for start, end in occupied):
                occupied.append(preceding.span())
            period = preceding["period"]
            return re.sub(r"[.\s]", "", period) if re.fullmatch(r"[ap]\.?(?:\s*)m\.?", period) else period
        return ""

    if expected == "time" and reference_clock and re.fullmatch(period_pattern, value.strip(" .!?")):
        period = value.strip(" !?")
        if re.fullmatch(r"[ap]\.?(?:\s*)m\.?", period):
            period = re.sub(r"[.\s]", "", period)
        hour, minute = (int(part) for part in reference_clock.split(":"))
        add_clock(hour % 12, minute, period)
        occupied.append((0, len(value)))

    # Consume complete invalid numeric clocks too; never accept their prefix.
    clock_suffix = r"(?:-?ks)?" if language == "et" else ""
    for m in matches(prefix + rf"(?P<h>\d{{1,3}})[:.](?P<m>\d{{1,3}}){clock_suffix}(?:\s*(?P<period>{period_pattern}))?"):
        if len(m["m"]) != 2:
            result.issue = "invalid_time"
        else:
            add_clock(int(m["h"]), int(m["m"]), period_for(m), ambiguous=language != "et" and not m["h"].startswith("0"))

    colloquial = {
        "et": rf"(?:(?:kell|kella)\s+)?(?P<kind>pool|poole|veerand|veerandi|kolmveerand|kolmveerandi)\s+(?P<h>{number_pattern})(?:\s+(?P<period>{period_pattern}))?",
        "en": rf"(?:at\s+)?(?P<kind>half past|quarter past|quarter to)\s+(?P<h>{number_pattern})(?:\s+(?P<period>{period_pattern}))?",
        "ru": rf"(?:в\s+)?(?P<kind>половина|половине|половину|половины|половиной|пол|четверть|четверти|четвертью)\s*(?P<h>{_alternatives(RU_DAYS)})(?:\s+(?P<period>{period_pattern}))?",
    }[language]
    for m in matches(colloquial):
        if language == "ru" and re.search(r"без\s+$", value[:m.start()]):
            occupied.remove(m.span())
            continue
        hour = RU_DAYS[m["h"]] if language == "ru" else _number(m["h"], language)
        target_hour = hour
        kind = m["kind"]
        if language == "et" or language == "ru":
            hour -= 1
        elif kind == "quarter to":
            hour -= 1
        minute = 45 if kind in {"kolmveerand", "kolmveerandi", "quarter to"} else 15 if kind in {"veerand", "veerandi", "quarter past", "четверть", "четверти", "четвертью"} else 30
        period = period_for(m)
        explicit_period = bool(period)
        if hour == -1 and target_hour == 0:
            hour = 23
        if target_hour == 12 and (language == "ru" or kind == "quarter to"):
            if period in {"am", "a.m.", "ночи"}:
                hour, period = 23, ""
            elif period in {"pm", "p.m.", "дня", "in the afternoon", "afternoon"}:
                hour, period = 11, ""
        if not 0 <= hour <= 23:
            result.issue = "invalid_time"
        else:
            add_clock(hour, minute, period, ambiguous=language != "et" and not explicit_period)

    minutes_pattern = {
        "et": rf"(?P<m>{number_pattern})\s+(?:minutit\s+)?(?P<kind>enne|üle|pärast)\s+(?P<h>{number_pattern})(?:\s+(?P<period>{period_pattern}))?",
        "en": rf"(?:at\s+)?(?P<m>{number_pattern}|quarter)\s+(?:minutes?\s+)?(?P<kind>to|past)\s+(?P<h>{number_pattern})(?:\s+(?P<period>{period_pattern}))?",
        "ru": rf"(?:в\s+)?(?P<kind>без)\s+(?P<m>{number_pattern}|четверти)\s+(?:минут\s+)?(?P<h>{number_pattern})(?:\s+(?P<period>{period_pattern}))?",
    }[language]
    for m in matches(minutes_pattern):
        minutes = 15 if m["m"] in {"quarter", "четверти"} else _number(m["m"], language)
        hour = _number(m["h"], language)
        if not 0 < minutes < 60 or not 0 <= hour <= 23:
            result.issue = "invalid_time"
            continue
        if m["kind"] in {"enne", "to", "без"}:
            hour, minutes = (hour - 1) % 24, 60 - minutes
        add_clock(hour, minutes, period_for(m), ambiguous=language != "et")

    if language == "ru":
        for m in matches(rf"(?:в\s+)?(?P<m>{number_pattern})\s+(?:минут(?:ы|у)?\s+)?(?P<h>{_alternatives(w for w in RU_DAYS if w.endswith(('ого', 'его')))})(?:\s+(?P<period>{period_pattern}))?"):
            hour, minute = RU_DAYS[m["h"]] - 1, _number(m["m"], language)
            if 0 <= hour <= 23 and 0 < minute < 60:
                add_clock(hour, minute, period_for(m), ambiguous=True)
            else:
                result.issue = "invalid_time"

    for m in matches(prefix + rf"(?P<h>{number_pattern})(?:\s+(?:часа?|часов|hours?))?\s+(?:ja\s+|and\s+)?(?P<m>{number_pattern})(?:\s+(?:минут(?:ы|у|а)?|minutes?|minutit))?(?:\s+(?P<period>{period_pattern}))?"):
        compound = m["h"] + " " + m["m"]
        if compound in NUMBERS[language] and NUMBERS[language][compound] <= 23:
            occupied.remove(m.span())
            continue
        marked = bool(re.match(r"kell(?:a|aks)?\b|at\b|[вк]\b|на\b", m[0]))
        if not marked and not m["period"] and expected != "time":
            occupied.remove(m.span())
            continue
        if m["h"].isdigit() and not m["m"].isdigit() and _number(m["m"], language) < 10:
            result.issue = "ambiguous_time"
            continue
        add_clock(_number(m["h"], language), _number(m["m"], language), period_for(m), ambiguous=language != "et")

    for m in matches(prefix + rf"(?P<h>{number_pattern})(?:\s*(?:o'clock|часа?|часов))?(?:\s*(?P<period>{period_pattern}))?"):
        # Unmarked plain numbers can be a party size or a day of the month.
        marked = bool(re.match(r"kell(?:a|aks)?\b|at\b|[вк]\b|на\b", m[0]))
        if not marked and not m["period"] and expected != "time":
            occupied.remove(m.span())
            continue
        hour = _number(m["h"], language)
        add_clock(hour, 0, period_for(m), ambiguous=language in {"en", "ru"})

    for m in matches({"et": r"keskpäeval|keskpäevaks|keskööl|keskööks", "en": r"(?:at )?(?:noon|midday|midnight)", "ru": r"(?:в )?(?:полдень|полночь)"}[language]):
        add_clock(0 if re.search(r"kesköö|midnight|полночь", m[0]) else 12, 0)

    remainder = value
    for start, end in sorted(occupied, reverse=True):
        remainder = remainder[:start] + " " + remainder[end:]
    remainder = re.sub(r"[.,!?;:]", " ", remainder)
    wrappers = {
        "et": r"\b(?:palun|sobib|tulen|soovin|tulla|selle|päeval|päevaks|aastal|kell|tallinna|eesti|aja|järgi|kohaliku)\b",
        "en": r"\b(?:please|on|the|of|at|i|will|arrive|come|works|for|me|a|an|year|tallinn|local|time)\b",
        "ru": r"\b(?:пожалуйста|на|в|во|к|го|мне|подходит|приеду|приду|года|году|по|таллиннскому|таллинскому|местному|времени)\b",
    }[language]
    cleaned = re.sub(wrappers, " ", remainder).strip()
    if not result.dates and expected == "date" and re.fullmatch(r"(?:the )?" + day_pattern + r"\.?", value):
        result.issue = "ambiguous_date"
        result.is_answer = True
    if result.times and re.search(r"(?:tunni|hours?|час\w*|minuti|minutes?|минут\w*)", cleaned):
        # A remaining duration component must never authorize a partial result.
        result.issue = "ambiguous_time"
        result.is_answer = True
    if result.times and re.search(r"\b(?:alates|pärast|enne|after|before|by|после|до|позже|раньше)\b", cleaned):
        result.issue = "ambiguous_time"
        result.is_answer = True
    if result.dates and re.fullmatch(r"\d+", cleaned):
        result.issue = "ambiguous_date"
        result.is_answer = True
    if result.dates and re.search(r"thousand|hundred|tuhande|tuhat|тысяч|сот", cleaned):
        result.issue = "ambiguous_date"
        result.is_answer = True
    if result.times and re.search(r"\b(?:utc|gmt|est|eest|cet|cest|eet|pst|pdt|london|moscow|московск\w*|москв\w*|лондон\w*|londoni|moskva)\b", value):
        result.issue = "different_timezone"
        result.is_answer = True
    if re.search(r"(?:kell|at|в)\s+\d+[:.]\d+[:.]\d+", value):
        result.issue = result.issue or "invalid_time"
        result.is_answer = True
    if not cleaned and (result.dates or result.times or result.issue):
        result.is_answer = True
    if len(result.times) > 1:
        result.issue = "ambiguous_time"
    if len(result.dates) > 1 and result.is_answer:
        result.issue = "ambiguous_date"
    if result.dates and re.search(r"\b(?:umbes|paiku|around|about|примерно|около)\b", value) and not result.times:
        result.issue = "ambiguous_date"
        result.is_answer = not re.sub(r"\b(?:umbes|paiku|around|about|примерно|около)\b", "", cleaned).strip()
    if re.search(r"\b(?:või|or|или|либо)\b", value) and (result.dates or result.times):
        result.issue = "ambiguous_date" if len(result.dates) > 1 else "ambiguous_time"
    if not result.dates and re.fullmatch(r"(?:(?:in|on|в|на)\s+)?" + month_pattern + r"|järgmis\w* nädal\w*|next week|(?:на )?следующ\w* недел\w*", value.strip(" .!?")):
        result.issue = result.issue or "vague_date"
        result.is_answer = True
    vague_calendar = {
        "et": r"(?:(?:järgmis\w*|selle|sel|eelmis\w*)\s+(?:nädal\w*|kuu\w*|aasta\w*)(?:\s+(?:lõpus|alguses))?|nädalavahetus\w*|(?:nädala|kuu)\s+(?:lõpus|alguses))",
        "en": r"(?:(?:next|this|last) (?:week|month|year|weekend)|(?:at )?(?:the )?(?:start|end|middle) of (?:next|this|the) (?:week|month|year))",
        "ru": r"(?:(?:на |в )?(?:следующ\w*|эт\w*|будущ\w*|прошл\w*) (?:недел\w*|месяц\w*|год\w*)|в (?:конце|начале) (?:следующ\w* )?(?:недел\w*|месяц\w*))",
    }[language]
    if not result.dates and re.fullmatch(vague_calendar, value.strip(" .!?")):
        result.issue = result.issue or "vague_date"
        result.is_answer = True
    daypart_answer = re.search(r"\b" + period_pattern + r"(?!\w)|pärast lõunat|after lunch|после обеда", remainder)
    daypart_answer = daypart_answer or re.fullmatch(r"this (?:morning|afternoon|evening)|tonight|этим (?:утром|вечером)|сегодня ночью", value)
    if not result.times and daypart_answer:
        result.issue = result.issue or "vague_time"
        result.is_answer = not re.sub(r"\b" + period_pattern + r"(?!\w)|pärast lõunat|after lunch|после обеда", "", cleaned).strip()
    if re.search(r"\b(?:umbes|paiku|around|about|примерно|около|kuni|between|до)\b", value) and result.times:
        result.issue = "ambiguous_time"
        result.is_answer = not re.sub(r"\b(?:umbes|paiku|around|about|примерно|около|kuni|between|до|või|or|или|либо|and|ja|и)\b", "", cleaned).strip()
    if re.search(r"\b(?:ei|ära|ärge|mitte|not|don't|не|нет|отмен\w*)\b", value):
        result.is_answer = False
    # Local DST gaps/folds must not silently move a requested appointment.
    if len(result.dates) == len(result.times) == 1 and result.dates[0]["status"] == result.times[0]["status"] == "resolved":
        result.issue = result.issue or validate_local_datetime(result.dates[0]["date"], result.times[0]["time"], now)
    return result
