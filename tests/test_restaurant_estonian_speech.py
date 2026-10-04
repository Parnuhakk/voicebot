"""Estonian dates remain one spoken unit; guest counts use the correct case."""

import asyncio
import xml.etree.ElementTree as ET

import pytest

from app.providers.azure_tts import ssml
from app.providers.speech_delivery import spoken_estonian_date
from app.restaurant_call import COPY

SSML = "{http://www.w3.org/2001/10/synthesis}"


@pytest.mark.parametrize("backend", ["basic", "blingfire"])
def test_streaming_sentence_splitter_keeps_the_estonian_recap_date_together(backend):
    pytest.importorskip("livekit.agents")
    from livekit.agents import tokenize

    # Native TTS uses blingfire; the basic fallback splits numeric ordinals.
    text = COPY["et"]["recap"].format(
        date=spoken_estonian_date("2026-11-02"),
        time="18:05",
        party=1,
        name="Meretuule Demo Restaurant",
        duration=90,
        guest="Mari Tamm",
        question=COPY["et"]["confirmation_question"],
    )

    async def split():
        stream = getattr(tokenize, backend).SentenceTokenizer().stream()
        for pos in range(0, len(text), 7):
            stream.push_text(text[pos : pos + 7])
        stream.end_input()
        try:
            return [event.token async for event in stream]
        finally:
            await stream.aclose()

    chunks = asyncio.run(split())
    assert "teisel novembril 2026" in chunks[0]
    assert "kell 18:05" in chunks[0]
    assert chunks[-1] == COPY["et"]["confirmation_question"]


@pytest.mark.parametrize(
    "day,words",
    [
        (1, "esimesel"),
        (2, "teisel"),
        (3, "kolmandal"),
        (8, "kaheksandal"),
        (10, "kümnendal"),
        (11, "üheteistkümnendal"),
        (19, "üheksateistkümnendal"),
        (20, "kahekümnendal"),
        (21, "kahekümne esimesel"),
        (30, "kolmekümnendal"),
        (31, "kolmekümne esimesel"),
    ],
)
def test_estonian_spoken_dates_do_not_leave_an_ordinal_sentence_boundary(day, words):
    assert f", {words} oktoobril 2026" in spoken_estonian_date(f"2026-10-{day:02d}")


@pytest.mark.parametrize("voice", ["et-EE-AnuNeural", "et-EE-KertNeural"])
@pytest.mark.parametrize(
    "count,words",
    [
        (1, "ühele"),
        (2, "kahele"),
        (4, "neljale"),
        (8, "kaheksale"),
        (10, "kümnele"),
        (11, "üheteistkümnele"),
        (20, "kahekümnele"),
    ],
)
def test_estonian_recap_headcount_is_pronounced_in_the_correct_case(
    voice, count, words
):
    text = f"Saan pakkuda lauda kell 18:05, {count} inimesele. Kas teile sobib?"
    root = ET.fromstring(ssml(text, voice, "et-EE"))
    assert f"{words} inimesele" in [
        node.get("alias") for node in root.iter(SSML + "sub")
    ]
    assert "".join(root.itertext()) == text


@pytest.mark.parametrize(
    "text",
    [
        "Telefon +372 5900 1700.",
        "Hind 4 eurot.",
        "Kood A4 inimesele.",
        "Laud 21 inimesele.",
        "Laud 0 inimesele.",
        "Laud 1.5 inimesele.",
    ],
)
def test_estonian_headcount_alias_does_not_reinterpret_other_numbers(text):
    root = ET.fromstring(ssml(text, "et-EE-AnuNeural", "et-EE"))
    assert not list(root.iter(SSML + "sub"))
    assert "".join(root.itertext()) == text
