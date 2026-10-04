"""Shared Azure/Groq source-language policy through LiveKit's async STT contract.

LiveKit owns VAD adaptation, cancellation, retries and metrics. The restaurant
default uses unrestricted MAI recognition; Groq remains available for rollback.
"""

from __future__ import annotations

import os

import httpx
from livekit import rtc
from livekit.agents import (
    NOT_GIVEN,
    APIConnectionError,
    APIConnectOptions,
    APIStatusError,
    APITimeoutError,
    LanguageCode,
    NotGivenOr,
    stt,
)
from livekit.agents.utils import AudioBuffer

from ..languages import LANGUAGES
from .azure_stt import (
    AZURE_STT_MODEL,
    AZURE_STT_PATH,
    azure_stt_base,
    azure_stt_request,
    parse_azure_transcription,
    stt_provider_from_env,
)
from .transcription import parse_transcription


class TelephoneSTT(stt.STT[str]):
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        mode: str = "auto",
        provider: str = "groq",
        region: str | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        super().__init__(
            capabilities=stt.STTCapabilities(streaming=False, interim_results=False)
        )
        if mode not in {"auto", *LANGUAGES}:
            raise ValueError("invalid telephone language mode")
        if provider not in {"azure", "groq"}:
            raise ValueError("invalid telephone recognition provider")
        self._provider, self.mode = provider, mode
        self._model = AZURE_STT_MODEL if provider == "azure" else model
        self._http = httpx.AsyncClient(
            base_url=azure_stt_base(region)
            if provider == "azure"
            else "https://api.groq.com",
            transport=transport,
            headers=(
                {"Ocp-Apim-Subscription-Key": api_key}
                if provider == "azure"
                else {"Authorization": f"Bearer {api_key}"}
            ),
            timeout=30,
        )

    @classmethod
    def from_env(cls, *, model: str, mode: str = "auto", env=None, transport=None):
        env = os.environ if env is None else env
        provider = stt_provider_from_env(env)
        return cls(
            api_key=env["AZURE_SPEECH_KEY" if provider == "azure" else "GROQ_API_KEY"],
            model=model,
            mode=mode,
            provider=provider,
            region=env.get("AZURE_REGION"),
            transport=transport,
        )

    @property
    def model(self) -> str:
        return self._model

    @property
    def provider(self) -> str:
        return "Azure" if self._provider == "azure" else "Groq"

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _recognize_impl(
        self,
        buffer: AudioBuffer,
        *,
        language: NotGivenOr[str] = NOT_GIVEN,
        conn_options: APIConnectOptions,
    ) -> stt.SpeechEvent:
        audio = rtc.combine_audio_frames(buffer).to_wav_bytes()
        if self._provider == "azure":
            path, options = AZURE_STT_PATH, azure_stt_request(audio)
            parse = parse_azure_transcription
        else:
            path, options = (
                "/openai/v1/audio/transcriptions",
                {
                    "data": {
                        "model": self._model,
                        "response_format": "verbose_json",
                        "temperature": "0",
                    },
                    "files": {"file": ("chunk.wav", audio, "audio/wav")},
                },
            )
            parse = parse_transcription
        try:
            response = await self._http.post(
                path,
                **options,
                timeout=httpx.Timeout(30, connect=conn_options.timeout),
            )
        except httpx.TimeoutException:
            raise APITimeoutError("telephone transcription timeout") from None
        except httpx.RequestError:
            raise APIConnectionError(
                "telephone transcription connection failed"
            ) from None
        if response.status_code >= 400:
            raise APIStatusError(
                "telephone transcription rejected", status_code=response.status_code
            ) from None
        try:
            result = parse(response.json())
            return stt.SpeechEvent(
                type=stt.SpeechEventType.FINAL_TRANSCRIPT,
                alternatives=[
                    stt.SpeechData(
                        text=result.text,
                        language=LanguageCode(result.language or "und"),
                        metadata={"unsupported_language": result.unsupported},
                    )
                ],
            )
        except (KeyError, TypeError, ValueError, AttributeError):
            raise APIStatusError(
                "invalid telephone transcription", status_code=502
            ) from None
