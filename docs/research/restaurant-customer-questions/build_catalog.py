"""Build review artifacts from explicit trilingual research rows, never runtime knowledge."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from app.restaurant_answers import format_schedule  # noqa: E402
from app.restaurant_data import load_restaurant_data  # noqa: E402

LANGUAGES = ("et", "en", "ru")
UNKNOWN = {
    "et": "Mul ei ole kinnitatud infot {scope}. Palun täpsustage seda restorani töötajaga.",
    "en": "I don't have confirmed information about {scope}. Please check with the restaurant team.",
    "ru": "У меня нет подтверждённой информации {scope}. Уточните это у сотрудника ресторана.",
}
ALLERGY = {
    "et": "Koostis ja võimalik ristsaastumine tuleb köögiga kinnitada. Ma ei saa allergiaohutust garanteerida.",
    "en": "Check ingredients and possible cross-contact with the kitchen. I can't guarantee allergy safety.",
    "ru": "Уточните состав и возможность перекрёстного контакта у кухни. Я не могу гарантировать безопасность при аллергии.",
}
MEDICAL = {
    "et": "Toidu individuaalse sobivuse kohta palun küsige oma tervishoiutöötajalt.",
    "en": "Please ask your healthcare professional about the food's suitability for your individual needs.",
    "ru": "Индивидуальную пригодность еды обсудите со своим медицинским специалистом.",
}
FAMILY_PREFIX = {
    "children_menu": {"et": "Lastemenüü on olemas.", "en": "A children's menu is available.", "ru": "Детское меню есть."},
    "play": {"et": "Mängunurk on olemas.", "en": "A play corner is available.", "ru": "Игровой уголок есть."},
    "drawing": {"et": "Joonistamisvõimalus on olemas.", "en": "Drawing activities are available.", "ru": "Возможность порисовать есть."},
    "toy": {"et": "Mänguasjad on olemas.", "en": "Toys are available.", "ru": "Игрушки есть."},
}
DESIGN_SOURCES = {
    "family": ["tourism-family", "family-label", "operator-family"],
    "accessibility": ["visit-access"], "allergens": ["pta-food", "uk-allergy"],
    "menu": ["operator-faq"], "drinks": ["operator-faq"],
    "privacy": ["aki-calls"], "service": ["operator-faq", "ttja-disputes"],
    "payment": ["operator-faq"], "events": ["operator-faq"],
    "seating": ["operator-faq", "family-label"],
    "location": ["visit-access", "family-label"],
}


def rows(path: Path, width: int):
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        values = [part.strip() for part in line.split("|")]
        if len(values) != width or not all(values):
            raise ValueError(f"{path.name}:{line_number}: expected {width} nonempty columns")
        yield values


def unknown_entries():
    for path in sorted((HERE / "drafts").glob("*.txt")):
        if path.stem == "reviewed":
            continue
        category = path.stem
        for row in rows(path, 8):
            identifier, owner_field = row[:2]
            question = dict(zip(LANGUAGES, row[2:5]))
            answer = {language: UNKNOWN[language].format(scope=scope)
                      for language, scope in zip(LANGUAGES, row[5:8])}
            fact_sources = []
            if category == "family":
                stem = owner_field.split(".", 1)[1]
                for key, prefix in FAMILY_PREFIX.items():
                    if stem.startswith(key):
                        answer = {language: prefix[language] + " " + answer[language]
                                  for language in LANGUAGES}
                        fact_sources.append("owner-family")
                        break
            if category == "allergens" and identifier not in {"halal", "kosher", "vegan-child"}:
                for language in LANGUAGES:
                    answer[language] += " " + (MEDICAL if identifier in {"pregnancy", "diabetes"} else ALLERGY)[language]
                fact_sources.append("profile")
            yield {
                "id": category + "." + identifier, "category": category,
                "status": "staff_confirmation", "risk": "high" if category in {"allergens", "privacy"} else "ordinary",
                "question": question, "answer": answer, "required_owner_fields": [owner_field],
                "fact_sources": fact_sources, "design_sources": DESIGN_SOURCES.get(category, []),
                "delivery": "research_proposal",
                "action_boundary": "No staff request, booking, payment or transfer is performed by this answer.",
            }


def reviewed_entries():
    for row in rows(HERE / "drafts/reviewed.txt", 9):
        category, identifier, source = row[:3]
        status = {"owner-family": "owner_confirmed", "profile": "demo_profile", "runtime": "workflow_policy", "112": "urgent_guidance"}[source]
        yield {
            "id": category + "." + identifier, "category": category,
            "status": status, "risk": "urgent" if source == "112" else "high" if category in {"allergens", "payment"} else "ordinary",
            "question": dict(zip(LANGUAGES, row[3:6])), "answer": dict(zip(LANGUAGES, row[6:9])),
            "required_owner_fields": [], "fact_sources": [source], "design_sources": [],
            "delivery": "research_proposal",
            "action_boundary": "Workflow explanations are not evidence that an action has been completed.",
        }


def hours_entries():
    profile = load_restaurant_data(ROOT / "data/demo/restaurant-demo.json")
    days = [
        ("monday", "esmaspäeval", "Monday", "в понедельник"),
        ("tuesday", "teisipäeval", "Tuesday", "во вторник"),
        ("wednesday", "kolmapäeval", "Wednesday", "в среду"),
        ("thursday", "neljapäeval", "Thursday", "в четверг"),
        ("friday", "reedel", "Friday", "в пятницу"),
        ("saturday", "laupäeval", "Saturday", "в субботу"),
        ("sunday", "pühapäeval", "Sunday", "в воскресенье"),
    ]
    cases = [("general", ["Mis on teie lahtiolekuajad?", "What are your opening hours?", "Какие у вас часы работы?"], None, False)]
    for index, (key, estonian, english, russian) in enumerate(days):
        cases.append((key, [f"Mis kell olete {estonian} avatud?", f"What are your opening hours on {english}?", f"Во сколько вы открыты {russian}?"], (index,), False))
    cases.extend([
        ("weekend", ["Mis kell olete nädalavahetusel avatud?", "What are your weekend opening hours?", "Какие часы работы в выходные?"], (5, 6), False),
        ("weekdays", ["Mis kell olete tööpäevadel avatud?", "What are your weekday opening hours?", "Какие часы работы в будни?"], (0, 1, 2, 3, 4), False),
        ("kitchen", ["Mis on köögi lahtiolekuajad?", "What are the kitchen hours?", "Какие часы работы кухни?"], None, True),
        ("kitchen-friday", ["Mis kell köök reedeti sulgub?", "When does the kitchen close on Friday?", "Когда кухня закрывается в пятницу?"], (4,), True),
    ])
    for identifier, questions, indices, kitchen in cases:
        answers = {}
        for language in LANGUAGES:
            prefix = {"et": "Demo köök: " if kitchen else "Demo lahtiolekuajad: ", "en": "Demo kitchen hours: " if kitchen else "Demo opening hours: ", "ru": "Часы работы кухни в демоверсии: " if kitchen else "Часы работы в демоверсии: "}[language]
            answers[language] = prefix + format_schedule(profile, language, days=indices, kitchen=kitchen) + "."
        yield {"id": "hours." + identifier, "category": "hours", "status": "demo_profile", "risk": "ordinary",
               "question": dict(zip(LANGUAGES, questions)), "answer": answers, "required_owner_fields": [],
               "fact_sources": ["profile"], "design_sources": [], "delivery": "research_proposal",
               "action_boundary": "Configured hours do not establish live availability or holiday event arrangements."}


def build() -> dict:
    entries = list(unknown_entries()) + list(reviewed_entries()) + list(hours_entries())
    identifiers = [entry["id"] for entry in entries]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Duplicate question concept ID")
    questions = [(lang, entry["question"][lang]) for entry in entries for lang in LANGUAGES]
    if len(questions) != len(set(questions)):
        raise ValueError("Duplicate question within a language")
    sources = {item["id"] for item in json.loads((HERE / "sources.json").read_text(encoding="utf-8"))["sources"]}
    for entry in entries:
        if set(entry["question"]) != set(LANGUAGES) or set(entry["answer"]) != set(LANGUAGES):
            raise ValueError("Missing language")
        if (set(entry["fact_sources"]) | set(entry["design_sources"])) - sources:
            raise ValueError("Unknown source")
        if bool(entry["required_owner_fields"]) != (entry["status"] == "staff_confirmation"):
            raise ValueError("Unknown answer without owner field")
    return {
        "schema_version": 1, "review_date": "2026-10-04", "languages": list(LANGUAGES),
        "scope": "Synthetic restaurant research. Answers are reviewed proposals; see separate runtime observations before treating them as implemented.",
        "counts": {"concepts": len(entries), "language_pairs": len(entries) * len(LANGUAGES),
                   "categories": dict(sorted(Counter(item["category"] for item in entries).items())),
                   "statuses": dict(sorted(Counter(item["status"] for item in entries).items()))},
        "entries": sorted(entries, key=lambda item: (item["category"], item["id"])),
    }


def write() -> None:
    catalog = build()
    (HERE / "questions.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    owner_fields = [{"field": field, "category": entry["category"], "question": entry["question"],
                     "risk": entry["risk"], "value": None, "confirmed_by": None,
                     "confirmed_at": None, "evidence": None}
                    for entry in catalog["entries"] for field in entry["required_owner_fields"]]
    (HERE / "owner-fields.json").write_text(json.dumps({
        "scope": "Owner intake draft. Null means unconfirmed, never unavailable. This file is not loaded by the running bot.",
        "confirmed_family_facilities": dict.fromkeys(("drawing", "toys", "play_corner", "children_menu"), True),
        "fields": owner_fields,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (HERE / "questions.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["id", "category", "status", "risk", "language", "question", "reviewed_answer", "required_owner_fields", "fact_sources", "design_sources", "delivery"])
        for entry in catalog["entries"]:
            for language in LANGUAGES:
                writer.writerow([entry["id"], entry["category"], entry["status"], entry["risk"], language,
                                 entry["question"][language], entry["answer"][language],
                                 "; ".join(entry["required_owner_fields"]), "; ".join(entry["fact_sources"]),
                                 "; ".join(entry["design_sources"]), entry["delivery"]])
    template = (HERE / "review-template.html").read_text(encoding="utf-8")
    observations_path = HERE / "observations.json"
    observations = json.loads(observations_path.read_text(encoding="utf-8")) if observations_path.exists() else {}
    sources = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
    for placeholder, value in (("__CATALOG__", catalog), ("__OBSERVATIONS__", observations), ("__SOURCES__", sources)):
        template = template.replace(placeholder, json.dumps(value, ensure_ascii=False).replace("<", "\\u003c"))
    template = template.replace("__UNKNOWN_COUNT__", str(catalog["counts"]["statuses"]["staff_confirmation"]))
    (HERE / "review.html").write_text(template, encoding="utf-8")
    print(json.dumps(catalog["counts"], ensure_ascii=False))


if __name__ == "__main__":
    write()
