# Grounded browser restaurant replies

## Implementation

- Browser questions use generated wording and a separate model review against
  configured restaurant facts. All three supported languages follow this path.
- Menu recommendations and deductions can combine facts; current table capacity
  does not imply availability. No generated-answer request receives booking tools.
- Final speech accepts only the exact approved reply for the current turn,
  language and fact digest. Booking summaries, consent, backend writes,
  cancellation, uncertain results and allergy safety keep their existing guards.
- A translated **Food recommendation** example button exercises the same endpoint
  as microphone questions. Existing responsive layout and voice choices remain.
- See [operation and limitations](../operations/grounded-restaurant-answers.md).

## Local checks

Project core Python 3.13.15 and pinned dependencies, with synthetic provider
responses and temporary SQLite storage:

- Complete core suite before the final upstream integration: **10,742 passed,
  67 skipped, 36 subtests passed**. One existing Starlette TestClient deprecation.
- After integrating upstream `f8edaa1`: restaurant reasoning, HTTP, conversation,
  consent, receipts, domain and provider checks: **539 passed, 36 subtests passed**.
- New reasoning regression module: **43 passed**. Covers ET/EN/RU wording, known
  source IDs, language, provider and review failures, malformed output, tool and
  success claims, stale approvals, disabled operation, strict request schemas,
  request timeouts, history, guest-count and closing-time implications, and
  untrusted guest instructions. These are fixture checks, not live model evals.
- Separate media environment: restaurant native booking/greeting checks:
  **107 passed**, with one existing warning. Native speech remains reviewed.
- Chrome 154 restaurant browser checks passed after upstream integration:
  translated recommendation buttons and replies, consent, saved booking details,
  cancellation, reload, microphone capture, logout isolation, desktop and mobile,
  and retired-host denial. **0 page errors and 0 external requests**.
- Booking browser and streaming audio browser checks passed with local synthetic
  audio; actual layout and playback/receipt logic exercised.
- Desktop and mobile screenshots inspected. JavaScript syntax, `git diff --check`
  and `flake8.cmd --select E9,F` passed.
- `basedpyright.cmd --pythonpath <project core Python> --level error` reports
  **0 errors/warnings** in the new reasoning module. The five changed production
  Python modules together retain **17 existing errors**; the same four legacy
  modules at upstream `f8edaa1` had 20. Exact diagnostics comparison shows three
  removed errors and no added errors. The repository-wide type check is not green.

## Live verification boundary

The public backend policy/capability and the versioned frontend asset must be
checked after deployment; a merge alone does not establish live activation.
This Windows workspace has no production operator credential or provider key.
Authenticated live model generation and listening quality therefore remain
unverified. Local browser responses are synthetic and the model reviewer cannot
guarantee perfect semantic accuracy in real conversations.
