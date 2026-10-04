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

### Latest capability, family and booking-side-question integration

The reviewed voice checkpoint committed `da29be5` and is pushed to the recovery
branch. Normal `0487c2e` integration keeps contributor family facts, capability
disclosures, side-question continuation and faster speech, while retaining local
receipt, ownership, allergy, language, capture and uncertain-write protections.
Eleven textual conflict files were resolved explicitly; updated faster default
recap-rate fixtures remain aligned with the published source.

Three independent new-delta reviews found five P1s: mandatory capability topics
could be dropped after three information topics; a positive mixed booking clause
discarded later cancellation/correction; compact ranges chose an endpoint;
children's-menu allergens inherited the ordinary catalogue; and a side question
could restore an obsolete party/date/time proposal after a correction.

Capability repair produced **4 actual HTTP REDs**, then **175** phone/reasoning
passes in 12.15 seconds. Canonical allergy/capability topics precede optional
information before truncation. Positive clause extraction accepts only a terminal
clause, so later unknown instructions are not silently discarded. Both independent
static closures are clear.

Compact-clock parser/HTTP regressions reproduced **28** prefixed/bare/request
failures plus **4** recognized-suffix failures. A reserved pytest parameter and an
unsupported suffix fixture were corrected before production implementation.
Context-bound compact-range rejection then passed **6,456** date/clock cases.
Narrow review found attached supported suffixes still selecting 19:00: **8 REDs /
4 existing passes**. Replacing the trailing word boundary with a digit guard kept
context containment and passed **6,464** date/clock cases, 23.68 seconds. Final
narrow independent static closure is clear.

Three actual ET/EN/RU HTTP REDs confirmed the children's-menu allergen mismatch.
Canonical unknown-detail/safety guidance now uses a full-input family-allergen
selector independent of the three-topic cap. An additional actual RED covers two
prior capability questions; neither may hide the unknown children's-menu scope.
Narrow review found inherited salmon selection still bypassing that guard: three
ET/EN/RU two-turn REDs preceded blocking previous-dish inheritance for an explicit
family question. A current explicitly named approved dish remains supported.

The disjoint side-question lane reproduced **22 REDs** and passed **612** scoped
cases. Corrections in non-information clauses revoke the old proposal, retain
corrected inquiry details and require a fresh check, exact recap and later consent.
Narrow review exposed numeric-terminal sentence punctuation: six text/audio
ET/EN/RU REDs. Recognized question-start separation preserves internal clock/date
dots and day ordinals. The first scoped run passed 950 but failed two Estonian
cases because the existing menu fixture starts with `milline`; adding that actual
question prefix passed **952** scoped cases, 68.78 seconds. All family, clock and
side-question independent narrow closures are clear; their reviews were static.

Fresh combined `0487c2e` integration verification:

- Core: **11,727 passed / 77 skipped / 36 subtests**, 127.34 seconds.
- Media, afterward: **12,126 passed / 6 skipped / 36 subtests**, 166.33 seconds.
- Eight Chromium journeys passed initially; the restaurant journey found that a
  new fixture's broad `unroute` removed the older gated-readback handler. Removing
  only its own handlers restored both failure-path checks; the complete restaurant
  journey then passed, including all languages, 12 side questions and gated reads.
- All **24** delivery/status cases passed, no external requests or page errors.
- Isolated Docker packaging **5 passed**, 11.10 seconds; 193 Python AST, 21 JS
  syntax, JSON, six asset hashes and credential/conflict/whitespace checks clean.

Newly published `8123638` includes natural Estonian wording, medical-food guidance,
proposal renewal/mobile feedback and runtime type boundaries. Normal `0487c2e`
integration is committed/pushed as `5e91f5a`; the newer delta was inspected in three
disjoint independent static reviews before normal integration.

### Proposal renewal, natural wording and runtime boundaries

The new renewal route initially lacked the fresh receipt required by the retained
protected workflow. Three ET/EN/RU HTTP REDs preceded moving the existing bound
receipt issuance into the shared prepare/renew result helper. The UI stores this
receipt with the canonical text/language and monotonic server lifetime; late async
results remain generation/session/epoch guarded. Receipt attempts, including stale
ones, are one-use; premature confirmation retires the proposal without writing.
Regressions preserve those closed failures rather than relaxing the protocol.

The newly renamed venue `Meretuule` initially lost Russian SSML pronunciation.
An actual canonical-recap RED preceded extending the existing approved-name alias
to the bare label, retaining the old full-label alias and exact literal text.
The integration scope passed **601** cases, 28.27 seconds. Both narrow independent
static closures are clear; the shared adapter/type-boundary review is also clear.

The first full core run found six failures: allergy-plus-price no longer returned
only canonical allergy guidance, and unknown cancellation spoke about whether a
reservation was saved. Restore allergy topic priority and use natural, action-
neutral uncertainty speech in all languages. Existing lost-result SQLite tests
retain the committed cancellation, history and sticky no-repeat state. The first
mobile quality run also reproduced Russian voice controls below the first screen;
two small header/breadcrumb spacing rules fix wrapping without hiding disclosures,
labels or reducing controls. The scoped **228** cases and full quality journey pass;
the disjoint narrow static closure is clear.

Fresh `8123638` combined-source gates:

- Core: **11,849 passed / 80 skipped / 36 subtests**, 137.26 seconds.
- All **ten** Chromium journeys passed, including ET/EN/RU first-screen controls,
  renewal requiring a new read, proposal expiry and sticky uncertain mutations.
- All **24** delivery/status checks pass; no external browser requests/page errors.
- Isolated Docker packaging **5 passed**, 10.46 seconds; 196 Python AST, 22 JS
  syntax, JSON, six asset hashes and credential/conflict/whitespace checks clean.
- Media, afterward: **12,254 passed / 6 skipped / 36 subtests**, 166.47 seconds.

A newer small published `56e7c9f` delta repairs spoken Estonian menu spelling and
mobile spacing. Its independent static review is clear; normal intake preserves
the owner's additional flex/min-width declarations and recomputes the CSS asset.
None of these local checkpoints proves live-provider or carrier acceptance.

### Final published spelling intake

Normal integration of `56e7c9f` preserves spoken Estonian `menü`/`menüü` recognition
and the mobile layout fix alongside the reviewed owner price/allergy guards and
additional breadcrumb flex/min-width. The resulting CSS hash remains
`bcee0c7e5fde`; JavaScript `f054ddea9a94`, playback `279720c050cc` and capture
`fb9adf1eaf2e` are verified against their index references.

Final combined-source core **11,852 passed / 80 skipped / 36 subtests**, 135.37
seconds, all **ten** Chromium journeys, **24** delivery/status cases and **five**
isolated packaging cases (10.63 seconds) pass. Syntax/JSON/asset/hygiene checks are
clean. Final sequential media **12,257 passed / 6 skipped / 36 subtests**, 155.64
seconds; all pre-publication gates are satisfied.

The reviewed controller was atomically installed under the shared lock, preserving
the prior installed file privately. Its SHA256 is
`11674bd00a92490b252e046547f69374293c420ad992b500d33bece849fe4763`.
This install did not restart native services or change systemd units/settings.
The fresh pre-publication snapshot at **2026-10-03 23:56:26 UTC** records healthy
services, the valid current incoming robot POST route, four database integrity
checks, zero active rooms, unchanged protected checkout/all 19 status entries and
all 23 unrelated running-service identities. Worker/bridge were already at
contributor revision `56e7c9f`; that is not this session's final deployment proof.

## Published live release — October 4

Final normal integration **`2ca82abddc1a7eefb9176b3d59c653307c7bf7cf`** was pushed
to both the recovery branch and `master` without force or discarded contributor
history. The configured webhook deployed that exact source. At **00:00:30 UTC**,
the running healthy web container and public robot website served the exact index
and all six matching assets. Restaurant-only/synthetic/language DTOs are correct;
`/hotel` and `/hotel/` return 410 without redirects, unauthenticated confirmation
returns 403.

The installed controller returned **`PASS: release_synced`**. At **00:03:50 UTC**,
worker and bridge are healthy on the exact same media image, labelled with that
release and the running web container identity. Native dependency validation
passes; public release status is `in_sync`, with common fingerprint
`182ce15549e2ce6d18f2e015592332f8717a5e26b6a157bd87ee039a04abd4ef`.
That is a dated controller identity check, not perpetual carrier/provider health.

Headless Chromium on the actual public site verifies ET/EN/RU landmarks and
first-screen mobile controls, no overflow, page errors, external or mutation
requests; it does not access a physical microphone. The retired Meretuule host
does not serve the website, API, health or asset paths and does not redirect:
the live proxy responds **503**, not the initially over-specific expected 404.
No DNS removal or carrier operation is inferred, and that hostname was not
republished or changed during this release.

The first bounded fictional RTC batch produced a **Russian PASS**: seven final
inputs, nine replies, three canonical recap segments and 4,117 voiced frames;
premature/conditional/declined turns did not write, and an independent strong-
ownership ledger check verified the later confirmed reservation and cancellation.
ET/EN attempts failed after two final inputs/four replies without a canonical
recap. The batch therefore failed overall; no three-language PASS is inferred.

An isolated real-provider boundary check identified the machine ISO caller date
as ambiguous in Estonian while time/party were correct. The runner also failed
to recognize the existing canonical date-ambiguity clarification. Six actual
unit REDs preceded a probe-only repair: speak one named calendar date using the
existing date renderer (without an additional relative weekday), and answer
that canonical ambiguity prompt with the explicit date. All **80** probe cases
pass, including ownership, premature/conditional/declined writes, exact ledger
details, bounded independent cleanup, cancellation and child-process failure.
No application speech/parser/consent policy, room deadline or cleanup guard was
relaxed. A failed temporary diagnostic wrapper was repaired separately; no raw
speech/transcript/credential was saved or printed.

The probe-only independent static closure is clear. Fresh full source suites pass:
**11,858 core / 80 skipped / 36 subtests**, 141.62 seconds, followed by
**12,263 media / 6 skipped / 36 subtests**, 156.02 seconds. Browser/packaging
results above attest the unchanged application; `git diff 2ca82ab -- app data/demo`
is empty. Neither production image copies the host acceptance script.

The named-date provider batch still **failed overall**: Estonian reached six
inputs/eight replies/two canonical recaps but returned `probe_confirm_unproven`;
English returned `probe_no_recap` after two inputs/four replies; Russian again
passed its complete owned confirmation/cancellation, 4,126 voiced frames.
Blind acceptance retries stopped. Scoped boundary diagnostics now inspect only
parsed field/keyword/confirmation predicates, canonical reply categories and
owned-ledger count/match/status flags, never raw text or credentials.

Application services remain at verified `2ca82ab`; shipping the reviewed host
probe/evidence with `[skip cd]` deliberately avoids restarting that unchanged
runtime. Final preservation and completion remain gated on actual ET/EN proof,
the final cleanup results and the final evidence audit.

### Live clock-unit root cause and caller-fixture repair

The same finalized English input was traced through a temporary SQLite policy
mirror: literal premature `Yes` did not lock a language; the subsequent English
reservation request selected English correctly but acquired the `hours` topic,
leaving no booking inquiry. A whole-WAV provider check reproduced that topic.
The sole matched word `hours` was within the existing clock-prefix span; no
opening/closing word or information-question prefix existed. This supersedes
the earlier unconfirmed language-lock hypothesis, not a reason to relax it.

Seven actual native/HTTP REDs preceded replacing only `hours` inside existing
clock spans or immediately after them with equal-width spaces. Clock, safety,
capability and independent opening-hours wording remains intact. Native requests
now yield canonical planning with no write; HTTP audio-double turns prepare an
owned recap but leave delivery/approval false. Three genuine hours-question
regressions remain read-only. A first HTTP GREEN attempt used a nonexistent test
recap key; the assertion now checks the actual canonical `start` field, without
changing runtime receipt authorization.

Estonian whole-WAV checks reproduced the wrong numeric ordinal and unsupported
short consent before RTC. Neither another approved caller voice nor neutral
delivery solved them. The host fixture now speaks explicit Estonian day words,
four guests and six in the evening, with the existing accepted natural affirmative
`Jah, olen nõus.`. Thirty-two actual REDs preceded this change, with independent
literal expectations for all 31 calendar days. The revised request and consent
both pass same-model real-provider preflight; no raw audio/transcript is saved.
This does **not** establish reliable recognition of every short affirmative.

Phone/time/correction scopes **369 passed**, 18.03 seconds; probe/phone/consent/
native scopes **566 passed**, 36.86 seconds. Both disjoint independent static
closures are clear; all ten fresh Chromium journeys pass. Final whole-source
core **11,900 passed / 80 skipped / 36 subtests**, 153.98 seconds, then media
**12,305 passed / 6 skipped / 36 subtests**, 181.74 seconds. All 24 delivery
checks and five isolated packaging cases (13.66 seconds) pass. 196 Python AST,
22 JavaScript syntax, JSON, six asset hashes and cumulative 119-file hygiene
checks are clean. Counts overlap between environments and are not summed.

The first pre-publication snapshot attempt safely deferred on the busy shared
controller lock. The bounded retry captured **2026-10-04 01:03:54 UTC** under
that lock: all services healthy, current incoming route and four database
integrity checks valid, zero active rooms, unchanged effective configuration
since the first rollout, all 23 unrelated running services and the original
protected checkout retained. This snapshot includes immutable call-session
identity hashes; holds remain ephemeral lifecycle state, not historical records.
Publication, idle reconciliation and new live RTC proofs remain pending.

### Published clock repair and actual RTC results

The verified repair is committed and normally pushed to both recovery branch and
`master` as `2aced8392e09a1db71c095999e5a2fe910e86114`. At **01:07:12 UTC** the
running public web container is healthy on that source, with the exact index,
all six assets, restaurant-only ET/EN/RU DTO, retired hotel HTTP 410 and
unauthenticated confirmation HTTP 403. Native worker/bridge at **01:08:58 UTC**
are healthy on the same revision and image, bound to the actual running website
container. Their common loaded fingerprint is
`ce56374ff7079d3765303111e7e3814f54496dd99e2505640233ab0347ffdea5`;
dependency check passes. The first explicit controller invocation deferred on
the shared lock while the scheduled controller reconciled; the later invocation
returns `PASS: release_current`. Installed controller bytes remain unchanged.

The new fictional real-provider RTC batch on that exact runtime:

| Language | Outcome | Final inputs / replies / recaps | Voiced frames |
| --- | --- | --- | --- |
| ET | FAIL `probe_no_recap` | 2 / 4 / 0 | not accepted |
| EN | PASS, owned confirmation and same-booking cancellation | 7 / 9 / 3 | 4,206 |
| RU | PASS, owned confirmation and same-booking cancellation | 7 / 9 / 3 | 4,116 |

Both successful flows independently prove exact intended date/time/party and
zero premature, conditional or declined writes, with later explicit consent and
bounded cleanup. The aggregate batch **fails** because ET is not accepted.
It completes with zero active rooms and no native restart. ET preflight success
does not substitute for its RTC failure; a scoped no-confirmation finalized-turn
diagnostic is the next justified step, not blind repetition.

Fresh unauthenticated public Chromium at **01:18:45 UTC** verifies ET/EN/RU
mobile voice/microphone controls on the first screen, five widths without
overflow, zero page errors/external requests/mutation requests, and refreshed
`in_sync` status. A prior browser attempt stopped at its stale alignment receipt
while the long RTC batch held the deployment lock. The 180-second freshness
guard correctly refused a current-status claim; it was not weakened, and the
controller refresh resolved that verification gate. No physical microphone or
carrier acceptance is implied.

### Qualified ET root cause after the failed RTC batch

The scoped ET finalized-turn diagnostic finishes without live confirmation:
both owned-ledger reads remain empty and cleanup leaves zero rooms. Its temporary
policy mirror sees a supported-language candidate and the exact requested
date/time/party only when the parser is forced to treat a prior inquiry as active;
there is no recognized booking keyword, no information topic, and no stored
inquiry. Actual replies are categorized as English `information_unknown`.

A same-provider whole-WAV **sequential policy** check then independently isolates
both failures: the synthesized premature Estonian `Jah` is recognized as a short
English `Yeah`/`Yep` with supported EN metadata, selecting and locking EN. The
following recognized ET request lacks the booking keyword: parsing **without**
a forced prior returns `None`; parsing with `{}` extracts the correct fields.
The earlier preflight therefore established only field extraction and is not
evidence of usable booking intent, planning, or RTC acceptance.

Ten actual state/audio-HTTP/installed-SDK REDs precede adding only `yeah` and
`yep` to the existing weak-language-evidence set. Exact explicit commitments,
selected-language stickiness, unsupported-source rejection and later owned
consent remain unchanged. The repaired scope **462 passed**, 26.37 seconds.
The caller fixture now says natural `Soovin lauda…`; the date/time/party and all
probe protocol limits remain unchanged. An actual same-voice/provider preflight
now requires the parser **without prior**, canonical planning and independently
expected fields. Sequential premature acknowledgement, request and affirmative
all pass those appropriate predicates; no dispatcher action is executed.

Both new disjoint independent static reviews are clear; reviewers did not run
providers or suites. The canonical probe **112 passed**, 20.11 seconds. All ten
fresh Chromium journeys, all 24 delivery cases and five isolated Docker packaging
cases (10.54 seconds) pass. Fresh own-source core **11,908 passed / 80 skipped**,
145.71 seconds; media **12,315 passed / 6 skipped**, 159.02 seconds; each has 36
passing subtests. Syntax/JSON/assets and cumulative 119-file hygiene are clean.

The pre-rollout snapshot at **01:32:17 UTC** retains all stable rows from before
the first publication, four database integrity checks, original volumes/current
incoming route, unchanged effective configuration, zero rooms, all 23 unrelated
service identities and the protected checkout. A contributor native release
`598a1a1` appeared during verification; published `master` now normally includes
it as `2b65eee`. The session froze that intake in a read-only persistent worktree
and reviews it before normal integration. These own-source counts do not verify
that still-pending combined source. No stale/force push or runtime overwrite is
attempted. Final combined gates, publication, reconciliation and RTC/preservation
acceptance remain pending.

### Normally integrated final contributor refinement

Verified own weak-acknowledgement repair checkpoint `7a1bf07` is committed.
The unchanged native tests have identical Python AST to `2aced83` after excluding
the new regression; other native-test differences are formatting only.
Frozen published `2b65eee` is normally merged without conflicts. Its seven
changed files are byte-identical in the combined tree, preserving contributor
clock-alternative/repeated-unit safeguards, grounded allergen-capability aliases,
installed-SDK audio regressions and separately qualified evidence.

Both disjoint NEW-upstream static reviews are clear. Final combined core
**11,950 passed / 81 skipped / 36 subtests**, 160.25 seconds. All ten combined
Chromium journeys, all 24 delivery cases and five isolated packaging cases
(10.51 seconds) pass. 197 Python AST/22 JavaScript syntax/JSON/six assets and
cumulative 121-file credential/conflict/whitespace checks are clean. Final
sequential combined media **12,361 passed / 6 skipped / 36 subtests**, 173.19
seconds, exit 0. The normal merge is now verified for publication; new live
acceptance and final preservation remain required. Earlier own-source or
contributor counts are not substituted for these combined-source results.

### Verified merge publication and running web

Normal reviewed merge `8494f8a7c6a5917f2811bb3178e11e6164fcdebf` is atomically
pushed to recovery branch and `master`, retaining `7a1bf07`, `2b65eee`, `598a1a1`
and all prior contributor history. Web proof at **01:45:49 UTC** verifies that
exact running image/source, health, restaurant-only ET/EN/RU DTO, exact index and
six assets, retired hotel HTTP 410/no redirect and unauthenticated confirmation
HTTP 403. Its newly loaded fingerprint is
`17397da1f0d7ea37095b38469f42bb786d050f9bd581a06db1ca1fd8da71a29a`.
Explicit installed-controller reconciliation returns `PASS: release_current`;
the separate native identity/dependency verification is still required before
the new fictional acceptance batch.

Retired-host read-only proof at **01:46:35 UTC** verifies root, health, restaurant
DTO and JavaScript paths all return the actual generic proxy HTTP 503, without
redirect or application content. No DNS-removal, account/ingress change or retired
hostname republication is claimed.

### Meaningful-language runtime acceptance and preservation qualification

Native verification at **01:47:31 UTC** establishes worker/bridge health, same
media image, bound running web container, successful dependency check and the
same loaded fingerprint as web on `8494f8a`. The unchanged installed controller
matches reviewed repository bytes.

The bounded canonical RTC batch retains bare premature agreement, conditional
agreement and decline checks, then requests a fresh recap before consent:

| Language | Result | Final inputs / replies / recaps | Voiced frames |
| --- | --- | --- | --- |
| ET | FAIL `probe_confirm_unproven` | 6 / 8 / 2 | not accepted |
| EN | PASS, exact owned confirmation and cancellation | 7 / 9 / 3 | 4,202 |
| RU | PASS, exact owned confirmation and cancellation | 7 / 9 / 3 | 4,113 |

ET now reaches recaps but still does not prove the intended owned confirmation.
EN/RU independently verify exact intended date/time/party, zero premature,
conditional and declined writes, later consent and same-booking cancellation.
Aggregate acceptance **fails**; whole-WAV preflight is not substituted for ET RTC.
The batch ends at **01:56:58 UTC** with zero rooms, healthy services and unchanged
native container identities. A single instrumented canonical ET diagnostic is
scoped to finalized-input consent/rejection flags, closed reply categories and
owned-ledger counts; it changes neither dialogue protocol nor runtime guards.

Read-only preservation at **01:57:00 UTC** retains all stable historical rows
against both first and immediate pre-publication baselines, immutable call-session
identity hashes, four database integrity checks, effective configuration, original
volumes, current incoming route, all original 23 unrelated service identities and
the protected checkout's HEAD, tracked diff and 19 status entries. One additional
unrelated service is preserved too. No raw records or credentials are saved.

The original composite comparison exits nonzero on ET acceptance and on an
incorrect revision predicate: the private snapshot helper reads only web-specific
`SOURCE_COMMIT`, which is absent on native services. A separate retained
qualification uses the captured native `voicebot.release` labels, correctly
matching `8494f8a`, and the independently verified loaded identity. The failed
original proof is not rewritten; **preservation and source alignment pass, ET
acceptance does not**. Mutable hold/session lifecycle bytes are not asserted
unchanged, and original-number continuity is still not claimed.

### Supported negative-path and caller-only qualification

The instrumented unchanged canonical ET dialogue at **02:10:23 UTC** reproduces
the confirmation failure. Its decline and consent finalized captions both carry
the worker's explicit unsupported-source marker; both actual replies are ET
repeat-input recovery. All six owned-ledger reads remain empty, two exact ET
recaps are received, cleanup leaves zero rooms and native identities remain
unchanged. Original provider language cannot be inferred from the substituted
caption. This establishes rejection before approval; it does **not** rule out
an additional delivery-callback problem or prove semantic decline handling.

An independent Codex-account static review confirms those limits. A default
reviewer route initially hit its Go usage limit and produced no review; the
requested supported reviewer path completed. A complete recap caption alone is
never accepted as evidence of the internal delivery callback. Fresh owned
confirmation must still prove the whole guarded path. Negative RTC acceptance
will also require recognized conditional/decline cues without rejection markers,
not merely empty ledger reads after unsupported input.

Same-provider PCM to installed real Silero VAD/native STT proves isolated old
consent can be accepted, but does not reproduce RTC transport. Controlled longer
caller variants are qualified before retention: one is rejected as unsupported;
others retain ET metadata but corrupt an expected confirmation word. None is
accepted by broadening the runtime grammar. A simple declarative affirmative
passes existing composition, and the clearer decline passes supported ET and
isolated no-approval/no-write checks. Short cancellation and a Kert full-context
control fail the existing exact cancellation predicate; an Anu full-context
control passes it. No alias is added to authorization lists.

The selected test caller now uses approved **Anu** with natural affirmative,
explicit decline and the existing full-context same-call cancellation request.
Whole seven-turn Anu PCM → real native VAD/STT → temporary canonical policy
passes: supported input, exact intended date/18:00/party-four planning, no
premature/conditional/declined write, fresh second recap, later confirmation and
same-booking cancellation. The isolated delivery acknowledgement is explicitly
simulated; this is **preflight, not RTC**. Its first scratch helper used a
nonexistent connection method, failed without acceptance, and was corrected only
after reading the actual read-only connection context manager.

Four reply-fixture expectation REDs and one voice/cancellation qualification RED
precede the retained four-literal caller change. The existing short affirmative
control is preserved. Latest scope **432 passed**, 29.61 seconds; own-source core
**11,952 passed / 81 skipped / 36 subtests**, 133.62 seconds. Operator voices,
language rejection, consent/cancellation grammar, recap rate, exact ownership,
history, conversation limits and independent cleanup remain unchanged.

Fresh preservation at **02:38:59 UTC** retains configuration, volumes, stable
first/last historical rows, four database integrity checks, current incoming
route, zero rooms, protected checkout and all 23 original unrelated services.
Another normally published contributor release `9721803` is now running; its
15-file intake is frozen in a read-only worktree for disjoint business/UI review
and normal integration. These own-source counts do not verify that combined
source. Fresh combined checks, publication and actual supported-input RTC
acceptance remain required.

Final caller-only source gate: media **12,363 passed / 6 skipped / 36 subtests**,
192.88 seconds, exit 0, following the own-source core gate above. The application,
demo data and operator voice settings are byte-unchanged from tested `8494f8a`;
the retained probe AST differs only in its four qualified ET fixture literals.
Syntax, intended three-file scope, credential/conflict/whitespace checks pass.
This checkpoint is safe to commit before the normal contributor merge; it is not
an acceptance or combined-source completion claim.

### Guest-current contributor intake and whole-question retention repair

Caller qualification is retained in `8182f7a`, then contributor `9721803` is
normally merged into `ea92957`. Both histories remain ancestors; there is no
force-push, reset or protected-checkout mutation. The new UI/browser static review
finds no P0/P1, but its layout matrix asserts guest-workspace overflow only, not
whole-page overflow freedom. Both static reviewers are independent Codex-account
lanes; neither substitutes for the owner's executed checks.

The business reviewer identifies a new P1: the whole-read whitelist clears a
valid incomplete inquiry and replaces recognized location/highchair answers with
unknown-information recovery. Owner's isolated canonical reproduction extends
the same defect to seven already-supported direct question forms. Exact FAQ-demo
and parking controls retain preferences. Fourteen state/HTTP regressions fail
with the missing canonical answer; seven unknown-count mixed-question controls
pass before the repair.

The minimal fix adds those seven exact alternatives inside the existing whole
`fullmatch`; it does not authorize arbitrary topic substrings or relax correction,
allergy, ownership or consent rules. New checks require canonical answers,
retained date/four-person count, a subsequent independently expected 14:00 plan,
a fresh unapproved/undelivered recap and denial of a write without delivery.
Mixed unknown-count clauses still cannot inherit the old four-person plan.

Scoped core verification: **704 passed / 8 skipped**, 53.49 seconds. An initial
command referenced a nonexistent test filename, ran no tests and is not counted
as a pass; the corrected path is `tests/test_restaurant_phone_answers.py`.
Independent static follow-up closes the concrete P1 and finds no new P1 in the
repair. It does not claim exhaustive information-phrasing support. Fresh isolated
restrictive-source Docker packaging: **5 passed**, 11.19 seconds, network disabled
with the existing local image and read-only non-root runtime. Final combined
core/media, all eleven Chromium journeys, delivery checks, publication, real RTC
and final preservation gates are still pending.

Final combined gate after the retention repair:

- Core `python -m pytest tests -q -p no:cacheprovider --tb=short`:
  **12,222 passed / 83 skipped / 36 subtests**, 168.52 seconds.
- Pinned media same command: **12,635 passed / 6 skipped / 36 subtests**,
  200.46 seconds. Counts overlap and are not summed; warnings are the existing
  Starlette/httpx and Python `audioop` deprecations.
- All **eleven** Chromium journeys pass with zero external requests. The new
  guest-current journey covers nine native-validation combinations, 45 failure
  paths, three structured recaps, receipt/renewal rejection and multilingual
  interludes; no independent provider or microphone proof is implied.
- All **24** delivery cases pass; isolated packaging remains **5 passed**.
- **199 Python AST / 23 JS syntax / 10 JSON parses / 6 asset digests** pass;
  cumulative **216 text-file** credential/conflict/whitespace checks are clean.
- Thirteen contributor files are byte-identical to frozen `9721803`; its existing
  guest-current test AST remains unchanged. Its policy differs only in the three
  reviewed exact-whole alias lines. Prior source, contributor and caller commits
  remain ancestors. Fresh publication/deployment/RTC acceptance is not claimed
  from these local gates.

Fresh pre-publication preservation at **03:04:46 UTC** confirms unchanged
configuration/volumes/current route, all four database integrity checks, stable
first/later history, prior immutable call identities, zero rooms, all 23 original
unrelated service IDs and the protected checkout. The first comparison attempt
also required a later additional container `relaxed_lehmann`, now absent before
publication. Its disappearance is independently isolated; cause is unproven and
no recreation/removal is performed. The original 23 services all match. This
qualification is retained in the private snapshot, not hidden as a green all-ID
comparison. A further concurrent master/native revision `870aa41` is observed;
the tested repair will be checkpointed before bounded normal intake of that delta.

### Final published-phone safeguard intake

Verified retention repair `3ab502d` is checkpointed before normally merging
contributor `870aa41` into candidate `527505c`, without conflicts. The bounded
six-file delta retains repeated-clock-unit and semicolon-alternative clarification,
adds one exact ET FAQ recognition variant and includes corresponding no-write
regressions. Its independent static review is clear and explicitly does not
validate historical provider claims. Because application/data changed, both full
suites and browser/delivery gates are refreshed once for this candidate.

Latest candidate core: **12,233 passed / 83 skipped / 36 subtests**, 165.63 seconds.
All eleven Chromium journeys and 24 delivery cases pass again, no external
requests. Syntax/JSON/six assets/216-file hygiene pass. Eighteen of twenty incoming
files are byte-identical to frozen `870aa41`; existing contributor guest-current
test AST remains unchanged and its policy differs only in the reviewed three
whole-question alias lines. Both Dockerfiles and installed/repository controller
remain byte-identical to the already executed five-case packaging gate. Latest
media and actual publication/deployment/RTC gates are not inferred from core.

Read-only retired-host verification at **03:13:47 UTC** returns generic HTTP 503
without redirects on root, hotel, public-restaurant and status paths. No DNS,
account or ingress setting is changed and that hostname is not republished.

Latest **`527505c` combined media**: **12,646 passed / 6 skipped / 36 subtests**,
245.74 seconds, exit 0. This is the final code gate paired with the 12,233 core
gate above, not a sum of overlapping suites. The gate-record commit changes this
evidence file only; application, fixtures, tests, assets and deployment source
remain the exact verified candidate. Publication and acceptance still require
fresh live evidence.

### Qualified release publication and native readiness

Evidence-only gate commit **`94baece`** is atomically and normally pushed to
recovery and master; independent remote verification confirms both exact heads.
At **03:20:48 UTC**, live web is healthy on its exact source/image, application/
data digest matches the tested tree, index and all six assets are byte-exact,
restaurant DTO is fictional ET/EN/RU, both hotel paths return 410 and unauthenticated
confirmation returns 403.

The installed controller returns `DEFER: release_locked` rather than overlapping
a shared rollout. Independent native readiness at **03:22:19 UTC** verifies
healthy worker/bridge on `94baece`, same media image, binding to the running web,
exact common application/data digest and successful dependency check. Common
fingerprint **`e661cc747185a04710d33e169c0252e17d05acd752b0ef52a82f92dc3f990d94`**
matches public `in_sync`. Controller bytes remain reviewed SHA256 `11674bd0…`.
No runtime success is inferred from the deferred command itself.

One current-source canonical RTC batch is running under the shared idle lock.
In addition to unchanged canonical owned-ledger assertions, it captures closed
finalized-input flags requiring supported conditional, decline, consent and
cancellation cues and independently exact first-request fields. No transcript,
audio or credential is saved. Acceptance and final post-batch preservation are
still pending; a long lock-held batch may legitimately age the 180-second public
alignment receipt until an idle controller refresh.

### Qualified RTC outcome and cancellation investigation

The `94baece` batch ends **03:32:04 UTC**, with unchanged healthy service IDs and
zero rooms. ET independently exact requests and supported conditional/decline/
consent recognition pass; all pre-consent reads are empty and one exact owned
reservation is confirmed. The supported cancellation caption does not match the
existing ET cancellation vocabulary and the owned row remains confirmed after
that turn: **`probe_cancel_unproven`**. Probe cleanup subsequently cancels only
its proven owned fictional reservation; cleanup is not spoken acceptance.

EN and RU each pass the unchanged canonical probe, including exact owned
confirmation and same-booking cancellation, seven finalized inputs, nine spoken
replies and two canonical recaps (3,176 and 3,157 voiced frames respectively).
Their supported conditional/decline/consent and exact-request flags also pass.
The additional cancellation qualifier incorrectly compares every language to the
ET-only `CANCELLATIONS` set. This evidence-helper defect is separate from the real
ET failure; the original failed qualified artifacts are retained and not relabelled.
Future qualification must use the runtime's language-specific sets.

Isolated **03:38:14 UTC** Anu PCM → actual Silero/native STT reproduces an exact,
supported full-context cancellation. Three other existing ET cancellation forms
do not match after native recognition. These results support retaining the
full-context fixture and investigating its RTC boundary, not adding fuzzy runtime
authorization or claiming isolated STT as acceptance. A single instrumented RTC
diagnostic will compare closed expected-word flags and reply categories. The goal
remains active; publication is verified, three-language acceptance is not.

The corrected ET word-boundary trace at **03:45:35 UTC** reproduces the same
owned-cancellation failure. Seven of eight expected words match in position and
membership; only `broneering` differs. No question mark, quote or semicolon is
present. Supported conditional/decline/consent and exact planning still pass,
and the unmatched cancellation returns unknown-information recovery while the
owned booking remains confirmed. This localizes the observed mismatch to the
recognized noun, not its upstream acoustic cause. The first diagnostic draft
aborted early on a nonexistent `COPY` key; one input, no booking and clean room/
service preservation are retained as a helper failure, not application evidence.

A punctuation-only no-comma candidate fails isolated native recognition at
**03:48:41 UTC** and is not sent through RTC or retained in source. No authorization
grammar is expanded. The existing short canonical cancellation on the already
approved Anu caller is the next bounded preflight; any isolated success still
requires actual owned RTC cancellation before acceptance.

Live public layout diagnosis at **03:51:26 UTC** verifies translated ET/EN/RU
headings and language selection, zero horizontal overflow in all fifteen
320/390/800/801/1440 px combinations, zero page errors, external requests and
mutation requests. At 390×844, voice and microphone controls are on the first
screen in all languages. At 320×844, English and Russian need vertical scrolling;
Russian microphone bottom is 1,005 px. The overbroad above-fold probe is stopped
after failure and these measured limits are not relabelled green. Its first draft
also incorrectly equated pre-session language choice with `replyLanguage`, which
tracks the last reply; the actual handler changes `demoLanguage` and localized
controls. Screenshots accompany the read-only diagnosis. No UI/source change is
made to satisfy a new unrequested all-width above-fold assertion.

The isolated existing short Anu cancellation also fails exact recognition at
**03:52:48 UTC** (one supported ET final segment, two words, no cancellation
match). It is not retained or run in RTC. Independent diagnostic review confirms
that no ownership/guard defect is demonstrated, upstream acoustic cause is
unproven and no further arbitrary phrase/voice retries or grammar expansion are
justified. Unsupported premature acknowledgement coverage is described only as
no-write rejection, never as a recognized supported ET premature-yes test.

### Published-release preservation checkpoint, not goal completion

Read-only **03:57:10 UTC** comparison against first, intermediate and immediate
pre-publication baselines passes configuration hashes, shared volumes, current
incoming POST route, all four database integrity checks, stable historical rows,
immutable call identities, all 23 original unrelated service IDs, immediate
unrelated IDs and protected checkout/19 status entries. Healthy web/native IDs
and exact `94baece` labels are verified before/after the snapshot, with matching
loaded fingerprints and zero rooms. The later nonoriginal `relaxed_lehmann`
absence already documented before publication remains explicitly qualified.

A manual receipt-refresh attempt safely defers to another Python lock holder;
that process is not interrupted. An independent subsequent public read is
`in_sync`, so no stale receipt is accepted and no second rollout is inferred from
the deferred command. This snapshot is nonexclusive and validates stable healthy
IDs across its read-only boundaries. Private proof explicitly has
`preservation_pass: true` and **`overall_release_acceptance: false`** because
three-language spoken cancellation acceptance is still incomplete.

No additional application, probe, test, operator voice or authorization change
is made after verified `94baece`. This evidence-only publication preserves all
failed artifacts and limitations. Goal tasks 6/7 stay open; no completion audit
or `goal_complete` call is justified by the partial acceptance.

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
