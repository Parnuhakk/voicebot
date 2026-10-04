"""Reviewed replies to service questions whose details have not been confirmed."""

from __future__ import annotations

import re
import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

LANGUAGES = ("et", "en", "ru")
SCOPES: dict[str, tuple[str, str, str]] = {
    "payment_tax": ("hindade maksude ja lisatasude kohta", "taxes and additional fees in prices", "о налогах и дополнительных сборах в ценах"),
    "family_certification": ("ametliku peresõbralikkuse märgise kohta", "an official family friendly certification", "об официальной отметке семейного ресторана"),
    "play_hours": ("mängunurga eraldi lahtiolekuaegade kohta", "separate opening hours for the play corner", "об отдельных часах работы игрового уголка"),
    "facility_safety": ("mänguasjade ja joonistamisvahendite materjalide ning allergiaohutuse kohta", "toy and drawing materials and their allergy safety", "о материалах игрушек и принадлежностей для рисования и их безопасности при аллергии"),
    "food_stock": ("roogade tänase saadavuse kohta", "today's dish availability", "о наличии блюд сегодня"),
    "family_serving": ("lapse toidu varem serveerimise kohta", "serving a child's meal first", "о возможности принести еду ребёнку раньше"),
    "last_order_help": ("viimase toidutellimuse vastuvõtmise korra kohta", "the last food order policy", "о порядке приёма последнего заказа еды"),
    "dietary_certification": ("halal- või koššertoidu ja sertifikaatide kohta", "halal or kosher food and certification", "о халяльной или кошерной еде и сертификации"),
    "access_support": ("kuulmist toetavate abivahendite kohta", "support for guests with hearing difficulties", "о средствах помощи гостям с нарушением слуха"),
    "drinks_help": ("joogivaliku ja roogadega sobitamise kohta", "the drinks selection and meal pairings", "о выборе напитков и сочетаниях с блюдами"),
    "delivery_help": ("restorani kojuveo piirkonna, tasu ja ooteaja kohta", "the restaurant's delivery area, fees and waiting time", "о районе, стоимости и времени ожидания доставки ресторана"),
    "event_details": ("erimenüüde, ürituste, piletite ja soodustuste kohta", "special menus, events, tickets and discounts", "о специальных меню, мероприятиях, билетах и скидках"),
    "contact_help": ("restorani avalike kontaktide ja ametliku menüü veebilingi kohta", "public restaurant contacts and an official menu link", "о публичных контактах ресторана и ссылке на официальное меню"),
    "other_pets": ("teiste lemmikloomade lubamise kohta", "admitting pets other than dogs", "о посещении с другими домашними животными"),
    "pet_details": ("lemmiklooma lisatingimuste ja tarvikute kohta", "pet conditions and facilities", "о дополнительных условиях и удобствах для животных"),
    "child_allergens": ("lastemenüü koostise ja eridieetide kohta", "children's menu ingredients and dietary requirements", "о составе детского меню и особых требованиях к питанию"),
    "ingredient_details": ("küsitud koostisosa ja eraldi valmistamise tingimuste kohta", "the requested ingredient and separate preparation conditions", "о запрошенном ингредиенте и условиях отдельного приготовления"),
    "medical_food": ("roa täpse koostise ja valmistamise kohta", "the dish's exact ingredients and preparation", "о точном составе и приготовлении блюда"),
    "payment_help": ("makseviiside, arve jagamise ja arve väljastamise tingimuste kohta", "payment methods, split bills and invoices", "о способах оплаты, разделении счёта и выставлении счёта"),
    "privacy_help": ("selle teenuse salvestamise, andmete säilitamise ja andmekaitse kontakti kohta", "this service's recording, retention and privacy contact details", "об условиях записи, хранения данных и контакте по защите данных этого сервиса"),
    "amenities_help": ("küsitud mugavuse või selle kasutustingimuste kohta", "the requested facility and its conditions of use", "о запрошенном удобстве и условиях его использования"),
    "seating_help": ("kindla laua valimise ja eripaigutuse kohta", "choosing a specific table or seating arrangement", "о выборе конкретного столика и особом размещении"),
    "menu_formats": ("menüü ligipääsetavate vormide kohta", "accessible menu formats", "о доступных форматах меню"),
    "children_services": ("lapsehoiu, lapsevankri, mähkimisvõimaluse ja muude pere eritingimuste kohta", "childcare, stroller space, changing facilities and other family arrangements", "о присмотре за детьми, месте для коляски, пеленании и других условиях для семьи"),
    "food_modifications": ("roa valmistusviisi ja muudatuste võimaluse kohta", "dish preparation and possible modifications", "о способе приготовления и возможности изменить блюдо"),
    "complaints_help": ("restorani kaebuste kanali, leitud esemete ja hüvitiste korra kohta", "the restaurant's complaint channel, lost property and compensation process", "о канале жалоб, найденных вещах и порядке компенсаций в ресторане"),
}
PATTERNS = {
    "payment_tax": r"käibemaks|\bvat\b|\bндс\b|налог|service charge|teenindustasu|сбор.*обслуживан",
    "family_certification": r"peresõbralik\w*.*(?:märgis|sertifika)|family.?friendly.*(?:certif|label)|официальн\w*.*(?:отметка|сертификат).*семейн|семейн\w*.*(?:сертификат|отметка)",
    "play_hours": r"mängunur\w*.*(?:avatud|lahtiolek|kell)|(?:kell|lahtioleku).*mängunur|play corner.*(?:opening hours|open|close)|(?:open|close).*play corner|(?:часы|когда).*игров\w*\s+угол|игров\w*\s+угол\w*.*(?:открыт|закрыт|час)",
    "facility_safety": r"(?:mänguas|joonist|toy|crayon|drawing|игруш|рисован).*(?:lateks|latex|allerg|аллерг|латекс)|(?:lateks|latex|allerg|аллерг|латекс).*(?:mänguas|joonist|toy|crayon|drawing|игруш|рисован)",
    "food_stock": r"(?:lõhe|supp|risot|roog).*(?:täna.*saadaval|otsa saanud)|(?:salmon|soup|risotto|dish).*(?:still available|sold out|available today)|(?:лосос|суп|ризотто|блюд).*(?:сегодня.*(?:есть|налич)|законч)",
    "family_serving": r"lapse.*toit.*(?:enne|varem)|child'?s.*(?:food|meal).*(?:before|first)|еду.*реб[её]нк.*раньше",
    "last_order_help": r"viimase tellimuse|latest time.*order|last (?:food )?order|до какого времени.*заказ",
    "dietary_certification": r"halal|koššer|kosher|халяль|кошер",
    "access_support": r"kuulmisrask|hearing difficulties|нарушен\w*\s+слуха",
    "food_order_help": r"\b(?:tellin|telli|soovin tellida).*(?:supp|mahl|roog|toit)|\border.*(?:food|soup|juice|meal)|хочу заказать.*(?:суп|сок|еду)|закажите.*(?:суп|сок|еду)",
    "delivery_help": r"kohaletoimet|kojuveo|delivery (?:fee|cost|wait)|how (?:much|long).*delivery|район.*достав|сто(?:ит|имость).*достав|сколько.*достав",
    "drinks_help": r"(?:vein|wine|вино).*(?:soovit|recommend|посовет|порекоменд)|(?:soovit|recommend|посовет|порекоменд).*(?:vein|wine|вино)",
    "event_details": r"aastavahetus|new year'?s eve|новогодн|soodustus|discounts?|скидк",
    "contact_help": r"restorani (?:telefon|e-posti)|restaurant'?s (?:phone|email)|телефон\w*\s+ресторана|почта ресторана|(?:ametlik|official|официальн).*(?:menüü|menu|меню).*(?:veeb|online|интернет)",
    "emergency_help": r"rask\w*\s+hingat|(?:kaotas|kaotanud)\s+teadvuse|tulekahju|tugev\w*\s+allergil\w*\s+reaktsioon|ähvardab.*inimes|struggling to breathe|can'?t breathe|(?:lost|lose|losing) consciousness|(?:there is|there'?s) a fire|severe allergic reaction|threatening people|трудно дышать|не могу дышать|потерял\w* сознание|пожар\b|сильн\w* аллергическ\w* реакци|угрожает людям",
    "payment_secret": r"(?:panga)?kaardi\s+(?:numbr|turvakood)|\b(?:card number|security code|cvv|cvc)\b|номер\s+(?:банковской\s+)?карт|защитн\w*\s+код",
    "other_pets": r"\b(?:cats?|rabbits?|birds?|kass\w*|jänes\w*|linnuga|кошк\w*|кролик\w*|птиц\w*)\b",
    "pet_details": r"(?:koer|dog|собак).*(?:rihm|suur|veekaus|lead|leash|large|size|water|повод|больш|размер|мис)|(?:suur|large|big|больш\w*).*(?:koer|dog|собак)|(?:rihm|lead|leash|повод).*(?:koer|dog|собак)",
    "medical_food": r"rased\w*|pregnan\w*|беремен\w*|diabe\w*|диабет\w*",
    "ingredient_details": r"\b(?:egg|soy|sesame|mustard|sulphites?|lupin)\b|munasisald|(?:kas|on).*\bmuna\b|soja|seesam|sinep|sulfit|lupiin|арахис|яйц\w*|со[яю]|кунжут|горчиц|сульфит|люпин|eraldi\s+(?:fritüür|vahend|töövahend)|separate\s+(?:fryer|utensil)|отдельн\w*\s+(?:фритюр|прибор)",
    "privacy_help": r"(?:kõne|vestlus).*(?:salvesta|salvestus)|andme\w*.*(?:säilita|kustuta|koopia|teenusepakku|reklaam)|privaatsus|andmekaitse|\b(?:recorded|recording|retention|privacy|my data|data deletion|data kept|marketing)\b|(?:звонок|разговор).*(?:запис|хран)|персональн\w*\s+данн|мо[ий]\w*\s+данн|хранят.*данн|конфиденц|защит\w*\s+данн|номер.*реклам",
    "payment_help": r"kaardiga|sularaha|telefoniga.*maks|arve.*(?:eraldi|ettevõt)|ettevõt.*arve|kinkekaart|jootraha|\b(?:pay by card|cash|pay with my phone|split the bill|invoice|gift voucher|tip by card)\b|оплат.*(?:карт|налич|телефон|сертификат)|принимаете налич|разделить сч[её]т|сч[её]т на компанию|чаевые карт",
    "menu_formats": r"punktkir|suure kirjaga|large print|braille|шрифт\w*\s+Брайля|крупным шрифтом",
    "children_services": r"lapsehoid|mähkim|lapsevank|istmekõrgendus|beebipüree|beebitoi|\bimetam|\b(?:babysitter|childcare|stroller|booster seats?|baby pur[ée]+e?|baby food|baby changing|breastfeeding)\b|нян\w*|пеленал\w*|детск\w*\s+коляск|коляск.*(?:стол|оставить)|сиденья-подушки|пюре.*малыш|детск\w*\s+питани|кормлени\w*\s+грудью",
    "seating_help": r"ooteala|waiting area|где.*подождать|aknaal|lauanumbr|kindla.*laua|mängunur\w*\s+(?:kõrvale|kõrval)|(?:laud|lauad|lauda).*(?:kokku lük|eraldi|mängunur)|(?:table|tables).*(?:window|number|join|play corner)|(?:sit|seating).*(?:beside|near).*play corner|(?:window|particular|specific).*table|(?:join|separate).*tables|столик.*(?:окна|номер|рядом с игров)|стол\w*.*(?:сдвинуть|отдельн)|(?:сдвинуть|выбрать конкретн).*стол",
    "amenities_help": r"\bwi[ -]?fi\b|garderoob|pagas|kohvri|tualet|suitset|veip|riietus|elav muusika|spordiülek|konditsioneer|pleed|pildista|sülearvut|\b(?:charge my phone|cloakroom|suitcase|toilet|smoking|vaping|dress code|live music|sports|air conditioned|blankets|photos|laptop)\b|гардероб|чемодан|туалет|курени|вейп|дресс-код|жив\w*\s+музык|спортивн\w*\s+трансля|кондиционер|плед|фотограф|ноутбук|зарядить телефон",
    "food_modifications": r"vürtsik|ilma.*sool|kastm\w*.*eraldi|(?:kartul|lisand).*(?:vaheta|asenda)|portsjon|\b(?:spicy|without added salt|sauce.*separately|swap potatoes|raw or cooked|doneness|portion|share a dish|calorie)\b|острая|без добавления соли|соус отдельно|заменить.*(?:картоф|гарнир)|сырой или приготовлен|прожарк|порци|разделить блюдо|калорийн",
    "complaints_help": r"kaebus|kaebuse|kaotatud|vale roog|(?:raha tagasi|hüvitis).*(?:teenindus|halb)|\b(?:complain|complaint|lost jacket|lost property|wrong dish|poor service)\b|пожаловаться|жалоб|потерянн|не то блюдо|плохое обслуживан",
    "language_help": r"mis keeltes|millist\w* keel\w*.*(?:rääg|mõist)|which languages|what languages|какие языки|на каких языках",
    "booking_window": r"kui kaugele.*broneer|how far ahead.*book|насколько заранее.*брон",
}
GENERAL_TOPICS = tuple(PATTERNS) + ("child_allergens",)
CONFLICTS = {
    "payment_tax": {"allergens", "price", "menu"},
    "family_certification": {"family", "family_details", "menu"},
    "play_hours": {"family", "family_details", "hours", "children"},
    "facility_safety": {"family", "family_details", "allergens", "children", "menu"},
    "food_stock": {"menu"},
    "family_serving": {"children", "menu"}, "last_order_help": {"staff", "kitchen"},
    "dietary_certification": {"menu", "allergens"}, "access_support": {"menu"},
    "food_order_help": {"menu", "staff", "extras"}, "delivery_help": {"price", "staff", "children_services"},
    "drinks_help": {"menu", "extras"}, "event_details": {"menu", "children", "groups", "price"},
    "contact_help": {"menu", "location"},
    "other_pets": {"pets"}, "pet_details": {"pets"},
    "child_allergens": {"family", "family_details", "children", "menu", "allergens"},
    "ingredient_details": {"menu", "allergens", "kitchen"}, "medical_food": {"menu", "allergens", "children"},
    "payment_help": {"groups", "children", "price"}, "payment_secret": {"groups", "staff"},
    "privacy_help": {"policies", "location"}, "menu_formats": {"menu", "children"},
    "children_services": {"family", "family_details", "children", "location", "accessibility"},
    "seating_help": {"family", "family_details", "children", "location"},
    "amenities_help": {"location", "policies"}, "food_modifications": {"children", "menu"},
    "complaints_help": {"menu", "staff"},
}
CHILD = re.compile(r"laste\w*|lapse\w*|\b(?:child(?:ren)?|kids?)\b|детск\w*|реб[её]н\w*")
DIET = re.compile(r"allerg|allergeen|glut|laktoos|vegan|аллерг|глют|лактоз|веган|milk allergy|piimaallerg")
FOOD = re.compile(r"\b(?:food|foods|dish|meal|eat|salmon|soup|risotto)\b|toit|toidu|roog|roa\b|lõhe|supp|risot|блюд|ед[ауы]\b|питани|лосос|суп")


def _read_key(text: str) -> str:
    return " ".join(text.casefold().replace("’", "'").split()).strip(" .!?;")


# Whole reviewed interludes preserve booking fields. A loose topic match alone
# never authorizes retaining fields across a mixed correction or action clause.
def _load_read_forms() -> frozenset[str]:
    path = Path(__file__).resolve().parents[1] / "data/demo/restaurant-service-questions.json"
    raw = cast(object, json.loads(path.read_text(encoding="utf-8")))
    if not isinstance(raw, dict):
        raise ValueError("Invalid reviewed restaurant service questions")
    data = cast(dict[str, object], raw)
    raw_questions = data.get("questions")
    if data.get("schema_version") != 1 or not isinstance(raw_questions, list):
        raise ValueError("Invalid reviewed restaurant service questions")
    questions = cast(list[object], raw_questions)
    if not questions or not all(isinstance(question, str) and question.strip() for question in questions):
        raise ValueError("Invalid reviewed restaurant service questions")
    return frozenset(_read_key(question) for question in questions if isinstance(question, str))


READ_FORMS = _load_read_forms()


def general_read_question(text: str) -> bool:
    return _read_key(text) in READ_FORMS


def general_topic(text: str) -> str | None:
    text = text.casefold()
    # Urgent help and payment secrets precede ordinary venue questions.
    for topic in ("emergency_help", "payment_secret"):
        if re.search(PATTERNS[topic], text):
            return topic
    if re.search(PATTERNS["facility_safety"], text):
        return "facility_safety"
    if CHILD.search(text) and DIET.search(text):
        return "child_allergens"
    for topic, pattern in PATTERNS.items():
        if topic == "medical_food" and not FOOD.search(text):
            continue
        if re.search(pattern, text, re.IGNORECASE):
            return topic
    return None


def general_reply(data: Mapping[str, object], topic: str, language: str) -> str:
    index = LANGUAGES.index(language)
    if topic == "emergency_help":
        return (
            "Kui elu või tervis on ohus või vajate kiiret abi, helistage kohe 112 ja kutsuge lähedal olev töötaja appi. Ma ei saa teie eest hädaabikõnet teha.",
            "If life or health is in danger, or you need urgent help, call 112 immediately and alert a nearby member of staff. I can't make the emergency call for you.",
            "Если жизнь или здоровье в опасности либо нужна срочная помощь, сразу позвоните 112 и позовите ближайшего сотрудника. Я не могу вызвать экстренную помощь за вас.",
        )[index]
    if topic == "payment_secret":
        return (
            "Palun ärge öelge pangakaardi numbrit ega turvakoodi. Ma ei võta makseid vastu.",
            "Please don't share your card number or security code. I don't take payments.",
            "Не называйте номер карты или защитный код. Я не принимаю платежи.",
        )[index]
    if topic == "language_help":
        return (
            "Aitan eesti, inglise ja vene keeles. Palun kasutage üht neist keeltest.",
            "I can help in Estonian, English and Russian. Please use one of those languages.",
            "Я могу помочь на эстонском, английском и русском. Используйте один из этих языков.",
        )[index]
    if topic == "food_order_help":
        return (
            "Saan aidata lauabroneeringuga, kuid toidutellimust ma vastu ei võta. Palun pöörduge restorani töötaja poole.",
            "I can help with a table booking, but I can't place a food order. Please contact the restaurant team.",
            "Я могу помочь с бронью столика, но не принимаю заказы еды. Обратитесь к сотруднику ресторана.",
        )[index]
    if topic == "booking_window":
        days = data["advance_days"]
        return (
            f"Saadavust saab kontrollida kuni {days} päeva ette. Laud tuleb valitud aja jaoks eraldi kontrollida.",
            f"I can check dates up to {days} days ahead. A table still needs to be checked for your chosen time.",
            f"Можно проверять даты на {days} дней вперёд. Наличие столика на выбранное время нужно проверить отдельно.",
        )[index]
    scope = SCOPES[topic][index]
    reply = (
        f"Mul ei ole kinnitatud infot {scope}. Palun täpsustage seda restorani töötajaga.",
        f"I don't have confirmed information about {scope}. Please check with the restaurant team.",
        f"У меня нет подтверждённой информации {scope}. Уточните это у сотрудника ресторана.",
    )[index]
    if topic in {"child_allergens", "ingredient_details"}:
        notice = data.get("allergy_notice")
        configured = cast(Mapping[str, object], notice).get(language) if isinstance(notice, Mapping) else None
        reply += " " + (configured if isinstance(configured, str) and configured else (
            "Koostis ja võimalik ristsaastumine tuleb köögiga kinnitada. Ma ei saa allergiaohutust garanteerida.",
            "Check ingredients and possible cross-contact with the kitchen. I can't guarantee allergy safety.",
            "Уточните состав и возможность перекрёстного контакта у кухни. Я не могу гарантировать безопасность при аллергии.",
        )[index])
    if topic == "medical_food":
        reply += " " + (
            "Toidu individuaalse sobivuse kohta palun küsige oma tervishoiutöötajalt.",
            "Please ask your healthcare professional about the food's suitability for your individual needs.",
            "Индивидуальную пригодность еды обсудите со своим медицинским специалистом.",
        )[index]
    return reply
