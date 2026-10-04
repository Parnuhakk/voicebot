"""Headless authored-calendar live/preview regression; local fixture only.

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
        const values = color.match(/[\d.]+/g).slice(0, 3).map(Number).map(v => {
          v /= 255; return v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4;
        });
        return values[0] * .2126 + values[1] * .7152 + values[2] * .0722;
      };
      let parent = node;
      while (getComputedStyle(parent).backgroundColor === 'rgba(0, 0, 0, 0)') parent = parent.parentElement;
      const text = luminance(getComputedStyle(node).color);
      const background = luminance(getComputedStyle(parent).backgroundColor);
      return (Math.max(text, background) + .05) / (Math.min(text, background) + .05);
    }""")


def check(page, origin):
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
    page.goto(origin + "/booking-calendar.html", wait_until="networkidle")
    assert page.locator("#calendar-mode").input_value() == "live"
    page.wait_for_function(
        "document.querySelector('#table-summary').textContent === '5 tables · 18 seats'"
    )
    assert page.locator("#tables .table-button").count() == 5
    assert "unknown" in page.locator("#availability-count").inner_text().lower()
    assert page.locator("#new-booking").is_hidden()
    assert page.locator("#preview-panel").is_hidden()
    assert page.locator('a[href="/dashboard#demo-section"]').first.is_visible()
    # Resolve the actual cross-page CTA target, not merely its href string.
    handoff = page.context.new_page()
    try:
        handoff.goto(origin + "/booking-calendar.html", wait_until="networkidle")
        handoff.locator("#real-booking").click()
        handoff.wait_for_load_state("networkidle")
        assert handoff.url == origin + "/dashboard#reservation-heading"
        target = handoff.locator("#reservation-heading")
        assert target.count() == 1, "Reservation CTA has no dashboard target"
        bounds = target.bounding_box()
        assert 0 <= bounds["y"] < handoff.viewport_size["height"]
        assert handoff.evaluate("document.activeElement.id") == "reservation-heading"
    finally:
        handoff.close()
    page.locator("#operator-key").fill("restaurant-fixture-operator")
    page.locator("#connect-calendar").click()
    page.wait_for_function(
        "document.querySelector('#calendar-status').textContent.includes('Updated')"
    )
    assert page.locator("#operator-key").input_value() == ""
    assert page.evaluate("localStorage.length + sessionStorage.length") == 0
    assert "Bearer" not in page.url
    assert "5 tables" in page.locator("#table-summary").inner_text()
    # Fixture-only real hold through the existing preparation route.
    # The fixture store is shared by both viewports; give each its own day.
    tomorrow = page.evaluate(
        "days => new Date(Date.now() + days * 86400000).toLocaleDateString('en-CA', {timeZone:'Europe/Tallinn'})",
        1 if page.viewport_size["width"] > 700 else 2,
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
    page.locator("#date-picker").fill(tomorrow)
    page.locator("#date-picker").dispatch_event("change")
    page.wait_for_function(
        "document.querySelector('#calendar-status').textContent.includes('Updated')"
    )
    page.locator("#time-select").select_option("14:00")
    assert page.locator("#tables").inner_text().count("Held") == 1
    assert contrast(page, ".table-button.reserved > .table-caption") >= 4.5
    assert contrast(page, ".table-button:not(.reserved) > .table-caption") >= 4.5
    for selector in (
        ".floor-header p",
        ".year",
        ".window-wall span",
        ".room-name",
        "footer > span",
        ".table-button.reserved .table-shape strong",
        ".day-button[aria-pressed='true'] span",
        ".table-button:not(.reserved) .table-shape strong",
    ):
        assert contrast(page, selector) >= 4.5, selector
    page.locator("#timeline-tab").click()
    assert page.locator(".timeline-block").count() == 1
    assert "Held" in page.locator(".timeline-block").inner_text()
    assert contrast(page, ".timeline-block") >= 4.5
    page.locator("#time-select").select_option("16:00")
    page.locator(".timeline-block").click()
    assert "Held" in page.locator("#table-dialog-detail").inner_text()
    page.locator('[data-close="table-dialog"]').first.click()
    page.locator("#time-select").select_option("14:00")
    page.locator("#floor-tab").click()
    OUT.mkdir(parents=True, exist_ok=True)
    width = page.viewport_size["width"]
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(
        path=str(OUT / f"restaurant-calendar-live-{width}.png"), full_page=True
    )
    # Unknown on failure, including clearing an already-open private detail.
    page.locator("#tables .reserved").click()
    assert "Held" in page.locator("#table-dialog-detail").inner_text()
    page.locator('[data-close="table-dialog"]').first.click()
    page.route(
        "**/api/restaurant/calendar?*",
        lambda route: route.fulfill(status=503, json={"detail": "fixture unavailable"}),
    )
    page.locator("#refresh-calendar").click()
    page.wait_for_function(
        "document.querySelector('#calendar-status').textContent.includes('unavailable')"
    )
    assert page.locator(".timeline-block").count() == 0
    assert "unknown" in page.locator("#availability-count").inner_text().lower()
    assert page.locator("#tables .reserved").count() == 0
    assert page.locator("#table-dialog-detail").inner_text() == ""
    page.unroute("**/api/restaurant/calendar?*")
    page.locator("#refresh-calendar").click()
    page.wait_for_function(
        "document.querySelector('#calendar-status').textContent.includes('Updated')"
    )
    page.clock.fast_forward(60001)
    assert "expired" in page.locator("#calendar-status").inner_text().lower()
    assert "unknown" in page.locator("#availability-count").inner_text().lower()
    assert page.locator(".timeline-block").count() == 0
    # A disconnected in-flight response must never repopulate the room.
    page.evaluate(
        """() => { window.pendingCalendar = null; const original = window.fetch; window.fetch = (...args) => args[0].startsWith('/api/restaurant/calendar') ? new Promise(resolve => {window.pendingCalendar = resolve;}) : original(...args); }"""
    )
    page.locator("#refresh-calendar").click()
    page.wait_for_function("window.pendingCalendar !== null")
    page.locator("#disconnect-calendar").click()
    page.evaluate(
        "window.pendingCalendar(new Response(JSON.stringify({items: []}), {status:200}))"
    )
    page.wait_for_timeout(100)
    assert "unknown" in page.locator("#availability-count").inner_text().lower()
    assert page.locator("#operator-key").input_value() == ""
    # Preview owns a separate twelve-table inventory and no backend writes.
    writes = []
    page.on(
        "request",
        lambda request: writes.append(request.url) if request.method != "GET" else None,
    )
    page.locator("#calendar-mode").select_option("preview")
    assert page.locator("#time-select").input_value() == "19:00"
    assert page.locator("#tables .table-button").count() == 12
    assert "44 seats" in page.locator("#table-summary").inner_text()
    assert "not stored" in page.locator("#mode-notice").inner_text()
    page.locator("#capacity-all").focus()
    page.keyboard.press("ArrowRight")
    assert (
        page.locator('[role="tab"][aria-selected="true"][data-capacity]').get_attribute(
            "data-capacity"
        )
        == "4"
    )
    page.locator("#capacity-all").click()
    page.locator("#new-booking").click()
    page.locator("#booking-name").fill("Browser sample")
    page.locator('#booking-form button[type="submit"]').click()
    assert page.locator("#booking-dialog").is_hidden()
    assert "Demo booking added" in page.locator("#toast").inner_text()
    page.locator("#new-booking").click()
    page.locator("#booking-party").select_option("8")
    page.locator('#booking-form button[type="submit"]').click()
    page.locator("#new-booking").click()
    page.locator('#booking-form button[type="submit"]').click()
    assert (
        "All tables for 8 people are reserved"
        in page.locator("#booking-error").inner_text()
    )
    page.locator('[data-close="booking-dialog"]').click()
    page.locator("#replay").click()
    page.wait_for_function(
        "document.querySelector('#voice-stage').dataset.stage === 'confirmed'",
        timeout=10000,
    )
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(
        path=str(OUT / f"restaurant-calendar-preview-{width}.png"), full_page=True
    )
    page.locator("#calendar-mode").select_option("live")
    assert page.locator("#tables .table-button").count() == 5
    assert page.locator("#tables .highlighted").count() == 0
    assert page.locator("#preview-panel").is_hidden()
    assert "unknown" in page.locator("#availability-count").inner_text().lower()
    assert writes == []
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
                for size in (
                    {"width": 1440, "height": 1000},
                    {"width": 390, "height": 844},
                ):
                    context = browser.new_context(
                        viewport=size, reduced_motion="reduce"
                    )
                    page = context.new_page()
                    check(page, origin)
                    assert page.evaluate(
                        "document.documentElement.scrollWidth <= innerWidth"
                    )
                    context.close()
                    print(json.dumps({"calendar": "passed", "viewport": size}))
            finally:
                browser.close()
    finally:
        server.terminate()
        server.wait(timeout=15)


if __name__ == "__main__":
    main()
