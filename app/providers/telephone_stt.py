"""Groq Whisper with language metadata through the public LiveKit STT contract.

The pinned Groq plugin requests JSON, which omits Whisper's detected language.
Verbose JSON lets the telephone worker choose the reply voice without a second
model request. LiveKit owns VAD adaptation, cancellation, retries and metrics.
"""

from __future__ import annotations

import httpx
from livekit import rtc
from livekit.agents import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    APIConnectOptions,
    LanguageCode,
    NOT_GIVEN,
    NotGivenOr,
    stt,
)
from livekit.agents.utils import AudioBuffer

from ..languages import LANGUAGES
from .transcription import parse_transcription


class TelephoneSTT(stt.STT[str]):
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        mode: str = "auto",
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        super().__init__(
            capabilities=stt.STTCapabilities(streaming=False, interim_results=False)
        )
        if mode not in {"auto", *LANGUAGES}:
            raise ValueError("invalid telephone language mode")
        self._model, self.mode = model, mode
        self._http = httpx.AsyncClient(
            base_url="https://api.groq.com",
            transport=transport,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )

    @property
    def model(self) -> str:
        return self._model

    @property
    def provider(self) -> str:
        return "Groq"

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _recognize_impl(
        self,
        buffer: AudioBuffer,
        *,
        language: NotGivenOr[str] = NOT_GIVEN,
        conn_options: APIConnectOptions,
    ) -> stt.SpeechEvent:
        data = {
            "model": self._model,
            "response_format": "verbose_json",
            "temperature": "0",
        }
        try:
            response = await self._http.post(
                "/openai/v1/audio/transcriptions",
                data=data,
                files={
                    "file": (
                        "chunk.wav",
                        rtc.combine_audio_frames(buffer).to_wav_bytes(),
                        "audio/wav",
                    )
                },
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
            result = parse_transcription(response.json())
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
