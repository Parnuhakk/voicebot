# Restaurant speech recognition

The restaurant browser and native worker use Azure **MAI-Transcribe-2** when
the existing Azure Speech account is configured. No new SDK, credentials,
server or model weights are needed. Groq still supplies the conversation model.
The old recognition path remains the default without Azure configuration and
for the explicit hotel/spa mode.

MAI is **public preview**, without a production SLA. Its availability was
verified on the existing `northeurope` account on 2026-10-04, not on every Azure
region or subscription. This fictional private pilot is not production-approved.
See [Microsoft's model and REST guide](https://learn.microsoft.com/azure/ai-services/speech-service/mai-transcribe).

## Why this changed

The old automatic Whisper path mislabeled short Estonian count/consent answers
as foreign languages, which the strict source-language gate then correctly
discarded. Selecting Eesti in the UI only chooses the reply language; it does
not resolve source recognition. A forced Estonian decode was deliberately not
used because it can turn unsupported speech into apparently valid consent.

The new provider recognizes the source language without a locale hint, prompt,
expected confirmation or booking text. Each nonempty phrase must carry ET, EN
or RU source metadata. A foreign phrase rejects the whole input, even if the
combined transcript looks like an Estonian confirmation. Empty recognition and
malformed/source-less responses never authorize actions. The existing delivered
recap, later explicit consent and owned-cancellation safeguards are unchanged.

## Configuration and rollback

Leave `VOICEBOT_STT_PROVIDER` unset or empty for the business/account default.
Use `VOICEBOT_STT_PROVIDER=azure` to require MAI explicitly, or
`VOICEBOT_STT_PROVIDER=groq` to return both transports to Whisper. The Azure
selection requires the existing protected `AZURE_SPEECH_KEY` and `AZURE_REGION`
environment variables. No key belongs in repository configuration or commands.
The media deployment forwards the same provider selection as the web process.
Release identity includes the effective recognizer, actual model and API version;
changing Azure/Groq selection invalidates an earlier synchronization receipt.
Credential values are never included. Malformed phrase locale codes fail closed
rather than being normalized into supported-language confirmation.

After changing it, publish/deploy the web revision and allow the normal telephone
release synchronization to finish. Verify `/api/status` → `models.stt.provider`,
`model` and `preview`, plus actual native recognition/provider metadata. Status
is configuration evidence, not speech acceptance. A provider error returns the
existing recognition-unavailable prompt; it does not bypass language or consent
checks or silently switch to a different recognizer.

## Measured limits

The initial provider comparison accepted 9/10 authored synthetic Estonian clips
instead of 6/10 with the previous automatic Whisper path, with the important
count, time, ordinary confirmation, hours and cancellation phrases preserved.
English/Russian controls remained supported and German/Spanish/Finnish controls
kept their foreign source tags. Silence produced no phrases. These are bounded
fixtures, not a population accuracy benchmark.

The isolated synthetic greeting `Tere!` still had ambiguous source detection;
do not weaken the gate or claim every very short utterance is fixed. Physical
microphones, browser pauses/background noise and public carrier calls need
separate qualification. A complete WAV bypasses browser endpointing and native
VAD segmentation. Successful provider recognition also does not establish that
every natural restaurant follow-up preserves its dialogue state.

The final integration comparison used the actual native Azure TTS SDK and an
8 kHz mu-law round trip. MAI passed 11 of 13 authored ET/EN/RU/foreign-control
cases versus 8 of 13 for Groq Turbo. Both missed the same very short agreement;
both also failed to preserve one other short affirmative as an accepted whole
turn. Neither failure is reinterpreted as consent. On this sample, median STT
was 377 ms for MAI and 298 ms for Turbo: the selected recognizer improved these
cases, not every latency metric. See [final speech evidence](../evidence/2026-10-04-final-estonian-speech.md).

## Estonian dates and clock extraction

Recognition and booking-field extraction are separate boundaries. Correctly
heard words previously could still produce a wrong date or drop clock minutes.
The shared browser/native policy now accepts these bounded forms:

- `pärast kahte päeva`, `nädala pärast`, and spaced `üle homme`;
- `viiendal kuupäeval oktoobris`, `5-ndal oktoobril`, and an explicit
  `2027. aastal` or `aastal kaks tuhat kakskümmend seitse`;
- separate month, year and day answers without losing the earlier details;
- a native VAD split of `…2027.` then `aastal`, while waiting for the clock,
  without erasing the date; the trailing word alone never supplies a date or consent;
- `kell 18. 30`, `kell 18 : 30`, and `kell kuus, kolmkümmend õhtul` → 18:30;
- split `kolm veerand seitse õhtul` → 18:45, `poolseitse õhtul` → 18:30,
  and `kell kuus pärast lõunat` → 18:00;
- `jah, seitse õhtul` during an earlier six-o'clock clarification → 19:00,
  rather than selecting the previous hour just because “evening” was heard.

`kell kuus` still asks morning or evening; unsupported clock material cannot
resolve an earlier ambiguous hour. Invalid minutes such as `kell 18. 70` clear
the previous valid clock. A day-only correction such as `tegelikult kuuendal`
asks for its missing month rather than silently retaining the old date.
Short `ülejärgmisel reedel` means the Friday after the next occurrence; explicit
`ülejärgmisel nädalal reedel` names a Monday-based calendar week. Calendar dates
use Europe/Tallinn, and retaining an explicit year does not bypass the existing
advance-booking window, availability, recap delivery or consent checks.
Date alternatives/ranges still clarify, including comma-separated `või` and
unspaced dash forms. A spaced short numeric date answered to a date question
cannot replace a separately requested clock. Dangling clock colons remain invalid.

The bounded synthetic provider/policy probe still rejects the isolated
`kell kaheksateist kolmkümmend` when MAI misidentifies its original language.
This is a remaining acoustic/source-detection limit, not permission to guess
18:00, force Estonian decoding or reuse an old time. Parser and HTTP tests verify
actual inquiry/recap fields; synthetic audio is not physical microphone or
carrier qualification.
