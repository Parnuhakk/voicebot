# Restaurant answers in the browser

The restaurant website's text and recorded microphone turns can now compose
short answers in Estonian, English and Russian from the configured venue facts.
Guests can ask for recommendations, combine several rules, or ask a follow-up.
The **Food recommendation** example button sends a dietary preference question
in the selected language. It uses the same conversational endpoint as speech.

## Sources and approval

The primary Groq client receives the approved menu, opening and kitchen hours,
reservation and capacity rules, current venue date and information policies.
Configured capacity is explicitly **not** current table availability. At most
eight recent user/assistant messages supply context; tool messages and guest
fixture details are excluded. The provider receives this bounded conversation
text, as in ordinary model turns; it must not treat guest instructions as venue
facts.

A first request generates JSON containing a new reply, its supporting fact IDs
and language. Local checks reject malformed output, unknown sources, unsupported
actions, prices, contact collection and allergy guarantees. A second, separate
request to the same configured model checks relevance, language and whether all
claims and deductions follow from the supplied facts. Approval expires when the
turn, language or fact snapshot changes. Internal reasoning and source IDs are
not shown or spoken.

The default GPT-OSS models use Groq's strict JSON schema mode without tools or
streaming. Other configured Groq models use JSON object mode and the same local
checks. See [Groq structured outputs](https://console.groq.com/docs/structured-outputs).
The existing low reasoning effort and hidden reasoning configuration remains;
see [Groq reasoning](https://console.groq.com/docs/reasoning).

The reviewer is a model judgment, not a formal proof of factual or mathematical
correctness. Shared model mistakes remain possible. Venue facts must be kept
accurate, and real conversations should be checked with provider access.

## Consequential state

Owned booking summaries, delivery receipts, later consent, backend writes,
confirmed booking details, cancellation, uncertainty, language recovery, allergy
safety and human handoff retain their existing authoritative handling. Generated
answers cannot invoke tools or establish booking consent. The separate native
telephone worker continues to use reviewed restaurant answers. Optional external
voice dialogue profiles are unchanged.

Information questions while collecting a booking use generated wording with
the server's next missing prompt appended. Questions during a prepared summary
use approved venue wording followed by a fresh reading of the same owned
summary. See [questions during a booking](booking-side-questions.md).

## Operation and fallback

`VOICEBOT_RESTAURANT_REASONING` defaults to `1`. Set it to `0` and restart the web
process to return browser questions to reviewed wording. Existing Groq credentials
are reused; there is no new key, dependency or public model-call endpoint.

An eligible question adds up to two model requests, each with an eight-second
HTTP timeout and no helper retries. Replies are capped at 650 characters and
prompted to use at most three short sentences. This can increase latency and
model usage compared with a direct stock answer. Provider failures, rejected
reviews or invalid output retain the approved canonical response and produce the
`grounded_reply_unavailable` turn warning; booking tools are never replayed.

`GET /api/public/restaurant` reports `answer_policy_version` as
`grounded-restaurant-v1` and `grounded_answers_ready` for configured, enabled
support. These fields establish deployed code/configuration, not a successful
live provider request. Test fixtures establish routing and fallback behavior,
not live voice quality or model accuracy.
