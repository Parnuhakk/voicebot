"""Closed clock vocabulary regressions; no audio, providers or booking policy."""

import unicodedata

import pytest

from app.restaurant_times import parse_spoken_time

MINUTE_GENITIVES = (
    "nulli",
    "ühe",
    "kahe",
    "kolme",
    "nelja",
    "viie",
    "kuue",
    "seitsme",
    "kaheksa",
    "üheksa",
    "kümne",
    "üheteistkümne",
    "kaheteistkümne",
    "kolmeteistkümne",
    "neljateistkümne",
    "viieteistkümne",
    "kuueteistkümne",
    "seitsmeteistkümne",
    "kaheksateistkümne",
    "üheksateistkümne",
    "kahekümne",
    "kahekümne ühe",
    "kahekümne kahe",
    "kahekümne kolme",
    "kahekümne nelja",
    "kahekümne viie",
    "kahekümne kuue",
    "kahekümne seitsme",
    "kahekümne kaheksa",
    "kahekümne üheksa",
    "kolmekümne",
    "kolmekümne ühe",
    "kolmekümne kahe",
    "kolmekümne kolme",
    "kolmekümne nelja",
    "kolmekümne viie",
    "kolmekümne kuue",
    "kolmekümne seitsme",
    "kolmekümne kaheksa",
    "kolmekümne üheksa",
    "neljakümne",
    "neljakümne ühe",
    "neljakümne kahe",
    "neljakümne kolme",
    "neljakümne nelja",
    "neljakümne viie",
    "neljakümne kuue",
    "neljakümne seitsme",
    "neljakümne kaheksa",
    "neljakümne üheksa",
    "viiekümne",
    "viiekümne ühe",
    "viiekümne kahe",
    "viiekümne kolme",
    "viiekümne nelja",
    "viiekümne viie",
    "viiekümne kuue",
    "viiekümne seitsme",
    "viiekümne kaheksa",
    "viiekümne üheksa",
)


@pytest.mark.parametrize("ending", ["", "ks"])
@pytest.mark.parametrize("minute,word", list(enumerate(MINUTE_GENITIVES)))
def test_every_closed_inflected_minute_keeps_its_exact_value(minute, word, ending):
    selection = parse_spoken_time(f"kella kaheksateistkümne {word}{ending}")
    assert selection and selection.value == f"18:{minute:02d}"
    assert not selection.invalid and selection.candidates is None


@pytest.mark.parametrize("ending", ["", "ks"])
@pytest.mark.parametrize(
    "minute,word",
    [(minute, word) for minute, word in enumerate(MINUTE_GENITIVES) if " " in word],
)
def test_joined_inflected_compound_minutes_are_not_shortened(minute, word, ending):
    selection = parse_spoken_time(f"kella kuue {word.replace(' ', '')}{ending} õhtul")
    assert selection and selection.value == f"18:{minute:02d}"
    assert not selection.invalid and selection.candidates is None


@pytest.mark.parametrize(
    "text,expected",
    [
        ("kella kuue kolmekümneks õhtul", "18:30"),
        ("kella kaheksateistkümne kolmekümneks", "18:30"),
        ("kella kuue ja kolmekümneks õhtul", "18:30"),
        ("kuue kolmekümneks ajal õhtul", "18:30"),
        ("viie minuti üle kuue õhtul", "18:05"),
        ("kolmekümne minuti üle kuue õhtul", "18:30"),
        ("kell kuue läbi kolmekümne õhtul", "18:30"),
        ("kolmekümne minuti enne keskööd", "23:30"),
        (unicodedata.normalize("NFD", "kella kuue kolmekümneks õhtul"), "18:30"),
    ],
)
def test_inflected_minutes_share_the_existing_clock_grammar(text, expected):
    selection = parse_spoken_time(text)
    assert selection and selection.value == expected and not selection.invalid


def test_inflected_bare_clock_requires_time_context_and_preserves_ambiguity():
    assert parse_spoken_time("kuue kolmekümneks") is None
    selection = parse_spoken_time("kuue kolmekümneks", allow_bare=True)
    assert selection and selection.candidates == ("06:30", "18:30")
    assert selection.value is None and not selection.invalid
    assert parse_spoken_time("õhtul", pending=selection.candidates).value == "18:30"


@pytest.mark.parametrize("pending", [None, ("06:00", "18:00")])
@pytest.mark.parametrize(
    "text",
    [
        "kella kuue -1 õhtul",
        "kella kuue 60 õhtul",
        "kella kuue 70 õhtul",
        "kella kuue 1000 õhtul",
        "kella kuue kuuekümneks õhtul",
        "kella kuue seitsmekümne õhtul",
        "kella kuue seitsmekümneks õhtul",
        "kella kuue üheksakümne üheksaks õhtul",
        "kella kuue seitsmekümneüheksaks õhtul",
        "18:30 kolmekümneks",
        "keskpäeval kolmekümneks",
        "pool seitse kolmekümneks õhtul",
        "kella kuue kolmekümneks viieks õhtul",
        "kella kuue kolmekümneks või seitsmeks õhtul",
        "kella kaheksateistkümne kolmekümneks või üheksateistkümneks",
        "kella kuue kolmekümneks õhtul või kell seitse õhtul",
        "kella kuue kolmekümneks hommikul ja õhtul",
    ],
)
def test_invalid_minutes_tails_and_choices_never_select_an_hour_prefix(text, pending):
    selection = parse_spoken_time(text, allow_bare=True, pending=pending)
    assert selection and selection.invalid
    assert selection.value is None and selection.candidates is None


@pytest.mark.parametrize("pending", [None, ("06:00", "18:00")])
@pytest.mark.parametrize(
    "text",
    [
        "kuue 70 õhtul",
        "kaheksateistkümne 60",
        "kuue seitsmekümneks õhtul",
        "kaheksateistkümne kuuekümne",
        "kuue kolmekümneks seitsmekümneks õhtul",
    ],
)
def test_invalid_bare_minutes_are_rejected_without_reusing_a_pending_clock(
    text, pending
):
    selection = parse_spoken_time(text, allow_bare=True, pending=pending)
    assert selection and selection.invalid
    assert selection.value is None and selection.candidates is None


ALLATIVE_DINERS = (
    "ühele",
    "kahele",
    "kolmele",
    "neljale",
    "viiele",
    "kuuele",
    "seitsmele",
    "kaheksale",
    "üheksale",
    "kümnele",
    "üheteistkümnele",
    "kaheteistkümnele",
    "kolmeteistkümnele",
    "neljateistkümnele",
    "viieteistkümnele",
    "kuueteistkümnele",
    "seitsmeteistkümnele",
    "kaheksateistkümnele",
    "üheksateistkümnele",
    "kahekümnele",
)


@pytest.mark.parametrize("count", ALLATIVE_DINERS)
def test_diner_allatives_cannot_be_clocks_even_after_a_time_question(count):
    assert parse_spoken_time(count) is None
    assert parse_spoken_time(count, allow_bare=True) is None
    assert parse_spoken_time("kell " + count, allow_bare=True) is None


@pytest.mark.parametrize("count", ALLATIVE_DINERS)
def test_diner_allatives_after_a_clock_cannot_be_minutes(count):
    selection = parse_spoken_time("kell 14 " + count)
    assert selection and selection.value == "14:00" and not selection.invalid


@pytest.mark.parametrize(
    "text,value,candidates",
    [
        ("kuueks", None, ("06:00", "18:00")),
        ("kaheksateistkümneks", "18:00", None),
        ("at six thirty PM", "18:30", None),
        ("at six oh five PM", "18:05", None),
        ("в восемнадцать тридцать", "18:30", None),
        ("без двадцати пяти минут семь вечера", "18:35", None),
    ],
)
def test_clock_translatives_and_english_russian_controls_survive(
    text, value, candidates
):
    selection = parse_spoken_time(text, allow_bare=True)
    assert selection and (selection.value, selection.candidates) == (value, candidates)
    assert not selection.invalid


@pytest.mark.parametrize("text", ["at six seventy PM", "в шесть семьдесят вечера"])
def test_english_and_russian_invalid_minute_controls_survive(text):
    selection = parse_spoken_time(text)
    assert selection and selection.invalid
    assert selection.value is None and selection.candidates is None
