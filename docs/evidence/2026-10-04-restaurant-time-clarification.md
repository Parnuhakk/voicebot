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

## Candidate verification

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
