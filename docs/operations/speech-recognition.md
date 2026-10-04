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

## Estonian field retention repair (2026-10-04)

The follow-up to the live caller report separates recognition from dialogue:

- Explicit diner allatives (`neljale`, `viiele`, `üheteistkümnele`) are counts,
  not bare calendar days or clock hours, including out-of-order answers.
- Every recognized clock span, including conflicting choices, is excluded from
  diner extraction. Resolving `tuleme 6:30 või 7:30` never invents six diners.
- A partial compound such as `kahekümne ühele` cannot become one diner. The same
  whole-number check applies to adults, children, subsets and explicit totals;
  uncertain larger quantities ask for clarification rather than a smaller table.
- Closed cardinal case forms through twenty and collectives through ten are
  understood as input. This does not increase the restaurant's configured
  maximum party size or imply availability for a larger group.
- A whole Estonian correction beginning with `tegelikult` or `hoopis` can change
  one field during incomplete collection without erasing unrelated fields.
  Unknown neighboring clauses still cannot inherit a complete plan.
- `nelja inimese jaoks` retains the previously requested date and clock.
- Inflected minutes such as `kella kuue kolmekümneks õhtul` retain **18:30**,
  rather than silently accepting the hour prefix as 18:00. Invalid minutes and
  unconsumed numeric tails still require clarification.
- Completing an owned month/year with the same named month keeps its explicit
  year. A fresh explicit year wins; a different month does not blindly reuse it.
- Whole spaced numeric dates and the ordinal `päeval` scaffold are validated as
  dates, never clocks. Ambiguous, malformed and impossible dates remain rejected.

The in-memory diagnostic used synthesized caller audio reduced to **8 kHz,
mu-law**, then resampled to the worker's **24 kHz upload**. On the same twelve
Anu-voiced Estonian field samples, exact fields with matching original source
metadata passed **8/12** with MAI, **9/12** with Whisper Turbo and **8/12** with
full Whisper after the parsing repairs. MAI rejected the authored French-text
control and returned an empty result for silence; both Whisper variants missed
those expected outcomes in this bounded experiment. The French text used an
allowed English-locale multilingual caller voice, so this does **not** prove
genuine French-audio accuracy or unsafe Whisper source detection. The evidence
is insufficient for a safe provider swap: MAI stays configured, with no
automatic foreign-source override, forced locale or consent prompt.

Other Nova-voiced diagnostic samples were substantially less reliable. These
small synthetic results are not human-call accuracy estimates or proof that a
different model is universally better. Isolated counts and some short clocks
still fail original-source qualification. Audio and recognized text were kept
only in memory; the recorded evidence contains case IDs and match booleans.
Native finalized-turn and delivered-recap regressions cover state retention;
they do not establish physical-microphone, carrier or public-ingress acceptance.

## Weak initial acknowledgements

First-turn `ja`, `jaa`, `yah`, `ya` and `ah`, or a terminal question mark on a
known weak acknowledgement, do not select a reply language solely from a noisy
supported source tag. A later clear ET/EN/RU request selects it normally. This
only delays language locking: original-source rejection, explicit language
requests, full commitments, delivered-recap consent and cancellation are
unchanged. It does not repair incorrectly recognized words or empty speech.
