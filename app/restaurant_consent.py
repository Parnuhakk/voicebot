"""Compositional affirmative replies to a delivered restaurant proposal.

Recognize affirmative expressions with ordinary politeness and emphasis rather
than enumerating complete answers. The entire turn must express agreement:
questions, conditions, changed details and unrelated text leave unmatched words.
This helper does not authorize a write; CallTools owns delivery and consent.
"""

import re
import unicodedata

CONFIRMATION_QUESTIONS = {
    "et": "Kas teile sobib?",
    "en": "Does that work for you?",
    "ru": "Вам подходит?",
}


_EN_EMPHASIS = (
    r"(?:(?:very|really|so|quite|absolutely|totally|completely|perfectly|"
    r"just|exactly|pretty)\s+)*"
)
_EN_POSITIVE = (
    r"(?:good\s+to\s+go|good|great|perfect|fine|wonderful|excellent|fantastic|lovely|correct|right|"
    r"okay|ok|all\s+right|awesome|amazing|brilliant|terrific|ideal|acceptable|spot\s+on)"
)
_EN_SUBJECT = r"(?:that|this|it|everything|the\s+(?:time|date|table|reservation|booking))"
_EN_TARGET = r"(?:that|this|it|the\s+(?:table|reservation|booking))"
_EN_PERSON = r"(?:me|us|everyone|all\s+of\s+us|our\s+group)"
_EN_PERSON_TAIL = rf"(?:\s+(?:for|to|by|with)\s+{_EN_PERSON})?"
_EN_ACTION = r"(?:book|reserve|confirm)"
_EN_CONTRACTIONS = {
    "thats": "that's",
    "its": "it's",
    "everythings": "everything's",
    "im": "i'm",
    "youre": "you're",
    "lets": "let's",
    "thatll": "that will",
    "itll": "it will",
    "thisll": "this will",
    "thatd": "that would",
    "that'll": "that will",
    "it'll": "it will",
    "this'll": "this will",
    "that'd": "that would",
}
_EN_CONTRACTION = re.compile(
    r"\b(?:" + "|".join(re.escape(word) for word in _EN_CONTRACTIONS) + r")\b"
)


EXPRESSIONS = {
    "et": (
        r"ideaalne\s+variant|suurepärane\s+idee|"
        r"jah+|jaa+|jep+|jepp|jup+|jess?|jees|mhm|muidugi|loomulikult|kindlasti|täpselt|"
        r"õige|õigus|päri|nõus|nõustun|sobib|sobivad|klapib|kinnit(?:an|a|age|ame|ää|än)|"
        r"okei|okay|ok|olgu|selge|super|suurepärane|suurepäraselt|"
        r"perfektne|ideaalne|"
        r"kõlab(?:\s+(?:väga|igati|täiesti))?\s+(?:hästi|suurepäraselt|ideaalselt)|"
        r"(?:see\s+)?oleks(?:\s+(?:väga|igati|täiesti))?\s+(?:hea|tore|suurepärane|ideaalne)|"
        r"hästi|hea|kena|tore|vahva|vägev|sobiv|sobilik|just|võib\s+küll|kõik\s+on\s+korras|"
        r"(?:(?:see|pakutud)\s+)?(?:aeg|kellaaeg|kuupäev|laud|broneering)\s+(?:sobib|klapib)|"
        r"(?:mulle|meile)\s+sobib\s+(?:see\s+)?(?:aeg|kellaaeg|kuupäev|laud|broneering)|"
        r"(?:tee|tehke|teeme)\s+(?:laua)?broneering(?:u)?|"
        r"(?:teeme|tehke|tee)(?:\s+selle)?\s+(?:ära|nii)|las\s+käia|peab\s+paika|"
        r"(?:pane|pange|paneme)(?:\s+(?:see|meid|broneering))?\s+(?:kirja|lukku)|"
        r"(?:võtan|võtame)\s+selle(?:\s+laua)?|teeme|"
        r"broneeri(?:ge|me)?|või(?:d|te)\s+(?:(?:selle|broneeringu)\s+)?(?:ära\s+)?(?:kinnitada|broneerida)|"
        r"minu\s+poolest|meie\s+poolest|ei\s+ole\s+probleemi|pole\s+probleemi"
    ),
    "en": (
        # Match complete declarations/actions before shorter affirmative words.
        rf"{_EN_SUBJECT}(?:'s|\s+is|\s+(?:would|will)\s+be)\s+{_EN_EMPHASIS}{_EN_POSITIVE}{_EN_PERSON_TAIL}|"
        rf"(?:{_EN_SUBJECT}\s+)?(?:sounds|looks)\s+{_EN_EMPHASIS}{_EN_POSITIVE}{_EN_PERSON_TAIL}|"
        rf"(?:{_EN_SUBJECT}\s+)?works(?:\s+(?:really\s+)?(?:well|nicely|perfectly))?{_EN_PERSON_TAIL}|"
        rf"{_EN_SUBJECT}\s+(?:would|will)\s+work(?:\s+(?:really\s+)?(?:well|nicely|perfectly))?{_EN_PERSON_TAIL}|"
        rf"{_EN_SUBJECT}(?:'s|\s+is)\s+{_EN_EMPHASIS}what\s+(?:i|we)\s+(?:want(?:ed)?|need(?:ed)?)|"
        rf"(?:i|we)\s+{_EN_EMPHASIS}(?:agree|consent)(?:\s+(?:with|to)\s+{_EN_TARGET})?|"
        rf"(?:i(?:'m|\s+am)|we(?:'re|\s+are))\s+{_EN_EMPHASIS}(?:happy|fine|okay|ok|good|pleased)\s+with\s+{_EN_TARGET}|"
        rf"(?:i|we)\s+(?:want|would\s+like)\s+to\s+(?:{_EN_ACTION}\s+{_EN_TARGET}|go\s+ahead|proceed)|"
        rf"(?:i|we)(?:'d|\s+would)\s+(?:like|love)\s+(?:{_EN_TARGET}|to\s+(?:{_EN_ACTION}\s+{_EN_TARGET}|go\s+ahead|proceed))|"
        rf"(?:i(?:'m|\s+am)|we(?:'re|\s+are))\s+happy\s+to\s+(?:{_EN_ACTION}\s+{_EN_TARGET}|go\s+ahead|proceed)|"
        rf"you(?:'re|\s+are)\s+{_EN_EMPHASIS}(?:right|correct)|"
        rf"(?:let's|let\s+us)\s+(?:do\s+(?:it|that)|{_EN_ACTION}\s+{_EN_TARGET}|go\s+ahead|proceed)|"
        rf"(?:you\s+can\s+)?{_EN_ACTION}\s+(?:{_EN_TARGET}|a\s+table)|"
        r"(?:make|complete)\s+(?:the|this|that)\s+(?:booking|reservation)|"
        r"all\s+(?:those|the)\s+details\s+are\s+(?:correct|right)|"
        rf"{_EN_EMPHASIS}{_EN_POSITIVE}{_EN_PERSON_TAIL}|"
        r"sure\s+thing|for\s+sure|very\s+well|you\s+bet|go\s+for\s+it|count\s+(?:me|us)\s+in|"
        r"it(?:'s|\s+is)\s+a\s+deal|deal|affirmative|no\s+objections|"
        r"that\s+will\s+do|that\s+makes\s+sense|no\s+worries|all\s+(?:good|correct)|"
        r"yes+|yeah+|yep+|yup|aye|sure|absolutely|certainly|definitely|of\s+course|"
        r"ok|okay|alrighty?|all\s+right|agreed|agree|confirm(?:ed)?|"
        r"cool|go\s+ahead|"
        r"(?:that\s+|this\s+|it\s+)?suits\s+(?:me|us)|"
        r"no\s+problem"
    ),
    "ru": (
        r"да\s+можно|да|ага|угу|конечно|разумеется|безусловно|точно|верно|правильно|"
        r"соглас(?:ен|на|ны)|соглашаюсь|подходит|устраивает|"
        r"подтвержда(?:ю|ем|йте)|подтверди(?:те)?|"
        r"звучит(?:\s+(?:очень|просто))?\s+(?:хорошо|отлично|замечательно|прекрасно|идеально)|"
        r"хорошая\s+идея|отличная\s+идея|в\s+самый\s+раз|принимаю|делайте|"
        r"хорошо|отлично|замечательно|прекрасно|идеально|супер|ок(?:ей)?|ладно|"
        r"(?:это\s+)?(?:очень\s+)?(?:хороший|отличный|прекрасный)\s+вариант|"
        r"(?:это\s+)?было\s+бы\s+(?:очень\s+)?(?:хорошо|отлично|замечательно|прекрасно|идеально)|"
        r"давайте(?:\s+(?:так\s+)?и\s+сделаем)?|договорились|"
        r"можете\s+(?:бронировать|забронировать|подтвердить|оформить)|"
        r"бронируем|забронируем|оформим|подтвердим|бронируйте|забронируйте|оформляйте|"
        r"сделайте\s+(?:бронь|бронирование)|"
        r"без\s+проблем|не\s+против|всё\s+верно|все\s+верно"
    ),
}
MODIFIERS = {
    "et": (
        r"palun|aitäh|tänan|suur\s+tänu|tänud|väga|igati|täiesti|"
        r"nii|täitsa|ideaalselt|ka|küll|ja|ning|see|selle|seda|sellega|kõik|mulle|minule|meile|"
        r"ma|mina|me|meie|olen|oleme|on|siis|täielikult|broneeringu|testbroneeringu|laua|"
        r"just\s+nii|igatpidi|igapidi"
    ),
    "en": (
        r"please|thanks|thank\s+you|very\s+much|very|so\s+much|really|totally|"
        r"completely|perfectly|indeed|well|and|i|we|do|this|that|it|the|"
        r"booking|reservation|test\s+booking|table|for\s+me|for\s+us"
    ),
    "ru": (
        r"пожалуйста|большое\s+спасибо|спасибо\s+большое|спасибо|благодарю|"
        r"очень|вполне|полностью|именно|просто|абсолютно|и|я|мы|мне|нам|меня|нас|"
        r"это|такой|такое|этот|всё|все|так|бронирование|бронь|столик|с\s+удовольствием"
    ),
}
_AFFIRMATIVE = {
    language: re.compile(rf"(?:{expression})(?=\s|$)")
    for language, expression in EXPRESSIONS.items()
}
_PARTS = {
    language: re.compile(rf"(?:(?:{EXPRESSIONS[language]})|(?:{modifier}))(?=\s|$)")
    for language, modifier in MODIFIERS.items()
}


def is_restaurant_confirmation(text: object, language: str) -> bool:
    if not isinstance(text, str) or not text.strip() or len(text) > 500:
        return False
    if language not in _PARTS:
        return False
    value = unicodedata.normalize("NFKC", text).casefold()
    value = value.translate(str.maketrans({"’": "'", "‘": "'", "ʼ": "'"}))
    if language == "en":
        # Speech recognition and typed replies often omit contraction apostrophes.
        value = _EN_CONTRACTION.sub(lambda match: _EN_CONTRACTIONS[match[0]], value)
    # Keep question marks, quotes, numbers and other punctuation unmatched.
    value = " ".join(re.sub(r"[.,!;…–—-]", " ", value).split())
    # ASR may omit question punctuation; subject/auxiliary inversion is not
    # agreement. Declarative "I do confirm" remains a complete affirmation.
    if language == "en" and re.search(r"\bdo\s+(?:i|we|you)\b", value):
        return False
    affirmative = False
    while value:
        match = _PARTS[language].match(value)
        if match is None:
            return False
        affirmative |= _AFFIRMATIVE[language].fullmatch(match[0]) is not None
        value = value[match.end() :].lstrip()
    return affirmative
