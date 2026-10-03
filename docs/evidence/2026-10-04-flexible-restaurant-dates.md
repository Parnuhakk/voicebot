# Flexible restaurant calendar input — 2026-10-04

## Behavior

The shared ET/EN/RU calendar resolver repairs close month/day spellings and
relative calendar words in bounded date context. Examples include `oktobte`,
`neljanadl oktobte`, `fourth Octobre` and `четвретого октябра`. Regression
fixtures cover a misspelling of every month in each supported language.

Exact booking words, recognized calendar grammar and clock words are protected:
`kahe päeva pärast` stays an offset, `lauaks` stays a booking word and Russian
`вечера` stays evening rather than becoming yesterday. An exhaustive small
alphabet comparison checks bounded edit distance against a full reference
matrix, including adjacent letter transpositions.

Explicit numeric year/month/day forms accept slash/dot separators. Slash/dash
day/month orders resolve only when their valid interpretations name the same
date; competing interpretations ask for clarification. Explicit spoken years
work in ET/EN/RU, including partial month/year answers followed by a day.
February 29 without a year selects the next actual leap day. Impossible dates,
declined dates, competing spellings and unsupported compound years still ask
for clarification. No numeric digit is repaired.

The displayed/stored caller input remains original. Only the preference parsing
copy is repaired. The existing recap delivery and later consent remain required
before a booking write. Availability and the advance booking window still apply.

## Local verification

- Final restaurant suite plus English calendar/clock regressions: **8304 passed**
  in the project's pinned Python 3.13 media environment.
- The full repository run initially had **11311 passed, 14 failed, 10 skipped,
  36 subtests passed**. Comparing those failures with pristine upstream
  `afe1e0c` reproduced **11 existing failures** in hotel/spa language/provider
  fixtures. The three introduced Russian evening failures were repaired and
  passed in the final restaurant run above. The repository-wide suite is not
  fully green.
- The two existing multilingual month/day fixture failures were separately
  reproduced on upstream. Their initial utterances now use the intended caller
  language, matching the current first-caller-language policy.
- HTTP typed and mock speech recognition turns use real routes and the shared
  parser in all three languages. The recognition fixture preserves original
  transcripts, reaches a held recap and does not silently confirm a booking.
- LiveKit SDK final-turn tests exercise the same date repair and retain original
  caller messages. They use local business state and make no telephone calls.
- Chrome 154 restaurant browser checks cover three languages, repaired calendar
  inputs, stepwise clocks/party sizes, recap receipts, confirmations,
  cancellations, reload, microphone encoding and logout. Desktop/mobile layout
  checks passed with **0 page errors and 0 external requests**. Screenshots were
  inspected.
- `flake8.cmd --select E4,E7,E9,F`, JavaScript syntax and `git diff --check`
  passed. Native `basedpyright.cmd` reports **0 errors and 0 warnings** in the
  two new modules. The shared date resolver has no type errors. The changed
  server retains the same **13 existing type errors** as pristine upstream;
  exact diagnostic comparison found no added errors.

## Production verification boundary

Public HTTP/status access was healthy before publication. Live activation is
checked separately using `capabilities.restaurant_flexible_dates_ready`.
Local speech tests use synthetic provider responses, not real acoustic input.
This workspace has no production operator credential for an authenticated live
conversation and no access to the separate native worker's deployed revision.
No live microphone recognition quality or carrier call is claimed.
