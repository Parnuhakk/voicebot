# Restaurant release reliability — 2026-10-03

## Canonical source and preservation

This follow-up starts from published restaurant release `8bab6fb`. Its
`RestaurantAdapter`, physical tables, configurable 90-minute sittings,
`RestaurantCallTools`, restaurant knowledge and authored frontend remain intact.
The earlier local `DemoTableAdapter` alternative was never deployed. Do not
activate its different ledger beside existing `restaurant_reservations` records.
Published contributor updates must be integrated normally before final rollout.

The original dirty checkout was not reset, pulled, switched or used as a build
context. Hash comparison retained its HEAD, tracked diff and all 19 status
entries. A private mode-600 hash-only runtime snapshot recorded existing legacy
and restaurant rows, configuration and the unchanged incoming route. No row
contents, credentials, recordings or transcripts are included here.

## Reproduced repairs

- Direct recap acknowledgement previously accepted a hold identifier alone.
  Preparation now issues a one-use receipt bound to the exact pending object,
  canonical text and language. Deliberate reading consumes it; later explicit
  confirmation remains separate. Replaced, expired, changed or uncertain
  preparations cannot reuse it.
- A rejected direct request could increment the general acquisition counter and
  preserve an incomplete stream's receipt. Disconnect revocation now follows
  the exact private audio transport. Its identity is not serialized to clients.
- Earlier microphone capture could attach pre-recap speech to a new text recap.
  Text turns retire capture centrally; audio submissions require the current
  capture generation/session/epoch. Private responses are checked after body
  parsing, late readbacks are retired, and completed writes do not await
  unrelated booking/history reads. Failed writes are not automatically retried.
- Explicit weekday corrections retained an earlier date. Matching owned holds
  also made ambiguous-consent recovery appear unavailable. Corrections now
  replace the date; live owned holds are durably revalidated and re-prepared
  without confirmation or additional holds. Allergy guidance precedes price,
  and price intent precedes menu descriptions.
- Release comparison omitted restaurant/history configuration; bridge replacement
  failure could leave the cleanly stopped old bridge offline. Profile comparison
  now includes these settings, and replacement is inside protected recovery.
  A concurrently replaced identity is never restarted and failure is not hidden.
- Restrictive archive directories reproduced non-root import failures. Both
  Dockerfiles now give application and fixture copies to the existing runtime
  user, without making the service root or adding dependencies.

## Verified local checkpoint before upstream fan-in

Commands ran in an isolated environment, using the existing project/media Python,
Node and installed Playwright. These are checkpoint counts, not final rollout
counts; overlapping suites are not added together.

- Full media: `python -m pytest tests -q -p no:cacheprovider --tb=short`:
  **3,147 passed, 6 skipped, 36 subtests passed**, 62.83 seconds. Two existing
  deprecation warnings: Python `audioop` and Starlette/httpx integration.
- `node tests/run_browser_checks.cjs <playwright> <project-python>`:
  all **nine** journeys passed, zero external requests. Restaurant journeys
  cover ET/EN/RU, separate consent, readback/cancellation, synthetic WAV capture,
  logout isolation and desktop/mobile layouts.
- `node tests/restaurant_delivery_checks.cjs <playwright> <project-python>`:
  **21 passed**, zero external requests. Endpoint interceptions exercise real
  UI control flow, not independent production booking acceptance.
- Actual restrictive-archive packaging: **5 passed**, existing local image,
  network disabled and read-only UID10001 runtime.
- Scoped independent Codex-account static reviews reported no remaining P0/P1
  in policy repairs, receipt/transport/controller/packaging or the new UI guards.
  Reviewers did not execute these suites or approve an unverified rollout.
- Python/JavaScript syntax, asset digests, conflict-marker, credential-pattern
  and whitespace checks passed.

An initial parallel run timed out in three unchanged Node checks and two browser
operations during heavy host load. They passed unchanged in sequential reruns.
Two legacy packaging assertions were updated to retain the fixture-copy check
with its repaired ownership. No deadline or correctness guard was weakened.

Final upstream fan-in, full core/media reruns, commit/push, deployed source/assets,
bounded real-provider restaurant acceptance and preservation comparison are
recorded separately when verified. Synthetic browser audio does not establish
physical-microphone, acoustic-quality, PSTN or production-readiness acceptance.

## Verified upstream fan-in

Normal integration of `3af499b` preserves the published canonical Meretuule
domain, authored short ET/EN/RU recaps/spoken dates, closed explicit Estonian
confirmation spellings and saved-booking navigation. Conflict resolution retains
both the new booking links/date/page reset and the repaired nonblocking reads,
capture ownership and one-use recap controls.

Fresh serial full runs after that integration: core **2,928 passed / 61 skipped**
(44.09 seconds), media **3,193 passed / 6 skipped** (61.23 seconds), each with
36 passing subtests. All nine browser journeys and all 21 restaurant delivery
checks passed again. Restaurant journeys additionally verify ASR confirmation,
saved bookings after reload and page reset. External requests remained zero.

Restaurant asset digests: JavaScript `9d03bebcf432`, capture `fb9adf1eaf2e`,
playback `27698f675462`, CSS `34bd7c817179`. Deployment and real-provider results
are still pending at this versioned pre-rollout checkpoint.

The merge-only review caught a verification race: the published journey checked
bookings immediately after write controls unlocked. A gated actual booking read
reproduced the failing assertion. The journey now proves controls unlock while
the read is held, then waits for the exact booking ID/localized status before
checking rows, page and highlight. That real SQLite/Chromium journey passed;
the narrow independent static recheck closed the finding. Production readbacks
remain nonblocking. Three-language committed-cancellation/lost-response cases
also reproduced confirmation-specific uncertainty wording; neutral short action
wording now preserves sticky uncertainty and forbids repeating the mutation.
