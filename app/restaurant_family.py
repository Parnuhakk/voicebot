"""Owner-confirmed family facilities and bounded questions about them."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import cast

FACILITIES = ("drawing", "toys", "play_corner", "children_menu")
LABELS = {
    "et": ("joonistamisvõimalus", "mänguasjad", "mängunurk", "lastemenüü"),
    "en": ("drawing activities", "toys", "a play corner", "a children's menu"),
    "ru": ("возможность порисовать", "игрушки", "игровой уголок", "детское меню"),
}


def _fold(text: str) -> str:
    return text.casefold().translate(str.maketrans({"ä": "a", "ö": "o", "õ": "o", "ü": "u", "ё": "е", "’": "'"}))


def _pattern(text: str) -> re.Pattern[str]:
    return re.compile(_fold(text))


MENU = _pattern(r"lastemenüü|laste\s+menüü|(?:children'?s?|kids'?|child)\s+(?:menu|meals?)|детск\w*\s+меню")
ACTIVITIES = _pattern(
    r"joonist\w*|värvim\w*|mänguas\w*|mängunur\w*|laste\s+(?:nurk|tegevus)\w*|"
    + r"colou?ring|crayons?|\bdraw(?:ing)?\b|art supplies|toys?|play\s+(?:corner|area|room)|"
    + r"рисова\w*|порисова\w*|рисун\w*|раскрас\w*|игруш\w*|игров\w*\s+(?:угол\w*|комнат\w*|зон\w*)"
)
WELCOME = _pattern(
    r"(?:kas|võib|saab).*(?:lastega|lapsega).*(?:tulla|külastada)|"
    + r"(?:mida|kas|on).*(?:lastele|laps\w*).*(?:teha|tegevus|mängida)|"
    + r"(?:kas|on).*(?:laste|pere)sõbralik|"
    + r"(?:are|is).*(?:child|kid|family)[ -]friendly|"
    + r"(?:can|may).*(?:bring|come with).*(?:children|kids|child|baby)|"
    + r"(?:do you|are).*(?:welcome|allow).*(?:children|kids)|"
    + r"(?:what|anything|activities).*(?:children|kids).*(?:do|play)|"
    + r"(?:можно|можем).*(?:с\s+(?:детьми|реб[её]нком)|привести\s+реб[её]нка)|"
    + r"(?:подходит|подойд[её]т).*(?:детям|для\s+детей)"
    + r"|(?:есть|чем|что).*(?:заняться|делать|поиграть).*(?:детям|реб[её]нку|для\s+детей)"
    + r"|чем.*(?:дети|реб[её]нок).*заня\w*"
)
DETAILS = _pattern(
    r"järelevalv|lapsehoid|vanus|vanuse|puhast|tasut|maksab|hind|broneer|kaasa|pliiats|kriit|"
    + r"supervis|babysit|childcare|age\b|ages\b|clean|free\b|charge|cost|price|reserv|take.*home|pencils?|crayons?|"
    + r"присмотр|нян|возраст|убира\w*|чист\w*|бесплат|платн|стоит|стоим|брон|домой|карандаш|мелк"
)
MENU_DETAILS = _pattern(
    r"allerg|allergeen|аллерг|ingredient|koostis|состав|sisald|contain|"
    + r"mis\s+(?:road|toidud|valik)|mida.*(?:süüa|lastemenüüs|pakute)|"
    + r"what.*(?:dishes|food|serve|include|on|in)|"
    + r"(?:какие|что).*(?:блюд|ед|меню|входит)|pasta|pizza|friik|burger|паст|пицц"
)


def family_topic(text: str) -> str | None:
    """Separate facility facts from party counts and unconfirmed details."""
    text = _fold(text)
    menu = MENU.search(text)
    activity = ACTIVITIES.search(text)
    if not (menu or activity or WELCOME.search(text)):
        return None
    if DETAILS.search(text) or (menu and MENU_DETAILS.search(text)):
        return "family_details"
    return "family"


def family_reply(
    data: Mapping[str, object], language: str, *, details: bool = False
) -> str:
    raw = data.get("family_facilities")
    known: Mapping[str, object] = (
        cast(Mapping[str, object], raw) if isinstance(raw, Mapping) else {}
    )
    available = [
        label
        for key, label in zip(FACILITIES, LABELS[language])
        if known.get(key) is True
    ]
    if available:
        connector = {"et": " ja ", "en": " and ", "ru": " и "}[language]
        names = (
            connector.join(available)
            if len(available) < 3
            else ", ".join(available[:-1]) + connector + available[-1]
        )
        reply = {
            "et": f"Lastele on olemas {names}.",
            "en": f"For children, we have {names}.",
            "ru": f"Для детей есть {names}.",
        }[language]
    else:
        reply = {
            "et": "Mul ei ole kinnitatud infot lastele mõeldud võimaluste kohta.",
            "en": "I don't have confirmed information about facilities for children.",
            "ru": "У меня нет подтверждённой информации об удобствах для детей.",
        }[language]
    if details or len(available) != len(FACILITIES):
        reply += (
            " "
            + {
                "et": "Täpse valiku, kasutustingimused ja muud üksikasjad palun täpsustage restorani töötajaga.",
                "en": "Please check the exact choices, conditions of use and other details with the restaurant team.",
                "ru": "Точный выбор, условия использования и другие подробности уточните у сотрудника ресторана.",
            }[language]
        )
    return reply
