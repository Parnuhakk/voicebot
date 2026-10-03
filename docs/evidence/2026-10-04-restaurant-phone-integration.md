# Restaurant telephone capability integration

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
Private live ET/EN/RU acceptance and deployment of this final correction remain
pending until recorded against the actual synchronized release.

This document does not claim a physical microphone test, a carrier/PSTN call,
real restaurant acceptance, an allergy-safe meal, a food order or a real booking.
