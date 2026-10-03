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

## Recovered contributor integration

The server restart erased the temporary worktree. Reviewed commits `b8e5192`
and `bb711a8` were recovered into the persistent isolated worktree
`/home/arle/voicebot-restaurant-release-recovered-20261003`; the original dirty
checkout's HEAD, tracked diff and all 19 status entries remained unchanged.
Normal merges retain published `649d23e` and `20bffec`, including multilingual
spoken dates/times, clarification, approved restaurant answers, voice previews,
language radios, operator navigation and detailed saved-reservation receipts.

The user's later explicit hostname correction supersedes the earlier Meretuule
publication: `75bc112` retires that separate site and redirects. Robot remains
the restaurant/operator website. Local real-host tests deny the retired hostname
with empty HTTP 410/no-store while preserving robot health, assets, facts,
authenticated bookings/history and the existing telephone endpoints.

Fresh full verification after `20bffec` integration and probe repairs:

- Main core, with the still-owned probe file excluded during its repair:
  **10,611 passed, 62 skipped, 36 subtests passed**, 77.56 seconds.
- Complete media, including the repaired probe: **11,022 passed, 6 skipped,
  36 subtests passed**, 102.39 seconds.
- Nine local Chromium journeys and 21 delivery checks passed at the `649d23e`
  checkpoint; the current restaurant journey also passed retired-host denial,
  exact receipt delivery, later ET/EN/RU confirmation/cancellation, gated reads,
  saved-booking reload, speech/date forms, WAV capture, logout and mobile checks.
  All browser requests remained local; page errors and external requests were zero.
- Actual restrictive-archive Docker checks: **5 passed**, 11.35 seconds, using
  an existing local image, no network and read-only nonroot runtime.
- Python and embedded probe-code syntax, JavaScript syntax, asset digests,
  conflict markers, credential patterns and whitespace checks passed.

One full-suite failure was an upstream direct-booking fixture that omitted the
mandatory one-use recap receipt; HTTP 409 correctly prevented confirmation.
The fixture now supplies the preparation receipt and asserts acknowledgement
before separate confirmation. All 73 HTTP tests passed. Three reviewed browser
fixtures likewise needed owned audio identity or programmatic central-retirement
input, rather than clicking disabled recording controls. Runtime guards were
not relaxed; actual browser checks and the narrow static recheck passed.

Independent review reproduced a new rejected-caption SDK defect: assigning a
plain string to `SpeechData.language` bypassed `LanguageCode` normalization and
crashed recognition before caption emission. Six ET/EN/RU real-SDK regressions,
with and without a later supported fragment, failed first. The two-line SDK-type
repair retains private rejection markers and blocks later-fragment consent;
161 native/recovery/language cases passed, and static P1 recheck closed the issue.

The recovered restaurant RTC runner received two lifecycle P1 repairs and a
separate native-key ownership repair. Ambiguous room creation now still deletes
only its generated UUID room. Caller synthesis uses a killable subprocess with
environment-only credentials and privately captured WAV bytes. Conversation,
process and independent cleanup waits are bounded; cleanup failure cannot PASS.
Ownership is proved by real native confirmation hashes, scoped guest, venue,
hold, request fingerprint and immutable canonical response, not an invented key
prefix. Actual `RestaurantCallTools.dispatch`/SQLite regressions prove writes are
visible and cleanup preserves foreign/baseline reservations and action history.
The repair lane reported 63 core passes/6 SDK skips and 69 media passes; the
owner's complete media run above independently includes them. Narrow independent
static review found no remaining P0/P1 in the ownership/lifecycle scope.

Final English-invitation merge `c8afb06`, current-source reruns, publication,
deployed-source/browser verification and real-provider acceptance are subsequent
delivery evidence, not claims implied by these local checkpoint counts.

### Tested publication candidate including `c8afb06`

The final normal merge retains the approved native English invitation without
removing any affirmation/recovery/owned-hold safeguards. The exact invitation
whitelist remains below unknown-outcome, mutation-truth, canonical-recap and
inquiry priorities; appended success prose is rejected. A narrow independent
Codex static review found no concrete P0/P1 in that merge scope.

Fresh sequential full runs on that combined source, including the recovered and
reviewed canonical probe:

- Core: **10,676 passed, 69 skipped, 36 subtests passed**, 81.37 seconds.
- Media: **11,025 passed, 6 skipped, 36 subtests passed**, 103.66 seconds.
- All **nine** local Chromium journeys and all **21** restaurant delivery cases
  passed again; no external requests or page errors. Browser 153.0.8010.12.
- Existing deprecation warnings remain: Starlette/httpx in core and media,
  Python audioop in media. Skipped tests are reported, not called verified.

These are overlapping suites, not a summed test total. Live rollout/provider
metrics are recorded in the persistent goal evidence after delivery; these local
checks do not establish physical-microphone or carrier acceptance.

### Further published natural-conversation integration

Master advanced during publication and rejected the direct push. The tested
`a41ddcc` checkpoint was pushed to the isolated recovery branch instead; no
force-push or contributor overwrite occurred. Normal integration of `f8edaa1`
retains natural complete-turn agreement, initial caller-language selection,
additional voices and grounded dietary recommendation context. A later natural
affirmative now intentionally confirms the current delivered owned proposal;
premature agreement, questions, conditions and declines remain unauthorized.

Independent review found and owner regressions reproduced:

- Unpunctuated "Do I confirm the reservation" was treated as agreement. The
  compositional recognizer now rejects auxiliary/subject inversion while keeping
  "I do confirm"; actual prepared/delivered SQLite tests assert denied approval,
  `consent_required` and no booking.
- A number-only first input could permanently lock a language from misleading
  ASR metadata. Selection now reuses the existing ET/EN/RU numeric vocabulary
  before inference; 18 cases remain unlocked until a meaningful English opener.
- Validated allergen and group-policy detail followups lost inherited topics.
  The two fresh-utterance filters now exempt validated followups only; same-language
  and stale-context guards remain. Six cases preserve exact approved answers,
  allergen/dish selectors and allergy notices without any booking side effect.

These regressions produced **26 expected failures and 4 existing passes** before
the minimal repairs; the complete affected consent/language/natural-speech scope
then passed **413 cases**. Narrow independent static rechecks closed all findings.
Older fixtures were corrected to use an appropriate initial session/utterance,
auto recognition before language selection and a locked hint afterward. Recovery
tests now explicitly prove undelivered agreement cannot write, then require fresh
delivery and subsequent consent. The affected legacy/HTTP/recovery/date scope
passed **7,325 cases**; no runtime guard was weakened to satisfy old fixtures.

The owned RTC runner follows the current full confirmation-question suffix and
tests premature yes, a delivered conditional answer, decline, a fresh recap,
later natural agreement and cancellation. Real ET/EN/RU CallTools/SQLite cases
preserve foreign/baseline rows and history. The lane reports **74 media passes,
68 core passes/6 SDK skips**; ownership and lifecycle/process helpers are unchanged.
Parent execution and review of this alignment remain part of the final gate.

Current `f8edaa1` main-source core checkpoint, excluding the two-file probe lane:
**10,956 passed, 63 skipped, 36 subtests passed**, 91.77 seconds. All nine local
Chromium journeys and 21 delivery cases passed again, with zero external requests
or page errors. Newer published `fc5c4ae` Russian speech/grounded-answer changes
are being independently reviewed before normal integration. These checkpoint
counts do not verify that later combined source or live provider acceptance.

The matching `f8edaa1` main media run, also excluding the scoped probe, passed
**11,332 cases, 6 skips and 36 subtests** in 118.97 seconds. Parent then executed
all **74** current probe cases successfully in 17.85 seconds. The probe-alignment
static review is clear; syntax, assets, credential/conflict patterns and
whitespace checks passed before recording this integration checkpoint.

### Published Russian speech and grounded answers

Normal integration of `fc5c4ae` preserves both contributor features and prior
receipt, capture, ownership and uncertainty guards. New independent static
reviews found two P1s: approving models could speak unverified availability or
booking success, and an allergy question after three other topics lost its
safety classification. Actual HTTP/SQLite/SSML cases produced nine expected
failures and one existing pass before local claim guards, full-input allergy
priority, shared 600-character speech bounds, candidate normalization and the
Russian recap introduction were repaired. The affected two files passed 133
tests. A narrow review then found internal-newline bypass of the recognized
booking claim: two additional actual HTTP REDs, followed by whitespace-normalized
guard matching only. Original reviewed/stored/spoken text is not rewritten.
All independent narrow static findings are now closed; no system-wide semantic
or human-audio guarantee is claimed.

Fresh combined source verification after the last code repair:

- Core: **11,158 passed, 70 skipped, 36 subtests passed**, 105.63 seconds.
- Media: **11,541 passed, 6 skipped, 36 subtests passed**, 154.29 seconds.
- All nine Chromium journeys passed, including three grounded-answer journeys;
  21 delivery/capture/stale-response cases passed, external requests/page errors 0.
- 181 Python AST, 21 JavaScript syntax, JSON, six asset hashes, credential and
  conflict patterns and whitespace checks passed.
- Isolated Docker packaging: **5 passed**, 14.68 seconds. The first attempt
  failed because the running worker's backing image ID was absent from the local
  image store; read-only diagnosis confirmed `No such image`. An explicitly
  existing local immutable image was used next; no pulls, runtime restarts or
  configuration changes were made.

These are overlapping suites, not a summed test total. Immediately before
publication, immutable remote `97684ad` revealed newly published flexible-date
and release-status receipt changes. They are being independently reviewed for
normal integration; the counts above attest this `fc5c4ae` integration checkpoint,
not that newer combined source or live provider acceptance.

### Current receipt/calendar intake checkpoints

The reviewed `fc5c4ae` integration committed `bada923` and is durably pushed to
the isolated recovery branch. Normal `97684ad` integration retains contributor
date spelling, spoken years and channel release-status receipts; scope checks
initially passed 6,264 cases before independent review identified further bugs.

The release receipt must describe the configuration actually loaded by the
website, not just a file path or a new CLI read. A same-path replacement produced
an actual HTTP/file RED. Fingerprints now bind validated restaurant data, public
status uses the retained startup snapshot, and the controller gets that hash from
the running website through bounded loopback HTTP. Worker receipt replacement
still rejects a mismatch atomically. A regression proves changed CLI data cannot
refresh the website's older loaded snapshot and even a wrongly produced new-file
receipt is reported out of sync. Complete status/controller scope: **131 passed**,
6.71 seconds. Two legacy assertions were scoped to forbidden worker room queries,
not the newly required website HTTP read. Independent static recheck is clear.

Three actual Chromium REDs reproduced expired status surviving a pending poll,
visibility restoration and a poll without a deadline. Independent one-second
freshness rendering, immediate visibility rendering and a native ten-second
fetch abort then passed all **24** delivery/status cases, with no external requests
or page errors. The running published website accepted the controller's bounded
loopback query and returned a valid fingerprint; that is wire proof only, not
deployment of this candidate.

Calendar review found malformed spoken-year fallback, accepted numeric date
prefixes inside longer malformed chains, ignored short weekday contradictions,
and year parsing consuming ordinary nineteen/twenty guest counts. The resumed
implementation lane reproduced **13 expected REDs**, then passed 18 focused cases
and **7,642** scoped cases. Only the three date helpers and their regression file
changed. One intermediate day-range regression was corrected in the final scoped
run; no malformed year value is guessed. Parent status/controller/date/deployment
scope independently passed **6,423** cases, 22.98 seconds. An implementation quota
failure made no changes; no probe file changed. Independent narrow recheck and
final combined-source gates remained pending at that point. A narrow recheck then
found month-first malformed-year input still inventing a day. Three actual REDs
reproduced November 2; two ordinary ordinal cases already passed. Deferring the
recognized year span propagated its issue but exposed unconsumed suffix words
being parsed as party 27 (3 failed, 6,267 passed). Routing malformed scales through
the existing bounded suffix parser, with no inferred year value, preserves the
entire date issue and masks numeric words. The final three-date-file scope passed
**6,270** cases, 22.88 seconds, and the independent narrow static closure is clear.
186 Python AST, 21 JavaScript syntax, JSON, six asset hashes and credential,
conflict and whitespace checks are clean. The subsequently published conversational
voice delta `e53de15` has a clear independent static review; normal integration and
owner tests still remain. No current master, physical-microphone or PSTN readiness
is inferred from these earlier checkpoints.

### Conversational-voice integration checkpoint

Normal `97684ad` integration committed `ff7f052`, followed by the independently
reviewed `e53de15` conversational voice delta. Its only textual merge conflict was
the restaurant asset versions; current generated-answer, capture, release-expiry
and voice-selection logic remain together. Fresh combined verification:

- Full core: **11,396 passed / 74 skipped / 36 subtests**, 123.40 seconds.
- Full media, run sequentially afterward: **11,783 passed / 6 skipped / 36
  subtests**, 140.74 seconds. Existing Starlette/httpx and audioop warnings only.
- All **nine** Chromium journeys and **24** delivery/status cases passed.
- Isolated actual Docker packaging: **5 passed**, 14.50 seconds.
- 188 Python AST, 21 JavaScript syntax, JSON, six current restaurant asset hashes
  and cumulative credential/conflict/whitespace scans are clean.

The fresh pre-publication preservation snapshot at 22:31:34 UTC confirms healthy
services, database integrity, the current owned incoming route, original protected
checkout/diff/19 status entries and 23 unrelated running-service identities.
There was **one active native room**, so no rollout was initiated. Upstream had
advanced to `0487c2e`, including family facilities, booking side questions,
capability guidance, contextual clocks and faster speech. That exact immutable
delta is being independently reviewed and normally integrated; these passing
counts attest the `e53de15` checkpoint, not the newer combined source or live RTC.

## Pre-rollout preservation qualification

Read-only hash-only snapshot at 2026-10-03 20:34:39 UTC records healthy web,
worker and bridge on `67af353`, original shared volumes and a valid incoming
robot POST route. Existing canonical reservations/actions, legacy writes/stay
rows and calls/bookings/events are hash-preserved. Mutable session/hold hashes
had already changed before this session's rollout; unchanged row bytes are not
claimed for those lifecycle tables.

The original incoming number is no longer owned in the carrier account. A
different current owned number has the correct configured incoming route. This
external change predates our deployment: this session neither purchased/released
numbers nor rewrote account/bridge settings. Delivery must preserve the fresh
current configuration and report that original-number continuity is unproven,
rather than overwrite another owner's changes or claim the old baseline matches.
