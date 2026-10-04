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
