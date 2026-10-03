# Natural Estonian, English and Russian conversation

The telephone worker and protected HTTP demo share conversational wording and
Azure speech delivery. The existing Groq models, Azure voices and booking
adapters remain in use. No new provider account or dependency is required.

## Conversation

The restaurant assistant introduces itself as a virtual assistant in a fictional
demo. Estonian instructions request idiomatic Estonian, consistent informal
address, a direct answer followed by a short explanation when needed, and usually
one to three complete sentences. They avoid English terminology, fragmented
phrases, repeated introductions and an unnecessary follow-up question on every
turn. Reviewed FAQ wording remains exact rather than being freely paraphrased.

Restaurant identity and staff-transfer replies use their own reviewed wording.
They do not offer legacy spa or hotel bookings. Menu/allergen, food-order,
opening-hours and table-reservation questions use reviewed answers. Hours and
restaurant bookings remain unconfigured; the assistant does not invent them.
Legacy spa/stay integrations retain their separate catalogue and recap policy.

### English restaurant understanding

The shared restaurant router recognizes natural English table, menu, dietary,
allergy-note, takeaway/delivery and opening-hours requests. Whole-utterance
matching accepts polite introductions, hesitations and contractions such as
“I'd like a table for four” and “I was wondering if you're open on Sundays”.
Clear English restaurant clauses can override an erroneous ASR language label;
weak yes/no, numeric and AM/PM answers retain the current voice. A request
to speak English gets a short English acknowledgement. Transcripts and
write-consent phrases are not rewritten.

Reviewed FAQ answers remain authoritative. A table request receives the booking
limitation directly, without collecting dates or AM/PM for an unavailable
service. Each fully recognized clause of a mixed English request receives its
own reviewed answer; unknown extra clauses prevent the shortcut. Explicit topic
corrections such as “No, I meant the menu” select the new topic. Short followups
such as “What about Sundays?” use the last answered topic in the same call.
English repeat requests replay the last reviewed FAQ answer. Only a bounded
set of FAQ identifiers survives for this context, not caller text; unrelated
questions clear it. Existing owned-recap playback and fresh-consent rules still
apply separately.

Both native and HTTP Groq recognition support a short static English restaurant
spelling vocabulary when the current call is English. Fixed English mode also
sends `language=en`. Auto mode keeps language autodetection and permits switching
to Estonian/Russian; the spelling hint is removed after a language change. Native
context changes only after a final caller turn. HTTP uses separate per-call
provider views, so concurrent sessions cannot mutate shared recognition options.
The hint contains no caller history, caller names, requested dates/times, prices or
confirmation phrase. Other integrations retain their existing recognition
contract. See [Groq's transcription parameters](https://console.groq.com/docs/speech-to-text#using-the-api)
for the language and spelling-prompt API. This is a configuration change, not a
measured claim of improved word error rate.

`tests/test_english_restaurant_understanding.py` covers native/shared and HTTP
routing, wrong language metadata, contextual followups, topic corrections,
repeats, mixed requests and isolated multipart recognition requests. Synthetic
provider responses exercise English-to-Russian switching and cleanup. Live ASR
accuracy, accents, background noise and audible response quality still require
real calls after deployment to both processes.

### Multilingual date and time answers

Both transports parse finalized caller turns in Estonian, English and Russian
using one current `Europe/Tallinn` clock snapshot. Partial transcripts never
update booking preferences. Strong calendar words also identify the language of
short answers when ASR language metadata is missing or wrong; numeric answers
retain the current language and voice.

`app/temporal.py` recognizes month and weekday names, Estonian case endings,
Russian declensions, spoken days 1–31, spoken years 2000–2099, numeric dates,
ISO timestamps and explicit AM/PM or dayparts. Examples:

| Language | Date answer | Time answer |
| --- | --- | --- |
| Estonian | `homseks`, `kuuendaks oktoobriks`, `järgmisel kuul kuuendal` | `pool seitse õhtul`, `kella kuueks`, `18:30` |
| English | `tomorrow`, `October sixth`, `next month on the sixth` | `half past six pm`, `quarter to six pm`, `18:30` |
| Russian | `завтра`, `шестого октября`, `шестого числа следующего месяца` | `в половине седьмого вечера`, `без десяти шесть вечера`, `18:30` |

Relative durations include days, weeks, calendar months/years, hours, minutes,
compound hours/minutes and half/quarter hours. Elapsed hours/minutes add real
time in UTC before returning to Tallinn local time. Calendar month arithmetic
preserves the day; an impossible result such as January 31 plus one month needs
clarification. “The next day” needs a previously stated absolute date.

An omitted year means the next real occurrence, including today; February 29
resolves to the next leap year. Explicit years and past weekdays are preserved
and past appointments are rejected. Ambiguous slash dates, weekday references,
AM/PM (including English/Russian unpadded `6:30`), approximate clocks, ranges,
alternatives, vague dayparts, foreign named timezones and incomplete dates ask
for clarification. The bot never selects an
alternative on the caller's behalf. ISO offset timestamps convert the actual
instant; nonzero seconds need a minute-precision answer. Nonexistent DST wall
clocks and repeated autumn wall clocks cannot authorize an appointment. The
same validation runs again on tool arguments, including dates/times supplied on
separate turns.

`requested_dates`, `requested_times` and `temporal_issue` reach HTTP instructions;
native planning injects current parsed fields before the final user message.
Legacy booking inquiries retain known date/time fields across localized
followup questions. Ambiguous clocks retain a valid date privately while
blocking booking tools until a precise clock is supplied. A short daypart answer
such as `PM` or `вечером` resolves a single previous AM/PM ambiguity. A complete
resolved request feeds exact ISO date and HH:MM into the existing booking backend.
Booking confirmation still requires the owned recap to finish playing and a
new final caller turn containing explicit consent.

Restaurant table inventory remains unconfigured. The restaurant demo can
acknowledge understood visit dates/times but cannot create a real reservation.
Calendar parsing never creates availability, a hold, recap delivery or consent.
No new provider or dependency is added. The new multilingual tests exercise
ET/EN/RU grammar and mocked backend confirmation, HTTP planning and native final
turns; existing Estonian tests retain midnight/year/leap-year coverage. These
fixtures do not establish live ASR recognition or telephone audio quality.

Grammar references: [EKI numeral inflection](https://teatmik.eki.ee/teatmik/keelenouvakk/kuidas-kaanata-arve/),
[EKI compound numerals](https://keeleabi.eki.ee/viki/Arvsonade_kokku-_ja_lahkukirjutamine.html),
[Gramota ordinal date forms](https://gramota.ru/spravka/vopros/255101).

Standalone greetings, thanks, goodbyes, declines, repeat requests, frustration,
identity and human-transfer questions use reviewed replies in Estonian, English
or Russian directly.
These turns need no model request. Repeated social turns can select a different
reviewed reply within the same call. Mixed requests such as “Thanks, book a room”
still reach planning. The bounded conversation state stores intent and counters,
not the caller's words.

In legacy spa/stay integrations, service questions read the verified service
choices without also reciting the working schedule. Opening-hours questions read
the verified schedule and explain
that appointment availability requires a separate check. Backend names, quotes,
receipts and FAQ answers retain their authoritative wording.

“Could you repeat that?” during a pending proposal repeats the exact owned
recap. The hold and expiry stay the same, but delivery and consent reset. A late
playback event from the previous reading cannot approve the new reading. The
caller must hear the repeated recap and then give fresh explicit consent.

## Speech settings

| Variable | Default | Behavior |
| --- | --- | --- |
| `VOICEBOT_SPEAKING_STYLE` | `natural` | Shared speech styling; `neutral` removes prosody, pronunciation aliases, pause settings and expressive style. |
| `VOICEBOT_SPEECH_RATE` | `0.98` | Normal rate multiplier, accepted range `0.85`–`1.15`. |
| `VOICEBOT_RECAP_RATE` | `0.94` | Recap multiplier, capped at the normal rate so recaps never become faster. |

English `en-US-JennyNeural` uses Azure's supported `friendly` style at degree
`0.8`. Estonian Anu and other configured voices keep their normal voice style,
with the shared rate adjustment. Voice and locale continue to follow the active
language. Invalid settings fail before provider requests and do not echo values.

Estonian speech uses explicit Azure silence settings: zero leading silence,
120 ms at the end of a synthesis request, and 200 ms between sentences. Recaps
use a 240 ms tail and 320 ms sentence boundary. The shared renderer applies this
to both HTTP replies and native per-sentence synthesis, reducing silence added
between separate sentence requests. English and Russian delivery retain their
existing settings. These are a listening preset, not measured proof of perceived
naturalness. See [Azure's documented silence settings](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-structure#add-silence).

Estonian ISO dates, date-times, `kell H`, `kell H:MM`, valid clock ranges and
`Europe/Tallinn` use SSML pronunciation aliases. For example, `kell 9:30` is
pronounced “kell üheksa kolmkümmend”. Clock-range normalization and aliases occur
at synthesis, while the displayed reply stays unchanged. Delivery comparisons
and the transcript still use the exact server recap. Invalid dates/times remain
literal. Prices, quantities and identifiers are not reinterpreted as clocks.
All speech text is escaped before markup is introduced.

The native provider renders complete markup for each synthesis request **after**
LiveKit splits plain text into sentences. HTTP synthesis uses the same renderer.
This prevents sentence tokenization from splitting XML tags. Existing scoped
playback receipts, interrupted-recap handling, independent cached failure audio
and uncertain-write protection remain active.

`/api/status` reports the selected style and rates. It describes application
configuration and does not establish the telephone worker's deployed revision.

Browser reply audio uses Azure's high-fidelity 48 kHz / 96 kbit/s mono MP3 output,
instead of the previous downsampled 16 kHz / 32 kbit/s output. This preserves the
same voices, wording and speech settings, but increases transferred audio bytes.
The native worker retains 24 kHz PCM; PSTN codec bandwidth is unchanged.
See [Azure's supported audio formats](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech#convert-text-to-speech).
Higher fidelity is objectively verifiable, not proof that listeners perceive a
voice as human. Listening preference remains separate from configuration tests.

## Activation and listening

GitHub changes must reach both the web process and the separate telephone worker.
The deployment helper preserves these three optional settings from the trusted
web container; Compose supplies the defaults when they are absent. Follow the
[English telephone deployment runbook](english-telephone.md#deploy-the-telephone-worker)
using the existing shared booking volume.

To return to neutral speech, set `VOICEBOT_SPEAKING_STYLE=neutral` and restart
the affected processes. Conversational wording remains available.

With provider and server access, compare English and Estonian calls for clear
dates/times, comfortable pacing, short questions, repeated recaps, interruption,
explicit confirmation and cancellation. Local fixtures verify policy and request
construction; they cannot establish audible naturalness or live call latency.

Provider references:
[Azure SSML voice and prosody](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-voice),
[Azure voice/style support](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support),
[LiveKit Azure TTS](https://docs.livekit.io/agents/models/tts/azure/).
