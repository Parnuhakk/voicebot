# Restaurant day-part clarification — 2026-10-04

## Demonstrated bug and bounded repair

Correctly transcribed `hommikul või õhtul?` previously discarded the requested
date and guest count in both HTTP and native telephone dialogue. After an 18:00
recap it restarted the date interview instead of explaining the clock. This
was reproduced without a model or speech provider: 27 HTTP and 21 native cases.

The shared restaurant policy now answers the read-only question first:

- Saved 18:00: `18:00 tähendab kell kuus õhtul.`
- Ambiguous six: explain 06:00 and 18:00, then request a single selection.
- No clock anchor: `Millist kellaaega mõtlete?`

The requested date/count survive. An owned, unexpired proposal keeps its hold
and expiry, but receives a new recap identity with delivery/approval revoked.
Stale delivery receipts, questions, negations and mixed corrections cannot
confirm a reservation. Opening-hours questions during booking remain read-only.
English/Russian counterquestions use the same policy. Formatted-clock explanation
does not change the reservation parser's AM/PM clarification rules.

## First repair verification

Published recap fixes, Restobot/calendar release `7d82183`, and PR #44's Estonian
spoken-field repairs (`190535f`) were preserved by normal merges. Only
`app/restaurant_call.py` changes runtime behavior relative to that published
release; recognition, voices, safety copy and demo data do not.

- Failing-first regressions reproduced the reset/incorrect answer; 25 current
  clock-question regressions are included in the passing full suite.
- Integrated `python -m pytest tests -q`: **14,540 passed**, **36 subtests passed**,
  **6 skipped**, **2 existing deprecation warnings**, **263.64 seconds**.
- All **12** headless Chromium browser journeys passed with no external requests.
- Independent OpenAI/Codex review: **3,932 scoped passes**, 29 additional state
  controls and four read-only HTTP clock probes; no P0/P1. Its prefixed-noon P2
  was separately reproduced failing, repaired and verified in the full suite.
- After preserving the subsequently published PR #44: **15,072 passed**, **36
  subtests passed**, **6 skipped**, **2 existing warnings**, **248.63 seconds**;
  all four restaurant browser journeys passed again.

## Recognition remains separately qualified

An isolated real-provider synthetic check correctly transcribed the full ET
day-part question, but misrecognized one-word `õhtul` as Russian. A paired
MAI/full-Whisper-v3 comparison retained 15 completed cases before the foreign
caller voice hit the production TTS allowlist: MAI passed 12 versus Whisper's 8.
Both missed isolated evening. A second partial run also retained short-word
failures. Neither incomplete comparison is an 18-case pass or a population
accuracy benchmark; the alternate model is not evidence for a safe replacement.

The failed receipts remain failures. Audio, captured transcripts and credentials
were not persisted. No source-language/expected-answer hints or acceptance
threshold changes were introduced. The original private checker is unchanged.
Strict multilingual acoustic acceptance, physical microphones and the carrier
path remain unverified; this repair does not establish real restaurant bookings.

## Exact-recap day-part reply follow-up

After the first repair was published as PR #45 (`8bb146f`), correctly transcribed
single day-part replies still reset an exact-time recap's date/count. Nine failing
HTTP cases reproduced this in ET/EN/RU. The shared parser now passes the saved
24-hour clock to the existing period resolver. A compatible day part preserves
the exact time; a contradiction requests a new full clock, never a silent AM/PM
shift or booking approval. Bare counts remain counts. Invalid mixed clauses
cannot turn the single known clock into bogus ambiguity candidates.

- Final `python -m pytest tests -q`: **15,109 passed**, **36 subtests passed**,
  **6 skipped**, **2 existing warnings**, **267.83 seconds**.
- All four restaurant browser journeys passed again. The three installed native
  AgentSession clock cases also cover the subsequent day-part reply with zero
  model calls. The expanded file contains 37 additional regression cases.
- OpenAI/Codex review identified the invalid singleton-candidate branch. It was
  reproduced failing and repaired; targeted re-review found **0 P0/P1** with
  **568 scoped passes**, seven original HTTP counterexamples, stale-receipt and
  ownership/expiry/recovery controls. These overlapping checks are not added to
  the full-suite count.
- After preserving published PR #46's weak-first-language safeguard and the
  unified workspace (`de7d077`), the resumed full suite passed **15,325 tests**,
  **36 subtests**, with **6 skips** and **2 existing warnings** in **261.29 seconds**.
  All **12** browser journeys, six landing widths and eight calendar viewports
  passed. The interrupted runs were cancelled, not counted as passes.

The first release's bounded live clock probe passed the request and full day-part
question, including exact captions and independent recognition of response audio.
It then failed the isolated evening caller reply with input similarity **0.0**.
End-of-run runtime and whole restaurant state checks passed. This remains a
**failed 2/3 diagnostic**, not a passing strict multilingual batch. No recognition,
voice, data, safety-copy, checker threshold or independent-ASR hint was changed.

## Published follow-up and remaining speech boundaries

PR #47 was merged as `592d7083150ac047c6ee2d5907e96878ca1cdf6e`. Both jobs in
PR CI `37199404975` and master CI `37199552343` passed. Locked delivery checks
matched **102 application/demo source hashes in each web/worker/bridge role**,
the worker/bridge image IDs, the unchanged speech profile and infrastructure,
and the original data volume. Prior persistent and event-row prefixes survived;
the whole prepublication restaurant digest also matched at this check.

A fresh strict serial FAQ run failed after two Estonian passes. The third,
special-request refusal had exact, fresh captions but failed the independent
audio-content gate (raw similarity **0.970760**). End-of-batch runtime and whole
restaurant-state checks passed. Separate one-case note diagnostics passed; three
unhinted decodes of the same later PCM agreed, with only an already-permitted
compound-word space. These diagnostics **do not replace the failed batch**, prove
its failed audio correct, or demonstrate recognizer nondeterminism.

A complete eight-case paired short-input comparison scored **5/8 for MAI-1.5
and 5/8 for MAI-2**. Both failed isolated evening input; MAI-1.5 also failed a
foreign-language source control. Foreign controls used the existing Estonian
caller voice, so the accent limits that evidence. Recognition and production
voices remain unchanged; no safe replacement was established.

The newer host-only recovery release `8c3b2c7` was preserved by fast-forward;
its application source is identical to `592d708`. The public browser helper now
checks the published unified calendar link (`/dashboard#calendar-section`), its
native section and all three legacy 308 aliases with preserved query strings.
Desktop/mobile public checks and four negative-navigation controls passed;
existing privacy, asset, health and retired-host checks remain intact. This is a
test-only update to the published navigation contract, not an application change.

The next instrumented strict run on `8c3b2c7` also failed after two Estonian
passes at the note's **0.970760** audio-content gate. Two further unhinted decodes
of that identical failed PCM agreed with its original rejected transcription:
negation counts matched, but there were two character replacements and one
compound-space insertion. Those decodes did not promote the failed result.
Whole restaurant state, runtime and checker integrity remained unchanged.

The telephone goal remains active. No fresh passing 12-case batch, genuine human
microphone, carrier path, number ownership or real-restaurant acceptance is claimed.

## Whole validated reply synthesis — candidate

The failed note was reproduced **before RTC** through the installed
`TelephoneTTS` provider, with the same voice and approved text. Sentence-split
synthesis at the unchanged **1.12** rate failed the original independent gate at
**0.970760**; the changed approved-word positions were 6 and 8. Complete-reply
synthesis at **1.12** passed at **0.994152**, with only the existing whole-answer
compound-spacing equivalence. Diagnostic complete/split samples at **1.0** also
passed. No production voice, rate, recognizer, safety wording or checker changed.
This locates the reproducible mismatch upstream of RTC; it does not establish
which provider's pronunciation or recognition interpretation is linguistically
correct, nor explain short caller-word recognition.

The bounded candidate routes fully validated restaurant replies through the
existing native provider's public `synthesize` method as one request. HTTP audio
still streams in frames; it is not buffered until the full audio completes.
Voice locking, configured connection options, recap speed, guarded captions,
fallback, cancellation and completed-item consent callbacks remain in the shared
worker path. Other businesses and non-native test providers retain the SDK path.

Three installed AgentSession regressions failed first because each approved
ET/EN/RU refusal became two provider requests. They pass with the candidate.
Additional real-provider-transport fixtures cover configured connection options,
metrics, owned recap/question/later-consent flow, failed synthesis and interrupted
stream cleanup. Retained review probes also cover partial-audio transport failure,
expiry at playback completion and replacement of the pending proposal.
**319 scoped tests passed**, with one existing warning. Independent OpenAI review
found no P0/P1; its P2 coverage suggestion is now retained in those tests.
The local real-AgentSession candidate, using provider-backed synthesis and
unhinted independent recognition, passed the original note gate at **0.994152**
with exact captions, no model call and no booking writes. Live state and runtime
were unchanged. This is not a deployed RTC check. Final full checks and exact
publication remain separate gates. Final `python -m pytest tests -q` passed
**15,339 tests + 36 subtests**, with 6 skips and 2 existing warnings (256.41s).
All **12 browser journeys** passed; native optional-dependency collection also
skips correctly in the core-only environment. Exact publication and a fresh
strict multilingual batch are still pending at this candidate check.

## PR #48 publication and current acceptance result

The reviewed repair was committed as `7540d2e` and merged as
`6fd6e4d5df4d4abb78c5dcb12431278265fb199c`. PR CI `37204656161` and master CI
`37204876841` passed both jobs; the merged tree equals the verified candidate.
The guarded shared synchronizer respected lock deferrals. Locked delivery checks
matched all **102 source hashes per role**, equal worker/bridge images, unchanged
speech settings and infrastructure, the original volume, four database integrity
checks and preserved persistent/event prefixes. The whole prior restaurant digest
also matched. Mutable-table and non-atomic cross-database qualifications remain.

The existing configured number still points to the canonical webhook using
**POST**. Read-only number lookup and signed/unsigned webhook, stream binding and
`no-store` checks passed. Desktop/mobile public checks passed; the separate
Meretuule host still returned **503** on all four tested routes.

The first fresh strict batch on `6fd6e4d` **failed at the first Estonian menu
caption gate**, before an independent-audio case ran. Two fresh assistant finals
did not combine into the exact approved reply. Whole restaurant state, runtime
and checker integrity stayed unchanged. A separate one-case diagnostic found an
extra short final followed by the exact menu final; its post-input audio passed
the original independent gate at **0.980392**. That audio diagnostic does not
promote either caption failure or constitute whole-batch acceptance.

Read-only metadata in the two diagnostic windows records two VAD speech starts,
one unsupported-language turn and then one recognized turn. This is consistent
with an input-fragment boundary problem, but does not identify the short caption's
generation or justify accepting rejected source-language input. The telephone goal
remains active; short human Estonian, physical microphones and PSTN remain unproven.

## Native utterance grouping — candidate

The same authored menu WAV reproduced the input-boundary failure without an RTC
room. Installed default VAD split it into two chunks: the **1.088-second** first
chunk was rejected as an unsupported source; the second was recognized as ET.
The complete WAV and diagnostic **1-second** silence grouping each preserved ET
recognition at **0.990654**. No production settings changed in that diagnostic.

The minimal candidate changes only restaurant `prewarm` to use the existing
Silero VAD's `min_silence_duration=1.0`; other businesses retain native defaults.
Nominal native end-of-speech detection waits an additional **450 ms**, not an
established end-to-end latency change. Speech-start threshold, prefix padding,
interruption, unrestricted recognition, foreign-source rejection and booking
consent policy remain unchanged.

Failing-first native tests produced **6 failures / 2 passes**: short pauses split
into two chunks/requests instead of one, and invalid business configuration did
not fail before loading the model. The initial green run exposed a test-cleanup
assumption: `StreamAdapter.aclose` removes its listener but does not close the
wrapped provider. Explicit test-provider cleanup resolved that failure.

Independent OpenAI **static review** found no P0/P1. Its two P2 suggestions are
retained: the submitted fixture WAV includes both complete speech bursts and
internal silence, and mixed supported/unsupported sources are rejected in either
order. These are buffering/policy tests, not human speech-quality evidence.
Published peer `8fbae42` was preserved. A separate static review of that new delta
also found no P0/P1; its native held-language-switch regression is retained.
That journey verifies the same hold at language change, exact English recap,
rejected early consent and late playback, then a fresh recap and one later
booking with zero model calls. Premature agreement must not resurrect the
discarded proposal; its existing invalidation policy was not changed.

All **138 scoped tests** passed. Final integrated full checks, including the
additional journey, passed **15,432 tests + 36 subtests**, 6 skips and 2 existing
warnings (243.58s); all **12 browser journeys** passed on the same application
bytes. The unchanged private checker/observer controls passed **186 tests**.
Exact publication and fresh strict speech acceptance remain separate gates.

A paired eight-case authored synthetic input comparison completed with **5/8**
for both default and candidate grouping. Both recognized the exact day-part
counterquestion; isolated morning/evening and prefixed morning still failed the
source/content criteria. Existing-ET-voice foreign controls remained rejected and
are accent-qualified. This repair addresses intra-utterance fragmentation, not
an established fix for isolated human Estonian words.

## Published grouping proof and remaining Russian selector boundary

PR **#49** published the grouping repair as **`86aefbe`**. Both PR and master
CI jobs passed. Locked deployed verification matched **102 source hashes per
role**, equal worker/bridge images and the reviewed candidate tree. Only the
native VAD silence duration changed; recognition, output voices/rates, other VAD
fields, infrastructure and original storage volume were preserved. Four database
integrity checks, persistent/event prefixes and the whole restaurant digest
passed. Configured-number routing still uses the canonical **POST** webhook with
signed/unsigned, stream-binding and `no-store` checks; no carrier call or number
ownership certification is claimed. Public desktop/mobile checks passed and all
four separate Meretuule routes remained **503**.

The fresh strict serial FAQ batch on that release **failed** after ten individual
passes: ET **4/4**, EN **4/4**, then RU menu/allergy. ET note retained the exact
fresh caption and independent-audio score **0.994152**. RU note failed its caption
gate; its input differed from the authored question by one grammatical ending.
Whole restaurant state, runtime and original checker were unchanged. No earlier
failed batch is promoted by these individual passes.

The original three-turn clock probe also **failed**: the ambiguous request and
exact “hommikul või õhtul?” counterquestion passed fresh-caption and audio gates,
but isolated “õhtul” failed fresh-input recognition with similarity **0.0**. The
counterquestion's independent audio scored **0.822967** under the unchanged
**0.78** floor. Neither this partial probe nor synthetic speech proves reliable
human short-word understanding.

A bounded RU input/caption diagnostic identified the recognized note question as
an authored booking-locative variant, one character different at the final word.
The existing finite capability bank did not include it, so the selector chose
`allergens` rather than `special_requests`. The candidate adds only that one
equivalent question to `booking-101`; all answer wording and policies stay exact.
Failing-first fresh, HTTP, held-consent, contextual and native-synthesis tests
produced **5 failures / 145 passes**. After the one-value addition, **418 scoped
tests** passed with one existing warning. Full verification passed **15,439 tests
+ 36 subtests**, 6 skips and 2 existing warnings (256.51s); all **12 browser
journeys** passed. The unchanged private checker/observer controls passed **186
tests**. Independent OpenAI **static review** found no P0/P1/P2; the reviewer
could not run commands and did not independently compare the bank against HEAD.
Owner verification separately checks that only this variant was added. Exact
publication and a new strict whole-batch speech check remain pending;
isolated-word recognition remains unresolved.

The installed recognizers were also compared on the same eight authored native
1-second-VAD inputs: **MAI-2 5/8**, **Groq Turbo 5/8**, **Groq large-v3 4/8**.
Turbo recognized both isolated Estonian day parts correctly, but both Groq models
lost the accent-qualified Spanish and German source-language controls. Groq also
provides global, not per-phrase, source metadata. The comparison completed with
unchanged production/state/runtime; its top-level success is not recognition
acceptance. No recognizer replacement or rejection-policy relaxation was made.
