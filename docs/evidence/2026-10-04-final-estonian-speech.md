# Final Estonian speech integration — 2026-10-04

## Bounded choices

- The restaurant conversational female profile uses Azure
  `en-US-NovaTurboMultilingualNeural` with explicit `et-EE`. English/Russian
  profile voices remain Emma; native English/Russian settings are unchanged.
- Shared default sentence pause is `0`: no fixed silence is injected. Explicit
  native-voice pacing of 100–500 ms and optional calm/warm profiles remain valid.
  Canonical recaps retain their full fields, natural timing and slower rate.
- Published collaborator change `ff11d69` supplies unrestricted
  `MAI-Transcribe-2` on the existing Azure Speech account. It superseded the
  earlier assumption that a separate deployment was needed. MAI is public
  preview without a production SLA; this is a fictional private pilot.
- `VOICEBOT_STT_PROVIDER=groq` selects the rollback path, defaulting to
  `whisper-large-v3-turbo`. `GROQ_STT_MODEL=whisper-large-v3` remains an explicit
  comparison/rollback option. Recognition never supplies a locale, prompt or
  expected booking/consent text.

## Measurements, not a naturalness benchmark

The first REST comparison synthesized one identical Estonian recap with three
voices and passed it through 24 kHz PCM → 8 kHz mu-law → 16 kHz WAV. Audio and
transcripts stayed in memory.

| Voice | First byte | Full synthesis | Audio length | Maximum internal quiet |
| --- | ---: | ---: | ---: | ---: |
| Anu | 1.074 s | 1.329 s | 6.32 s | 0.80 s |
| Emma | 0.594 s | 0.804 s | 6.15 s | 0.34 s |
| Nova Turbo | 0.576 s | 0.824 s | 5.57 s | 0.38 s |

Both Whisper models preserved the tested date, 18:05 and four diners for all
three voices. A broader comparison passed 24 of 26 language/meaning checks;
both models rejected the same very short affirmative. This is not evidence
that short speech is always reliable.

The final native-SDK comparison used 13 authored cases per recognizer: an exact
Estonian booking with 18:05, a short count, four affirmative forms, a negative,
English/Russian booking and consent controls, and Finnish/French rejection.

| Recognizer | Passed | Median recognition |
| --- | ---: | ---: |
| MAI-Transcribe-2 (preview) | 11 / 13 | 0.377 s |
| Whisper large-v3 Turbo | 8 / 13 | 0.298 s |

Both recognizers still failed two short affirmative cases. MAI preserved the
exact Estonian booking fields, short count and another brief affirmative that
Turbo missed. English/Russian controls and foreign-language rejection passed
both. Nova's median native first byte for the seven Estonian inputs was 0.340 s.
Provider timings vary and exclude VAD, dialogue, network routing and playback;
these are not end-to-end call-latency guarantees or human listening results.

An earlier native smoke failed because its standalone script lacked LiveKit's
HTTP job context. After correcting that harness setup, its Whisper numerical
readback still failed. The final comparison above distinguishes actual native
synthesis from recognizer/parser acceptance instead of treating either as a
complete conversation proof.

## Safety and qualification

Whole-turn consent still requires an owned, unexpired, completely delivered
recap. Questions, corrections, negatives, conditions and foreign source metadata
cannot authorize a write. The integration review found and regression-tested
two additional gaps: malformed Azure locales and missing recognizer identity in
release receipts. Both are now rejected/represented in the shared paths.

Synthetic provider checks do not qualify physical microphones, background noise,
human-perceived naturalness or carrier/PSTN calls. The native RTC restaurant
acceptance runner separately checks exact fictional call-owned reservations,
no writes before consent, and owned cancellation on the deployed release.

Sources checked 2026-10-04:

- [Microsoft voice/language support](https://learn.microsoft.com/azure/ai-services/speech-service/language-support): Turbo supports full SSML; explicit multilingual locale controls.
- [MAI-Transcribe REST guide](https://learn.microsoft.com/azure/ai-services/speech-service/mai-transcribe): enhanced mode, unrestricted detection, verbatim default and preview/no-SLA warning.
- [Speech regions](https://learn.microsoft.com/azure/ai-services/speech-service/regions): MAI availability includes `northeurope`; actual account access was independently exercised.
- [Groq audio reference](https://github.com/groq/groq-python/blob/main/_autodocs/api-reference/audio.md): Whisper model IDs and verbose original-language results.
