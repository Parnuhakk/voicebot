"""Repair close calendar words in date context, leaving caller text untouched."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache

TOKEN = re.compile(r"\d+(?:st|nd|rd|th)?|[^\W\d_]+", re.UNICODE)
JOINERS = {"of", "the", "day", "числа"}
GUEST = re.compile(r"\s+(?:people|guests?|persons?|inimes\w*|külalis\w*|гост\w*|человек\w*)\b")
DATE_CONTEXT = re.compile(
    r"\b(?:table|reserv\w*|book\w*|lau(?:d|da|a\w*)|broneer\w*|столик\w*|брон\w*|"
    + r"open|lahti|avatud|открыт\w*|kuupäev\w*)\b"
)

# These observed spellings are farther from the inflected dictionary than a
# routine edit. They still need a date answer or an adjacent day selector.
MONTH_ALIASES = {
    "oktobte": "oktoober", "oktober": "oktoober", "oktobr": "oktoober",
}
DAY_ALIASES = {"forth": "fourth"}
COMPOUND_NOUN = re.compile(r"(?:lill|fest|festival|ский|ская|ское|ские)$")
YEAR_WORD = re.compile(r"(?:thousand(?:th)?|hundred|year|tuhat|tuhande\w*|sada|saja|aasta\w*|тысяч\w*|сто|ста|года?|году)\Z")
CLOCK_WORD = re.compile(
    r"(?:kell|tund\w*|minut\w*|hommik\w*|õhtu\w*|öö\w*|lõuna\w*|"
    + r"clock|oclock|morning|afternoon|evening|night|hours?|minutes?|"
    + r"вечер\w*|утр\w*|ноч\w*|дн[её]м|час\w*|минут\w*)\Z"
)


def _fold(word: str) -> str:
    return "".join(
        letter for letter in unicodedata.normalize("NFKD", word.casefold())
        if not unicodedata.combining(letter)
    )


def _distance(left: str, right: str, limit: int) -> int:
    """Bounded edit distance, counting adjacent transposed letters as one edit."""
    if abs(len(left) - len(right)) > limit:
        return limit + 1
    previous = list(range(len(right) + 1))
    before_previous = previous
    for row, letter in enumerate(left, 1):
        current = [row] + [limit + 1] * len(right)
        for column in range(max(1, row - limit), min(len(right), row + limit) + 1):
            other = right[column - 1]
            value = min(
                current[column - 1] + 1, previous[column] + 1,
                previous[column - 1] + (letter != other),
            )
            if row > 1 and column > 1 and letter == right[column - 2] and left[row - 2] == other:
                value = min(value, before_previous[column - 2] + 1)
            current[column] = value
        if min(current) > limit:
            return limit + 1
        before_previous, previous = previous, current
    return previous[-1]


@dataclass(frozen=True)
class CalendarText:
    text: str
    ambiguous_spans: tuple[tuple[int, int], ...] = ()


class CalendarSpelling:
    def __init__(
        self, months: dict[str, int], days: dict[str, int],
        relative: dict[str, int], weekdays: dict[str, int],
        *, protected: tuple[re.Pattern[str], ...] = (),
    ) -> None:
        self.forms: dict[str, dict[str, int]] = {"month": months, "day": days, "relative": relative, "weekday": weekdays}
        self.protected: tuple[re.Pattern[str], ...] = protected
        self.indices: dict[str, dict[int, list[tuple[str, str, int]]]] = {}
        for kind, forms in self.forms.items():
            buckets: dict[int, list[tuple[str, str, int]]] = {}
            for word, value in forms.items():
                if len(word) >= (3 if kind == "month" else 4) and " " not in word and "-" not in word:
                    folded = _fold(word)
                    buckets.setdefault(len(folded), []).append((folded, word, value))
            self.indices[kind] = buckets

    @lru_cache(maxsize=2048)
    def _closest(self, word: str, kind: str) -> tuple[str | None, bool]:
        if word in self.forms[kind] or not word.isalpha() or not 4 <= len(word) <= 32:
            return None, False
        if kind == "month" and COMPOUND_NOUN.search(word):
            return None, False
        aliases = MONTH_ALIASES if kind == "month" else DAY_ALIASES if kind == "day" else {}
        if word in aliases:
            return aliases[word], False
        folded = _fold(word)
        limit = 2 if len(folded) >= 6 else 1
        best = limit + 1
        selections: dict[int, str] = {}
        for length in range(len(folded) - limit, len(folded) + limit + 1):
            for candidate, canonical, value in self.indices[kind].get(length, ()):
                distance = _distance(folded, candidate, min(limit, best))
                if distance < best:
                    best, selections = distance, {value: canonical}
                elif distance == best and distance <= limit:
                    _ = selections.setdefault(value, canonical)
        if best > limit:
            return None, False
        return (next(iter(selections.values())), False) if len(selections) == 1 else (None, True)

    def normalize(self, text: str, *, date_reply: bool = False) -> CalendarText:
        tokens = list(TOKEN.finditer(text))
        if len(text) > 2000 or not tokens:
            return CalendarText(text)
        replacements: dict[int, str] = {}
        ambiguous: set[int] = set()
        protected_spans = [match.span() for pattern in self.protected for match in pattern.finditer(text)]
        protected_tokens = {
            index for index, token in enumerate(tokens)
            if DATE_CONTEXT.fullmatch(token[0]) or YEAR_WORD.fullmatch(token[0]) or CLOCK_WORD.fullmatch(token[0])
            or any(token.start() < right and token.end() > left for left, right in protected_spans)
        }

        def day(index: int) -> bool:
            if index in protected_tokens:
                return False
            word = tokens[index][0]
            numeric = re.fullmatch(r"\d{1,2}(?:st|nd|rd|th)?", word)
            return bool(numeric or word in self.forms["day"] or any(self._closest(word, "day")))

        def neighbours(index: int) -> list[int]:
            found: list[int] = []
            for direction in (-1, 1):
                other = index + direction
                for _ in range(4):
                    if not 0 <= other < len(tokens):
                        break
                    word = tokens[other][0]
                    if direction == 1 and GUEST.match(text[tokens[other].end():]):
                        break
                    if word in JOINERS:
                        other += direction
                        continue
                    if day(other):
                        found.append(other)
                        other += direction
                        continue
                    break
            return found

        # Resolve month spelling first so two imperfect neighbouring words can
        # share the same bounded calendar context.
        months: set[int] = set()
        for index, match in enumerate(tokens):
            word = match[0]
            if index in protected_tokens:
                continue
            if word in self.forms["month"]:
                months.add(index)
                continue
            if any(word in forms for forms in self.forms.values()):
                continue
            calendar_days = neighbours(index)
            if not (calendar_days or date_reply or len(tokens) == 1):
                continue
            canonical, uncertain = self._closest(word, "month")
            if canonical:
                replacements[index] = canonical
                months.add(index)
            elif uncertain and (calendar_days or date_reply):
                ambiguous.update([index, *calendar_days])
        for index in months:
            for other in neighbours(index):
                canonical, uncertain = self._closest(tokens[other][0], "day")
                if canonical:
                    replacements[other] = canonical
                elif uncertain:
                    ambiguous.update([index, other])

        calendar_context = date_reply or len(tokens) == 1 or bool(DATE_CONTEXT.search(text))
        if calendar_context:
            for index, match in enumerate(tokens):
                word = match[0]
                if index in protected_tokens or index in replacements or index in months or word in self.forms["day"]:
                    continue
                if any(word in forms for forms in self.forms.values()):
                    continue
                for kind in ("relative", "weekday", "day"):
                    if kind == "day" and not (date_reply and len(tokens) == 1):
                        continue
                    if not date_reply and len(tokens) != 1 and len(word) < 6:
                        continue
                    canonical, uncertain = self._closest(word, kind)
                    if canonical:
                        replacements[index] = canonical
                        break
                    if uncertain and date_reply:
                        ambiguous.add(index)
                        break

        # Masking positions belong to the normalized parsing copy. The HTTP
        # recognition result and native caller messages keep the original words.
        pieces: list[str] = []
        spans: list[tuple[int, int]] = []
        cursor, size = 0, 0
        for index, match in enumerate(tokens):
            gap = text[cursor:match.start()]
            replacement = replacements.get(index, match[0])
            pieces.extend((gap, replacement))
            size += len(gap)
            if index in ambiguous:
                spans.append((size, size + len(replacement)))
            size += len(replacement)
            cursor = match.end()
        pieces.append(text[cursor:])
        return CalendarText("".join(pieces), tuple(spans))
