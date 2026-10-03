"""Closed English/Russian calendar vocabulary, independent of booking consent.

Mixed ordinal/month cases are accepted only beside a known month. Numbers above
31 are recognized as well, so an impossible compound day cannot become its units.
"""


ENGLISH_CARDINALS = (
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
    "eighteen", "nineteen",
)
ENGLISH_ORDINALS = (
    "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth",
    "ninth", "tenth", "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth",
    "sixteenth", "seventeenth", "eighteenth", "nineteenth",
)
ENGLISH_DAY_FORMS = {"zero": 0}
for number, pair in enumerate(zip(ENGLISH_CARDINALS, ENGLISH_ORDINALS), 1):
    ENGLISH_DAY_FORMS.update(dict.fromkeys(pair, number))
for tens, cardinal, ordinal in (
    (20, "twenty", "twentieth"), (30, "thirty", "thirtieth"),
    (40, "forty", "fortieth"), (50, "fifty", "fiftieth"),
    (60, "sixty", "sixtieth"), (70, "seventy", "seventieth"),
    (80, "eighty", "eightieth"), (90, "ninety", "ninetieth"),
):
    ENGLISH_DAY_FORMS.update(dict.fromkeys((cardinal, ordinal), tens))
    for units in range(1, 10):
        for word in (ENGLISH_CARDINALS[units - 1], ENGLISH_ORDINALS[units - 1]):
            for separator in (" ", "-", ""):
                for prefix in (cardinal, ordinal):
                    ENGLISH_DAY_FORMS[prefix + separator + word] = tens + units


def _russian_variants(forms: tuple[str, ...]) -> set[str]:
    # ASR commonly omits the two dots; matching never changes stored speech.
    return set(forms) | {form.replace("ё", "е") for form in forms}


RUSSIAN_CARDINAL_BASES = (
    ("один", "одна", "одно", "одного", "одной", "одному", "одним", "одном"),
    ("два", "две", "двух", "двум", "двумя"),
    ("три", "трёх", "трём", "тремя"),
    ("четыре", "четырёх", "четырём", "четырьмя"),
    ("пять", "пяти", "пятью"), ("шесть", "шести", "шестью"),
    ("семь", "семи", "семью"), ("восемь", "восьми", "восемью", "восьмью"),
    ("девять", "девяти", "девятью"), ("десять", "десяти", "десятью"),
)
RUSSIAN_COUNTS = {
    form: number
    for number, bases in enumerate(RUSSIAN_CARDINAL_BASES, 1)
    for form in _russian_variants(bases)
}
RUSSIAN_COUNTS.update(
    {
        "двое": 2, "двоих": 2, "двоим": 2, "двоими": 2,
        "трое": 3, "троих": 3, "троим": 3, "троими": 3,
        "четверо": 4, "четверых": 4, "четверым": 4,
        "пятеро": 5, "пятерых": 5, "шестеро": 6, "шестерых": 6,
        "семеро": 7, "семерых": 7, "восьмеро": 8, "восьмерых": 8,
        "девятеро": 9, "девятерых": 9, "десятеро": 10, "десятерых": 10,
    }
)
RUSSIAN_DAY_FORMS = {**RUSSIAN_COUNTS, "ноль": 0, "нуль": 0}
RUSSIAN_ORDINAL_STEMS = (
    "перв", "втор", "трет", "четвёрт", "пят", "шест", "седьм", "восьм",
    "девят", "десят", "одиннадцат", "двенадцат", "тринадцат", "четырнадцат",
    "пятнадцат", "шестнадцат", "семнадцат", "восемнадцат", "девятнадцат",
)


def _russian_ordinals(stem: str) -> set[str]:
    endings = ("ый", "ой", "ое", "ого", "ому", "ым", "ом", "ая", "ую", "ые", "ых", "ыми")
    forms = {stem + ending for ending in endings}
    if stem == "трет":
        forms.update({"третий", "третье", "третьего", "третьему", "третьим", "третьем", "третья", "третью", "третьей", "третьи", "третьих"})
    return _russian_variants(tuple(forms))


for number, stem in enumerate(RUSSIAN_ORDINAL_STEMS, 1):
    RUSSIAN_DAY_FORMS.update(dict.fromkeys(_russian_ordinals(stem), number))
    if number >= 11:
        cardinal = stem.removesuffix("ат") + "ать"
        RUSSIAN_DAY_FORMS.update(
            dict.fromkeys((cardinal, cardinal.removesuffix("ь") + "и", cardinal + "ю"), number)
        )
for tens, cardinal, stem in (
    (20, "двадцать", "двадцат"), (30, "тридцать", "тридцат"),
    (40, "сорок", "сороков"), (50, "пятьдесят", "пятидесят"),
    (60, "шестьдесят", "шестидесят"), (70, "семьдесят", "семидесят"),
    (80, "восемьдесят", "восьмидесят"), (90, "девяносто", "девяност"),
):
    prefixes = {cardinal}
    if tens in (20, 30):
        prefixes.update({cardinal[:-1] + "и", cardinal + "ю"})
        prefixes.update(_russian_ordinals(stem))
    RUSSIAN_DAY_FORMS.update(dict.fromkeys(prefixes | _russian_ordinals(stem), tens))
    for form, units in list(RUSSIAN_DAY_FORMS.items()):
        if 1 <= units <= 9:
            for prefix in prefixes:
                for separator in (" ", "-", ""):
                    RUSSIAN_DAY_FORMS[prefix + separator + form] = tens + units

ENGLISH_MONTH_BASES = (
    ("january", "jan"), ("february", "feb"), ("march", "mar"),
    ("april", "apr"), ("may",), ("june", "jun"), ("july", "jul"),
    ("august", "aug"), ("september", "sep", "sept"), ("october", "oct"),
    ("november", "nov"), ("december", "dec"),
)
ENGLISH_MONTH_FORMS = {
    form: number
    for number, bases in enumerate(ENGLISH_MONTH_BASES, 1)
    for form in bases
}
RUSSIAN_MONTH_BASES = (
    ("январ", "ь"), ("феврал", "ь"), ("март", ""), ("апрел", "ь"),
    ("ма", "й"), ("июн", "ь"), ("июл", "ь"), ("август", ""),
    ("сентябр", "ь"), ("октябр", "ь"), ("ноябр", "ь"), ("декабр", "ь"),
)
RUSSIAN_MONTH_FORMS = {
    stem + ending: number
    for number, (stem, nominative) in enumerate(RUSSIAN_MONTH_BASES, 1)
    for ending in ((nominative, "а", "у", "ом", "е") if nominative == "" else (nominative, "я", "ю", "ем", "ём", "е"))
}
