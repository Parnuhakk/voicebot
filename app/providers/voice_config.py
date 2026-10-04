"""Shared speech/model settings for HTTP turns and the native telephone worker.

These are the Groq conversation and rollback-recognition models. Restaurants
with Azure configured default to MAI-Transcribe-2 (preview); explicit Groq
recognition uses Turbo, with large-v3 available for accuracy comparisons.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ..languages import LANGUAGES
from .azure_voices import validated_voice

STT_MODEL = "whisper-large-v3-turbo"
CHAT_MODEL = "openai/gpt-oss-120b"
STT_LANGUAGE = "et"
MAX_COMPLETION_TOKENS = 2048


@dataclass(frozen=True)
class SpeechConfig:
    mode: str = "auto"
    estonian_voice: str = "et-EE-AnuNeural"
    english_voice: str = "en-US-JennyNeural"
    english_locale: str = "en-US"
    russian_voice: str = "ru-RU-SvetlanaNeural"
    russian_locale: str = "ru-RU"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> SpeechConfig:
        env = os.environ if env is None else env
        mode = env.get("VOICEBOT_TELEPHONE_LANGUAGE", "auto").strip()
        et_voice = env.get("AZURE_VOICE", "et-EE-AnuNeural").strip()
        et_locale = env.get("AZURE_LANG", "et-EE").strip()
        en_voice = env.get("AZURE_EN_VOICE", "en-US-JennyNeural").strip()
        en_locale = env.get("AZURE_EN_LANG", "en-US").strip()
        ru_voice = env.get("AZURE_RU_VOICE", "ru-RU-SvetlanaNeural").strip()
        ru_locale = env.get("AZURE_RU_LANG", "ru-RU").strip()
        if (
            mode not in {"auto", *LANGUAGES}
            or et_locale != "et-EE"
            or not re.fullmatch(r"en-[A-Z]{2}", en_locale)
            or ru_locale != "ru-RU"
        ):
            raise ValueError("invalid telephone speech configuration")
        try:
            et_voice, et_locale = validated_voice(et_voice, et_locale)
            en_voice, en_locale = validated_voice(en_voice, en_locale)
            ru_voice, ru_locale = validated_voice(ru_voice, ru_locale)
        except ValueError:
            raise ValueError("invalid telephone speech configuration") from None
        return cls(mode, et_voice, en_voice, en_locale, ru_voice, ru_locale)

    @property
    def initial_language(self) -> str:
        return self.mode if self.mode in LANGUAGES else "et"

    def voice_for(self, language: str) -> tuple[str, str]:
        if language == "en":
            return self.english_voice, self.english_locale
        if language == "et":
            return self.estonian_voice, "et-EE"
        if language == "ru":
            return self.russian_voice, self.russian_locale
        raise ValueError("unsupported telephone speech language")


@dataclass(frozen=True)
class VoiceConfig:
    chat_model: str = CHAT_MODEL
    stt_model: str = STT_MODEL
    max_completion_tokens: int = MAX_COMPLETION_TOKENS

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> VoiceConfig:
        env = os.environ if env is None else env

        def model(name: str, default: str) -> str:
            value = env.get(name, default).strip() or default
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9/._-]{0,127}", value):
                raise ValueError("invalid voice model configuration")
            return value

        try:
            tokens = int(env.get("GROQ_MAX_COMPLETION_TOKENS", MAX_COMPLETION_TOKENS))
        except (TypeError, ValueError):
            raise ValueError("invalid voice completion limit") from None
        if not 512 <= tokens <= 8192:
            raise ValueError("invalid voice completion limit")
        return cls(
            chat_model=model("GROQ_CHAT_MODEL", CHAT_MODEL),
            stt_model=model("GROQ_STT_MODEL", STT_MODEL),
            max_completion_tokens=tokens,
        )

    def chat_options(self, model: str | None = None) -> dict[str, Any]:
        model = self.chat_model if model is None else model
        options: dict[str, Any] = {"max_completion_tokens": self.max_completion_tokens}
        if model in {"openai/gpt-oss-20b", "openai/gpt-oss-120b"}:
            # Reasoning uses the same completion budget as the spoken answer.
            # Keep enough room for valid tool arguments, with short reasoning.
            options.update(reasoning_effort="low", include_reasoning=False)
        return options
