"""Read-only calendar uses actual SQLite inventory, never guest/hold ownership."""

import asyncio
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from tests.test_restaurant_http import AUTH, client  # noqa: F401

NOW = datetime(2026, 10, 4, 10, tzinfo=ZoneInfo("Europe/Tallinn"))
DAY = "2026-10-07"


@pytest.fixture
def calendar_client(client):
    client.app.state.stack["slot"]._now = lambda: NOW
    return client


def get(client, query=f"date={DAY}", headers=AUTH):
    return client.get(f"/api/restaurant/calendar?{query}", headers=headers)


def test_calendar_projects_configured_inventory_and_private_intervals(calendar_client):
    adapter = calendar_client.app.state.stack["slot"]

    async def seed():
        slots = await adapter.search_tables(DAY, 2)

        async def hold(table):
            slot = next(
                s
                for s in slots
                if s["providerId"] == table and s["start"][11:16] == "19:00"
            )
            return await adapter.create_hold(slot["slotId"])

        confirmed = await hold("1")
        await adapter.confirm(
            confirmed.hold_id, {"email": "calendar@example.invalid"}, "calendar-confirm"
        )
        cancelled = await hold("2")
        booking = await adapter.confirm(
            cancelled.hold_id,
            {"email": "cancelled@example.invalid"},
            "calendar-cancel-confirm",
        )
        await adapter.cancel(str(booking["booking"]["id"]), "calendar-cancel")
        active = await hold("3")
        expired = await hold("4")
        with adapter._connection(write=True) as connection:
            connection.execute(
                "UPDATE restaurant_holds SET expires_epoch=? WHERE id=?",
                (NOW.timestamp(), expired.hold_id),
            )
            connection.execute(
                "INSERT INTO restaurant_holds SELECT 'other-restaurant',id,slot_json,table_id,start_epoch,end_epoch,expires_epoch FROM restaurant_holds WHERE id=?",
                (active.hold_id,),
            )
            connection.execute(
                "INSERT INTO restaurant_reservations (restaurant_id,hold_id,table_id,party_size,start_epoch,end_epoch,start_local,end_local,guest_scope_hash,status) SELECT 'other-restaurant',hold_id,table_id,party_size,start_epoch,end_epoch,start_local,end_local,guest_scope_hash,status FROM restaurant_reservations WHERE status='confirmed'"
            )
        return active.hold_id

    private_hold = asyncio.run(seed())
    before = sqlite3.connect(adapter.state_db)
    snapshot = list(before.iterdump())
    before.close()
    response = get(calendar_client)
    assert response.status_code == 200, response.text
    assert response.headers["cache-control"] == "no-store"
    data = response.json()
    assert data["date"] == DAY
    venue = data["restaurant"]
    assert len(venue["tables"]) == 5
    assert sum(t["capacity"] for t in venue["tables"]) == 18
    assert venue["maximum_party_size"] == 6
    assert venue["reservation_duration_minutes"] == 90
    assert venue["timezone"] == "Europe/Tallinn"
    assert venue["opening_hours"]["wednesday"] == {"start": "12:00", "end": "21:00"}
    assert [(i["table_id"], i["status"]) for i in data["items"]] == [
        ("1", "confirmed"),
        ("3", "held"),
    ]
    assert data["items"][1]["expires_at"] == (NOW + timedelta(seconds=120)).isoformat()
    assert all(
        i["start"] == DAY + "T19:00:00+03:00" and i["end"] == DAY + "T20:30:00+03:00"
        for i in data["items"]
    )
    assert private_hold not in response.text
    assert not any(
        word in response.text
        for word in (
            "guest_scope",
            "hold_id",
            "slotId",
            "example.invalid",
            "other-restaurant",
        )
    )
    assert all(
        set(i) <= {"table_id", "party_size", "start", "end", "status", "expires_at"}
        for i in data["items"]
    )
    with sqlite3.connect(adapter.state_db) as connection:
        assert list(connection.iterdump()) == snapshot
    assert get(calendar_client, "date=2026-10-08").json()["items"] == []


@pytest.mark.parametrize(
    "query",
    [
        "",
        "date=not-a-date",
        "date=2026-02-30",
        "date=2026-1-7",
        "date=9999-12-31",
        "date=2026-10-07&date=2026-10-08",
        "date=2026-10-07&table=1",
    ],
)
def test_calendar_authorizes_before_rejecting_malformed_or_extra_query(
    calendar_client, query
):
    denied = get(calendar_client, query, headers={})
    assert denied.status_code == 403
    assert denied.headers["cache-control"] == "no-store"
    invalid = get(calendar_client, query)
    assert invalid.status_code == 400, invalid.text
    assert invalid.headers["cache-control"] == "no-store"


def test_calendar_missing_auth_configuration_and_store_fail_closed(
    calendar_client, monkeypatch
):
    monkeypatch.delenv("OPERATOR_TOKEN")
    response = get(calendar_client, "date=invalid")
    assert response.status_code == 503
    assert response.headers["cache-control"] == "no-store"
    monkeypatch.setenv("OPERATOR_TOKEN", "restaurant-fixture-operator")
    adapter = calendar_client.app.state.stack["slot"]
    adapter.operational = False
    response = get(calendar_client)
    assert response.status_code == 503
    assert "items" not in response.json()
    assert response.headers["cache-control"] == "no-store"
    adapter.operational = True
    adapter.state_db += ".missing"
    response = get(calendar_client)
    assert response.status_code == 503
    from pathlib import Path

    assert not Path(adapter.state_db).exists()


def test_calendar_assets_are_local_versioned_and_link_real_dashboard(calendar_client):
    response = calendar_client.get("/booking-calendar.html")
    assert response.status_code == 200
    html = response.text
    assert 'id="calendar-mode"' in html
    for target in (
        "/dashboard#demo-section",
        "/dashboard#bookings-section",
        "/dashboard#reservation-heading",
    ):
        assert target in html
    import hashlib
    import re

    for name in ("booking-calendar.css", "booking-calendar.js"):
        match = re.search(rf"/{name}\?v=([a-f0-9]{{12}})", html)
        assert match, name
        asset = calendar_client.get("/" + name)
        assert asset.status_code == 200
        assert match[1] == hashlib.sha256(asset.content).hexdigest()[:12]
        assert "trycloudflare" not in asset.text
    assert "/booking-calendar.html" in calendar_client.get("/dashboard").text


def test_calendar_disabled_backend_is_controlled_unavailability(
    calendar_client, monkeypatch
):
    from fastapi.testclient import TestClient
    from app.server import create_app

    monkeypatch.setenv("RESTAURANT_DEMO_WRITES", "0")
    with TestClient(create_app()) as disabled:
        assert disabled.app.state.stack["slot"] is None
        response = get(disabled)
        assert response.status_code == 503
        assert response.json() == {"detail": "restaurant_calendar_unavailable"}
        assert response.headers["cache-control"] == "no-store"
        assert get(disabled, headers={}).status_code == 403
