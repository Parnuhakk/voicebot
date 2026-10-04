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
