# Restaurant telephone capability integration

## Current verified disposition

The pinned base for the emergency repair is `956ea785be975f2b15bb8cd492b70bdabdff7c9f`,
whose application, data, tests and deployment source is identical to PR39's
`0bbffde9d84b52272270adb4439a12b35253acc6`; only research documents changed.
The existing number's account ownership, voice capability and POST routing to
the robot webhook were verified through a read-only Twilio request at06:37:11Z.
No number/credentials were printed or saved and no paid call was made.

Published MAI-Transcribe-2 preview input recognition is retained, explicitly not
called unchanged ASR. Published voice profiles, delivery settings, canonical
safety copy and the shared booking pipeline are preserved rather than rolled back.
Only published peers were merged;
no other owner's dirty work was copied or reset. Current0bb combined checks pass
12,861 tests/36 subtests and all eleven browser journeys, with green masterCI.

A narrow Codex review found a P1 in PR39's emergency-interruption routing. The
bounded repair preserves an already recognized emergency while discarding
unreviewed booking details, and prevents a waitlist override. Its eighteen
ET/EN/RU fresh/partial/held regressions first produced15FAIL/3PASS for missing
112 guidance. The final repair passes 12,879 tests/36 subtests, all eleven browser
journeys and the focused Codex re-review. Only the two routing conditions and
guarded owned-proposal restoration change runtime behavior. The telephone goal
stays active pending final publication and synchronized native verification.
The completed a7be witness/audit below remains dated base evidence.

A parallel published speech repair advanced master and all three healthy roles to
`20b474994c3f883794f8f056faf3a9a27bd5420e` before publication. It is not rolled
back. The reviewed emergency repair is being integrated through normal merges,
with fresh combined checks for that newer source. The combined source passes
**13,143 tests/36 subtests**, all eleven browser journeys and the narrow Codex
integration review (788 scoped tests, twelve exact canonical replies and twelve
owned-proposal controls). Its only runtime difference from published20b is the
reviewed emergency repair. A 956 idle-baseline attempt
failed `release_locked` after its bounded wait; it is not preservation proof.
The peer introduces a Nova Turbo Estonian conversational profile, a zero default
sentence pause and effective recognizer identity in release fingerprints. These
are independently published changes, not described as unchanged voice settings.
The private checker remains unmodified, with 173 offline guards passing and no
expected-text or language hints supplied to independent recognition.

The fresh locked20b baseline at06:58:33Z has zero active rooms, the original data
volume and four successful integrity checks. It records88restaurant reservations,
173actions/0holds,42Easy writes,5Stay bookings and37call-booking associations.
The original/a7be/prepublish20b prefixes and whole current booking state pass a
separate exact read-only preservation check. Peer native activity added three
fictional reservations/six actions after the earlier85/167checkpoint; those older
records were not replaced. Effective native voices are Nova Turbo ET, Jenny EN and
Svetlana RU, with automatic language selection, natural1.12rate, recap1.0 and
zero fixed sentence pause. Publication/new exact-release acceptance follows.

### Auditeda7be checkpoint

Robot-only restaurant release `a7be09c992a7ce0a42e0750d7535ef726af0be4d` is
published and synchronized through PR38. It retains the published clock/FAQ,
whole-question retention and Russian staff-verification repairs, and clarifies
only the Russian refusal to notify kitchen staff. Both master CI jobs passed.
Combined checks passed 12,652 tests/36 subtests and all eleven Chromium journeys. All94
app/demo files match each healthy web/worker/bridge role; nine authorization and
no-store cases pass. Original volume/infrastructure and all original/earlier fresh-
premerge row prefixes remain intact. Fresh HTTPS/assets/menu/ET-EN-RU mobile and
robot-only retired-host checks pass. Restaurant/Easy/Stay booking state is unchanged;
new call-history rows do not invalidate exact preservation of every prior row.
The870/94/4ba receipts below remain dated checkpoints.

The bounded native acceptance batch on exacta7be passes **all twelve cases** at
2026-10-04T06:01:18Z: four each in ET/EN/RU, with exact fresh captions, independent
automatic recognition and unchanged restaurant state throughout the serial batch.
Both earlier4ba aggregate failures remain FAIL, alongside the intervening RU-only
diagnostic success. No failed or partial run is relabeled as full acceptance.
The new batch calls the original strict checker, with a rejection-only metadata
observer that never ran because no case failed. Required refusals/referrals and
production voices/ASR are unchanged.
The private ET whole-canonical compound-spacing correction and tightened Russian
staff/refusal/contradiction guards remain reviewed and unchanged. The first failed
batch is retained; a successful repeat does not establish deterministic recognition.
No physical-microphone, carrier/PSTN or real restaurant acceptance is claimed.
The once-only Codex telephone completion audit is **PASS**, with the raw-log
availability qualification below. The dashboard's completed audit is separate
and was not repeated.

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

## Published `870aa41` release and preservation receipts

- PR36 merged normally at2026-10-04T03:03:16Z under the shared release lock with
  zero active rooms. Fresh premerge:65 fictional restaurant reservations,
  127actions/0holds, Easy42writes and Stay5bookings; all original prefixes retained.
- Current headCI37172603075 and masterCI37172928009 passed both Linux/shared-image
  jobs. Published870 and reviewed8f complete Git trees are identical; only the
  evidence document differs from the full-suite6c98 tree. The existing
  reconciler deferred once on an occupied lock, then returned
  `PASS: release_current`; all three roles already matched the new published source.
- Locked03:07:44Z verification matched all94app/demo files in each healthy role,
  release/source links and identical media image. Original volume and original
  LiveKit/SIP/Redis IDs remain unchanged. Media configuration matches and initial
  recognition remains automatic. Nine private missing/wrong/valid authorization
  cases returned403/403/200, all `no-store`; no credentials were emitted.
- Read-only03:10:34Z transactions: all four integrity checks `ok`; every original
  and fresh-premerge row prefix preserved. Restaurant65reservations/127actions/
  0holds, Easy42writes and Stay5bookings. Business tables equal fresh premerge;
  legitimate call-history additions are preserved, not claimed as whole-table
  equality. This proof does not claim a global cross-database snapshot or lock.
- Fresh-environment signed webhook-only proof passed unsigned403/signed200,
  `no-store` and the bound stream contract. No agent dispatch/carrier call and
  no account/original-number ownership certificate are claimed.
- Fresh public Chromium proof passed HTTPSroot200, six exact same-origin asset
  fingerprints, three menu items, health/private denial, hotel410 and all four
  removed-host paths503. ET/EN/RU voice and microphone controls fit the first
  390x844 screen without overflow; all four new production screenshots were read.
- Installed-image packaging: the first wrapper used a nonexistent opt-in name,
  so only3passed/2skipped. After reading the actual test contract and supplying
  `VOICEBOT_PACKAGING_BASE_IMAGE` with the installed image digest, all5passed
  in10.71s; no image pulls or network. The initial skips are not relabeled passes.
- The branch was normally fast-forwarded to published870 and pushed. No other
  owner's worktree, goal, caller hold or stored booking was overwritten or cleared.

Receipts under `/tmp/opencode`: `restaurant-recovery-clock-972-{head-ci,
publication,idle-premerge}.json`, `restaurant-recovery-870-{master-ci,sync,
verification,preservation,incoming,live-summary}.json` and the four870screenshots.

## Strict870 native speech disposition

The same reviewed private helper and uniform in-memory `azure-calm` synthetic
caller ran serially on the exact detached870 release. Bot voices, production
recognition, automatic initial language and independent Azure ET/EN/RU candidate
recognition stayed unchanged. No expected-answer, caller-language or phrase hints
entered independent recognition; no captured speech/audio/credentials were stored.

| Language | Accepted cases | Complete acceptance |
| --- | --- | --- |
| ET | menu0.980, allergy0.998 | No: note independent-audio content mismatch |
| EN | menu1.000, allergy1.000, note1.000, takeaway0.994 | Yes:4cases/exact870/restaurant state unchanged |
| RU | menu0.973 | No: allergy independent-audio content mismatch |

ET note passed the fresh-input, exact-caption and voiced-PCM boundary before its
independent content failure. This distinguishes the repaired input selector from
the remaining output-recognition problem; exact identity with an earlier captured
input artifact is still not inferred. Russian mandatory staff verification remains
required. No incomplete language run is counted as four-case acceptance.

Private receipts: `restaurant-recovery-870-rtc-{et,en,ru,summary}.json`. Earlier
failures, transient state changes, incomplete input and shared-lock/runtime
deferrals remain preserved in the chronological sections/private receipts. Physical
microphone, carrier/PSTN, original-number continuity and real-restaurant acceptance
remain unverified. Final telephone completion auditing must wait for all criteria;
the dashboard's robot/auth/storage acceptance is a separate goal.

Direct production-voice/configuration synthesis, without RTC, reproduced the ET
note rejection at0.994: the **entire** independently recognized normalized answer
equals the approved answer except `allergia ohutust` versus `allergiaohutust`.
Required proposition6 is the only failed pattern. No loss of refusal, extra claim
or voice/delivery change was observed. A separate native metadata retry deferred
four times on the shared release lock, so it adds no native input/output identity
proof. Any proposed private-checker correction must be whole-canonical-only;
fuzzy medical-word substitutions and caption normalization remain excluded.

Russian direct output still fails proposition17 at0.983, with a noncanonical
staff-verification phrase. This is **not** accepted as the required clause, and
no Russian safety/referral exception is introduced. Diagnostic transcripts/audio
stay in memory; receipts contain only indexes, counts and public-fixture matches.

## Newer published `94baece` reconciliation

The once-only Codex dashboard completion audit passed all four robot-only870
snapshot criteria, independently inspecting receipts/screenshots/report publication
and recomputing14 preservation-prefix comparisons. It explicitly excludes later
descendants and telephone completion. Closure-time03:46:05Z verification found
newer master/deployed94 in all three healthy roles; the old audit is not presented
as current94 proof. That published history was normally merged ase46e4ab without
conflicts or another owner's dirty source/goal intake.

The new application's only delta to870 is three lines adding seven complete
known questions inside the existing `fullmatch`; mixed unknown-count corrections
still cannot retain stale four-person plans. The peer's four ET synthetic booking-
caller literals are qualified separately, not production voice/language/consent
changes and not a change to our private FAQ caller. Our own tracked difference
to published master is only this evidence document; no production redeployment
for documentation. Later report-only master013bce1 (`[skip cd]`) is normally
retained too; its application/data/tests/deployment source equals deployed94.

Fresh isolated combinede46 verification:

```bash
env -i PATH=/usr/bin:/bin HOME=/tmp/opencode LANG=C.UTF-8 \
  PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 EASY_LIVE_TESTS=0 \
  /home/arle/.cache/voicebot-restaurant-recovery-venv/bin/python -m pytest \
  -q -ra -p no:cacheprovider --tb=line \
  --basetemp=/tmp/opencode/restaurant-recovery-94-combined
```

**12,646 tests, 36 subtests PASS**, exit0,210.21s; six explicit opt-in skips and
two existing warnings. All eleven Chromium journeys pass, including the current
guest failure/renewal/receipt matrix, with no JavaScript errors/external requests.
Release94 masterCI37173731889 passed both Linux/shared-image jobs.

Independent Codex review qualified only the new94 delta:24targeted tests and
63 supplemental state assertions passed (42 appended-clause negatives,7current
hold/expiry/proposal cases,14expired/unowned cases), no concreteP0/P1. No provider,
live recognition, fabricated-to-live receipt equivalence or repeated dashboard
completion audit is claimed from those supplemental checks.

Locked03:51:05Z current94 verification: all94files per healthy role, original
volume/LiveKit-SIP-Redis IDs, matching media configuration/image, automatic initial
language and nine403/403/200/no-store authorization cases PASS. All four integrity
checks are `ok`; every original and earlier972 idle-premerge row prefix remains
intact. Current restaurant85reservations/167actions/0holds, Easy42writes/Stay5bookings
include concurrent additions, not deletions or byte equality of growing tables.
Read-only transactions do not claim a global cross-database atomic snapshot.

Fresh signed webhook-only03:51:47Z403/200/no-store/bound stream proof passed without
agent/carrier invocation. Fresh public Chromium verifies HTTPS200, six exact
same-origin asset fingerprints/menu3/private denial/hotel410/removed-host503 and
ET/EN/RU first-screen voice/microphone controls without overflow/JavaScript errors.
All four new94 production screenshots were read. Receipts in `/tmp/opencode`:
`restaurant-recovery-94-{master-ci,verification,incoming,live-summary}.json`.

## Reviewed private ET compound boundary

Direct unchanged production synthesis proved that the entire ET note reply was
canonical except `allergia ohutust` spacing. Only the private audio comparator
now admits that word-boundary equivalence when **all normalized words** then equal
the approved reply. It does not normalize captions, other compounds, missing
negations, extra words, staff-verification clauses or production recognition.
The raw similarity remains measured on unmodified recognized text with the
existing0.78 floor. The ET accepted fixture returns0.994152, not1.

Failing-first:2expected failures/122passes. The first green invocation had
4failures/120passes because four negative fixtures used lowercase replacement
against capitalized `Allergia`; their mutation never occurred. Those fixtures
were corrected and each asserts its replacement target exists. **124offline checks
passed** in4.35s, zero providers. Independent Codex approved the narrow boundary
with124tests and24 supplemental assertions, including all12 canonical positives,
high-similarity negatives and caption rejection. Its first root import-path
invocation had116passes/8dependency failures; corrected execution scope passed
without edits. The attempted Spark route failed before execution because the
ChatGPT account does not support it; the existing Codex-account route was used,
never a Go fallback. All failures remain recorded as failures or invalid fixtures.

Russian `нужно проверить с сотрудником` remains mandatory; noncanonical or missing
staff verification is still rejected. A fresh exact94 ET/EN/RU run held the
shared release lock across the serial batch, preserving every freshness, canonical
caption, audio, language, safety and unchanged-restaurant-state requirement.
Only English satisfied all4cases/exactrelease/unchangedstate. ET menu/allergy/note
passed at0.980/0.998/0.994 before takeaway audio failed; RU menu passed at0.982
before allergy audio failed. Both incomplete runs remain FAIL, exit1 aggregate.
Current receipts: `restaurant-recovery-94-rtc-{et,en,ru,summary}.json`.

Direct unchanged production-voice ET takeaway synthesis reproduced the rejection
at0.989583 with only proposition8 missing. The entire normalized recognized reply
equals canonical except **both** `kaasa müügi` and `laua broneeringuga` spacing;
no contradiction or unrelated word mutation. Metadata-only receipt:
`restaurant-recovery-94-direct-takeaway-diagnostic.json` (public full candidate5,
12expected/14recognized words). This is not RTC acceptance. A further bounded
private whole-canonical correction requires failing-first tests and independent
review; no fuzzy medical/referral matching or caption relaxation is permitted.

## Explicit Russian staff-verification notice candidate

The reviewed ET takeaway correction admits only the three observed complete
compounds and rejects immediately if repairing one leaves any noncanonical words;
it closes the demonstrated similarity-fallback gap, not production booking logic.
Failing-first2/144 then4/144;148private checks and the narrow Codex review pass.
Two supplemental rejection assertions in untouched generic fallback failed; they
are retained as limits, not universal canonical-equivalence success. Strict exact94
ET now passes all four cases at0.980/0.998/0.994/0.990 with unchanged restaurant
state. The final aggregate still fails because RU allergy recognition misses only
the staff-verification proposition at0.982609; it says the public noncanonical
staff phrase, not the approved referral. English94all4proof remains unchanged.

Production Russian SSML preserves the literal notice and has no pronunciation
substitutions. A bounded same-voice/same-delivery experiment reproduced the old
recognition failure, then tested the explicit subject:

> В меню указаны аллергены. Сотрудник ресторана должен проверить состав и возможный контакт с аллергенами на кухне. Я не могу обещать еду без аллергенов. При серьёзной аллергии поговорите с рестораном до заказа.

This says the restaurant employee **must** check composition and possible kitchen
allergen contact; it retains the refusal to promise allergen-free food and the
serious-allergy/before-ordering referral. It changes no ingredient/menu fact,
booking authority, kitchen-notification ability or real-restaurant claim.
Two direct repetitions scored0.991489. A separate metadata-only check retained
all four required clauses and the entire public answer aside from `ё`/`е`, which
existing dish/referral patterns already support. No voice, production ASR or
expected-answer/caller-language hints changed. This is direct diagnostic evidence,
not RTC acceptance. Receipts: `restaurant-recovery-94-ru-wording-{experiment,clause-diagnostic}.json`.

Failing-first native/HTTP/held-recap regressions:3FAIL, then3FAIL after correcting
one held-fixture oracle. The first fixture used an unlisted complete question whose
existing safe policy clears the pending proposal; the retention test now uses an
already-whitelisted milk-allergy statement. No booking grammar was broadened.
The shared Russian notice line alone changed;131phone-answer tests pass9.48s.
Private missing/optional/reversed/wrong-actor/ingredient/cross-contact checks had
7FAIL/152PASS before the new literal obligation was required. After the first
guard159PASS; two added leading-negation/bigger-word tests failed, then exact
word boundaries and negative lookbehind made161offline checks pass, zero providers.
The old `нужно проверить с сотрудником` requirement remains enforced for old
fixtures; the new approved notice requires its explicit employee obligation.
No missing referral or noncanonical recognized staff phrase is normalized away.
The full isolated repository run passes **12,649 tests/36 subtests**, exit0,
206.27s, with six explicit opt-in skips and two existing deprecation warnings.
All eleven Chromium153journeys pass with no JavaScript errors/external requests,
including the guest preparation/renewal/receipt matrix. JSONparse confirms only
the Russian notice changed in restaurant data; all93otherapp/demo files, menu,
prices, tables, ET/ENcopy, productionvoices/ASR and booking logic are unchanged.
Codex round1 passes the production semantics/three new regressions and161private
tests (164total), but reports a private P1: with existing `ё`/`е` variation, an
intact staff obligation plus a second reversed obligation passes at0.832143/
0.833631. Four literal contradiction variants fail before repair; one finite
contradiction pattern now rejects staff `не должен`/`может не` with `проверить`/
`проверять`. All165private offline checks pass, zero providers. This is a tightened
negative guard, not a recognition/referral exception or a production source change.
Focused Codex P1 re-review passes165tests: all four reported contradictory forms
reject above0.78, while removing only the new regex in memory makes them accept.
All12canonical positives and legacy staff/refusal/allergen negatives pass. One
initial supplemental harness incorrectly assumed every legacy mutation exceeded
0.78; correcting that test assumption required no repository edit. No concrete
P0/P1 remains in the reviewed finite repair. The publication and native receipts
below supersede this candidate checkpoint; direct synthesis does not close the goal.

## Published4ba preservation and native continuation

PR37 merged normally as `4ba789b917318de74bdffd9d63505812714188a8` at
2026-10-04T05:00:55Z under the shared release lock with zero rooms. Reviewed
`b62fcbddb9025fd6ed32e99e0666fbc193ca57eb` and published complete trees are equal.
The owned recovery branch fast-forwarded and was pushed. The first isolated
GitHub CLI attempt failed authentication at exit4 before invoking merge; the
correct existing private environment succeeded. Both outcomes are retained.
Head CI37178339618 and master CI37178656208 passed `linux-release`/`shared-images`.
The existing Node20 action annotation remains, not a job failure.

Existing `release_sync.py` on the exact detached4ba snapshot returned
`PASS: release_current`. Locked05:05:59Z verification matched94app/demo files in
each healthy web/worker/bridge role, original volume and LiveKit/SIP/Redis IDs,
matching media/source configuration and unchanged production voice/delivery/model
profiles. Nine missing/wrong/valid authorization cases return403/403/200 and
`no-store`. Four database integrity checks pass; every original, earlier972 and
fresh idle-premerge row prefix survives. Whole tables also equal this fresh
premerge checkpoint:85restaurant reservations/167actions/0holds,42Easy writes,
5Stay bookings. No cross-database atomicity claim is made.

Fresh HTTPS/assets/menu/retired-host/mobile checks pass; all four production
screenshots were read. ET/EN/RU controls stay on the first screen with no overflow.
Fresh webhook-only proof passes unsigned403/signed200, `no-store` and bound stream
contract, without native-agent dispatch or carrier invocation. This does not prove
PSTN access, number continuity or account ownership.

The first complete serial4ba batch, shared lock held throughout, exits1:

| Language | Menu | Allergy | Note | Takeaway | Complete |
| --- | --- | --- | --- | --- | --- |
| ET | .980 | .998 | .994 | .990 | PASS, state unchanged |
| EN | 1.000 | 1.000 | 1.000 | .994 | PASS, state unchanged |
| RU | .973 | independent-audio content FAIL | not reached | not reached | FAIL |

At05:15:08Z the metadata-only RU diagnostic repeat passed all four cases through
the original checker at .973/.991/1.000/.994, with fresh exact captions and unchanged
restaurant state. The allergy answer retained every required proposition and was
equal aside from existing `ё`/`е` orthography. Its observer only emitted metadata
before calling the original guard; it changed no on-disk helper, synthesis, ASR,
score, caption or predicate. The first batch lacks proposition-level metadata;
its cause is not invented or inferred from the successful repeat. The prior failure
and recognition variability remain explicit. The subsequent uninstrumented full
serial batch also exits1: ET4PASS at .980/.998/.994/.990, EN4PASS at
1.000/1.000/1.000/.994, RU menu/allergy PASS at .982/.991, then note FAIL
`independent_audio_content_mismatch`; takeaway is not reached. This receipt is
`restaurant-recovery-4ba-rtc-final-summary.json`, not a passing final acceptance.
Complete-batch retries stop after these two failures. No final telephone
completion audit has been launched.

A selected-note same-PCM diagnostic was deferred at `rooms_busy` with unchanged
restaurant state and no recognition metadata. It provides no content/identity
evidence and does not justify disrupting another caller. A room-free bounded
comparison instead uses the unchanged production `TelephoneTTS` and installed
SDK's per-sentence tokenizer, then runs independent automatic recognition three
times on one in-memory PCM. This separates synthesis/recognition evidence from
RTC transport. It reproduced the old-note rejection three times at0.989899 with
16expected/16recognized words, no matched contradiction and only the kitchen-
notification proposition missing. The metadata localizes the difference to the
canonical word `кухню`; it does not preserve or invent the replacement word. This
does not establish the exact cause of an earlier uninstrumented batch failure.

Private receipts in `/tmp/opencode/`:
`restaurant-recovery-ru-notice-{publication,head-ci,master-ci,sync,verification,incoming,live-summary,rtc-summary}.json`
and `restaurant-recovery-4ba-{ru-native-diagnostic,rtc-final-summary,ru-note-same-pcm-diagnostic}.json`.

## Explicit kitchen-staff refusal candidate

The room-free per-sentence SDK experiment compares the existing refusal with:

> Я не сохраняю особые пожелания и не уведомляю сотрудников кухни. Я не могу подтвердить безопасность при аллергии.

Only the kitchen object becomes explicit kitchen staff; inability to save special
requests, notify the kitchen and confirm allergy safety remains unchanged. Two
separately synthesized candidate answers are independently recognized exactly,
score1.000, retaining all three refusals. A later old-answer control also scored
1.000, so variability remains; no deterministic-recognition claim is made. The
last prototype emitted an SDK FFI finalizer assertion after all result metadata
and exit0. That cleanup qualification is retained, not called a pristine run.
Receipts: `restaurant-recovery-4ba-ru-note-{sdk-same-pcm,wording}-diagnostic.json`.
The prototype is not production code or native RTC acceptance.

The retained implementation changes only `booking-101.answer_ru` in the existing
shared `data/demo/restaurant-phone-faq.json`; no alias/parser, app, menu, voice,
ASR or delivery change. Three new native/automatic-audio HTTP/owned-held-proposal
tests fail first, then pass through actual canonical consumers after the line edit.
Phone answers:134PASS9.83s. A held side question keeps the same hold/expiry, replaces
proposal identity, revokes delivery/approval and rejects confirmation without fresh
consent. The private checker requires the exact kitchen-staff refusal, retains
legacy kitchen wording and extends its existing contradictory-notification guard.
Seven missing/reversed/wrong-actor/altered-kitchen/double-negation fixtures fail
before the new mandatory clause. An initial added-promise fixture passed because
its spelling mutation already broke another refusal; correcting only the connective
exposes the intended false accept before the negative guard repair. All173private
offline checks now pass with zero provider calls. No new Russian normalization,
missing-notification exception, caption relaxation or expected-answer hint exists.
The full isolated suite passes **12,652 tests/36 subtests**, exit0,211.64s, with
the same six explicit opt-in skips and two existing warnings. All eleven Chromium
journeys pass, no JavaScript errors/external requests. The source manifest confirms
only the FAQ's one Russian answer value changes among94app/demo files; all questions,
aliases, other data and production code/settings stay unchanged. Narrow Codex
review passes176tests (three production-path/173private),12canonical positives,
legacy refusals and eight new rejection cases. Removing only the new guards in
memory makes all eight accept above0.78, proving the regressions are nonvacuous.
No concrete P0/P1 is found in this delta. This remains offline approval;
the publication below supersedes the candidate checkpoint, not native acceptance.

## Publisheda7be preservation and fresh native gate

PR38 merged normally as `a7be09c992a7ce0a42e0750d7535ef726af0be4d` at
2026-10-04T05:44:41Z under the shared release lock with zero rooms. Reviewed
`5a6520975e4e54a6055fa928614bb633ca1605c6` and published complete trees are equal;
the owned recovery branch was fast-forwarded and pushed. Head CI37180561281 and
master CI37180765398 passed both `linux-release` and `shared-images`. The existing
Node20 action annotation remains a warning, not a job failure.

The new web became healthy at05:45:55Z. The existing reconciler safely deferred
twice on `release_busy`, then returned `PASS: release_synced` at05:47:52Z. All94
app/demo files match each healthy web/worker/bridge role; original volume,
LiveKit/SIP/Redis IDs, media configuration and production voice/delivery/model
profiles remain unchanged. Initial language stays automatic. All nine authorization
and `no-store` cases pass. Fresh HTTPS/assets/menu/retired-host/ET-EN-RU mobile
checks pass, and all four production screenshots were read. Fresh signed-webhook-
only proof at05:54:07Z passes403/200, `no-store` and bound stream contract without
agent dispatch or carrier invocation. Fresh Twilio values are used only from the
environment; number/account ownership is not verified.

The initial verification receipt at05:53:29Z fails an additional whole-call-history
equality assertion, not a preservation check: one call, one session and36events
were appended since the fresh premerge snapshot. All original, earlier972,4ba and
fresh-premerge row prefixes match exactly; all four integrity checks pass. The
failed receipt remains retained. A fresh locked zero-room read at05:55:44Z verifies
those same prefixes and whole unchanged booking state:85restaurant reservations,
167actions,0holds;42Easy writes;5Stay bookings;34call-booking associations. Whole
history equality is explicitly not claimed. No cross-database atomic snapshot or
identity/source claim for the appended call is made.

A complete strict serial ET/EN/RU batch ran on the exact detached `a7be09c`.
The shared lock spans all languages; the synthetic caller's private `azure-calm`
remap changes no production settings. The reviewed on-disk helper is pinned to
`4a8d490c1cf3cd8a93d57fc683dd2ba7fd20afcaf87371a73a425d160e08bcdc`.
Its original audio guard is called first, unchanged; a failure-only observer emits
metadata and rethrows rather than repairing or accepting rejected content. No
expected answer, caller language or phrase hints reach independent recognition.
Fresh final input, exact captions, audible PCM, language, required propositions,
contradictions, raw0.78floor and unchanged restaurant state remain mandatory.
The batch exits0 at06:01:18Z with all twelve cases passing:

| Language | Menu | Allergy | Note | Takeaway | Result |
| --- | --- | --- | --- | --- | --- |
| ET | .980 | .998 | .994 | .990 | 4/4 PASS |
| EN | 1.000 | 1.000 | 1.000 | .994 | 4/4 PASS |
| RU | .973 | .991 | 1.000 | .994 | 4/4 PASS |

Every case has fresh final input, exact approved captions and voiced PCM. All
mandatory safety propositions and the appropriate output language survive
independent automatic recognition; no contradiction is accepted. Restaurant
state is unchanged for each language and the entire serial batch. Exact runtime
and source-lineage checks pass at its end; content hashes were matched before the
batch. There were no failure-observer records.
The result establishes this bounded native RTC witness, not deterministic ASR,
physical listening, carrier/PSTN reachability, number continuity/ownership or
real-restaurant acceptance. Earlier failures and all diagnostic qualifications
remain retained. The once-only telephone completion audit passes as qualified below.

Receipts in `/tmp/opencode/`:
`restaurant-recovery-ru-staff-note-{publication,head-ci,master-ci,sync,verification,verification-final,incoming,live-summary,rtc-summary}.json`.

## Final independent telephone completion audit

The explicitly selected OpenAI/Codex-account reviewer returns **PASS** for all
four substantive goal criteria, with no concrete unmet criterion or remaining
P0/P1. The audit independently checked the native raw output, the scoped-review
176-test raw output, published source, strict checker, catalogue/FAQ consumers,
consent/ownership tests and preservation/publication receipts. It did not repeat
provider calls, the completed dashboard audit or another owner's pipeline work.

The full-suite and browser raw-log paths were unavailable to the auditor; a
subsequent parent availability check confirms those two files absent while native
and scoped-review raw logs remain present. Full-suite results were assessed from
the retained tested-source manifest and green head/masterCI; browser results from
the retained manifest, not independently reread raw browser logs. This explicit
qualification is not an additional rerun or a claim that CI ran browser journeys.
The reviewer found no unmet criterion from it. Historical failed runs and scope
limits remain unchanged.

The full native evidence report was already committed/pushed as `447755a5…` and
GitHub content-verified. This audit disposition is a documentation-only addendum;
application/test/deployment source remains the verifieda7be release and is not
redeployed merely to update the report.

## Publishedff recognition integration — new native result pending

During close-out, the dateda7be runtime guard correctly rejected the separately
published/deployed `ff11d69279d1b0e7f9fe59b4c1ce77b262dd1aa3`. This is a substantive
input-recognition delta, not document-only source drift. Its published changes
were normally merged into the owned branch without rollback or dirty-worktree
copying. The current application/test/deployment tree equals publishedff; only
this report differs.

The complete new combined suite passes **12,696 tests/36 subtests**, exit0,
214.19s, with six explicit opt-in skips and two existing warnings. All eleven
Chromium journeys pass without JavaScript errors/external requests. Published
master CI37182061857 passes both release/image jobs. Unlike the missing older
audit log paths, the new full/browser raw logs are copied to bounded private
`restaurant-recovery-ff-{full,browser}.log` artifacts with hashes in
`restaurant-recovery-ff-tests.json`; this does not retroactively change the
older audit's raw-log availability qualification.

Locked06:22:20Z proof matches95app/demo files per healthy web/worker/bridge role,
original volume/infrastructure/media, original voices/delivery/chat and all nine
authorization/no-store cases. Four database integrity checks and every original,
972,4ba anda7be premerge row prefix pass. Production input ASR now uses unrestricted
Azure `MAI-Transcribe-2` preview through the published peer repair; independent
output recognition remains automatic Azure standard with no answer/language hints.
An initial verification incorrectly required the transport-only bridge to select
the recognition provider too and failed at `source_profiles`; that failed receipt
is retained. Actual recognition roles are web/worker, both Azure; the bridge has
no recognizer. No production setting or source was changed to correct the
verification-role assumption.

The narrow Codex recognition integration review passes769tests/43.73s, no P0/P1.
All twelve fresh exactff cases pass individually, but the aggregate at06:28:01Z
remains **FAIL**: the final runtime check observed PR39's web release rather than
the pinnedff lineage, so the entire-batch end state check was not executed. The
individual checks prove each language's unchanged restaurant state, not a full
successful aggregate. The failed receipt is retained; no freshness guard was
changed to accept it. Later observation found all three roles synchronized to0bb.
The completed once-onlya7be audit stays dated base approval.

## Latest published peers and urgent phone delivery

PR39 adds grounded uncertainty/service-question handling through the shared
restaurant pipeline. Current0bb checks pass12,861tests/36subtests in236.86s,
six opt-in skips/two existing warnings and all eleven Chromium journeys. Master
CI37182869738 passes both jobs. Raw full/browser logs are retained and hashed in
`/tmp/opencode/restaurant-recovery-0bb-tests.json`. Subsequent956 changes only three
research documents;97app/demo hashes and app/data/tests/deploy match0bb exactly.

The initial0bb preservation assertion fails because its newerff call-session
prefix changed, not because original records or bookings disappeared. Diagnostics
verify all original/972/4ba/a7be prefixes, four integrity checks and unchanged
whole booking state85reservations/167actions/0holds,42Easy writes,5Stay bookings
and34call-booking associations. Three browser sessions subsequently expired,
each with only one appended `ended/expired` event. Read-only in-memory replay of
the four fields written by `call_history.end` restores the **exact originalff
prefix hash**; no identities/counters/other fields are ignored and no database
was modified. The failed first receipt and the lifecycle qualification remain
retained. No cross-database atomicity or identity of newly appended calls is claimed.

The Codex PR39 review passes665scoped tests,12canonical answers,12owned-hold seams
and9mixed-action negatives, but reproduces emergency guidance lost during booking
or a waitlist clause. The minimal pending repair changes only those two routing
conditions: unreviewed booking fields are still discarded, held ownership/expiry
stays intact, and delivery/approval must be revoked. No new emergency classifier,
booking route, voice setting, ASR hint or private-checker relaxation is introduced.

The existing configured number is already account-owned, voice-capable and routed
directly to the robot webhook with POST (no trunk/application override). This is
provider configuration proof, not a carrier/PSTN test call. Final repair publication,
service synchronization and exact new-release native proof remain pending.

The first emergency repair preserved 112 routing but still lost six held proposals
because the generic observer cleared `pending` before an early safety return.
The focused re-review and the initial full suite both retain that failure (full:
6failed/12,873passed/36subtests). The final bounded addition restores only an
unexpired, owned, unconfirmed prior hold into a new proposal object, with delivery
and approval both false; discarded booking preferences are not resurrected.
The current focused urgency suite passes27cases in5.66s, including all eighteen
new regressions. Final focused Codex re-review passes44tests plus twelve isolated
ET/EN/RU valid/expired/unowned/already-confirmed controls, resolving both P1s with
no remaining concrete P0/P1. Invalid proposals are not restored. All eleven final
browser journeys pass. The final full suite passes **12,879 tests/36 subtests**
in239.78s, with six opt-in skips and the same two existing warnings. Raw output
is retained and SHA256-verified in
`/tmp/opencode/restaurant-recovery-emergency-tests.json`; source hashes still
match the reviewed candidate. Publication and newer-peer integration follow.
