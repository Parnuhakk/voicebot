"""Bounded English restaurant requests and followups; never invent facts."""

import re
from datetime import datetime

from .temporal import TALLINN, interpret_temporal


def normalize_english(text):
    value = text.casefold().replace("’", "'")
    for short, long in (
        ("i'd", "i would"), ("we'd", "we would"), ("i'm", "i am"),
        ("we're", "we are"), ("you're", "you are"), ("what's", "what is"),
        ("that's", "that is"), ("don't", "do not"), ("can't", "cannot"),
    ):
        value = re.sub(r"\b" + re.escape(short) + r"\b", long, value)
    value = " ".join(re.sub(r"[.,!?…]", " ", value).split())
    for _ in range(4):
        updated = re.sub(r"^(?:um|uh|erm|well|so|hi|hello|please|excuse me|i was wondering if|i am wondering if|could you tell me|can you tell me)\s+", "", value)
        updated = re.sub(r"\s+(?:please|thanks|thank you)$", "", updated)
        if updated == value:
            break
        value = updated
    return value


DAY = r"(?:today|tomorrow|tonight|this evening|(?:on )?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?)"
TIME = rf"(?:\s+{DAY})?(?:\s+(?:at|until|after)\s+\d{{1,2}}(?::\d{{2}})?(?:\s*(?:am|pm))?)?"


def restaurant_question_ids(text, previous=()):
    """Whole utterances only: an extra command must not disappear into a FAQ."""
    if not isinstance(text, str) or not text.strip() or len(text) > 2000:
        return ()
    value = normalize_english(text)
    correction = re.fullmatch(r"(?:no )?(?:i mean|i meant|actually) (?:the |your )?(?P<topic>menu|opening hours|table reservations?|takeaway|takeout)", value)
    if correction:
        return ({"menu": "booking-046", "opening hours": "booking-103", "table reservation": "booking-104", "table reservations": "booking-104", "takeaway": "booking-102", "takeout": "booking-102"}[correction["topic"]],)
    patterns = {
        "booking-103": (
            rf"(?:are you|you are|is the restaurant) (?:still )?open{TIME}",
            rf"(?:what time|when) (?:do you|does the restaurant) (?:open|close|start serving|stop serving)(?: (?:food|dinner|lunch))?(?:\s+{DAY})?",
            r"(?:(?:what are|tell me) )?(?:your|the restaurant) (?:opening|business) hours",
        ),
        "booking-046": (
            r"(?:can i see|can you show me|do you have|have you got|where is) (?:a|the|your) menu",
            r"(?:what|which) (?:food|dishes|meals) (?:do you serve|do you have|are available)",
            r"(?:do you have|have you got|do you serve|can i get|is there|are there|what about|and) (?:any |anything )?(?:vegan|vegetarian|gluten free|gluten-free|dairy free|dairy-free|nut free|nut-free)(?: (?:food|dishes|options|meals))?",
            r"(?:i am|one of us is|my partner is) (?:vegan|vegetarian|gluten intolerant|lactose intolerant)",
            r"(?:i have|my partner has|one of us has) (?:a |an )?(?:peanut|nut|dairy|food) allergy(?: is (?:your|the) food safe)?",
            r"(?:what|which) allergens (?:are in|does) (?:your|the) food(?: contain)?",
        ),
        "booking-101": (
            r"(?:can you|could you|please)?\s*(?:tell|notify|let) (?:the|your) kitchen (?:know )?(?:about|of) (?:my|our|a) (?:peanut |nut |food )?allergy",
            r"(?:can you |could you )?(?:add|record|save|note|write down) (?:my|our|a) (?:allergy|special request)(?: (?:on|to|in) (?:my|our|the) (?:booking|reservation))?",
        ),
        "booking-102": (
            r"(?:do you (?:do|offer)|is there|what about) (?:takeaway|take away|takeout|take out|delivery|home delivery)",
            r"(?:can i|could i|can we|i would like to|we would like to|i want to) (?:order|place an order for) (?:some )?(?:food|dinner|lunch|takeaway|take away|takeout|take out|delivery)(?: (?:for|to) (?:collection|pickup|pick up|delivery|take away|takeout))?",
        ),
    }
    for identifier, alternatives in patterns.items():
        if any(re.fullmatch(pattern, value) for pattern in alternatives):
            return (identifier,)

    # Parse a table request's trailing party size/calendar separately. Using
    # arbitrary .* would incorrectly discard a second question or instruction.
    table = re.match(
        r"^(?:i would like(?: to (?:book|reserve))?|we would like(?: to (?:book|reserve))?|i want(?: to (?:book|reserve))?|can i (?:book|reserve|have|get)|could i (?:book|reserve|have|get)|can we (?:book|reserve|have|get)|could you (?:book|reserve)|can you (?:book|reserve)|book|reserve|do you have) (?:me |us )?(?:a )?table\b(?P<tail>.*)$",
        value,
    )
    if table:
        tail = table["tail"].strip()
        tail = re.sub(r"^(?:for|for a party of)\s+(?:\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)(?:\s+(?:people|guests|of us))?\b", "", tail).strip()
        if not tail or tail in {"here", "at the restaurant"}:
            return ("booking-104",)
        # Keep clock punctuation intact; normalize_english intentionally removes
        # full stops, but named dates and ordinals still parse without them.
        tail = re.sub(r"^(?:for|on)\s+", "", tail)
        temporal = interpret_temporal(tail, "en", datetime.now(TALLINN))
        if temporal.is_answer:
            return ("booking-104",)

    if previous == ("booking-103",) and re.fullmatch(rf"(?:and |what about |how about )?{DAY}", value):
        return previous
    if previous == ("booking-046",) and re.fullmatch(r"(?:and |what about |how about )?(?:for children|for kids|allergens|allergies|gluten|nuts|dairy)", value):
        return previous
    return ()


def english_evidence(text):
    """Short restaurant clauses are stronger than an erroneous ASR language tag."""
    if not isinstance(text, str) or len(text) > 2000 or re.search(r"[а-яё]", text, re.I):
        return False
    value = normalize_english(text)
    return bool(
        restaurant_question_ids(text)
        or re.search(r"\b(?:i would like|we would like|i want|we want|are you|do you|have you got|can i|can we|could you|what about|how about)\b", value)
    )
