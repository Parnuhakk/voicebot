# One restaurant workspace

## Intent

Fix table/chair overlap and put the calendar inside the existing restaurant
operator dashboard. One page and one operator connection must cover the floor
plan, timeline, saved bookings, voice demo and restaurant information.

## Chosen approach

Embed the authored calendar markup natively as `#calendar-section` after the
existing voice/reservation workspace. Keep the mobile voice controls in their
current first-screen position. Scope calendar selectors and styles to its
component so they cannot change dashboard forms, layout or landmarks. Rename
the preview date field to avoid the existing saved-booking date ID.

Do not use an iframe: it would retain a second document and connection.
Do not rebuild the calendar or introduce a UI framework: reuse its existing
inventory projection, floor/timeline views and explicit isolated preview.

## Authentication and state

The dashboard remains the sole connection owner. The calendar requests data
through the existing authenticated API transport, without copying the operator
value into another form, DOM attribute, event payload, URL or browser storage.
A small component interface receives connected/disconnected and language
changes. Existing API generation cancellation and calendar request versions
must prevent old reads from restoring private data after logout/date changes.

Live mode stays read-only: five configured tables/eighteen seats, confirmed
reservations and unexpired holds. A stale, failed or disconnected read shows
unknown occupancy and clears private details/timeline blocks. Switching to
preview never disconnects the rest of the workspace; switching back performs
a fresh live read if connected. Fictional preview inventory and animation
never become authoritative occupancy or send backend writes.

## Layout

Size grid cells from the full table and chair footprint, not only the tabletop.
Use responsive minimum-width columns and content-sized rows; never compress
rows to a viewport-height budget. All table hit targets and their children must
fit their cells and stay disjoint at laptop/mobile widths. Keep the floor panel
usable in the narrower dashboard content area, without hiding overflow to mask
the defect. The dashboard palette and typography remain authoritative.

## Navigation and compatibility

Dashboard calendar navigation becomes a same-document anchor. Landing calendar
links go directly to `/dashboard#calendar-section`. GET/HEAD requests for the old
calendar page and slash aliases redirect to that section with query strings
preserved. Existing canonical-host redirects, retired-host behavior, APIs,
carrier handlers, stored data and booking consent flows remain unchanged.

## Verification

- Reproduce overlap with actual table/chair bounding boxes, then show RED/GREEN.
- One-page browser checks: unique IDs, one connection form, native component,
  shared login/logout, date and view controls, ET/EN/RU, preview isolation,
  read failures, expiry and logout-in-flight races.
- Browser layout checks at 320/390/540/800/1024/1280/1366/1440 px, including short
  laptop heights. No intersecting table footprints or document overflow.
- Existing restaurant voice/booking browser journeys and full repository suite.
- Independent review, intended-file/known-key checks, commit/push, CI and live
  read-only deployment acceptance. Preserve all persistent records.
