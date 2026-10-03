# Booking confirmation and visible details

## Behavior

- After a successful restaurant write, the Estonian assistant says
  `Teie broneering on tehtud. Broneeringu detailid leiate siit lehelt.`
  English and Russian have equivalent confirmations.
- The conversation and direct booking form immediately show the committed
  date, Tallinn time interval, guest count, configured table name and booking ID.
- The authenticated reservation list refreshes and selects the saved date.
  Cancellation updates the visible receipts. Logout clears private UI data.
- SQLite reservation persistence and the existing ownership, consent, recap
  delivery and idempotency rules remain in use. This is a fictional demo;
  reservations are saved in the demo system, not a real restaurant provider.
- Failed or unknown mutations do not produce successful booking receipts.
  Optional display metadata cannot turn an already completed write into failure.

## Local verification

- Full core suite: **3116 passed, 65 skipped, 36 subtests passed**. One existing
  FastAPI/Starlette TestClient deprecation warning remains.
- Restaurant browser checks passed with real local HTTP requests and SQLite,
  synthetic speech, all three languages, immediate receipt details, cancellation,
  reload persistence, failed writes and logout isolation.
- Booking and streaming browser checks passed. No page errors or external
  requests. Inspected desktop and 320 px screenshots of the saved receipt.
- `node --check`, `git diff --check` and `flake8.cmd --select E9,F` passed.
- `basedpyright.cmd` on the four changed Python files reported 19 errors.
  A clean checkout of the deployed base reported the same 19 error messages;
  no type errors were introduced. Dynamic-type warnings remain.

## Verification boundary

Provider speech is synthetic in these checks. No live authenticated booking or
pronunciation check was performed: the production operator credential is not
available in this workspace. Public deployment readback checks the website,
health endpoint and exact versioned JS/CSS bytes separately.
