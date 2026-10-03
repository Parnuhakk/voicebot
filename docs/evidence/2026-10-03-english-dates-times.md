# English ordinal dates and spoken clock follow-ups

The reported `4th October` and `6 o clock` inputs now use the shared ET/EN/RU
calendar and spoken clock parsers. An ambiguous six retains 06:00 / 18:00 while
asking for AM or PM. A later `pm` or `in the evening` resolves that hour without
discarding the date or guest count. Model arguments cannot bypass clarification.
The preceding question distinguishes a bare hour from a bare guest count.
Negated or invalid times clear a previous selection instead of silently reusing
it. Adjacent `12pm` and `11am` values cannot become a date's two-digit year.

## Local verification

- Final media environment suite: **4738 passed, 10 skipped, 36 subtests passed**.
  One existing FastAPI/Starlette TestClient deprecation warning remains.
- Focused shared clock, English date/time, conversation and native hook suite:
  **398 passed** after integrating the current shared parsers.
- The real local HTTP route was exercised with typed replies and synthetic audio
  through Groq's transcription metadata adapter. Date, 18:00 and four guests
  reached the recap without an early reservation write.
- Chrome browser fixture passed English ordinal dates and `6 o clock` followed
  by `in the evening`, recap delivery, separate confirmation, immediate receipts,
  cancellation, all three languages, unsupported-language prompts, synthetic
  microphone WAV capture, reload/logout isolation and 320/390/1440px layouts.
  No external requests or browser page errors. The inspected receipt showed
  4 October 2026, 18:00–19:30, four guests and the stored table identifier.
- Flake8 E4/E7/E9/F, JavaScript syntax and Git diff whitespace checks passed.
- BasedPyright used the project's media interpreter. Current files and pristine
  master both report the same **13 existing server errors**, with no introduced
  errors. The changed calendar/clock modules and conversation policy have no
  type errors. Existing dynamic-type warnings remain.

## Deployment verification boundary

The public status flag `capabilities.restaurant_english_dates_times_ready` marks
the deployed implementation. Website/health/status readback can confirm release
availability without operator credentials. Local synthetic transcripts and
native final-turn hooks do not verify acoustic recognition from a physical
microphone, live speech providers, a carrier call or the separate native worker's
release. Reservations are still fictional restaurant demo records.
