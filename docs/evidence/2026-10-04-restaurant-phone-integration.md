# Restaurant telephone capability integration

## Current verified disposition

The robot-only restaurant release `598a1a1c498f24bac524083e83780b74ce680e52`
and its published descendant `2b65eee73585b460bf7f6b74627b99bc635ad138` have
verified synchronization checkpoints. All 94 app/demo files matched the healthy
web/worker/bridge roles; original volume and LiveKit/SIP/Redis connections were
preserved. The combined 972/clock repair/final literal-question tree passed
12,623 tests and 36 subtests, plus eleven browser journeys. Newer published
`97218039288dcefefa38e6e3b40598de10c50be1` was observed healthy with matching
source links in all three roles at02:48:42Z, then retained by normal integration.
Its source/storage acceptance and final repair publication remain separate gates;
neither is inferred from older receipts.

Strict final native telephone acceptance is **not complete**: the first 598 suite
passed ET menu/allergy before an unexpected note reply; EN menu/allergy/note before
an independent takeaway-audio rejection; RU menu before an allergy-audio rejection.
These failures remain recorded and are under metadata-only root-cause investigation.
No physical-microphone, carrier/PSTN or real restaurant acceptance is claimed.

The sections below retain the chronological repair and verification history;
their earlier “current”/“final” checkpoints are not the latest acceptance result.

## Scope and preserved upstream work

The recovery integrates only the outstanding restaurant telephone behavior into
the current published restaurant implementation. It does not restore the older
standalone booking backend, replace the operator UI, or republish the retired
Meretuule website. The later robot-only domain decision is preserved.

Normal merges retain the published contextual confirmations, first-caller
language selection, male voice choices, dietary followups, grounded browser
reasoning and omission of spoken timezone labels. Call-scoped consent,
delivered-recap receipts, unknown-write protection and saved reservations remain
owned by the existing pipeline.

## Behavior and failing-first evidence

- Reviewed ET/EN/RU capability answers explain that this demo cannot store
  special requests, notify a kitchen, guarantee allergy safety, or accept food,
  takeaway and delivery orders. They use the existing ordered question selectors,
  not a parallel transcript or answer store.
- A positive mixed booking request collects its actual date, time and party
  details. Quoted instructions, negations and how-to examples do not create a
  hold. Complete and partial ET/EN/RU requests are covered by real HTTP/SQLite
  and call-constructor checks.
- Capability disclosures accompany missing-detail and date/time clarification
  prompts, and remain part of the exact pending recap across followups. Canonical
  recap equality still governs delivery receipts; no notice authorizes a write.
- Unknown outcomes and tool errors keep priority. Partial input cannot change
  language, booking state or consent; ordered combined questions repeat in the
  caller's order.
- Newly published generated browser wording is retained for ordinary questions,
  but cannot reword these capability limits. Adversarial generation/review
  doubles reproduced two incorrect action promises before the selector guard.

Independent Codex reviews reproduced the routing gaps, quoted/negated holds,
missed positive requests and omitted notices. Owner regressions failed before
each bounded correction: initial missing answers/routing, fourteen mixed-plan
assertions, nine clarification notices, and two generated capability promises.
No confirmed booking or consent bypass was demonstrated in the quoted cases.

The next Codex review reproduced an inherited generated-wording promise on an
unmatched chef request and an ordinary menu question. Twenty failing-first
HTTP/final-response cases reproduced those and ET/EN/RU action variants. The
shared local wording validator now conservatively rejects capability-operation
wording and first-person action commitments, regardless of detected question or
model approval; the same check runs again immediately before a generated reply
is returned for speech. Rejection retains the trusted canonical response. This
is a bounded deterministic guard, not proof of arbitrary model entailment.

The private speech checker also reproduced eight reversed capability clauses
that had passed a global "some negation survives" check. It now checks every
required refusal separately. Its 39 offline checks pass without provider calls;
that result is not live-audio acceptance.

A further concrete Codex P1 probe found passive special-request acceptance.
Five new HTTP candidates plus a final-state bypass reproduced that omission,
then the same shared guard conservatively excluded special-request/note wording
(including Russian passive requests). The 157 phone/reasoning checks pass.
The private checker now also protects staff verification, fictional-booking
status and the tested allergen-list facts; 48 offline checks pass. Earlier full
counts below predate this final correction and are not final publication proof.

## Combined verification

```bash
env -i PATH=/usr/bin:/bin HOME=/tmp/opencode LANG=C.UTF-8 \
  PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 EASY_LIVE_TESTS=0 \
  /home/arle/.cache/voicebot-restaurant-recovery-venv/bin/python -m pytest \
  -q -ra -p no:cacheprovider --tb=line \
  --basetemp=/tmp/opencode/restaurant-recovery-afe1-final
```

The initial combined result was 11,370 passed in 120.12 seconds. After the
wording-boundary correction and normal merge of published `fc5c4ae` Russian
phrasing, the fresh combined result is **11,470 passed, 36 subtests passed,
4 private-backend opt-in skips**, in 127.87 seconds (same command, basetemp
`/tmp/opencode/restaurant-recovery-fc5c-final`). Two upstream warnings remain:
Python `audioop` deprecation and
Starlette's HTTPX test-client deprecation. This run made no provider calls.

Final integration with published `97684ad` (flexible dates and release-channel
checks) passed **11,661 tests, 36 subtests, 4 private-backend opt-in skips**, with
the same two warnings in 124.07 seconds. Command above, basetemp
`/tmp/opencode/restaurant-recovery-97684-final`. The updated restaurant and
English browser journeys also pass; these retain exact recap, no-write,
saved-record, unsupported-language, logout and retired-host assertions and add
calendar-spelling repair. The seven other browser scenarios are unchanged from
the preceding successful nine-scenario run.

The final independent Codex-account review against `97684ad` is **PASS**, with
205 scoped tests and additional offline HTTP/final-state/audio mutation probes.
No remaining concrete P0/P1 was reproduced in the repaired boundaries. This
review establishes the bounded source safeguards, not universal model
entailment or live-provider/deployment acceptance.

The last publication ancestry check found newer published `e53de158`
conversational voice choices. A normal merge preserves those unchanged; none of
the reviewed restaurant capability modules is changed by that upstream delta.
Fresh combined verification then passed **11,694 tests, 36 subtests,
4 private-backend opt-in skips**, with two warnings in 120.42 seconds (basetemp
`/tmp/opencode/restaurant-recovery-e53-final`). All nine browser scenarios pass
again, with zero uncaught JavaScript errors and zero external requests. The
GitHub PR's Linux regression and actual shared-image build/fingerprint jobs also
pass; that CI result is not private speech or carrier acceptance.

Published `c48b4676` adds booking side questions and compact-clock clarification.
The normal integration preserves the same owned hold and expiry while replacing
the proposal identity and clearing delivery/approval after a question. Six
capability tests were updated from the superseded discard-hold assumption to
assert exact disclosures, same owned hold/expiry, revoked consent and refusal of
confirmation. Three new failing-first ET/EN/RU HTTP cases exposed a duplicated
notice when the same capability was asked again. The recap now omits only
canonical notices already contained in the trusted side answer; the full answer
and recap still define the new receipt. All three reject the older receipt.

Fresh combined checks against this integration: **11,738 passed, 36 subtests,
4 private-backend opt-in skips**, two warnings, 138.85 seconds (basetemp
`/tmp/opencode/restaurant-recovery-c48-final`). All nine Chromium scenarios pass,
including twelve booking-side-question turns, with zero JavaScript errors or
external requests. Focused capability/interruptions/reasoning/time checks:
308 passed. Independent Codex review of this overlapping merge is **PASS** with
380 scoped checks, including HTTP/native stale delivery and exact recap checks.

The next normal merge preserves published `6dbf78f` family facilities, responsive
background reads and voice-latency improvements. Both canonical family topics
and capability topics remain selectable; no older layout, language or provider
settings replace that work. The upstream five localized date followup cases and
language assertions are retained rather than the older three-case fixture.
Fresh full verification: **11,793 passed, 36 subtests, 4 private-backend opt-in
skips**, two warnings, 166.74 seconds, basetemp
`/tmp/opencode/restaurant-recovery-6db-final`. All nine Chromium scenarios pass
including family facilities and nonblocking/failure-recovering background reads,
with zero JavaScript errors or external requests. All twelve private probe
expected replies separately match the real canonical renderer with no holds,
bookings or provider calls.
The subsequent independent Codex review is **PASS**: 126 family/capability
combinations, including 42 pending-proposal consent cases. Eighteen combined
Russian facility/note questions conservatively select `family_details`; the
capability disclosure and fresh-consent gates remain intact. This is a recorded
lower-severity topic-selection limitation, not a live restaurant acceptance.

All nine committed local browser scenarios pass with Chromium 153.0.8010.12,
zero uncaught JavaScript errors and zero external requests. These cover the
operator layout, rollback fixtures, English controls, microphone races, real
synthetic MP3 decoding, first-chunk streaming, incomplete-audio receipt rejection,
restaurant ET/EN/RU reservations, saved bookings, confirmation/cancellation,
unsupported-language prompts and logout isolation.

The current-source voice scenario also passed the pure-local diagnostic and the
actual Uvicorn fixture without changing waits or assertions. Earlier timeouts
could not be reproduced against the current media-retirement contract; they are
not evidence of a newly established production root cause.

## Published-source test compatibility

A clean pinned upstream `189a927` checkout independently reproduced fourteen
language-policy failures without this capability integration. Fixtures were
adapted to the new contract: the initial audio is detected automatically, later
audio uses the selected caller language, initial booking text is localized, and
topic resets use an explicit language switch. The previously unused FAQ fixture
language argument now starts a real authorized session in that language.

The fifteenth failure arose from a date-window parameter computed at collection
before Tallinn midnight and used after midnight. The same 91-day rejection is
now computed at request time. The 48 affected checks pass; no assertion or
production language/date safeguard was removed to make the suite green.

## Deployment and acceptance boundary

Reviewed `b9a320e` was normally merged through PR #31 as `a1793f8` under the
existing release lock with zero active rooms. PR CI run `37158335936` and master
run `37158531147` passed both Linux regression and shared-image jobs. All 94
application/demo files matched the healthy web, worker and bridge release; the
media image IDs agreed. Read-only public browser acceptance passed robot HTTPS,
asset versions, restaurant content and mobile controls; the removed Meretuule
host did not publish content. The obsolete draft PR #6 was closed as superseded,
without deleting its branch or historical commits.

Published descendant `0487c2ec` passed an exact source/health check and nine
private authorization/no-store checks. Missing/wrong authorization returned 403,
valid authorization returned 200. Original shared volume and LiveKit/SIP/Redis
container IDs were preserved. Original restaurant, Easy and Stay row-prefix
digests matched the premerge baseline; four restaurant reservations and eight
actions had been added concurrently, so whole restaurant-table equality is not
claimed. The original records were not overwritten.

Private Estonian speech attempts failed closed on concurrent restaurant-state
changes, short-input timeout and then a menu-spelling mismatch. Metadata-only
diagnosis established fresh caller input with 0.991 similarity containing
`menüs`, no menu topic, and the canonical `information_unknown` reply. These
attempts are not accepted as provider-backed speech proof.

## Final menu-spelling and mobile-layout correction

Published `2119c343` retained the reviewed restaurant boundaries and added
operator quality controls. Three new real constructor/recognized-HTTP cases
failed on the observed single-vowel `menüs` spelling. The existing menu selector
now accepts both `menü` and `menüü`; no language, booking, allergy, capability or
consent rule is bypassed. The private check's first Estonian question is now a
full natural menu question, still with automatic initial language recognition
and all strict caller/reply/audio/storage checks.

The new quality-browser journey also failed on Russian at 390×844: translated
header wrapping placed the 69-pixel voice controls at y=799.97. Two mobile-only
spacing declarations fix the wrapping without hiding wording, changing desktop
layout or reducing the 44-pixel minimum touch targets. The stylesheet URL has
the matching content fingerprint. The entire quality journey then passed.

Fresh combined verification on this exact repair tree: **11,895 passed,
36 subtests passed, 4 private-backend opt-in skips**, two existing warnings,
131.80 seconds. Full command above with basetemp
`/tmp/opencode/restaurant-recovery-final-spoken-menu`. All **ten** Chromium
153.0.8010.12 scenarios passed, zero JavaScript errors and external requests,
including translated landmarks, first-screen voice controls, expiration,
renewal/fresh recap consent, uncertain-write protection and logout timers.
Focused phone/reasoning/interruptions: 221 passed. Private-check offline tests:
48 passed, zero provider requests.

Independent Codex-account narrow review against `2119c343`: **PASS**, three
added real-path tests and ten matcher priority/no-booking probes. No concrete
P0/P1 found. The review did not claim browser, provider or deployment proof and
could not independently establish the untracked private helper's baseline.
At this checkpoint, private live ET/EN/RU acceptance and deployment of the final
correction were still pending. The published receipts below supersede that status.

The normal merge of subsequently published `8123638` preserves its natural
restaurant replies, the configured name `Meretuule`, guest display names and
additional Estonian question variants. The only source conflict kept the new
price selector alongside the reviewed menu-spelling alias. Fresh combined
verification of this merge: **11,966 passed, 36 subtests passed, 4 private-backend
opt-in skips**, two warnings, 173.56 seconds; basetemp
`/tmp/opencode/restaurant-recovery-812-wording-final`. All ten Chromium journeys
pass again without JavaScript errors or external requests.

All twelve private expectations match the new actual canonical renderer and
final guard with no holds/bookings/providers. Four new failing-first offline
probes exposed missing first-person Russian/English refusal forms in the audio
validator; the validator now covers those forms while retaining historical
third-person and fictional-booking cases. All 52 offline checks pass. This is
acceptance-validator verification, not a claim that live speech has passed.

This document does not claim a physical microphone test, a carrier/PSTN call,
real restaurant acceptance, an allergy-safe meal, a food order or a real booking.

## Verified published snapshot

PR #34 normally merged the repaired integration as
`56e7c9ff37e32c7e17c4d8eb218131b494762b51`, with zero rooms under the shared
release lock. Head CI `37161746936` and master CI `37161932490` both pass
`linux-release` and `shared-images`. The tested and merged trees are identical.

Locked runtime observation at `2026-10-03T23:37:23Z` verifies all 94 app/demo
files on the healthy web, worker and bridge, with no missing/extra/changed files.
The media images and source labels agree; original shared volume and original
LiveKit/SIP/Redis container IDs remain unchanged. Nine private authorization
checks pass: missing/wrong/valid authorization yields 403/403/200 on bookings,
calls and call history, all `no-store`, with no credentials disclosed.

Read-only postrelease SQLite checks retain every original and premerge row in
all four databases; whole-table digests also equal the premerge snapshot.
Integrity checks are all `ok`: restaurant 33 reservations/63 actions/0 holds,
Easy 42 writes, Stay 5 bookings. Other sessions' legitimate added records remain.
The signed incoming webhook-only probe also passes with fresh environment
credentials: unsigned denial, signed bound-stream response and `no-store`.
It dispatches no paid/native agent and does not contact a carrier account API.

Fresh public Chromium verification passes robot HTTPS root, all six exact
versioned assets, three menu items, private route denial, retired hotel 410 and
retired Meretuule host 503 without redirects. On 390×844, voice and microphone
controls fit entirely on the first screen in ET/EN/RU; Russian controls start at
y=765.97 with height 69, retain 44-pixel minimum touch targets, and do not overflow.
No JavaScript errors occur; desktop and all three mobile screenshots were read.

The first repaired private-validator review is **PASS** with 67 offline checks: earlier
referral reversals and contradictory appended claims now reject, while twelve
canonical and four legacy positives accept. This is a bounded recognition guard,
not universal semantic proof. The first live Estonian menu case passed fresh
input/reply, voiced PCM and independent recognition (157,760 PCM bytes; similarity
0.960). The allergy case failed its strict independent-audio check and required
metadata-only diagnosis; that result is not a passing four-case Estonian suite or
complete ET/EN/RU speech acceptance.

## Current published descendant and independent speech verification

Normal fast-forward intake retains published `2ca82abddc1a7eefb9176b3d59c653307c7bf7cf`,
including the other owner's renewal receipts, nonblocking UI, date/time corrections,
family-allergen containment and release-state freshness. It retains this session's
menu-spelling correction and mobile spacing; the upstream breadcrumb flex/min-width
improvement remains. Master CI `37163514831` passed. No dirty source was copied.

Fresh combined media-interpreter suite: **12,257 passed, 36 subtests, 6 skips**,
two existing warnings, 171.58 seconds, basetemp
`/tmp/opencode/restaurant-recovery-2ca-final`. Four skips are private installed-
backend opt-ins; the other two packaging cases require an explicitly local image.
Running that packaging file with the already-installed image then passed all
**five** cases in 9.53 seconds, without pulls/network access. All **ten** Chromium
journeys and the additional **24** delivery/status/receipt race checks pass,
without JavaScript errors or external requests.

Locked runtime verification at `2026-10-04T00:11:41Z` matches all 94 app/demo files
on web, worker and bridge exactly. All three are healthy, media images/source
labels agree, the original data volume and LiveKit/SIP/Redis IDs remain unchanged,
and the nine private authorization/no-store checks pass. Fresh public browser
acceptance retains robot-only HTTPS and ET/EN/RU first-screen mobile controls;
the newer CSS/JS/capture fingerprints match. Signed incoming webhook-only proof
passes again without native-agent dispatch or a carrier-account API request.

Read-only SQLite transactions on the pinned release preserve every original and
premerge row-prefix digest across all four databases. All integrity checks are
`ok`. Other callers added records: the snapshot has 38 restaurant reservations,
73 actions and one active hold, Easy 42 writes and Stay 5 bookings. Whole-table
equality during their calls is intentionally not claimed. No other owner's hold
or booking is cleaned up. Carrier ownership/routing and original-number continuity
are not established by this signed protocol test; no account setting was changed.

Groq output-recognition diagnosis identified Russian `на вынос` versus `навынос`
and Estonian lexical/compound-word artifacts. The Russian spacing equivalence has
one failing-first positive and three refusal/added-promise rejection cases. No
Estonian fuzzy safety-word repair, expected-answer prompt or lower safety threshold
was introduced. Changing speech rate did not resolve the strict Estonian check.

The already-installed Azure standard recognizer independently passed the same
Estonian allergy propositions with 0.998 similarity. The private proof helper now
uses it uniformly for every language/case, via the published bounded private child
runner. Only PCM enters stdin and Azure environment credentials enter the child;
no expected answer, caller language or phrase hints are supplied. Recognition text,
audio and credentials remain private/in-memory. ET/EN/RU are the automatic language
candidates; this is not an unsupported-language detection certificate. The bot's
Groq recognition, initial automatic caller language, voices and production settings
are unchanged.

At the first child checkpoint all **79** private offline checks passed.
Independent Codex source/mock review is
**PASS**, including **27** additional SDK/error/privacy/cancellation/timeout/child-
termination checks; no concrete new P0/P1 found. The installed published runner is
an explicit dependency. Serial native ET/EN/RU acceptance is being recorded against
the exact detached `2ca82ab` snapshot; diagnostic or earlier partial cases are not
substituted for its final three-language result.

The first native child invocation failed closed as `independent_audio_unavailable`.
The SDK signals a normal stream end through `cancellation_details` with
`EndOfStream` and `NoError`; the helper had treated every cancellation as failure.
Four actual-child-code stub scenarios preceded the bounded enum correction:
normal EOF failed first; SDK error, user cancellation and EOF/auth stayed rejected.
The full private suite then passed **83** checks. Independent Codex recheck passed
those four and **seven** additional late-cancel/no-result/timeout scenarios. The
isolated real child retained the exact ET allergy propositions at 0.998 similarity.
The next native attempt passed ET menu (0.980) and allergy (0.998), then rejected
the special-request input as `fresh_final_input_required`. It is not a four-case
passing suite. All earlier failed receipts remain preserved.

## Bounded Estonian capability-question spelling follow-up

Public synthetic input diagnostics found three complete-question spellings:
`kõügile`, `proneeringule eri soovi` and `allergiaproneeringule`. Their existing
literal selector missed the special-request refusal. Only these full questions
are added to `booking-101`'s ET variants; canonical notices and all other languages,
general matchers, booking parsers, voices and production recognition are unchanged.

Failing-first native, recognized-audio HTTP and pending-consent scenarios produced
**nine failures and three passing partial-input guards**. With the three aliases,
the focused phone/reasoning/interruption suite passed **294** checks. The full
combined suite passed **12,272 tests and 36 subtests**, six skips and two existing
warnings, 169.65 seconds; basetemp
`/tmp/opencode/restaurant-recovery-note-alias-final`. All ten Chromium journeys
passed again, with no JavaScript errors or external requests. Independent Codex
review passed the **12** new real-path cases and **23** additional bounded
selector/parser assertions: no concrete P0/P1 found. An alias alone creates no
booking; side questions retain the owned hold/expiry but replace proposal identity,
revoke delivery/approval and deny confirmation without fresh consent.

Normal fast-forward also retains published `b3ca570`'s bounded probe calendar-date
support; its **80** probe tests pass separately. It changes no deployed app/demo
source and carries `[skip cd]`. The three new aliases still require guarded
publication and deployed-source verification before any live acceptance claim.

The native special-request diagnostic had one final input, two caption words and
0.203 question similarity. A 400 ms leading-silence experiment did not improve it
and is discarded. Default local Silero segmentation retains almost the whole
question: Kert's segment is 2.656 seconds, but automatic recognition yields no
supported language; Anu's segment is 2.752 seconds and detects ET (0.951 similarity).
The public unsupported-language caption has exactly the same word count/similarity
as the failed native caption; exact native caption equality has not yet been
established. The safety rejection is not relaxed or treated as accepted speech.
Caller-voice diagnosis is distinct from production voice selection, and no initial
recognition language is forced. Final native ET/EN/RU acceptance remains active.

A controlled native Anu-caller diagnostic on the unchanged `2ca82ab` release
recognized all six question words, similarity0.951, and did not emit the unsupported
marker. Its reply then failed `approved_reply_mismatch`, consistent with the missing
literal `kõügile` selector. This separates a demonstrated selector correction from
the Kert synthetic-language-detection limitation. The diagnostic changes only the
in-memory test-caller preset; no production voice or recognizer is changed.

## Published alias repair and retained clock-unit correction

Master advanced to published `2aced839` during the first PR35 checks. Normal
merge `19c0e265` retains its clock-unit-versus-opening-hours correction and spoken
probe fixtures, alongside this session's three aliases. No conflicts or dirty
source were copied. Fresh combined verification passed **12,320 tests and 36
subtests**, six skips, two existing warnings, 166.15 seconds; basetemp
`/tmp/opencode/restaurant-recovery-clock-alias-combined`. All ten Chromium journeys
passed again with zero JavaScript errors or external requests. Independent Codex
clock/capability-seam review passed **ten** committed tests and **75** bounded
assertions, with no concrete P0/P1. All twelve live-check oracles independently
equal the canonical renderer/final guard on the combined tree without any holds
or bookings.

The final branch-to-master delta is exactly the intended FAQ bank, phone tests
and this report; cumulative credential/diff checks are clean. [PR35](https://github.com/Parnuhakk/voicebot/pull/35)
normally merged as `598a1a1c498f24bac524083e83780b74ce680e52` at
`2026-10-04T01:19:22Z`, under the shared release lock with zero active rooms.
Its head CI `37167354057` passed both jobs; tested `19c0e265` and merged `598a1a1`
trees are identical. Master CI and synchronized runtime acceptance are separate
post-publication gates, not inferred from that merge.

Fresh premerge read-only storage proof preserved every original and historical
premerge row prefix across all four databases, with integrity `ok`: restaurant
41 reservations, 79 actions, zero holds; Easy 42 writes and Stay 5 bookings. The
earlier attempted comparison to the 2ca snapshot failed only for its transient
hold; all original and permanent/call-history prefixes matched. That failed
comparison and shared-lock deferrals remain recorded, not relabeled as global
table equality. No other caller's hold or record was removed.

Final native proof uses the existing `azure-calm` synthetic caller preset uniformly
for ET/EN/RU in the private test process only. This diagnoses the observed Kert
automatic-language ambiguity without relaxing it: initial source-language
recognition and all caller/final-reply/PCM/output-proposition/storage/runtime/lock
guards remain unchanged. The independent Azure recognizer receives no expected
text, caller language or phrase hints. Kert ambiguity remains a coverage limit;
one synthetic caller fixture is not an accent, physical-microphone or PSTN proof.

Synchronization returned `PASS: release_synced`, exit0. Independent locked
runtime verification at `2026-10-04T01:22:23Z` matched all **94** application/demo
files in all three healthy roles, exact source labels, identical media images,
original data volume and original LiveKit/SIP/Redis IDs. Nine private authorization
checks on the three actual routes returned **403/403/200**, all `no-store`.
Master CI `37167653929` subsequently passed both release jobs. Five actual installed
image permission checks passed in9.41s without pulls/network.

Read-only postrelease storage checks preserved every original and fresh premerge
row prefix across all four databases, all integrity `ok`. Restaurant41reservations/
79actions/0holds, Easy42writes and Stay5bookings equal the fresh premerge business
tables; legitimate native-test call history grew, so that database's whole tables
are not claimed equal. Fresh-environment signed webhook-only proof passed
unsigned403/signed200, `no-store` and bound stream contract, without agent dispatch
or carrier invocation. It does not establish account ownership or phone continuity.

Public HTTPS/asset/menu/private-denial/retired-host checks passed again on598.
Desktop and all three language screenshots were re-read; layout/design remain
preserved. At390x844 ET controls are y699.28125/46.5px, EN699.28125/69px and
RU765.96875/69px, all44px+ and wholly on the first screen, no overflow/JS errors.

The first uniform azure-calm four-case598 run did **not** pass all cases:
ET menu/allergy0.980/0.998 then `approved_reply_mismatch`; EN menu/allergy/note
1.000 then `independent_audio_content_mismatch`; RU menu0.973 then the same
independent-content failure. Diagnostic-only follow-ups do not replace final
four-case acceptance. A first instrumentation attempt itself failed closed because
the existing `match_question` selector has keyword-only options, not a language
positional parameter; corrected instrumentation is separate from production code.

Receipts: `/tmp/opencode/restaurant-recovery-598-{sync,verification,preservation,
incoming,rtc-et,rtc-en,rtc-ru,rtc-summary}.json`, plus
`restaurant-recovery-alias-publication.json` and the public live summary. Historical
receipts stay intact. Both goals remain active pending final verified acceptance,
evidence publication and once-only completion audit.

## Explicit clock-choice clarification repair

Published 2b65 retained the literal capability aliases and added clock-unit
masking. Independent Codex review exposed a P1 planning regression: `six PM; or
1900 hours` could expose the first time, while `1800 hours and 19 hours` lost its
required clarification. Six failing-first actual-call/recognized-HTTP cases
reproduced these and `18 hours thirty hours`; all six failed before the repair.

The shared time parser now treats a semicolon as punctuation between a clock and
its alternative, and rejects a repeated hour unit after captured minutes. The
existing information selector masks those clock units while preserving genuine
hours questions and safety/capability priorities. No first offered time becomes
a plan: the caller must clarify, and no hold or booking is created.

Focused clock/SDK-audio-turn/phone/interruption checks: **421 passed** in42.91s.
Independent Codex re-review: **229 passed** plus **43** bounded assertions, no
concrete P0/P1. Whole repository on the repaired 2b65 tree: **12,357 passed,
36 subtests**, six explicit skips, two existing warnings, 181.05s; command above
with basetemp `/tmp/opencode/restaurant-recovery-2b65-clock-repair`. All ten
Chromium journeys passed again, zero JavaScript errors/external requests.

Metadata-only native and direct-output checks on 2b65 localized the English
takeaway rejection to the independent recognizer's `take away` spelling. The
private audio validator admits this whole-token equivalence **only when the
entire normalized response then equals the approved answer**. Generic input
normalization, exact captions, language matching, refusal/referral propositions,
canonical-plus-extra guard and raw0.78 threshold are unchanged. Existing explicit
contradiction checks also reject newly demonstrated kitchen/order promises added
to an otherwise near-canonical response. Four failing-first assertions and twelve
already-passing rejection cases preceded this private-only correction; **99**
offline checks passed. Independent Codex review passed the same99 and **71** audio
rejections, twelve canonical positives and two caption rejections. It did not
independently establish live/account authentication.

Russian allergy output remains strict: missing the staff-verification proposition
is still rejected, despite high similarity. Variable direct-recognition outcomes
do not justify dropping or normalizing that safety requirement. Estonian native
input still needs identification of the complete synthetic-question artifact;
no fuzzy production substitution is introduced. Concurrent state changes and
runtime-not-current deferrals stay failures, not accepted telephone evidence.

## SDK-segmented Estonian capability question

The published 8494 language intake preserves automatic recognition: weak `yeah`
and `yep` acknowledgements do not choose the initial call language. Changed-area
checks passed **292** tests in32.09s; independent Codex review passed **73** plus
**24** acknowledgement/consent/switch/refusal scenarios. The combined 8494/clock
repair tree then passed **12,367 tests, 36 subtests**, six skips and two warnings,
207.10s; basetemp `/tmp/opencode/restaurant-recovery-8494-clock-final`. All ten
browser journeys passed with no JavaScript errors or external requests.

Shared-lock deferrals prevented native candidate characterization on 8494; they
are not content failures or speech passes. An alternate real `TelephoneSTT` plus
default Silero `StreamAdapter` run on the public calm-caller synthetic question
identified a complete `külgile` question artifact, ET/six words/0.951 similarity,
with the old selector returning `allergens`. Comparison used only predefined
public substitutions; recognition text/audio/credentials were never printed or
stored. The diagnostic itself exited1 after attempting a nonexistent `VAD.aclose`
method following successful stream/adapter/recognizer closure. Its metadata is a
root-cause observation, not a clean native acceptance receipt.

Only `Kas saate minu allergiast külgile teatada?` is added to the existing ET
FAQ variants. Four real-path parameter cases guard canonical refusal, automatic
recognized-HTTP input, owned-hold/expiry retention with revoked delivery/consent,
and partial input that cannot change an English booking. Before the literal
addition, **three new cases failed** while thirteen existing/partial checks passed.
The focused phone/reasoning/interruption suite then passed **309** in23.32s.
No matcher, output safety substitution, booking parser, voice or recognition
setting changes. Exact identity with the earlier native artifact remains unproven;
final wire acceptance is still required, rather than inferred from local SDK input.

A fresh 8494 read-only storage checkpoint preserves every original and alias-
premerge prefix across all four databases, integrity `ok`: restaurant56reservations/
109actions/1othercallerhold, Easy42writes and Stay5bookings. It did not claim the
shared lock or whole-table equality. The fresh-environment signed incoming
webhook-only probe also passed403/200 and `no-store`, with no agent/carrier call.
Receipts: `restaurant-recovery-clock-premerge.json` and
`restaurant-recovery-8494-incoming.json` under `/tmp/opencode`.

Fresh full verification of the final alias/clock/inherited-language integration:
**12,372 passed, 36 subtests**, six explicit skips, two existing warnings, 176.18s;
command above with basetemp `/tmp/opencode/restaurant-recovery-kulgile-final`.
All ten Chromium journeys passed again with zero JavaScript errors and external
requests. Full native ET/EN/RU acceptance is still a separate pending gate.

Independent Codex final-alias review: **16** variant/partial cases and all **128**
phone-answer cases passed, plus bounded JSON/routing/context assertions. No
concrete P0/P1 found; exact phrase boundaries, capability priority and retained
owned-hold/fresh-delivery consent were verified. It makes no native-wire claim.

## Published guest-current intake

PR36 head9638 CI37171125464 passed both Linux/shared-image jobs. Its guarded
zero-room publication attempt correctly stopped with `published_base_changed`
when another session published newer guest-interface, renewal/receipt and medical-
context safeguards. No stale-base merge or deployment was performed. Published
9721803 was normally merged as6c98c22 without conflicts; no other owner's dirty
source or goal was copied or edited. Our cumulative delta remains six files.

All **eleven** local Chromium journeys pass on the combined source, including
the new guest-current journey: ET/EN/RU at320/390/1440px, 45 preparation failure
paths, structured recaps, wrong/missing/foreign/expired receipt/renewal rejection,
contrast minimum4.55, and zero JavaScript errors/external requests. The new
desktop/ET320/RU390 screenshots were also re-read. The full tests below and
narrow Codex interaction review passed before the updated branch ships.

Fresh combined6c98 verification passed **12,623 tests, 36 subtests**, six explicit
opt-in skips and two existing warnings in208.91s. The isolated command above used
basetemp `/tmp/opencode/restaurant-recovery-972-combined`; no provider opt-in or
inherited host credentials. The new published guest tests are included rather
than treating the earlier12,372 checkpoint as current combined coverage.

Independent Codex review of only the new guest/medical/renewal integration seams
passed **229 tests** and **42** temporary-state assertions; no concrete P0/P1.
The retained medical concern excludes generated recommendations without masking
canonical capability refusals. Existing owned-hold/expiry and renewal/receipt/
language/fresh-consent boundaries remain intact. Two supplementary comparison
probes had invalid forced-ET versus initial-English fixtures and are retained as
invalid-oracle failures, not product passes or a blanket native/HTTP equivalence
claim. This review makes no provider or deployment-acceptance claim.

The fresh read-only published972 public checkpoint passed root HTTPS200, six
versioned same-origin assets, three fictional menu items, denied private routes,
hotel410 and retired-host503, plus ET/EN/RU mobile controls within the first844px
screen without overflow or JavaScript errors. Receipt:
`/tmp/opencode/restaurant-recovery-972-live-summary.json`. Final repair-release
runtime/source/auth/storage/incoming and strict telephone checks are still pending.

All twelve private expected replies also matched the real renderer and guarded
fallback sequentially in each language on6c98, with zero providers/booking state.
Pure menu questions still permit separately reviewed free wording; this offline
comparison does not prove every eligible generated menu reply will be identical.
No supported reasoning is disabled to satisfy a witness. The live strict caption,
audio and safety checks remain necessary for the sampled native turns.
