"""Headless unified-workspace calendar regression; local fixture only.

Run: python3 tests/restaurant_calendar_browser_check.py /path/to/project/python
"""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/playwright"


def contrast(page, selector):
    return page.locator(selector).first.evaluate(r"""node => {
      const luminance = color => {
        const values = color.match(/[\d.]+/g).slice(0,3).map(Number).map(v => {v /= 255; return v <= .04045 ? v / 12.92 : ((v+.055)/1.055)**2.4;});
        return values[0]*.2126 + values[1]*.7152 + values[2]*.0722;
      };
      let parent = node;
      while (getComputedStyle(parent).backgroundColor === 'rgba(0, 0, 0, 0)') parent = parent.parentElement;
      const text = luminance(getComputedStyle(node).color), background = luminance(getComputedStyle(parent).backgroundColor);
      return (Math.max(text,background)+.05)/(Math.min(text,background)+.05);
    }""")


def footprints(page):
    """Measure the actual footprint, including rotated/SVG chairs and hitboxes."""
    problems = page.locator("#calendar-section .tables").evaluate("""grid => {
      const rect = node => { const r = node.getBoundingClientRect(); return {left:r.left, right:r.right, top:r.top, bottom:r.bottom}; };
      const inside = (a,b) => a.left >= b.left-.5 && a.right <= b.right+.5 && a.top >= b.top-.5 && a.bottom <= b.bottom+.5;
      const intersects = (a,b) => a.left < b.right-.5 && b.left < a.right-.5 && a.top < b.bottom-.5 && b.top < a.bottom-.5;
      const failures = [], room = rect(grid), tables = [...grid.querySelectorAll('.table-button')].map(button => {
        const hit = rect(button), parts = [...button.querySelectorAll('.table-shape, .chair, .table-caption, svg')].map(rect);
        for (const part of parts) if (!inside(part,hit)) failures.push('child outside '+button.dataset.table);
        const caption = rect(button.querySelector('.table-caption'));
        for (const chair of button.querySelectorAll('.chair')) if (intersects(rect(chair),caption)) failures.push('chair/caption overlap '+button.dataset.table);
        if (!inside(hit,room)) failures.push('hitbox outside grid '+button.dataset.table);
        return {id:button.dataset.table, hit, footprint:{left:Math.min(...parts.map(r=>r.left)), right:Math.max(...parts.map(r=>r.right)), top:Math.min(...parts.map(r=>r.top)), bottom:Math.max(...parts.map(r=>r.bottom))}};
      });
      tables.forEach((a,i) => tables.slice(i+1).forEach(b => {
        if (intersects(a.hit,b.hit) || intersects(a.footprint,b.footprint)) failures.push('overlap '+a.id+'/'+b.id);
      }));
      return failures;
    }""")
    assert not problems, f"{page.viewport_size}: {problems}"
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (
        page.viewport_size
    )


def check(page, origin, day_offset):
    errors, external = [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.clock.install()

    def local_only(route):
        if not route.request.url.startswith(origin + "/"):
            external.append(route.request.url)
            route.abort()
        else:
            route.continue_()

    page.route("**/*", local_only)
    page.goto(origin + "/dashboard", wait_until="networkidle")
    assert page.locator("#calendar-section").count() == 1, (
        "Native calendar is missing from the shared workspace"
    )
    cal = lambda name: page.locator("#cal-" + name)
    assert page.locator('input[type="password"]').count() == 1
    assert page.locator("iframe").count() == 0
    assert page.evaluate(
        "(() => {const ids=[...document.querySelectorAll('[id]')].map(n=>n.id); return new Set(ids).size===ids.length;})()"
    )
    assert page.evaluate(
        "document.querySelector('.workspace').compareDocumentPosition(document.querySelector('#calendar-section')) & Node.DOCUMENT_POSITION_FOLLOWING"
    )
    page.locator('input[name="demo-language"][value="en"]').check()
    page.wait_for_function(
        "document.querySelector('#cal-table-summary').textContent === '5 tables · 18 seats'"
    )
    assert cal("calendar-mode").input_value() == "live"
    assert "unknown" in cal("availability-count").inner_text().lower()
    footprints(page)
    # Same-document navigation retains page identity and the single connection.
    page.evaluate("window.workspaceMarker = 'same-document'")
    page.locator('.navigation a[href="#calendar-section"]').click()
    assert page.url == origin + "/dashboard#calendar-section"
    assert page.evaluate("window.workspaceMarker") == "same-document"
    cal("real-booking").click()
    assert page.url.endswith("#reservation-heading")
    assert page.evaluate("document.activeElement.id") == "reservation-heading"
    page.locator("#operator-token").fill("restaurant-fixture-operator")
    page.locator("#connect").click()
    page.wait_for_function(
        "document.querySelector('#cal-calendar-status').textContent.includes('Updated')"
    )
    assert page.locator("#operator-token").input_value() == ""
    assert page.evaluate("localStorage.length + sessionStorage.length") == 0

    # Real hold, projected by the real read-only calendar API.
    tomorrow = page.evaluate(
        "days => new Date(Date.now() + days * 86400000).toLocaleDateString('en-CA', {timeZone:'Europe/Tallinn'})",
        day_offset,
    )
    headers = {"Authorization": "Bearer restaurant-fixture-operator"}
    session = page.request.post(
        origin + "/api/booking/session", data={"language": "en"}, headers=headers
    ).json()["session_id"]
    response = page.request.post(
        origin + "/api/restaurant/reservation/prepare",
        data={
            "session_id": session,
            "date": tomorrow,
            "start_time": "14:00",
            "party_size": 4,
        },
        headers=headers,
    )
    assert response.status == 200 and response.json()["ok"], response.text()
    cal("date-picker").fill(tomorrow)
    cal("date-picker").dispatch_event("change")
    page.wait_for_function(
        "document.querySelector('#cal-calendar-status').textContent.includes('Updated')"
    )
    cal("time-select").select_option("14:00")
    assert cal("tables").inner_text().count("Held") == 1
    cal("tables").locator(".table-button:not(.reserved)").first.hover()
    assert (
        contrast(page, "#calendar-section .table-button:hover > .table-caption") >= 4.5
    ), "Dashboard hover styles leaked into the calendar"
    for selector in (
        ".table-button.reserved > .table-caption",
        ".table-button:not(.reserved) > .table-caption",
        ".floor-header p",
        ".year",
        ".window-wall span",
        ".room-name",
        ".table-button.reserved .table-shape strong",
        ".day-button[aria-pressed='true'] span",
        ".table-button:not(.reserved) .table-shape strong",
    ):
        assert contrast(page, "#calendar-section " + selector) >= 4.5, selector
    footprints(page)
    cal("timeline-tab").click()
    assert page.locator("#calendar-section .timeline-block").count() == 1
    assert contrast(page, "#calendar-section .timeline-block") >= 4.5
    page.locator("#calendar-section .timeline-block").click()
    assert "Held" in cal("table-dialog-detail").inner_text()
    page.locator('[data-close="table-dialog"]').first.click()
    cal("floor-tab").click()
    # Dynamic and static copy use the dashboard language, not independent state.
    for language, status, capacity, heading in (
        ("et", "Hoitud", "Kõik lauad", "Saal"),
        ("ru", "Удерживается", "Все столики", "Обеденный зал"),
        ("en", "Held", "All tables", "The dining room"),
    ):
        page.locator(f'input[name="demo-language"][value="{language}"]').check()
        assert status in cal("tables").inner_text()
        assert capacity in cal("capacity-all").inner_text()
        assert cal("floor-heading").inner_text() == heading
        assert cal("date-heading").inner_text() == page.evaluate(
            "({date, language}) => new Date(date+'T12:00:00Z').toLocaleDateString({et:'et-EE',en:'en-GB',ru:'ru-RU'}[language], {timeZone:'UTC',day:'numeric',month:'long'})",
            {"date": tomorrow, "language": language},
        )
        cal("tables").locator(".reserved").click()
        assert status in cal("table-dialog-detail").inner_text()
        page.locator('[data-close="table-dialog"]').first.click()
        footprints(page)

    # Preview is local and never disconnects the dashboard or writes the backend.
    writes = []
    page.on(
        "request",
        lambda request: writes.append(request.url) if request.method != "GET" else None,
    )
    cal("calendar-mode").select_option("preview")
    assert page.locator("#connection-state").inner_text() == "Connected"
    assert page.locator("#demo-start").is_enabled()
    assert cal("tables").locator(".table-button").count() == 12
    assert "44 seats" in cal("table-summary").inner_text()
    assert "not stored" in cal("mode-notice").inner_text()
    footprints(page)
    for language, room, mode, guests in (
        ("et", "Saal", "Fiktiivne eelvaade", "Külalise nimi"),
        ("ru", "Обеденный зал", "Вымышленный пример", "Имя гостя"),
        ("en", "The dining room", "Fictional preview", "Guest name"),
    ):
        page.locator(f'input[name="demo-language"][value="{language}"]').check()
        assert cal("floor-heading").inner_text() == room
        assert cal("mode-badge").inner_text() == mode
        cal("new-booking").click()
        assert (
            cal("booking-form").locator('label[for="cal-booking-name"]').inner_text()
            == guests
        )
        page.locator('[data-close="booking-dialog"]').click()
        footprints(page)
    cal("capacity-all").focus()
    page.keyboard.press("ArrowRight")
    assert (
        page.locator(
            '#calendar-section [data-capacity][aria-selected="true"]'
        ).get_attribute("data-capacity")
        == "4"
    )
    cal("capacity-all").click()
    cal("new-booking").click()
    cal("booking-name").fill("Browser sample")
    cal("booking-form").locator('button[type="submit"]').click()
    assert cal("booking-dialog").is_hidden()
    assert "Demo booking added" in cal("toast").inner_text()
    cal("new-booking").click()
    cal("booking-party").select_option("8")
    cal("booking-form").locator('button[type="submit"]').click()
    cal("new-booking").click()
    cal("booking-form").locator('button[type="submit"]').click()
    assert "All tables for 8 people are reserved" in cal("booking-error").inner_text()
    page.locator('[data-close="booking-dialog"]').click()
    cal("replay").click()
    page.clock.fast_forward(6300)
    assert cal("voice-stage").get_attribute("data-stage") == "confirmed"
    footprints(page)
    OUT.mkdir(parents=True, exist_ok=True)
    page.locator("#calendar-section").screenshot(
        path=str(OUT / f"restaurant-calendar-preview-{page.viewport_size['width']}.png")
    )
    cal("calendar-mode").select_option("live")
    page.wait_for_function(
        "document.querySelector('#cal-calendar-status').textContent.includes('Updated')"
    )
    assert cal("tables").locator(".table-button").count() == 5
    assert page.locator("#connection-state").inner_text() == "Connected"
    assert writes == [], writes

    # Read errors, malformed hold expiry, expiry, and pagehide clear all private UI.
    cal("date-picker").fill(tomorrow)
    cal("date-picker").dispatch_event("change")
    page.wait_for_function(
        "document.querySelector('#cal-calendar-status').textContent.includes('Updated')"
    )
    cal("time-select").select_option("14:00")
    snapshot = page.request.get(
        origin + "/api/restaurant/calendar?date=" + tomorrow, headers=headers
    ).json()
    cal("tables").locator(".reserved").click()
    page.locator('[data-close="table-dialog"]').first.click()
    page.route(
        "**/api/restaurant/calendar?*",
        lambda route: route.fulfill(status=503, json={"detail": "fixture unavailable"}),
    )
    cal("refresh-calendar").click()
    page.wait_for_function(
        "document.querySelector('#cal-calendar-status').textContent.includes('unavailable')"
    )
    assert cal("tables").locator(".reserved").count() == 0
    assert page.locator("#calendar-section .timeline-block").count() == 0
    assert cal("table-dialog-detail").inner_text() == ""
    page.unroute("**/api/restaurant/calendar?*")
    early = json.loads(json.dumps(snapshot))
    early["items"][0]["expires_at"] = page.evaluate(
        "value => new Date(Date.parse(value)+1500).toISOString()", early["fetched_at"]
    )
    page.route("**/api/restaurant/calendar?*", lambda route: route.fulfill(json=early))
    cal("refresh-calendar").click()
    page.wait_for_function(
        "document.querySelector('#cal-calendar-status').textContent.includes('Updated')"
    )
    page.clock.fast_forward(2000)
    assert "expired" in cal("calendar-status").inner_text().lower()
    assert page.locator("#calendar-section .timeline-block").count() == 0
    page.unroute("**/api/restaurant/calendar?*")
    malformed = json.loads(json.dumps(snapshot))
    malformed["items"][0]["expires_at"] = "not-a-date"
    page.route(
        "**/api/restaurant/calendar?*", lambda route: route.fulfill(json=malformed)
    )
    cal("refresh-calendar").click()
    page.wait_for_function(
        "document.querySelector('#cal-calendar-status').textContent.includes('unavailable')"
    )
    assert "unknown" in cal("availability-count").inner_text().lower()
    page.unroute("**/api/restaurant/calendar?*")
    cal("refresh-calendar").click()
    page.wait_for_function(
        "document.querySelector('#cal-calendar-status').textContent.includes('Updated')"
    )
    page.clock.fast_forward(60001)
    assert "expired" in cal("calendar-status").inner_text().lower()
    assert page.locator("#calendar-section .timeline-block").count() == 0
    cal("refresh-calendar").click()
    page.wait_for_function(
        "document.querySelector('#cal-calendar-status').textContent.includes('Updated')"
    )
    page.evaluate("window.dispatchEvent(new Event('pagehide'))")
    assert cal("table-dialog-detail").inner_text() == ""
    assert page.locator("#calendar-section .timeline-block").count() == 0
    page.evaluate("window.dispatchEvent(new Event('pageshow'))")
    page.wait_for_function(
        "document.querySelector('#cal-calendar-status').textContent.includes('Updated')"
    )

    # Neither date races nor logout races may restore an earlier private snapshot.
    page.evaluate(
        """() => { window.pendingCalendars=[]; const original=window.fetch; window.fetch=(...args)=>args[0].startsWith('/api/restaurant/calendar') ? new Promise(resolve=>window.pendingCalendars.push(resolve)) : original(...args); }"""
    )
    cal("refresh-calendar").click()
    page.wait_for_function("window.pendingCalendars.length===1")
    cal("next-week").click()
    page.wait_for_function("window.pendingCalendars.length===2")
    page.evaluate(
        "data=>window.pendingCalendars[0](new Response(JSON.stringify(data),{status:200}))",
        snapshot,
    )
    assert "unknown" in cal("availability-count").inner_text().lower()
    page.locator("#logout").click()
    page.evaluate(
        "data=>window.pendingCalendars[1](new Response(JSON.stringify(data),{status:200}))",
        snapshot,
    )
    page.wait_for_timeout(50)
    assert "unknown" in cal("availability-count").inner_text().lower()
    assert cal("table-dialog-detail").inner_text() == ""
    assert page.locator("#calendar-section .timeline-block").count() == 0
    page.reload(wait_until="networkidle")
    assert page.locator("#operator-token").input_value() == ""
    assert page.locator("#logout").is_disabled()
    assert cal("tables").locator(".reserved").count() == 0
    assert page.evaluate("localStorage.length + sessionStorage.length") == 0
    assert errors == [], errors
    assert external == [], external


def main():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    origin = f"http://127.0.0.1:{port}"
    server = subprocess.Popen(
        [
            sys.argv[1],
            "-m",
            "uvicorn",
            "tests.restaurant_browser_fixture:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--no-access-log",
        ],
        cwd=ROOT,
        env={"PATH": os.environ["PATH"], "PYTHONDONTWRITEBYTECODE": "1"},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    try:
        for _ in range(100):
            try:
                with urlopen(origin + "/api/status", timeout=1):
                    break
            except OSError:
                if server.poll() is not None:
                    raise RuntimeError(server.stderr.read().decode())
                time.sleep(0.1)
        else:
            raise RuntimeError("local calendar fixture did not start")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                for offset, (width, height) in enumerate(
                    (
                        (1440, 1000),
                        (1366, 768),
                        (1280, 720),
                        (1024, 768),
                        (800, 768),
                        (540, 844),
                        (390, 844),
                        (320, 740),
                    ),
                    1,
                ):
                    context = browser.new_context(
                        viewport={"width": width, "height": height},
                        reduced_motion="reduce",
                    )
                    check(context.new_page(), origin, offset)
                    context.close()
                    print(
                        json.dumps(
                            {
                                "calendar": "passed",
                                "viewport": {"width": width, "height": height},
                            }
                        )
                    )
            finally:
                browser.close()
    finally:
        server.terminate()
        server.wait(timeout=15)


if __name__ == "__main__":
    main()
