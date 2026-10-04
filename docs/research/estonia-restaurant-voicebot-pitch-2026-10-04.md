# Estonia restaurant voicebot: market, telephone demand and economics

**Research date:** 4 October 2026. **Purpose:** defensible hackathon pitch and pilot design, not a sales forecast. Repository evidence is pinned to [`7dcb14b`](https://github.com/Parnuhakk/voicebot/tree/7dcb14b299c67d42e94a303db2dfeb52e86b7949); later integration work is outside this assessment. See the [short pitch brief](restaurant-voicebot-pitch-brief-2026-10-04.md).

## 1. Executive findings

1. **A real, bounded local market:** Estonia had **2,228 restaurant and mobile-food-service enterprises in 2024**, with **€905.74 million annual turnover** and **17,274 persons employed**. These are enterprises, not physical restaurant locations or a qualified customer list. 2024 is the latest detailed observation year available in the checked datasets. [S01], [S02]
2. **Phone demand matters, but foreign evidence is not local measurement:** Yelp and Slang report approximately **70% and 71% revenue-related call intent** in their own restaurant datasets. This includes orders, waitlists and catering, not just bookable tables; this demo does not support all those actions. [S12], [S13]
3. **Do not pitch a universal missed-call rate:** Revmo's 12,091-call vendor study reports **9.0% missed for full-service restaurants**, versus **40.1% for quick-service restaurants**. Estonia-specific representative call volume and missed-call rates remain unknown. [S11]
4. **The economics can work, but not for every venue:** the explicit base scenario below yields **€405/month incremental dining contribution**, less a hypothetical €149 fee = **€256/month** before other incremental customer costs. The low scenario loses €68/month on bookings alone. These are estimates, not achieved results.
5. **Eight additional seated parties cover the assumed fee:** at 2.5 diners × €25 net spend × 30% contribution, one incremental seated party contributes €18.75. Eight parties contribute €150. A moved booking, an empty reservation or a displaced walk-in is not additional business.
6. **Keep a human option:** only **28% of surveyed UK consumers were comfortable booking or changing reservations with AI over the telephone**, despite 73% being comfortable with AI somewhere in the booking experience. Foreign survey questions are not interchangeable. [S15]
7. **Pitch a prototype, not existing customer traction:** inspected code supports a fictional ET/EN/RU restaurant receptionist and guarded demo reservations. Real restaurant calendar integration, completed human transfer and carrier-call acceptance are not established at this snapshot.

### Evidence labels used throughout

| Label | Meaning | Appropriate pitch use |
| --- | --- | --- |
| Official Estonia fact | Primary statistical/tax source, with year and unit | State the exact scope and period |
| Foreign vendor benchmark | Vendor-selected calls or named customer case | Attribute vendor and geography; no local extrapolation as fact |
| Consumer survey | Stated preference in a sampled population | Say “survey respondents,” not observed customer behavior |
| Assumption / derived estimate | Input chosen for a model, or arithmetic from stated inputs | Display assumptions; validate during pilot |
| Repository evidence | Inspectable implementation/test material | Demonstrated scope, not commercial adoption or universal accuracy |

## 2. Estonia market: what exactly can we count?

### Latest detailed official observations

| Estonia, 2024 | Enterprises | Annual turnover, € million | Persons employed, annual average | Employees, annual average |
| --- | ---: | ---: | ---: | ---: |
| Restaurants and mobile food service: NACE Rev. 2 **56.10** | **2,228** | **905.74** | **17,274** | **16,872** |
| All food and beverage service: NACE Rev. 2 **56** | **3,198** | **1,046.32** | **20,240** | **19,449** |

Sources: Statistics Estonia EM001 and Eurostat `sbs_ovw_act`. All eight observations agree after converting/rounding turnover units. These are two dissemination routes for the **same underlying national SBS statistics**, not two independent surveys. [S01], [S02]

**Unit and coverage warnings:**

- An enterprise may operate at several locations. The regional dataset reports **4,873 local units for the broader NACE 56 division**, not 4,873 restaurants. Regional activity detail is two digits; an authoritative current count of physical restaurant outlets specifically within 56.10 was not established. [S03], [S21]
- 56.10 includes restaurants, cafeterias, fast food, takeout, mobile food carts and some market-stall food preparation. Group 56.1 contains the single class 56.10, explaining national `I561` versus Eurostat `I5610`. Many counted enterprises do not take table reservations. [S05]
- SBS excludes sole proprietors in Estonia for 2021–2024 and excludes foreign branches with 19 or fewer persons employed. Restaurant activity inside an enterprise principally classified elsewhere is not necessarily counted here. This is not a census of every legal registration or dining venue. [S04], [S05]
- Turnover excludes VAT, excise and subsidies. Employment is an annual-average headcount, including part-time work and working proprietors; it is not FTE staffing. Turnover is neither profit nor phone-generated sales. [S06]
- Eurostat's restaurant enterprise counts were **2,113 / 2,168 / 2,229 / 2,228** in 2021 / 2022 / 2023 / 2024. The latest count is essentially flat, not evidence of a rapidly growing enterprise population. The 2021 methodology change makes earlier comparisons less straightforward. [S01], [S02]

The derived sector **mean** is approximately €407,000 annual turnover per enterprise, not a typical restaurant's sales. Multi-site groups and a skewed size distribution can make that mean unsuitable for individual pricing decisions.

### Local operating context

- The 2025 average gross monthly wage in **accommodation and food service together** was **€1,333**. This is not a restaurant host's measured wage. Using 2026 employer contributions of 33% social tax plus 0.8% unemployment insurance gives a payroll-only hourly proxy of **€10.29**, with an assumed 40-hour week. [S07], [S08]
- Estonian accommodation establishments recorded **3,693,465 accommodated tourist arrivals in 2025**, including **1,949,843 foreign-resident arrivals**. These are neither unique people nor restaurant patrons/calls. They provide tourism context, not a demand multiplier. [S09]
- In the 2021 census, **67% had Estonian and 29% Russian as their mother tongue**; 84% spoke or understood Estonian. This supports a localization rationale, not a current restaurant-call language split. English support is a reasonable tourism/pilot hypothesis, not proof that ET/EN/RU covers every customer. [S10]

### Subscription opportunity: ceilings versus a qualified market

Assume **€149/month excluding VAT**, one paid account per enterprise and 12 paid months. This price is hypothetical, not validated willingness to pay or an announced tariff.

| Model layer | Assumed paying accounts | Annual recurring revenue at €149/month | Interpretation |
| --- | ---: | ---: | --- |
| Mechanical sector ceiling | 2,228 | **€3,983,664** | All counted restaurant/mobile-food enterprises buy one account; unrealistic ceiling, not validated TAM |
| Low-fit serviceable scenario | 334 | **€597,192** | Floor of 15% × 2,228; reservation/phone/integration fit assumed |
| Base-fit serviceable scenario | 668 | **€1,194,384** | Floor of 30% × 2,228; fit not measured |
| High-fit serviceable scenario | 1,114 | **€1,991,832** | 50% × 2,228; fit not measured |
| Initial commercial scenario | 25 | **€44,700** | Assumed retained paying accounts, not a dated forecast |
| Small rollout scenario | 50 | **€89,400** | Same assumptions |
| Larger local rollout scenario | 100 | **€178,800** | Same assumptions |

Do not label €906 million restaurant turnover as software TAM. A real serviceable market must count **deduplicated qualified accounts/sites**, including group buying, phone volume, reservations, spare capacity, supported calendars and willingness to pay. Multi-site pricing, discounts, churn, support, tax and usage costs are omitted from this mechanical model. The broader 3,198-enterprise category is useful sector context, not an extra pool of proven reservation customers.

**Recommended first segment:** independent, reservation-taking, full-service venues with demonstrable peak-time or after-hours unanswered calls, an owner-approved menu/policy set and a calendar that can be safely connected. Tallinn, Pärnu and Tartu are sensible discovery locations, not a proven regional sales allocation. Deprioritize no-reservation counters, low-volume phones, already fully booked venues and operators requiring food ordering as the main use case.

## 3. What the restaurant-phone evidence really says

| Finding | Evidence and denominator | What it supports | What it does not support |
| --- | --- | --- | --- |
| 70% / 71% revenue-related intent | Yelp / Slang platform-selected restaurant calls; exact mix periods/subsamples incompletely disclosed | Separate first-party vendor reports agree that phones include commercially meaningful requests; statistical independence of samples is not established | 70% table-booking conversion, 70% incremental revenue, or an Estonian call mix [S12], [S13] |
| 20% pre-visit research | Yelp Host calls: menu, dining format, dietary accommodations and logistics | Approved FAQ coverage is a relevant product surface | Automatic resolution of all dietary/accessibility questions; overlapping categories should not be added to 100% [S12] |
| 9.0% full-service versus 40.1% QSR missed | Revmo, 12,091 calls across restaurant segments | Segment-specific variation; motivates measuring the actual venue | A countrywide average or the pitch claim “restaurants miss 43% of calls” [S11] |
| 69% say they might give up if unanswered | Harris/Hostie, online survey of 2,065 US adults | Unanswered phones can affect stated choice | Observed churn, realized lost sales or an actual 69% miss rate [S14], [S22] |
| 28% comfortable with AI booking by phone | SevenRooms, 1,000 UK consumers | Resistance is material; offer a human route and measure acceptance | Pooling this with broader AI comfort or US differently worded surveys [S15] |
| 24,000 conversations, 403 reported staff hours, 4,700 reservations in six months | Hostie's Stinking Rose **group**, vendor case | A named deployment can handle substantial call work | 4,000 calls/month at one restaurant, causal uplift or our traction [S16] |
| 84% without transfer; phone bookings +42%, total reservations +11% | Hostie's Harborview case | Feasibility of integrated restaurant phone service | An industry-wide resolution rate or incremental uplift without a control [S17] |
| More than one million platform calls | Yelp, October 2025–June 2026 | The category has real deployments | Our adoption, Estonia availability, error-free operation or per-venue volume [S18] |

**Critical conflicts and exclusions:**

- Slang's release says 66% of calls occur in business hours, but also says only 26% occur simultaneously or after hours. Those denominators/definitions cannot be reconciled publicly; neither after-hours percentage is used in the model. [S13]
- Revmo's original PDF confirms the segment table, but its examples of 25/30/40/50 calls per day are not a disclosed measured Estonian or industry-wide average. Its advertised monetary losses involve unclear conversion assumptions and inconsistent examples; they are not imported. [S11]
- A local-language vendor article claims 35% of Estonian bookings occur by phone and one in four peak calls is missed, without a disclosed study/sample. These are **not accepted as measured Estonia statistics**. Direct bookings are not “100% profit.” [S23]
- Harris's pollster write-up and Hostie's article report the same commissioned survey, not independent replication. Vendor cases may omit difficult venues and failures. [S14], [S22]

**Research gap:** no representative Estonia-specific inbound-call average, missed-call rate, phone-booking share or causal recovered-booking rate was established. The scenarios below are deliberate testable assumptions, not a disguised extrapolation of foreign statistics.

## 4. Transparent per-restaurant monthly economics

### Inputs: all hypothetical except the wage/tax proxy

Use 30 calendar days for the daily equivalent; actual trading days and seasonal peaks vary.

| Input | Low volume | Base | High volume | Definition |
| --- | ---: | ---: | ---: | --- |
| Inbound calls/month, C | 300 | 750 | 1,500 | 10 / 25 / 50 per calendar day; not a local measured average |
| Baseline missed share, m | 10% | 20% | 30% | Assumptions; 20% is not presented as an Estonia fact |
| Missed calls eligible for table booking, b | 40% | 40% | 40% | Excludes orders, waitlists, catering and unrelated calls |
| Eligible missed attempts completing usable bot bookings, q | 60% | 60% | 60% | Includes connection, speech, customer acceptance and availability failures |
| Completed bookings becoming net additional seated parties, i | 60% | 60% | 60% | Combined adjustment for duplicates, cancellations/no-shows, other-channel migration and displacement |
| Diners per additional seated party, d | 2.5 | 2.5 | 2.5 | Expected average, not an integer party promise |
| Net spend per diner, s | €25 | €25 | €25 | Excluding VAT; at 24% VAT, equivalent receipt spend is €31 |
| Incremental contribution margin, g | 30% | 30% | 30% | Net revenue less incremental food, labor and other variable serving costs; not net profit |
| Routine share of previously answered calls, a | 70% | 70% | 70% | Separate assumption, **not** Yelp's 70% revenue-related-intent metric |
| Net staff minutes avoided per routine call, t | 2 | 2 | 2 | After any review/follow-up; must be time-studied |
| Hypothetical all-in monthly fee, F | €149 | €149 | €149 | Excluding VAT; includes assumed service usage, but commercial feasibility is unvalidated |

### Formulas

```text
Baseline missed calls M = C × m
Usable bookings from missed calls U = M × b × q
Net additional seated parties P = U × i
Incremental net dining revenue R = P × d × s
Incremental dining contribution K = R × g
Booking-only customer benefit after assumed fee = K − F
Redeployed staff hours H = C × (1 − m) × a × t ÷ 60
Payroll-only hourly proxy w = €1,333 × (1 + 0.33 + 0.008) ÷ (40 × 52 ÷ 12)
Redeployed-time value = H × w
```

Labor counts only **previously answered** calls, so handling an otherwise missed call is not simultaneously credited as saved staff time. Count saved minutes net of supervision/rework. Contribution already includes incremental serving labor. Never credit the same labor reduction twice.

### Derived monthly results

| Result | Low volume | Base | High volume |
| --- | ---: | ---: | ---: |
| Baseline missed calls | 30 | 150 | 450 |
| Usable bookings from missed calls | 7.2 | 36 | 108 |
| **Net additional seated parties** | **4.32** | **21.6** | **64.8** |
| Additional diners | 10.8 | 54 | 162 |
| Incremental net dining revenue | €270 | €1,350 | €4,050 |
| **Incremental dining contribution** | **€81** | **€405** | **€1,215** |
| Less assumed €149 fee: booking-only benefit | **−€68** | **€256** | **€1,066** |
| Booking-only benefit ÷ fee | −45.6% | 171.8% | 715.4% |
| Redeployed staff hours | 6.3 | 14 | 24.5 |
| Payroll-only value of redeployed time | €64.83 | €144.06 | €252.10 |

Fractional bookings are expected values, not literal observed customers. The fee comparison omits onboarding, staff training and any extra customer integration costs. The “benefit ÷ fee” ratio is a limited scenario calculation, not a promised investment return. **Redeployed time is a capacity benefit; it becomes cash savings only if paid labor/overtime or hiring actually changes.** It is not automatically added to the booking-only cash benefit.

### Break-even and disconfirming sensitivities

- One additional seated party contributes 2.5 × €25 × 30% = **€18.75**. €149 ÷ €18.75 = 7.947, so **eight genuinely additional seated parties/month** cover the fee alone.
- Under the assumed 40% × 60% × 60% funnel, each baseline missed call produces €2.70 expected contribution. **At least 56 missed calls/month** cover €149 in expectation. At a 20% missed share this corresponds to **276 inbound calls/month**, rounded up from the continuous threshold; this does not guarantee eight observed seated parties.
- **Base case, only 20% net incrementality:** contribution falls from €405 to **€135**, making booking-only benefit **−€14**.
- **Base case, only 10% contribution margin:** likewise **€135 contribution / −€14 after fee**.
- **Base case, zero net incrementality:** €0 additional revenue, **−€149 after fee**. A full restaurant may simply move existing demand between channels.
- **Base case, €25 spend including 24% VAT instead of excluding it:** contribution becomes **€326.61**, not €405; after fee, **€177.61**. Keep the tax basis consistent.
- **Base case, only one net minute saved per routine call:** seven redeployed hours, payroll-only value **€72.03**, not €144.06. Stinking Rose's own reported group totals imply about **1.01 staff minutes per conversation**, a useful warning against assuming long calls everywhere. [S16]
- Labor-only fee coverage needs approximately **14.48 hours/month** at the proxy wage, but avoided minutes alone do not establish a payroll reduction.

## 5. Pricing and provider unit economics

As accessed on 4 October 2026, Yelp lists Host Basic at **US$249/month**, subject to usage limits/extra charges, and Plus at **US$399/month** with unlimited usage. Its older US$149 comparisons should not be reused. This is a foreign competitor price anchor, not a euro conversion, like-for-like service comparison or Estonia availability claim. Slang's fetched pricing page contained duplicated/term-dependent Core 399/379 and Premium 599/539 blocks; no single comparable entry tariff is asserted. [S19], [S20]

**The proposed €149 is a pricing experiment.** Do not promise unlimited sustainable service until paid provider invoices, carrier costs, support time and call duration have been measured.

Illustrative provider-side base usage: 750 calls × **2.5 billable minutes/call** = 1,875 minutes. Assume **€20/month** allocated hosting/support and a combined variable minute cost for media, telephone, recognition, generation and synthesis. All of these cost inputs are assumptions, not actual provider quotes.

| Assumed combined variable cost/minute | Variable cost/month | Total with €20 allocation | €149 less modeled direct costs | Modeled direct contribution as % of fee |
| --- | ---: | ---: | ---: | ---: |
| €0.02 | €37.50 | €57.50 | €91.50 | 61.4% |
| €0.05 | €93.75 | €113.75 | €35.25 | 23.7% |
| €0.10 | €187.50 | €207.50 | −€58.50 | −39.3% |

At 1,500 calls and €0.05/minute, the same duration/allocation also costs €207.50 and loses €58.50 against €149. These figures omit acquisition, engineering, setup, tax and unallocated overhead; they are not company net margins. Commercial testing should consider a clear included-minute allowance and overage or a higher-volume tier, without assuming a tariff has already been implemented.

## 6. What our inspected prototype can honestly demonstrate

| Capability / metric | Repository evidence at the pinned snapshot | Pitch boundary |
| --- | --- | --- |
| Restaurant reception, ET/EN/RU, approved facts | `README.md:3–29`; `docs/operations/restaurants.md:5–20` | Prototype scope; unsupported/allergy-safety facts require staff verification |
| Durable fictional table reservation and owned cancellation | `docs/operations/restaurants.md:37–53,155–168` | Local SQLite reservations, not a verified real restaurant calendar |
| Explicit consent after complete recap; guarded capacity | `README.md:3–6`; `docs/operations/restaurants.md:43–53,98–103` | Demonstrable design/control, not proof of zero real-world failures |
| Call/session metadata and error counters | `app/call_history.py:49–76,142–168,350–391` | Counts inputs/errors; `recognized_turns` is **not** recognition accuracy |
| Receipt-linked summary | `app/call_history.py:171–215,243–265,430–456` | Accepted receipt kinds are legacy `slot`/`stay`; do not assume all restaurant receipts are represented. `with_booking` is receipt presence, not net active/seated bookings; cancellation can still leave a receipt |
| Speech timing instrumentation | `app/worker.py:454–500` | Up to 60 samples per stage per call; log p50/p95, not persisted fleet-wide SLOs or carrier answer rate |
| Telephone status | `app/server.py:384–400` | Explicit `public_ingress_verified=False`, `carrier_call_verified=False`, `synthetic_private_pilot`; release synchronization does not prove a real carrier call |
| Legacy dashboard metrics | `app/dashboard/demo.py:83–89`; `app/dashboard/api.py:235–237` | Seeded “100%” fidelity and “1 / 3 demo calls” are not measurements or traction |
| Existing question research | `docs/research/restaurant-customer-questions/README.md:3,63–75,91–107` | 270 concepts / 810 multilingual question-answer pairs / 17 categories; authored text coverage, not 810 customer calls or a speech accuracy rate |
| Narrow speech comparison | `docs/evidence/2026-10-04-final-estonian-speech.md:37–51,67–70` | MAI 11/13 versus Turbo 8/13 authored cases; small synthetic/provider test, not production accuracy, human naturalness or end-to-end latency |

**Not established:** paying customers, measured recovered revenue, representative completion/accuracy, real calendar interoperability, food ordering, payments, waitlists, callbacks, kitchen notification or completed live human transfer. Do not present suggested future actions as delivered capabilities. The older spa hackathon playbook and seeded hotel dashboard do not define current restaurant scope.

## 7. Pilot: replace assumptions with measurements

### Design and readiness gates

**Suggested research pilot, not executed:** recruit 5–10 reservation-taking restaurants; measure at least **14 days of baseline carrier traffic** and **28 days of monitored service**, covering weekdays, weekends and meal peaks. Record opening/trading days and seasonal/events context. A longer or matched control design is needed for stronger causal conclusions.

Before real guest traffic: approve venue facts, connect and reconcile the real calendar, verify carrier calls in ET/EN/RU, exercise failure/consent/cancellation paths and implement an actually monitored human fallback. The current prototype cannot itself complete that transfer. If these gates are unmet, remain in operator-controlled fictional demonstrations. Privacy/retention and AI disclosure need an owner-approved review; do not assume current synthetic-session metadata alone is a production analytics/compliance implementation.

For attribution, use a crossover or matched untreated peak-window/venue comparison where safe. Normalize rates to comparable trading hours/days and control for occupancy, promotion, seasonality and opening hours; do not intentionally leave urgent calls unanswered. Compare **total seated business**, not just the number of phone bookings. Uncontrolled before/after changes are descriptive, not proof of recovered business. Do not run outreach, collect caller data or alter routing solely because this research plan exists.

### KPI definitions and collection gaps

| KPI | Definition / denominator | How to establish it |
| --- | --- | --- |
| Offered inbound calls | All eligible carrier attempts, including busy, failed and abandoned-before-answer calls; disclose exclusions | Carrier records; bot session starts alone omit missed traffic |
| Baseline missed-call share | Eligible attempts not answered before caller abandonment/failure or the pre-agreed ring timeout ÷ eligible offered attempts | Same carrier definition and hours before/after; segment peak/off-peak/closed hours |
| Timely answer rate | Eligible attempts receiving a meaningful live response within the agreed answer budget ÷ eligible attempts | Carrier plus audio timing; connection alone is not a useful greeting |
| Call intent / language | Booking, cancellation/change, approved FAQ, order, group/event, complaint, other; ET/EN/RU/unsupported | Audit de-identified labels; report unknowns and multi-intent calls separately |
| Booking completion | Valid committed calendar bookings ÷ eligible booking attempts, deduplicated by attempt | Real calendar receipt/ownership checks; include failed/abandoned attempts |
| Booking correctness | Audited bookings correct in **every** required field (date, local time, party count and ownership) ÷ audited bookings | Compare to independently checked request and authoritative calendar; report field-level accuracy separately, not as booking correctness |
| Safe mutation failures | Writes without consent, unauthorized cancellation, duplicate/overbooked or falsely claimed writes | Audit all incidents; zero observed incidents is not proof of a zero population rate |
| Autonomous resolution | Audited eligible calls correctly completed without staff work ÷ audited eligible calls; apply sampling weights if stratified | Audit exhaustively or use a representative sample with coverage, weights and uncertainty disclosed. Count silent failures, abandonments, later corrections and follow-up labor as failures/work, not success |
| Human assistance | Requested, attempted and **completed** transfers/callbacks separately | Actual human acceptance; saying “contact staff” is not a completed handoff |
| End-to-end response latency | End of caller speech → first audible meaningful reply, p50/p95 and sample size | Include endpointing, recognition, model/tool time, routing and playback; provider first-byte timing is insufficient |
| Redeployed staff hours | Counterfactual human call minutes avoided minus monitoring/rework/follow-up | Time study or matched observation; payroll savings reported separately |
| Net additional seated parties | Additional seated parties versus the counterfactual, net of no-shows, duplicates, channel substitution and displacement | Calendar plus seated/POS reconciliation and a control/comparison; a receipt is not incremental attendance |
| Net customer benefit | Incremental net sales less variable serving costs, service fee and other incremental customer costs | Actual net-of-VAT spending and contribution assumptions; no double counting of labor |
| Provider direct margin | Net service fee minus actual billed media/provider/carrier usage and support/hosting allocation | Invoices and support time; never assume free-tier economics scale |
| Customer acceptance / willingness to pay | AI opt-out, complaints, staff satisfaction, retained paid pilots and accepted price | Ask neutrally; free trials or stated interest are not recurring revenue |

**Proposed targets to agree before the pilot, not current results:** ≥95% timely answers within 10 seconds, ≥60% eligible booking completion, ≥98% of audited bookings correct in every required field, and response latency p50 <1.5 seconds / p95 <3 seconds. Report every safety incident and halt affected writes until resolved. Require a real positive booking-only benefit or separately demonstrated cash labor savings before claiming customer ROI; seek at least three paying retained pilots before claiming validated pricing. These are operational hypotheses, not sourced industry norms.

Report raw denominators and uncertainty by venue/channel/language. Do not combine synthetic/typed/browser tests with real carrier calls. Small samples cannot support sweeping precision: with **zero errors in 300 independent audited cases**, the approximate one-sided 95% upper error bound is **1%** (`3/n` rule), not zero. Correlated calls or a biased audit sample make that shortcut inappropriate. Sparse language subgroups should be marked insufficient rather than given an impressive p95 or accuracy headline.

## 8. Pitch choices: use / qualify / reject

| Use | Qualify explicitly | Reject |
| --- | --- | --- |
| “2,228 restaurant and mobile-food-service enterprises, Estonia, 2024” | Enterprise scope, coverage exclusions, not outlets | “Estonia has 2,228 restaurant locations” |
| “Phones contain commercially meaningful requests” | Foreign Yelp/Slang vendor datasets | “70% of calls become reservations” |
| “Missed calls are a pilot opportunity” | Measure each restaurant; foreign FSR benchmark is 9% | “Estonian restaurants miss 43% of calls” |
| “Our base scenario needs eight additional seated parties to cover €149” | Spend, contribution, incrementality and price assumptions | “Guaranteed €1,350 recovered monthly revenue” |
| “Staff can focus on guests” | Redeployed time, not necessarily lower payroll | “We save a full receptionist salary” |
| “ET/EN/RU prototype with controlled demo booking” | Fictional data and unverified production integrations | “Production-ready autonomous bookings in every restaurant” |
| “270 concepts and 810 multilingual Q&A pairs” | Authored research catalogue | “810 real customer calls, 100% accurate” |
| “Local subscription ceiling ~€4m/year at €149” | Mechanical all-enterprise ceiling; fit/adoption unknown | “€906m voicebot software TAM” |

## 9. Method and reproducibility

The work used four rounds: ten-angle discovery; original-source retrieval and contradiction checks; wage/pricing/local context and scenario calculation; official enterprise/local-unit reconciliation. Native runs `32313f4d-2115-4315-953f-aa72356e4283` and the official-market lane's `cb4b5deb-def0-4b68-826c-48a8710be39a` retained searchable evidence. The first run ranked 60 unique URLs and extracted 16 documents, with ten extraction failures; weak official-market coverage was closed with targeted searches and original APIs. GitHub/Google discovery routes were circuit-broken, and two initial researcher routes exceeded provider quota; alternate research and direct primary-source checks continued. No provider configuration changed.

All cited material was accessed on **4 October 2026**. Vendor articles are evidence of their own claims, not peer-reviewed causal estimates. The two original report PDFs were extracted after increasing a bounded public-file transport cap; no login, paywall or form gate was bypassed. No raw customer calls, personal contacts or live booking databases were inspected, and no application behavior was changed.

### Reproduce the official market query

Read-only POST to `https://andmed.stat.ee/api/v1/en/stat/EM001`:

```json
{
  "query": [
    {"code": "Näitaja", "selection": {"filter": "item", "values": ["V11110", "V16110", "V16130", "V12110"]}},
    {"code": "Tegevusala", "selection": {"filter": "item", "values": ["I561", "I56"]}},
    {"code": "Tööga hõivatud isikute arv", "selection": {"filter": "item", "values": ["TOTAL"]}},
    {"code": "Vaatlusperiood", "selection": {"filter": "item", "values": ["2024"]}}
  ],
  "response": {"format": "json-stat2"}
}
```

Expected EM001 turnover: `I561 = 905738.9` and `I56 = 1046323.8`, **thousand euros**. Its JSON-stat `updated` field returned an unusable `9999-12-31T21:59:59Z`; use the displayed table update, not that placeholder. Eurostat filters: annual / `EE` / `I5610,I56` / `2024` / `ENT_NR,EMP_NR,SAL_NR,NETTUR_MEUR`; links below preserve those exact queries. Local-unit filters use `EE00`, `I56`, `LOC_NR,EMP_LOC_NR`. No selected Eurostat observations carried flags.

## Source ledger

Confidence describes the claim **within its stated definition**, not generalizability to Estonia customers. Quoted passages are short excerpts; publication dates and observation dates are deliberately separate. Single-source official facts are labeled as such; repeated publisher coverage is not treated as independent corroboration.

### S01 — Statistics Estonia EM001: official national financial statistics

- **Date/scope:** displayed update 2 February 2026; observation 2024; Estonia, economically active enterprises; confidence **high within coverage**.
- **Evidence:** API labels “Number of enterprises,” “Average annual number of persons employed,” and “Turnover, thousand euros.” `I561`: 2,228 / 17,274 / 16,872 / 905,738.9 thousand euros; `I56`: 3,198 / 20,240 / 19,449 / 1,046,323.8 thousand euros. Footnote: “From the reference year 2021, the final frame of economically active units is used.”
- **Limit:** enterprise counts, not outlets; methodology break and excluded legal forms. Same underlying statistics as S02. [Table][S01]; [read-only API](https://andmed.stat.ee/api/v1/en/stat/EM001).

### S02 — Eurostat `sbs_ovw_act`: official detailed enterprise statistics

- **Date/scope:** API updated 30 September 2026, 11:00 +0200; observations 2021–2024; annual Estonia; confidence **high**.
- **Evidence:** `I5610` labeled “Restaurants and mobile food service activities”; 2024 enterprise / employed / employee / net-turnover observations 2,228 / 17,274 / 16,872 / €905.74m. The exact 2024 multi-indicator query is preserved in [S02]. A separate same-dataset `ENT_NR` query without a year filter returned the four annual counts shown above.
- **Limit:** a dissemination consistency check, not an independent sample or 2026 observation.

### S03 — Eurostat `sbs_r_nuts2021`: official local-unit statistics

- **Date/scope:** API updated 30 September 2026; 2024 / Estonia NUTS 2 `EE00` / broader `I56`; confidence **high within definition**.
- **Evidence:** “Local units - number” = **4,873**; “Persons employed in local units - number” = **20,582**. Exact query: [S03].
- **Limit:** broader food/beverage locations, including catering/beverage service; not restaurant-specific public-facing venues. Do not mix regional employment with enterprise employment.

### S04 — Eurostat Estonia-specific SBS methodology

- **Date/scope:** metadata updated 27 August 2026, reference period 2024; confidence **high**. [S04]
- **Passages:** “Sole proprietors are not included”; “FIEs are included in BD statistics, [but] they are excluded from SBS for the reference years 2021–2024”; foreign branches with “19 or fewer persons employed are excluded.” The 2024 data “were published on 30 of December 2025.”
- **Limit:** use the newer explicit SBS coverage to resolve confusing sole-proprietor wording elsewhere; do not equate SBS with business-demography registrations.

### S05 — Official NACE Rev. 2 explanatory manual

- **Date/scope:** published 2008; classification used by the selected observation; confidence **high for definitions**, not current market counts. [S05]
- **Passages:** printed p.77 / PDF p.79 places sole class 56.10 under 56.1; printed p.245 / PDF p.247 includes “restaurants,” “cafeterias,” “fast-food restaurants,” “take-out eating places,” “mobile food carts” and food preparation in market stalls. Printed p.22 / PDF p.24 defines principal activity by the greatest contribution to value added.
- **Limit:** confirms broad category membership; does not establish reservation suitability or count outlets.

### S06 — Statistics Estonia enterprise-finance definitions

- **Date/scope:** metadata updated 30 August 2025; confidence **high for units**. [S06]
- **Passages:** turnover “does not include VAT and excises”; “Turnover excludes subsidies.” Persons employed are counted “irrespective of the length of their working week” and “measured as an annual average.”
- **Limit:** not profit, FTE staffing or phone sales; newer S04 resolves sole-proprietor coverage ambiguity.

### S07 — Statistics Estonia wages

- **Date/scope:** published 5 March 2026; 2025 accommodation **and** food service; single-source official wage, confidence **high within sector**. [S07]
- **Passage:** lowest average gross wages were in “accommodation and food service activities (1,333 euros).”
- **Limit:** using this for a restaurant receptionist is only a proxy; working hours and other costs are model assumptions.

### S08 — Estonian Tax and Customs Board rates

- **Date/scope:** updated 26 March 2026; effective 2026; confidence **high**. [S08]
- **Passages:** social tax “33 per cent”; unemployment insurance “0.8% for the employer”; standard VAT “24%.” [Invest in Estonia](https://investinestonia.com/business-in-estonia/taxation/labour-taxes/) repeats employer rates, not a second wage study.
- **Limit:** €10.29/hour is derived using assumed 40 × 52 ÷ 12 hours; excludes benefits, coverage, recruitment and other overhead.

### S09 — Statistics Estonia accommodation tourism / TU112

- **Date/scope:** news published 10 February 2026; TU112 displayed update 10 August 2026; observation 2025; confidence **high within accommodation coverage**. [S09]
- **Passage:** establishments served “about 3.7 million tourists”; establishments with “5 or more bed places” are included. [TU112](https://andmed.stat.ee/en/stat/TU112) exact totals: 3,693,465 / 1,949,843 foreign / 1,743,622 domestic; 6,716,281 nights. Agent query used `Maakond=EE`, `Elukohariik=WORLD,EE,FOR`, `Vaatlusperiood=2024,2025`, `Näitaja=OCC_ARR,OCC_NI`.
- **Limit:** arrivals can include repeat visitors; not restaurant customers or demand attribution.

### S10 — Statistics Estonia census languages

- **Date/scope:** published 16 November 2022; observation 2021; survey generalizable to ages 3+; confidence **high for the historical census**. [S10]
- **Evidence:** Estonian mother tongue 67%, Russian 29%, Estonian spoken/understood 84%.
- **Limit:** not a 2026 restaurant-caller language distribution; no claimed ET/EN/RU percentage coverage.

### S11 — Revmo: State of Restaurant Calls 2026

- **Date/scope:** release 6 August 2026, Phoenix dateline; **12,091 actual restaurant call recordings**; US-oriented named brands, exact country frame/fieldwork/subgroup sizes not fully disclosed; confidence **medium as vendor descriptive evidence**. [S11]
- **Passage:** full-service “Answer rate: 91.0% (miss rate: 9.0%)”; QSR “Answer rate: 59.9% (miss rate: 40.1%)”; pizza 6.9% missed; fast casual 24.8% missed. [Original report landing page](https://revmo.ai/guides/state-of-calls-report) links [chapter PDF](https://usfjhsnxcejsjujlxihb.supabase.co/storage/v1/object/public/brand-assets/reports/state-of-calls-report-2026.pdf), p.3 table.
- **Limit:** subgroup methodology incomplete, fast-casual rounding inconsistency, modeled daily examples and unclear loss calculations; not representative Estonia evidence.

### S12 — Yelp: restaurant call intent

- **Date/scope:** published 1 October 2026; Yelp Host platform-selected calls; exact mix window/geography not fully disclosed; confidence **medium**. [S12]
- **Passages:** “70% of calls handled are revenue-driving: reservations, waitlist, and takeout orders”; “20% of all calls ... are pre-visit research.”
- **Limit:** intent is not conversion or incrementality; categories can overlap; many actions exceed current demo scope.

### S13 — Slang AI proprietary 2025 report announcement

- **Date/scope:** published 21 August 2025; “millions of calls” across US full-service customer base; exact sample/window not publicly supplied; confidence **medium**. [S13]
- **Passage:** approximately “71% ... tied to revenue, including reservations, orders, private dining, and catering inquiries.”
- **Limit:** platform bias, no Estonia mapping; business-hours/simultaneous-call percentages are unreconciled and excluded.

### S14 — Hostie / Harris Poll: unanswered-phone survey

- **Date/scope:** published 27 July 2025; fieldwork 29 May–2 June 2025; online **2,065 US adults aged 18+**; confidence **medium for stated preference**. [S14]
- **Evidence:** 63% prefer phone contact; 69% say likely to give up if unanswered; 20% say calls always/often ignored; 89% open to some restaurant AI task, but 47% open to AI making a reservation.
- **Limit:** not observed customer churn, actual missed-call share or a general AI-phone acceptance rate; commissioned survey, not independent of S22.

### S15 — SevenRooms UK restaurant trends 2025

- **Date/scope:** 2025 report; 1,000 UK consumers aged 16+, weighted online survey 27 December 2024–6 January 2025; 258 operators, 24 December 2024–15 January 2025; confidence **medium for the specified survey**. [S15]
- **Passages:** PDF p.39: **28%** comfortable AI booking/modifying “over the phone”; p.11: **73%** comfortable AI somewhere in booking. Methodology p.41.
- **Limit:** differently worded questions and foreign population; important disconfirming evidence, not a current Estonia estimate.

### S16 — Hostie: Stinking Rose Group case

- **Date/scope:** published 10 September 2025; first six months, restaurant **group**; confidence **medium-low, uncontrolled vendor case**. [S16]
- **Evidence:** 24,000 conversations, 403 staff hours, 4,700 reservations, 80% resolved without transfer.
- **Limit:** 4,000 conversations/month is a group-derived mean, not per venue; 403 × 60 ÷ 24,000 ≈ 1.01 reported staff minutes/conversation; no randomized counterfactual.

### S17 — Hostie: Harborview Restaurant & Bar case

- **Date/scope:** published 19 September 2025; San Francisco, onboarding November 2024; confidence **medium-low, uncontrolled vendor case**. [S17]
- **Evidence:** 84% of calls without transfer; phone bookings +42%; total reservations +11%.
- **Limit:** no raw counts/control; not industry-wide uplift, net seated revenue or our performance.

### S18 — Yelp Host adoption release

- **Date/scope:** published 28 July 2026; platform calls October 2025–June 2026; confidence **medium as first-party adoption evidence**. [S18]
- **Passage:** more than one million calls; more than 40,000 on Mother's Day weekend, platform-wide.
- **Limit:** not venue average, Estonia deployment, independent quality validation or our traction.

### S19 — Yelp current public pricing

- **Date/scope:** live page accessed 4 October 2026, no publication date asserted; confidence **high for displayed offer only**. [S19]
- **Evidence:** Host Basic US$249/month subject to limits/extra charges; Plus US$399/month unlimited usage.
- **Limit:** currency, scope, contract/usage conditions and geography differ; verify commercial terms before purchase; older US$149 summaries are superseded.

### S20 — Slang current pricing ambiguity

- **Date/scope:** live page accessed 4 October 2026, no publication date asserted; confidence **low for a single comparable tariff**. [S20]
- **Evidence:** fetched page contained Core 399/379 and Premium 599/539 blocks.
- **Limit:** duplication/billing-term ambiguity; intentionally not used as an exact price anchor.

### S21 — Eurostat general SBS statistical-unit definitions

- **Date/scope:** metadata updated 4 August 2026; confidence **high**. [S21]
- **Passages:** “the enterprise for the country-level business statistics data and the local unit for the regional business data”; “An enterprise carries out one or more activities at one or more locations”; regional detail at “division level (2-digits).”
- **Limit:** prevents outlet/enterprise confusion; does not provide a restaurant-location count itself.

### S22 — Harris Poll: pollster corroboration of the Hostie survey

- **Date/scope:** visible publication date not established in extraction; same 29 May–2 June 2025 fieldwork as S14; confidence **medium for the same survey**. [S22]
- **Evidence:** pollster write-up repeats the 69% stated abandonment finding.
- **Limit:** commissioned-survey confirmation, **not an independent second sample**; no observed sales outcome.

### S23 — Local-language vendor claim: excluded from factual estimates

- **Date/scope:** Voicefleet article dated 16 March 2026; claims concern Estonia but no disclosed sample/method; confidence **low / rejected as measured evidence**. [S23]
- **Evidence:** claims 35% phone bookings and one in four unanswered peak calls.
- **Limit:** unsupported country-specific percentages and loss/profit rhetoric; not used to fill the Estonia evidence gap.

[S01]: https://andmed.stat.ee/en/stat/EM001
[S02]: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sbs_ovw_act?lang=en&freq=A&geo=EE&nace_r2=I5610&nace_r2=I56&time=2024&indic_sbs=ENT_NR&indic_sbs=EMP_NR&indic_sbs=SAL_NR&indic_sbs=NETTUR_MEUR
[S03]: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sbs_r_nuts2021?lang=en&freq=A&geo=EE00&nace_r2=I56&time=2024&indic_sbs=LOC_NR&indic_sbs=EMP_LOC_NR
[S04]: https://ec.europa.eu/eurostat/cache/metadata/EN/sbs_essbs21_ee.htm
[S05]: https://ec.europa.eu/eurostat/documents/3859598/5902521/KS-RA-07-015-EN.PDF
[S06]: https://www.stat.ee/en/metadata/20300
[S07]: https://stat.ee/en/news/average-wages-increased-by-56-last-year
[S08]: https://www.emta.ee/en/business-client/taxes-and-payment/income-and-social-taxes/tax-rates
[S09]: https://stat.ee/en/news/number-accommodated-tourists-increased-little-2025
[S10]: https://stat.ee/en/news/population-census-76-estonias-population-speak-foreign-language
[S11]: https://revmo.ai/news/state-of-restaurant-calls
[S12]: https://business.yelp.com/resources/articles/restaurant-ai-receptionist?domain=restaurants
[S13]: https://www.slang.ai/press-releases/slang-ai-releases-landmark-proprietary-report-2025
[S14]: https://hostie.ai/blogs/missed-connection-over-two-thirds-of-americans-would-ditch-restaurants-that-dont-answer-the-phone
[S15]: https://go.sevenrooms.com/rs/519-YNM-008/images/2025-UK-Restaurant-Trends-SevenRooms.pdf
[S16]: https://hostie.ai/blogs/how-the-stinking-rose-group-is-managing-24-000-calls-through-their-virtual-hostess
[S17]: https://hostie.ai/blogs/how-harborview-restaurant-and-bar-automated-84-of-calls-with-a-virtual-concierge
[S18]: https://blog.yelp.com/news/yelp-host-voice-ai-adds-opentable-reservations-and-takeout-ordering-for-restaurants/
[S19]: https://business.yelp.com/restaurants/yelp-restaurants-pricing/#yelp-host
[S20]: https://www.slang.ai/pricing
[S21]: https://ec.europa.eu/eurostat/cache/metadata/en/sbs_esms.htm
[S22]: https://theharrispoll.com/articles/state-of-beverages-2025-trend-report-how-does-gen-z-shop-restaurants-are-losing-business-by-not-answering-the-phone-should-workers-adapt-to-company-culture/
[S23]: https://voicefleet.ai/ee/blog/kuidas-eesti-restoranid-kaotavad-broneeringuid-vastamata-konede-tottu
