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

The final rollout uses the existing Coolify application and original shared
volume, with the existing release lock, a fresh zero-room check and normal
non-forced publication. Live activation, source hashes, private authorization,
data preservation and provider-backed ET/EN/RU results are recorded in the
session-owned goal evidence after publication, not inferred from these fixtures.

This document does not claim a physical microphone test, a carrier/PSTN call,
real restaurant acceptance, an allergy-safe meal, a food order or a real booking.
