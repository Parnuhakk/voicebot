# Restaurant voicebot: pitch-ready brief

**Prepared 4 October 2026.** Facts, estimates and prototype capabilities are separate below. Full definitions, formulas, contrary evidence and 23 source entries: [research report](estonia-restaurant-voicebot-pitch-2026-10-04.md).

## The strongest defensible story

> Restaurants should not have to choose between serving the guest in front of them and answering the next caller. We are building an Estonian, English and Russian restaurant receptionist that answers approved questions and guides callers through a reservation with a full recap and explicit confirmation. Our prototype currently uses fictional restaurant data; real calendar integration and carrier-call acceptance still need verification.
>
> Estonia had 2,228 restaurant and mobile-food-service enterprises in 2024. At an assumed €149 monthly fee, our illustrative base case needs eight genuinely additional seated parties per month to cover the fee. We will test the economics in real restaurants rather than claim every missed call is a lost booking.

Market source: [Statistics Estonia EM001](https://andmed.stat.ee/en/stat/EM001), cross-checked with Eurostat. Enterprises are not restaurant locations; many do not take table reservations. Economics are modeled, not achieved.

## Five slide numbers

| Slide | Number to use | Required label |
| --- | --- | --- |
| Local market | **2,228 enterprises** | Estonia, restaurants/mobile food service, **2024**; not outlets or qualified buyers |
| Sector scale | **€906m annual turnover; 17,274 persons employed** | Same official category/year; turnover is not software TAM, employment is not FTE |
| Phone relevance | **~70% revenue-related call intent** | Foreign Yelp/Slang vendor datasets; includes orders/waitlist/catering, not booking conversion |
| Illustrative value | **€405 monthly dining contribution** | Base assumptions: 750 calls, 20% missed, funnel/spend/margin below; before assumed fee |
| Fee break-even | **8 additional seated parties/month** | Assumed €149 fee, 2.5 diners × €25 net spend × 30% contribution per party |

Within the assumed one-account-per-counted-enterprise model, the qualified opportunity is an unmeasured subset: the mechanical ceiling at €149/month is **€3.98m/year**, not a validated TAM or a universal market upper bound. An assumed 30% customer-fit scenario gives **668 accounts / €1.19m/year**. **50 retained paying accounts = €89,400 ARR**; this is a scenario, not current traction or a dated forecast.

## Base case: show the funnel, not just the headline

```text
750 assumed monthly calls
× 20% assumed missed = 150 missed calls
× 40% eligible table-booking intent = 60 eligible attempts
× 60% usable booking completion = 36 bookings
× 60% net incremental seated factor = 21.6 additional seated parties
× 2.5 diners × €25 net spend = €1,350 incremental net dining revenue
× 30% incremental contribution = €405
− €149 hypothetical all-in fee = €256 booking-only monthly benefit
```

The net seated factor accounts for cancellations/no-shows, duplicates, customers who would book another way and displaced existing demand. Fractional counts are expected values, not observed customers. Fee and spend are excluding VAT; extra customer onboarding/integration costs are omitted. **All funnel inputs are assumptions.** No representative Estonian call-volume or missed-call rate was found.

| Monthly scenario | Low | Base | High |
| --- | ---: | ---: | ---: |
| Assumed calls / missed share | 300 / 10% | 750 / 20% | 1,500 / 30% |
| Incremental dining contribution | €81 | €405 | €1,215 |
| After assumed €149 fee | **−€68** | **€256** | **€1,066** |
| Redeployed staff time, separately modeled | 6.3 h | 14 h | 24.5 h |

Staff time assumes 70% of previously answered calls avoid two net staff minutes each. It is capacity freed for guests, **not automatic payroll savings**. With only 20% net incrementality or a 10% contribution margin, base contribution falls to **€135**, below the fee. A venue already full may generate no additional business.

## Why a pilot is necessary

- **Missed calls are not uniform:** Revmo reports 9.0% for full-service versus 40.1% for QSR, in a foreign vendor sample of 12,091 calls. Do not reuse “43% missed” as an Estonia fact.
- **Telephone-AI comfort is limited in this UK survey:** SevenRooms found only 28% of surveyed consumers comfortable booking with AI by telephone. The broader 73% AI-booking comfort figure is a different question, not a phone acceptance rate or a direct human-versus-AI preference measure.
- **Existing vendors demonstrate the category, not our traction:** named foreign deployments and Yelp's platform-scale calls do not establish our paying customers, recovered revenue or error rate.
- **€149 is a pricing hypothesis:** Yelp currently lists US$249 Basic / US$399 Plus, with different scope and terms. Our own provider costs, support load and willingness to pay are unvalidated; unlimited high-volume service can be unprofitable.

Original-source details: [telephone evidence](estonia-restaurant-voicebot-pitch-2026-10-04.md#3-what-the-restaurant-phone-evidence-really-says), [pricing/economics](estonia-restaurant-voicebot-pitch-2026-10-04.md#5-pricing-and-provider-unit-economics), [source ledger](estonia-restaurant-voicebot-pitch-2026-10-04.md#source-ledger).

## What to demo and what not to claim

**Demo:** an approved question in ET/EN/RU; collect date, exact time and total diners; read the full recap; require explicit consent; show the saved fictional reservation; demonstrate an owned cancellation and a refusal to invent an allergy-safety answer.

**Useful engineering evidence:** the repository already contains a 270-concept / 810-pair multilingual question catalogue across 17 categories. This is authored coverage, not customer traffic or measured speech accuracy. Session/error counters and bounded voice timing logs exist, but do not currently establish missed carrier calls, incremental seated business or production SLOs.

**Never claim:** real restaurant bookings, completed staff transfer, food orders/payments, carrier acceptance, 100% accuracy, guaranteed ROI, a receptionist salary saved, or fictional dashboard rows as traction. Inspected scope is pinned to `7dcb14b`; later integration work requires separate verification.

## Suggested pilot ask

> We are looking for 5–10 reservation-taking restaurants with busy phones. After verifying a real calendar, carrier calls and a monitored human fallback, we will measure two baseline weeks and four service weeks, using normalized trading-hour/day rates and a matched or crossover comparison. Success means correct consented bookings, additional seated parties against that counterfactual and an economic benefit after fees—not just more calls answered. Uncontrolled before/after changes are descriptive, not proof of recovered business.

Measure offered carrier calls, missed share, answer time, intent/language, audited booking correctness, safe-write incidents, autonomous resolution, completed human assistance, end-to-end p50/p95 latency, net staff time, seated/POS-linked incrementality and actual provider costs. Keep synthetic and real traffic separate.

**Proposed targets, not current performance:** ≥95% timely answers within 10 seconds; ≥60% eligible booking completion; ≥98% of audited bookings correct in every required field; response p50 <1.5s / p95 <3s; investigate every unsafe write; positive customer benefit and at least three retained paying pilots before claiming validated pricing. Report denominators and failures, not only percentages.

## One-line answers for judge questions

- **How many restaurants are there?** “The official 2024 category has 2,228 restaurant/mobile-food-service enterprises; we have not verified a restaurant-outlet count or qualified-buyer count.”
- **How much money do you recover?** “Not measured yet. The base model estimates €405 contribution before a hypothetical €149 fee, and the low case is negative.”
- **Why three languages?** “ET/RU have a strong local rationale and English serves a tourism hypothesis; the actual call-language mix will be measured.”
- **Is it already production-ready?** “No. The guarded multilingual prototype uses fictional data; real calendar, carrier and human-fallback gates remain.”
- **What is your advantage?** “The hypothesis is locally useful ET/EN/RU reception with approved facts and explicit booking consent. We still need comparative pilot evidence; we do not claim unique models or no competitors.”
