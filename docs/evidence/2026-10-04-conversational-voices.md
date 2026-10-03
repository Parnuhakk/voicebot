# Restaurant conversational voices — 2026-10-04

## Change

The website prefers `azure-conversational` after its authenticated catalog has
loaded. English and Russian use `en-US-EmmaMultilingualNeural`; the optional male
profile uses `en-US-AndrewMultilingualNeural`. Estonian retains Anu/Kert. These
profiles keep provider sentence timing instead of imposing an identical pause
after each sentence. Operator speaking-rate settings and slower booking recaps
remain effective. Voice choice stays owned by the session.

The shared SSML renderer explicitly sets multilingual `<lang xml:lang>`, including
neutral mode, and retains escaped canonical captions and pronunciation aliases.
Only the two documented multilingual speaker/locale pairs used here are allowed.
The telephone settings accept these voices when explicitly configured; existing
worker defaults/environment are not changed by the website default.

No provider/account change, new dependency, HD/preview endpoint, pitch shifting,
unsupported emotion styles or fake breathing is introduced. A provider rejection
can use the existing Azure voice before audio starts. Partial audio never switches
speaker or grants a completed booking recap receipt.

## Local checks

- Pinned media environment: **837 passed** across conversational voices, Azure
  profiles, catalog and selection, voice config, Russian pronunciation,
  restaurant HTTP/consent/native/greeting/conversation and natural speech suites.
- Chrome **154.0.8037.97**, existing restaurant browser runner: all three languages,
  six new profile/language auditions, preferred default, delayed catalog gating,
  explicit selection preserved after catalog refresh, desktop/mobile,
  reservations/receipts/confirmation/cancellation and microphone passed.
  **0 page errors; 0 external requests.**
- `flake8.cmd --select E4,E7,E9,F` on changed Python files passed.
- `basedpyright.cmd --level error` with the pinned media interpreter on changed
  provider files: **0 errors**.
- `node --check` and `git diff --check` passed. The restaurant script's content
  hash in the HTML was refreshed for browser cache invalidation.

These are local fixtures: Azure HTTP requests use synthetic MP3, and the real
LiveKit plugin's per-sentence request uses simulated PCM. They verify routing,
markup, failure handling and browser playback, not live provider pronunciation.
After integrating the current master, a full core run found eight instances of
one stale catalog expectation; 11,104 other cases passed, 72 skipped and 36
subtests passed. The catalog expectation was expanded to the new profile IDs,
and the shared legacy dashboard accepts the new catalog as well. The focused
catalog/UI checks and complete Linux CI cover the corrected integration.

## Listening boundary and rollback

Live Azure synthesis and human listening were not available in this workspace.
After publishing, use **Listen to voice** to compare the standard and
conversational profiles in English/Russian. Start a new session to change speaker.
The standard voice remains selectable; automatic failure metadata identifies it
when used. Subjective naturalness and real telephone audio are separate acceptance
checks and are not claimed by the fixture results.

Primary provider contracts checked 2026-10-04:
[multilingual speech and locale selection](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-voice#adjust-speaking-languages),
[documented voices and languages](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts).
