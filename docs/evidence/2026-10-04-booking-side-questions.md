# Answer a side question and resume booking

## Behavior

Restaurant questions during collection are answered before the same missing
date, exact clock or total guest count is requested again. Stored details,
clarification choices and offered alternative clocks survive the question.
Exact selections from the server's offered clocks are handled as those offered
24-hour times, without inferring AM/PM for other requests.

Questions during an owned, unexpired proposal keep the table hold and expiry but
replace the proposal object, revoke delivery/approval, answer from venue facts
and read the full summary again. No new search, hold or write occurs for the
question. Confirmation requires the new summary's delivery/reading receipt and
a subsequent affirmative turn. Old receipts and late native playback cannot
authorize it. An expired proposal is rechecked before a new summary/consent.

See [operation and deployment boundaries](../operations/booking-side-questions.md).

## Local evidence

Project Python 3.13.15, actual FastAPI routes and temporary SQLite, synthetic
provider responses/audio:

- New interruption module: **34 passed** covering ET/EN/RU, typed and microphone
  turns, all three collection stages, repeated questions, summary interruptions,
  hold/expiry/receipt identity, one saved reservation, generated wording and
  provider failure, unknown/numeric/date questions, allergy safety, partial
  transcripts, expired proposals, and spoken/read delivery boundaries.
- Restaurant conversation/reasoning/HTTP/receipt/consent/session-language checks:
  **576 passed** before the last upstream integration.
- Actual installed LiveKit SDK with local speech/output doubles: **100 passed**,
  including three new multilingual side-question booking scenarios. No live
  recognition, carrier call or paid model/audio generation was used.
- Chrome 154 website checks passed in all three languages, including twelve
  collection/summary side questions, fresh receipts, completed saved bookings,
  cancellation, reload, microphone capture and desktop/mobile layouts.
  **0 page errors and 0 external requests**.
- `basedpyright.cmd --pythonpath <project core Python> --level error` on all four
  changed production Python modules: **0 errors, 0 warnings**.
- `flake8.cmd --select E9,F`, JavaScript syntax and diff checks passed.

The first broad run exposed 13 existing language-related failures, reproduced
on untouched upstream `fc5c4ae`. The later upstream release/date fixes were
integrated, retaining the new booking flow. Final integrated results and CI are
reported in the PR; earlier baseline failures must not be described as a green
complete suite.

## Public readback

Deployment is checked using `/health` and the public restaurant metadata's
`booking_interruption_version: resume-booking-v1`. Public readback establishes
deployed code, not authenticated live model behavior. Production operator and
provider credentials are unavailable in this Windows workspace; live voice
quality and speech recognition therefore remain outside these local checks.
