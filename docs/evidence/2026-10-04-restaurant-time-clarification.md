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
