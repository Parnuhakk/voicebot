"""Keep native acceptance on the source-language-qualified caller fixture."""

import re

from app.languages import CANCELLATIONS_RU, select_language
from tests.test_restaurant_probe import DAY, load_probe


def test_russian_probe_uses_provider_qualified_owned_cancellation():
    # The short fixture was recognized with unsupported source metadata live.
    # This authored phrase was independently recognized as ru and cancellation.
    phrase = load_probe().scenario("ru", DAY)["cancel"]
    assert phrase == (
        "Пожалуйста, отмените бронирование, которое мы только что сделали в этом звонке."
    )
    normalized = " ".join(re.sub(r"[.,!]", " ", phrase.casefold()).split())
    assert normalized in CANCELLATIONS_RU
    assert select_language(phrase, "ru", "ru") == "ru"
