"""Static spelling vocabulary, never a desired caller answer or private history."""


ENGLISH_RESTAURANT_VOCABULARY = (
    "Meretuule Kitchen, restaurant, opening hours, table reservation, party size, "
    "menu, vegetarian, vegan, gluten-free, dietary requirements, allergens, "
    "cross-contact, takeaway, takeout, collection, delivery."
)


def recognition_prompt(language, business):
    return ENGLISH_RESTAURANT_VOCABULARY if language == "en" and business == "restaurant" else None
