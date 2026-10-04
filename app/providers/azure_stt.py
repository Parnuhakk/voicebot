"""Unrestricted MAI recognition; apply ET/EN/RU policy only after source detection.

Uses the existing Azure Speech account and httpx, not a new SDK. MAI-Transcribe-2
is preview; VOICEBOT_STT_PROVIDER=groq retains the previous runtime path.
"""

from __future__ import annotations

import json
import os
import re

import httpx

from ..business import business_type
from ..languages import language_code
from .errors import ProviderError, RetryableProviderError, raise_for_provider
from .transcription import Transcription
from .voice_config import VoiceConfig

AZURE_STT_MODEL = "MAI-Transcribe-2"
AZURE_STT_API_VERSION = "2025-10-15"
AZURE_STT_PATH = (
    f"/speechtotext/transcriptions:transcribe?api-version={AZURE_STT_API_VERSION}"
)


def stt_provider_from_env(env=None) -> str:
    env = os.environ if env is None else env
    configured = bool(env.get("AZURE_SPEECH_KEY") and env.get("AZURE_REGION"))
    default = "azure" if configured and business_type(env) == "restaurant" else "groq"
    provider = env.get("VOICEBOT_STT_PROVIDER", default).strip() or default
    if provider not in ("azure", "groq") or (provider == "azure" and not configured):
        raise ValueError("invalid speech recognition configuration")
    return provider


def stt_descriptor(env=None) -> dict[str, str]:
    """Effective recognizer identity; never include credential values."""
    env = os.environ if env is None else env
    provider = stt_provider_from_env(env)
    return {
        "provider": provider,
        "model": AZURE_STT_MODEL
        if provider == "azure"
        else VoiceConfig.from_env(env).stt_model,
        "api_version": AZURE_STT_API_VERSION if provider == "azure" else "v1",
    }


def azure_stt_base(region: str) -> str:
    if not isinstance(region, str) or not re.fullmatch(r"[a-z][a-z0-9]{1,31}", region):
        raise ValueError("invalid speech recognition region")
    return f"https://{region}.api.cognitive.microsoft.com"


def azure_stt_request(audio: bytes, filename: str = "chunk.wav") -> dict:
    # Never include locales or a prompt: that can translate foreign speech into
    # an apparently valid confirmation. Source language comes from each phrase.
    return {
        "files": {"audio": (filename, audio, "audio/wav")},
        "data": {
            "definition": json.dumps(
                {
                    "enhancedMode": {"enabled": True, "model": AZURE_STT_MODEL},
                }
            )
        },
    }


def parse_azure_transcription(payload: object) -> Transcription:
    if not isinstance(payload, dict) or not isinstance(payload.get("phrases"), list):
        raise TypeError("invalid transcription")
    phrases = payload["phrases"]
    if len(phrases) > 512:
        raise ValueError("invalid transcription")
    texts, languages = [], []
    for phrase in phrases:
        if not isinstance(phrase, dict):
            raise TypeError("invalid transcription")
        text, locale = phrase.get("text"), phrase.get("locale")
        if (
            not isinstance(text, str)
            or not isinstance(locale, str)
            # Azure emits language codes, optionally with a script and region.
            # Do not normalize malformed suffixes into supported consent.
            or not re.fullmatch(
                r"[A-Za-z]{2,3}(?:-[A-Za-z]{4})?(?:-(?:[A-Za-z]{2}|\d{3}))?", locale
            )
        ):
            raise ValueError("invalid transcription")
        if text.strip():
            texts.append(text.strip())
            languages.append(language_code(locale))
    # Inspect every phrase, not combinedPhrases (which lacks source metadata).
    # MAI's documented response uses confidence=0, so it is not a silence score.
    language = languages[0] if languages and all(languages) else None
    return Transcription(" ".join(texts), language)


class AzureSttClient:
    provider = "azure"
    model = AZURE_STT_MODEL
    preview = True

    def __init__(
        self,
        subscription_key: str,
        region: str,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._http = httpx.Client(
            base_url=azure_stt_base(region),
            transport=transport,
            headers={"Ocp-Apim-Subscription-Key": subscription_key},
            timeout=20,
        )

    def __repr__(self) -> str:
        return "AzureSttClient(redacted)"

    def close(self) -> None:
        self._http.close()

    def transcribe_with_metadata(
        self,
        audio: bytes,
        filename: str = "chunk.wav",
        *,
        language: str = "auto",
    ) -> Transcription:
        try:
            response = self._http.post(
                AZURE_STT_PATH, **azure_stt_request(audio, filename)
            )
        except httpx.RequestError:
            raise RetryableProviderError(
                "azure.stt: transport error", reason="transport_error"
            ) from None
        raise_for_provider(response, "azure.stt")
        try:
            return parse_azure_transcription(response.json())
        except (ValueError, TypeError, AttributeError):
            raise ProviderError(
                "azure.stt: invalid language metadata",
                reason="invalid_response",
                status_code=response.status_code,
            ) from None
