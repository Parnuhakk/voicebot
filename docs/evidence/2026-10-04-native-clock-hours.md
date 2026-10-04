# Native clock units must not become opening-hours questions

## Demonstrated boundary

On published restaurant snapshot `2ca82abddc1a7eefb9176b3d59c653307c7bf7cf`,
a bounded real-VAD/Groq diagnostic received one supported English final turn.
The independent reservation parser found the requested date, 18:00 and party
size two, but the conversation policy stored no inquiry: its information focus
and topic were `hours`. The checked reply was 13 characters. Current-turn
correlation and planner availability were valid; model calls, provider errors,
plans and actual booking writes were zero. Audio output was a double, so this
diagnostic does not establish live RoomIO, synthesis or booking acceptance.

The synthetic literal `Please reserve a table tomorrow at 1800 hours for two
guests total.` reproduces that policy diversion offline. The colon form
`18:00 hours` does too. A normal `six PM` control reaches planning. These are
authored test inputs, not retained caller transcripts.

## Minimal correction

`app/restaurant_answers.py` masks only the English `hours` clock unit in its
local information-selection view, using the existing clock selectors and
same-length spaces. Raw input, date/time parsing, language selection, actual
opening/kitchen-hours questions, staff/allergy guidance and consent are unchanged.
There is no global booking-over-information priority or new provider dependency.

An independent review found two P2 boundaries in the first candidate. Six new
failing cases reproduced them. The correction follows only contiguous clock
alternatives and leaves a second hours unit after captured minutes unmasked;
`18 hours thirty hours` cannot expose a malformed plan. Invalid alternatives
still require clarification. These conservative checks do not add a new grammar
for repeated units, hyphenated words or fraction-unit suffixes.

## Verification

- First core red: ten missing-inquiry failures, five real-information controls
  passed. Actual SDK 1.8.4 public audio/manual-commit red: two clock-unit cases
  failed; the original English and Estonian cases passed.
- Corrected focused core: `tests/test_restaurant_spoken_times.py`,
  `tests/test_restaurant_phone_answers.py`, `tests/test_restaurant_conversation.py`
  — **441 passed**, including six red-then-green review boundary cases.
- Actual pinned SDK audio fixture — **4 passed**. English cases start in ET,
  finish the queued ET greeting and English invitation, then latch supported EN.
  The public SDK commit invokes the real finalized hook. Exactly one plan and
  the complete canonical recap precede a separate confirmation; no early booking,
  model call or session error is accepted. STT and output are doubles, not VAD,
  Azure, microphone or carrier evidence.
- Whole corrected 2ca-based source: core **11,873 passed / 81 skipped**;
  pinned-media **12,276 passed / 12 skipped**; both have **36 passing subtests**,
  exit 0. Suites overlap; totals must not be added. Media used network=none,
  the installed immutable worker package, read-only offline test dependencies
  and the installed Node binary, without installing packages.
- Concurrent publication through `b3ca570d1c217bf3915eef617f5b8397851afa1b`
  was normally fast-forwarded. All three owned source/test files stayed
  byte-identical, and the original dirty checkout remained unchanged. Fresh
  combined upstream-probe and affected-core checks: **515 passed / 6 skipped**.
  Fresh integrated pinned-media upstream-probe/audio checks: **84 passed**.
- Both current restaurant Chromium suites passed: ET/EN/RU booking/cancellation,
  voice readback and renewed-delivery guards, zero page errors or external requests.
- Three Python files parse; scoped Ruff E9/F and Git whitespace checks pass.
  The first lint invocation used a venv without Ruff; the installed standalone
  executable passed. External guarded oracles: **177 passed**, zero network,
  subprocess or nonfixture database operations, 97 disposable connections.

Live native EN/ET booking, decline, whole recap, later confirmation, REST read,
cancellation and owned cleanup are separate rollout gates. No physical
microphone, outbound PSTN/carrier or real PMS acceptance follows from these tests.
