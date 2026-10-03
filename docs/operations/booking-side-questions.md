# Questions during a restaurant booking

In Estonian, English and Russian, restaurant turns answer an information question
and then resume the next missing reservation detail. Previously supplied date,
exact clock, guest count, unresolved clock/date choices and offered alternative
times remain in the call's existing bounded booking state. A short subsequent
answer belongs to the resumed booking prompt rather than the earlier menu/hours
topic. Information questions containing numbers or dates do not silently change
booking fields.

The browser's existing generated/reviewed information answers can supply the
answer while collecting details; the server appends the authoritative missing
question. Provider/review failures retain reviewed wording and the same prompt.
Allergy safety remains reviewed. No generated request invokes booking tools.

## Prepared summaries

A question during a valid owned proposal preserves the same table hold and
expiry. It creates a new proposal object with delivery and approval revoked.
The response reads the approved answer, a short return-to-booking sentence and
the complete canonical booking summary ending with the consent question.
Existing exact-response delivery checks therefore cover the entire reply,
including the summary. No second search/hold or booking write occurs just to
answer the question. Stale HTTP receipts and late native playback reference the
old proposal and cannot authorize the new one.

Later consent still requires completed current playback or explicit reading of
the current summary. JSON responses with failed audio remain readable and can
be explicitly acknowledged; failed synthesis itself grants no delivery. If the
proposal expired, the answer offers a new availability check, and agreement
replans rather than confirms the expired hold. A new summary and later consent
are then required. Declines, explicit changes/cancellation, recovery and uncertain
write handling do not revive the old proposal.

## Channels and deployment

The website's text and recorded microphone input share this behavior. The shared
native call tools also implement it; the separate native worker needs its normal
release synchronization to receive a new web revision. Optional external voice
dialogue profiles are unchanged. Local tests use synthetic transcripts/audio,
real HTTP routes, temporary SQLite and the installed media SDK. They are not
live speech recognition, provider generation or carrier call measurements.

`GET /api/public/restaurant` exposes `booking_interruption_version` as
`resume-booking-v1` for deployed-code readback. This marker does not establish
successful live provider requests.
