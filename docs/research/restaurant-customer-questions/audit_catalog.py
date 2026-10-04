"""Observe shared reviewed replies locally; heuristic flags are not semantic scores."""

from __future__ import annotations

import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from app.booking.restaurant import RestaurantAdapter  # noqa: E402
from app.booking_response import trusted_booking_response  # noqa: E402
from app.business import restaurant_dispatcher  # noqa: E402
from app.call_factory import make_call_tools  # noqa: E402
from app.restaurant_call import COPY  # noqa: E402
from app.restaurant_data import load_restaurant_data  # noqa: E402

RELATED = {
    "hours": {"hours", "kitchen"},
    "family": {"family", "family_details", "highchair", "allergens", "children_services", "food_modifications", "payment_help", "family_serving", "family_certification", "play_hours", "facility_safety"},
    "accessibility": {"accessibility", "allergens", "staff", "parking", "menu_formats", "access_support"},
    "allergens": {"allergens", "family_details", "menu", "child_allergens", "ingredient_details", "medical_food", "dietary_certification"},
    "amenities": {"pets", "terrace", "extras", "staff", "other_pets", "pet_details", "amenities_help"},
    "drinks": {"extras", "price", "allergens", "staff", "drinks_help"},
    "events": {"groups", "staff", "price"},
    "hours-special": {"hours", "kitchen", "price", "event_details", "last_order_help"},
    "location": {"location", "parking", "staff", "price", "contact_help"},
    "menu": {"menu", "allergens", "kitchen", "price", "staff", "food_modifications", "food_order_help", "food_stock"},
    "payment": {"price", "staff", "cancellation_help", "payment_help", "payment_secret", "event_details"},
    "privacy": {"privacy_help"}, "seating": {"terrace", "duration", "groups", "late", "accessibility", "family_details", "seating_help"},
    "service": {"staff", "extras", "allergens", "complaints_help", "emergency_help", "delivery_help", "food_order_help"}, "emergency": {"emergency_help"},
}


def run(output_name: str = "observations.json") -> None:
    catalog = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    profile = load_restaurant_data(ROOT / "data/demo/restaurant-demo.json")
    observations = []
    with tempfile.TemporaryDirectory(prefix="restaurant-question-audit-") as directory:
        adapter = RestaurantAdapter(str(Path(directory) / "restaurant.db"), data=profile, allow_writes=False)
        for entry in catalog["entries"]:
            for language in catalog["languages"]:
                state = make_call_tools(restaurant_dispatcher(adapter, profile), language=language)
                state.observe_user_text(entry["question"][language], language=language)
                reply = state.guard_reply("", [])
                selection = state._restaurant_question
                topics = list(selection.topics) if selection else []
                flags = []
                if reply == COPY[language]["information_unknown"]:
                    flags.append("generic_unknown")
                if entry["category"] not in {"booking", "voice"} and topics and not set(topics).intersection(RELATED.get(entry["category"], set())):
                    flags.append("topic_needs_review")
                if entry["category"] not in {"booking", "voice"} and state.booking_inquiry:
                    flags.append("unexpected_booking_inquiry")
                if entry["risk"] == "urgent" and "112" not in reply:
                    flags.append("urgent_guidance_missing")
                if entry["id"] == "amenities.pet-other" and reply == profile["pet_policy"][language]:
                    flags.append("dog_policy_for_other_pet")
                if entry["id"].startswith("allergens.child") and any(dish["name"][language] in reply for dish in profile["menu"]):
                    flags.append("adult_menu_for_child_allergen_question")
                if state.pending or state.bookings:
                    flags.append("unexpected_proposal_or_booking")
                action = trusted_booking_response(state)
                observations.append({
                    "id": entry["id"], "language": language, "question": entry["question"][language],
                    "reply": reply, "topics": topics, "flags": flags,
                    "proposed_action": action.get("name") if action else None,
                    "inquiry_fields": sorted((state.booking_inquiry or {}).keys()),
                    "matches_reviewed_text": reply == entry["answer"][language],
                })
    result = {
        "scope": "Fresh local shared-call states; dispatch is not executed; writes disabled. No live STT/TTS/model/carrier requests.",
        "interpretation": "Text equality and related-topic flags are descriptive triage. They do not establish semantic correctness or acoustic recognition accuracy.",
        "counts": {"turns": len(observations), "exact_reviewed_text": sum(item["matches_reviewed_text"] for item in observations),
                   "flags": dict(sorted(Counter(flag for item in observations for flag in item["flags"]).items()))},
        "observations": observations,
    }
    (HERE / output_name).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"]))


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) == 2 else "observations.json")
