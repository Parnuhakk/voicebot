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


_EN_EMPHASIS = r"(?:(?:very|really|so|quite|absolutely|totally)\s+)*"
_EN_POSITIVE = r"(?:good|great|perfect|fine|wonderful|excellent|fantastic|lovely|correct|right|okay|ok|all\s+right)"


EXPRESSIONS = {
    "et": (
        r"jah+|jaa+|jep+|jepp|jup+|jess?|jees|mhm|muidugi|loomulikult|kindlasti|täpselt|"
        r"õige|õigus|päri|nõus|nõustun|sobib|sobivad|klapib|kinnit(?:an|a|age|ame|ää|än)|"
        r"okei|okay|ok|olgu|selge|super|suurepärane|suurepäraselt|"
        r"perfektne|ideaalne|kõlab(?:\s+(?:väga|igati|täiesti))?\s+hästi|"
        r"(?:see\s+)?oleks(?:\s+(?:väga|igati|täiesti))?\s+(?:hea|tore|suurepärane|ideaalne)|"
        r"hästi|hea|kena|tore|võib\s+küll|"
        r"(?:teeme|tehke|tee)(?:\s+selle)?\s+(?:ära|nii)|las\s+käia|peab\s+paika|"
        r"(?:pane|pange)(?:\s+(?:see|meid|broneering))?\s+(?:kirja|lukku)|"
        r"broneeri(?:ge|me)?|või(?:d|te)\s+(?:(?:selle|broneeringu)\s+)?(?:ära\s+)?(?:kinnitada|broneerida)|"
        r"minu\s+poolest|meie\s+poolest|ei\s+ole\s+probleemi|pole\s+probleemi"
    ),
    "en": (
        r"yes+|yeah|yep+|yup|sure|absolutely|certainly|definitely|of\s+course|"
        r"ok|okay|alright|all\s+right|agreed|agree|confirm(?:ed)?|"
        r"great|perfect|wonderful|excellent|fantastic|fine|good|cool|correct|right|"
        rf"(?:sounds|looks)\s+{_EN_EMPHASIS}{_EN_POSITIVE}|"
        rf"(?:that|this|it|everything)(?:'s|\s+is)\s+{_EN_EMPHASIS}{_EN_POSITIVE}|"
        r"(?:that\s+|this\s+|it\s+)?works(?:\s+for\s+(?:me|us))?|"
        r"go\s+ahead|(?:let's|let\s+us)\s+do\s+(?:it|that)|"
        r"(?:you\s+can\s+)?(?:book|reserve|confirm)\s+(?:it|that|the\s+table)|"
        r"(?:i'm|i\s+am)\s+happy\s+with\s+(?:that|this|it)|"
        r"(?:that\s+|this\s+|it\s+)?suits\s+(?:me|us)|"
        rf"(?:that|this|it)\s+would\s+be\s+{_EN_EMPHASIS}{_EN_POSITIVE}|"
        r"all\s+good|no\s+problem"
    ),
    "ru": (
        r"да|ага|угу|конечно|разумеется|безусловно|точно|верно|правильно|"
        r"соглас(?:ен|на|ны)|соглашаюсь|подходит|устраивает|"
        r"подтвержда(?:ю|ем|йте)|подтверди(?:те)?|"
        r"хорошо|отлично|замечательно|прекрасно|супер|ок(?:ей)?|ладно|"
        r"(?:это\s+)?(?:очень\s+)?(?:хороший|отличный|прекрасный)\s+вариант|"
        r"(?:это\s+)?было\s+бы\s+(?:очень\s+)?(?:хорошо|отлично|замечательно|прекрасно)|"
        r"давайте|договорились|бронируйте|забронируйте|оформляйте|сделайте\s+бронь|"
        r"без\s+проблем|не\s+против|всё\s+верно|все\s+верно"
    ),
}
MODIFIERS = {
    "et": (
        r"palun|aitäh|tänan|suur\s+tänu|tänud|väga|igati|täiesti|"
        r"nii|täitsa|ka|küll|ja|ning|see|selle|seda|sellega|kõik|mulle|minule|meile|"
        r"ma|mina|me|meie|olen|oleme|on|siis|täielikult|broneeringu|testbroneeringu|laua|"
        r"just\s+nii|igatpidi|igapidi"
    ),
    "en": (
        r"please|thanks|thank\s+you|very\s+much|very|so\s+much|really|totally|"
        r"completely|perfectly|and|i|we|do|this|that|it|the|"
        r"booking|reservation|test\s+booking|table|for\s+me|for\s+us"
    ),
    "ru": (
        r"пожалуйста|большое\s+спасибо|спасибо\s+большое|спасибо|благодарю|"
        r"очень|вполне|полностью|именно|и|я|мы|мне|нам|меня|нас|"
        r"это|всё|все|так|бронирование|бронь|столик|с\s+удовольствием"
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
    value = unicodedata.normalize("NFKC", text).casefold().replace("’", "'")
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
