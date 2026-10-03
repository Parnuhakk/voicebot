"""English spoken times and remembered AM/PM clarification, never consent."""

from __future__ import annotations

import re
from dataclasses import dataclass

HOURS = {
    word: number for number, word in enumerate((
        "zero", "one", "two", "three", "four", "five", "six", "seven",
        "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
        "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
        "twenty one", "twenty two", "twenty three",
    ))
}
HOUR_WORDS = "|".join(
    re.escape(word).replace(r"\ ", "[ -]")
    for word in sorted(HOURS, key=len, reverse=True)
)
VALUE = re.compile(
    r"(?<!\w)(?P<at>at\s+)?(?P<hour>-?\d{1,3}|" + HOUR_WORDS + r")"
    + r"(?P<minutes>[:.]\d+)?(?P<oclock>\s+o\s*['’]?\s*clock)?"
    + r"(?:\s*(?P<suffix>[ap]\.?m\.?))?(?!\w|[:.]\d)"
)
PERIOD = re.compile(r"\b(?:[ap]\.?m\.?|morning|afternoon|evening|night|noon|midnight)\b")
DAYPART_AFTER = re.compile(r"\s+(?:(?:in|at)(?:\s+the)?\s+)?(?:morning|afternoon|evening|night|noon|midnight)\b")
COMPOUND_TAIL = re.compile(r"[ -]+(?:one|two|three|four|five|six|seven|eight|nine|\d+)\b")


@dataclass(frozen=True)
class TimeResolution:
    value: str | None
    candidates: tuple[str, ...]
    issue: str | None
    remaining_text: str


def resolve_english_time(
    text: str, *, candidates: tuple[str, ...] = (), expected_time: bool = False
) -> TimeResolution | None:
    """Use explicit time wording; a bare count is a time only after a time question."""
    text = text.casefold().replace("’", "'")
    periods = {match[0].replace(".", "") for match in PERIOD.finditer(text)}
    am = bool(periods & {"am", "morning", "midnight"})
    pm = bool(periods & {"pm", "afternoon", "evening", "noon"})
    values: list[tuple[int, int, bool]] = []
    spans: list[tuple[int, int]] = []
    invalid = (am and pm) or ("night" in periods and len(periods) > 1)
    for match in VALUE.finditer(text):
        standalone = text.strip(" .!?") == match[0].strip(" .!?")
        if not (
            match["at"] or match["minutes"] or match["oclock"] or match["suffix"]
            or DAYPART_AFTER.match(text[match.end():])
            or (expected_time and standalone)
        ):
            continue
        raw = match["hour"]
        hour = int(raw) if raw.lstrip("-").isdecimal() else HOURS[raw.replace("-", " ")]
        minute = int(match["minutes"][1:]) if match["minutes"] else 0
        spans.append(match.span())
        # Alternative/negated times cannot turn into one selected reservation.
        if re.search(r"\b(?:not|or|and|to|through)\s*$", text[:match.start()]) or re.match(r"\s*(?:or|and|to|through|[-–])\s+", text[match.end():]):
            invalid = True
        compound = COMPOUND_TAIL.match(text[match.end():])
        if compound:
            invalid = True
            spans.append((match.end(), match.end() + compound.end()))
        if not 0 <= hour <= 23 or minute > 59 or (match["minutes"] and len(match["minutes"]) != 3) or ((am or pm) and not 1 <= hour <= 12):
            invalid = True
            continue
        values.append((hour, minute, bool(match["minutes"] and raw.startswith("0"))))
    if not values and not spans:
        negated = any(
            re.search(r"\bnot(?:\s+(?:in|the|at))*\s*$", text[:match.start()])
            for match in PERIOD.finditer(text)
        )
        if periods and (invalid or negated):
            return TimeResolution(None, candidates, "time_ambiguous", text)
        if periods == {"noon"}:
            return TimeResolution("12:00", (), None, "")
        if periods == {"midnight"}:
            return TimeResolution("00:00", (), None, "")
        if not candidates or not periods:
            return None
        # A daypart answer resolves the previous exact hour, never a new one.
        if invalid or len(candidates) != 2:
            return TimeResolution(None, (), "time_ambiguous", text)
        if "night" in periods:
            am, pm = int(candidates[0][:2]) < 6, int(candidates[0][:2]) >= 6
        selected = candidates[0] if am else candidates[1] if pm else None
        return TimeResolution(selected, () if selected else candidates, None if selected else "time_ambiguous", "")
    remaining = list(text)
    for left, right in spans:
        remaining[left:right] = " " * (right - left)
    remainder = "".join(remaining)
    if invalid or not values or len(set(values)) != 1:
        return TimeResolution(None, (), "time_invalid" if invalid else "time_ambiguous", remainder)
    hour, minute, explicit_24h = values[0]
    if "night" in periods:
        am, pm = hour < 6 or hour == 12, 6 <= hour < 12
    if ("noon" in periods or "midnight" in periods) and (hour != 12 or minute != 0):
        return TimeResolution(None, (), "time_invalid", remainder)
    if am or pm:
        hour = hour % 12 + (12 if pm else 0)
    elif 1 <= hour <= 12 and not explicit_24h:
        options = (f"{hour % 12:02d}:{minute:02d}", f"{hour % 12 + 12:02d}:{minute:02d}")
        return TimeResolution(None, options, "time_ambiguous", remainder)
    return TimeResolution(f"{hour:02d}:{minute:02d}", (), None, remainder)
