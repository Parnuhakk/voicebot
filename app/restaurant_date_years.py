"""Explicit spoken years; neither omitted centuries nor numeric typos are guessed."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .restaurant_date_spelling import _distance

THOUSAND = re.compile(
    r"(?P<count>one|two|three|four|five|six|seven|eight|nine|üks|ühe|kaks|kahe|kolm|kolme|"
    + r"neli|nelja|viis|viie|kuus|kuue|seitse|seitsme|kaheksa|üheksa|"
    + r"одна|одной|две|двух|три|трех|трёх|четыре|четырех|четырёх|пять|пяти|"
    + r"шесть|шести|семь|семи|восемь|восьми|девять|девяти)\s*"
    + r"(?:thousand(?:th)?|tuhat|tuhande(?:s)?|тысяч[аиуе]*)\b(?:\s+and\b)?"
)
CENTURY = re.compile(r"(?P<count>nineteen|twenty)\b")
MARKER = re.compile(r"\s+(?:aasta(?:l|ks)?|года?|году|year)\b")
WORD = re.compile(r"\d+|[^\W\d_]+(?:-[^\W\d_]+)*", re.UNICODE)
SEPARATOR = re.compile(
    r"(?:at|kell|в|for|для|на|please|palun|aasta\w*|года?|году|year)\b"
)


@dataclass(frozen=True)
class SpokenYear:
    value: int | None
    end: int
    issue: str | None = None


class SpokenYears:
    def __init__(self, days: dict[str, int], *, guest_noun: re.Pattern[str]) -> None:
        self.guest_noun = guest_noun
        self.numbers: dict[str, int] = {
            word: value for word, value in days.items() if 0 <= value <= 99
        }
        # Calendar day morphology stops at 39 in Estonian; years need larger tens.
        for number, cardinal, genitive in (
            (40, "nelikümmend", "neljakümne"),
            (50, "viiskümmend", "viiekümne"),
            (60, "kuuskümmend", "kuuekümne"),
            (70, "seitsekümmend", "seitsmekümne"),
            (80, "kaheksakümmend", "kaheksakümne"),
            (90, "üheksakümmend", "üheksakümne"),
        ):
            for prefix in (cardinal, genitive):
                self.numbers[prefix] = number
                for word, value in days.items():
                    if 1 <= value <= 9:
                        self.numbers[prefix + " " + word] = number + value

    def after(self, text: str) -> SpokenYear | None:
        gap = re.match(r"(?:\s*,\s*|\s+)", text)
        if not gap:
            return None
        fragment = text[gap.end() :]
        words = list(WORD.finditer(fragment))[:7]
        # Share the numeric-year guest exclusion, including compound counts.
        if any(
            " ".join(fragment[: word.end()].split()) in self.numbers
            and self.guest_noun.match(fragment[word.end() :])
            for word in words
        ):
            return None
        prefix = THOUSAND.match(fragment) or CENTURY.match(fragment)
        malformed_scale = False
        if not prefix:
            # A close but unsupported explicit scale is not an omitted year.
            # Detect only an adjacent count + one-edit English thousand word;
            # never repair it into a guessed calendar year.
            if not (
                len(words) >= 2
                and 1 <= self.numbers.get(words[0][0], 0) <= 9
                and _distance(words[1][0], "thousand", 1) <= 1
            ):
                return None
            # Consume the recognized year suffix through the same parser so
            # its numeric words cannot leak into party/time extraction.
            base, prefix_end, malformed_scale = 0, words[1].end(), True
        else:
            count = self.numbers[prefix["count"]]
            base = count * (1000 if prefix.re is THOUSAND else 100)
            prefix_end = prefix.end()
        remainder = fragment[prefix_end:]
        tokens = list(WORD.finditer(remainder))[:7]
        value, end = 0, prefix_end
        selected = False
        for index, token in enumerate(tokens):
            raw = " ".join(remainder[: token.end()].strip().split())
            candidate = int(raw) if raw.isdecimal() else self.numbers.get(raw)
            if candidate is not None and 0 <= candidate <= 99:
                value, end, selected = candidate, prefix_end + token.end(), True
            if index > 0 and candidate is None:
                break
        tail = fragment[end:].lstrip()
        # A truncated compound year must not silently turn into 2000/2001.
        extra_number = next(WORD.finditer(tail), None)
        unclear = malformed_scale or bool(
            extra_number
            and (
                extra_number[0] in self.numbers
                or extra_number[0] in {"hundred", "sada", "saja", "сто", "ста"}
            )
        )
        if not selected and tail and not SEPARATOR.match(tail):
            unclear = True
        if prefix and prefix.re is CENTURY and (not selected or value < 10):
            unclear = True
        marker = MARKER.match(fragment[end:])
        if marker:
            end += marker.end()
        return SpokenYear(
            None if unclear else base + value,
            gap.end() + end,
            "date_ambiguous" if unclear else None,
        )

    def before(self, text: str) -> tuple[int, SpokenYear] | None:
        for prefix in THOUSAND.finditer(text):
            candidate = self.after(" " + text[prefix.start() :])
            if (
                candidate
                and MARKER.search(text[prefix.start() :])
                and not text[prefix.start() + candidate.end - 1 :].strip(" ,.:")
            ):
                return prefix.start(), candidate
        return None
