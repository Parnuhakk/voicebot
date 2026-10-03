"""Validated source-language evidence shared by browser and telephone speech."""

from __future__ import annotations

from dataclasses import dataclass

from ..languages import language_code


@dataclass(frozen=True)
class Transcription:
    text: str
    language: str | None

    @property
    def unsupported(self) -> bool:
        return self.language is None


def parse_transcription(payload: object) -> Transcription:
    """Require source language; never guess from the selected reply language."""
    if not isinstance(payload, dict):
        raise ValueError("invalid transcription")
    text, language = payload.get("text"), payload.get("language")
    segments = payload.get("segments", [])
    if (
        not isinstance(text, str)
        or not isinstance(language, str)
        or not language.strip()
        or not isinstance(segments, list)
    ):
        raise ValueError("invalid transcription")
    # Silence hallucinations must never produce consent or business actions.
    if segments and all(
        isinstance(segment, dict)
        and type(segment.get("no_speech_prob")) in (int, float)
        and segment["no_speech_prob"] >= 0.85
        and type(segment.get("avg_logprob")) in (int, float)
        and segment["avg_logprob"] < -1.0
        for segment in segments
    ):
        text = ""
    return Transcription(text, language_code(language))
