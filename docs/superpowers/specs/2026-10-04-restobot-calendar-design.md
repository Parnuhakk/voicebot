# Restobot calendar integration and hostname migration

## Purpose

Integrate the user's authored Meretuule table-calendar experience into the existing restaurant Voicebot and move the canonical browser hostname to `restobot.arleserver.cfd`. Keep the current operator dashboard, bookings, chat/microphone, consent gates, stored records and telephone service.

## Selected approach

Import the supplied authored HTML/CSS/JavaScript as local same-origin calendar assets, expose it as a first-class dashboard page, and add a read-only live calendar mode using the existing restaurant store. Keep the original animation and client-only samples in an explicitly separate preview mode. Do not embed the temporary TryCloudflare origin or replace the existing operator dashboard.

User steering: the root must open with a beautiful landing page in the authored calendar's light teal style. Serve the preserved operator dashboard at `/dashboard` (and `/dashboard/`), while `/` and `/index.html` serve the new landing. Landing CTAs link to `/dashboard#demo-section`, `/dashboard#reservation-heading` or `/booking-calendar.html`; no private data or credentials enter the marketing page.

## Landing design

Audience: restaurant operators evaluating RestoBot. Use the supplied self-hosted Figtree typography and palette (`#f6f9f9` canvas, `#233e47` ink, `#217e80` teal, `#268b69` mint-green accents, `#e4ecec` dividers). Distinctive hero shows the restaurant reception-to-table journey rather than stock imagery or generic metric cards. A quiet product navigation and two clear demo/calendar actions lead into a short practical explanation, genuine supported-language information and an honest fictional-demo disclosure. No invented testimonials, prices, clients, contact details or carrier-verification claims. Mobile navigation, keyboard focus and reduced-motion support are mandatory. Existing dashboard styling stays intact.

Alternative approaches rejected: temporary-origin iframe (fragile and disconnected); replacing the five-table backend with the prototype's twelve-table model (unrequested data/contract migration).

## Evidence and boundaries

Base revision: `80ab7d16635b7bf511316f3e3ac90d05f35c3131`, canonical repository `Parnuhakk/voicebot`, `master`. Integration uses a clean worktree; the stale `/home/arle/voicebot` and concurrent Estonian-date work remain untouched. User explicitly requires GPT-6/GPT-6.1 via Codex and rejects Go/older models. Live lookup confirms `openai/gpt-6.1-sol#high`; both implementation lanes and independent review use that family.

The supplied preview has twelve tables/44 seats, whereas `data/demo/restaurant-demo.json` configures five tables/18 seats and maximum party six. Existing `RestaurantAdapter` owns reservations and unexpired holds in shared SQLite. Existing operator booking DTOs intentionally omit guest names. Calendar reads must be restaurant-scoped and include both confirmed reservations and unexpired holds, without leaking guest scopes or owned-hold identifiers.

## Calendar behavior

- Preserve the authored light teal floor plan, week/date/time controls, capacity tabs, timeline, dialogs, reduced motion and responsive layouts. Existing dark-sidebar dashboard remains unchanged except for a calendar navigation entry.
- Default to live operator mode using authoritative configured tables, capacities, dining duration, Tallinn timezone and opening-hours information. Before authorization, show unknown/private occupancy, not fictitious availability.
- A protected, no-store calendar read projects confirmed reservations and active holds for one validated date; exclude cancelled reservations and expired holds. Use existing operator authorization before query processing. No schema migration or new booking store.
- Keep credentials only in page memory; never URL parameters, browser storage or parent-window messages. Disconnect must cancel pending fetches and clear private state. Read failures must not display stale results as current availability.
- Calendar writes are not new backend mutations. Actual reservation creation continues through the existing dashboard preparation/recap/explicit-consent flow, reached through a visible link. No arbitrary guest names or selected-table overrides are added to that API.
- Preview mode keeps the authored twelve-table animation and fictional sample form, with prominent warnings that samples are not stored operator bookings. Switching modes must clear/stop preview timers and avoid mixing the two inventories.
- Reciprocal links connect calendar, saved bookings and actual voice demo. Same-origin versioned assets remove the temporary tunnel from runtime dependencies.

## Hostname migration

Use the existing Cloudflare application tunnel, Coolify web application and Traefik telephone routing. Publish restobot first, preserve old-host API/telephone/websocket compatibility, then redirect old browser HTML pages to restobot. Never redirect carrier POST callbacks or websocket upgrades across hostnames.

Reconcile canonical public URL defaults and deployed overrides, fixed carrier signature URLs and actual webhook configuration together. Existing old-host callbacks may remain compatible during migration; security must validate a finite explicit set of trusted URLs, not an arbitrary caller-supplied Host. Do not weaken signature checks or revive the retired Meretuule host.

## Error handling and preservation

Invalid dates return controlled client errors after authorization. Missing operator configuration fails closed. Calendar read failures clear private display, with a useful retry message. Unknown/stale occupancy does not count as available. Existing allocator remains the sole booking authority.

Deployment preserves the original shared `/data` volume and existing restaurant/call-record identities. Do not compare whole live tables for equality while legitimate traffic may append records. Do not restart unrelated services or modify another session's worktree.

## Verification and shipping

Write expected-failing route/calendar/domain regressions first. Verify authoritative five-table inventory, confirmed/cancelled reservations, active/expired holds, authorization, malformed query and no-store behavior. Exercise preview controls and live-mode failure/disconnect behavior in headless desktop/mobile browsers. Run existing repository checks and the entire test suite; review the diff independently once unless serious findings require another round.

Commit/push only intended files and deploy the shipped revision. Verify restobot HTTPS readiness, assets, private API rejection without authorization, old browser redirect, old callback compatibility, telephone image/source parity and preserved baseline row identities. Record only non-sensitive operational evidence.
