"""Current published restaurant receipts exercise actual HTTP, policy and SQLite."""

import asyncio
import json

import pytest

from app.languages import CONSENT
from tests.test_restaurant_http import AUTH, prepared, start, tomorrow
from tests.test_restaurant_http import client as client  # noqa: F401


def read(client, session, preparation, receipt=None):
    return client.post(
        "/api/booking/recap",
        headers=AUTH,
        json={
            "session_id": session,
            "hold_id": preparation["hold_id"],
            "recap_delivery_id": receipt or preparation.get("recap_delivery_id"),
        },
    )


def test_bare_hold_cannot_acknowledge_an_unread_restaurant_proposal(client):
    key, preparation = prepared(client)
    response = client.post(
        "/api/booking/recap",
        headers=AUTH,
        json={
            "session_id": key,
            "hold_id": preparation["hold_id"],
        },
    )
    assert response.status_code == 400
    assert (
        client.app.state.demo_sessions.sessions[key].tools.pending["delivery"] is False
    )
    assert (
        client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()["items"]
        == []
    )


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_direct_read_receipt_is_one_use_and_still_needs_later_consent(client, language):
    key, preparation = prepared(client, language)
    receipt = preparation.get("recap_delivery_id")
    assert isinstance(receipt, str) and len(receipt) == 32
    session = client.app.state.demo_sessions.sessions[key]
    assert session.tools.pending["delivery"] is False
    assert read(client, key, preparation).status_code == 200
    assert session.tools.pending["delivery"] is True
    assert session.tools.pending["approved"] is False
    assert read(client, key, preparation).status_code == 409
    assert (
        client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()["items"]
        == []
    )
    confirmed = client.post(
        "/api/booking/confirm",
        headers=AUTH,
        json={
            "session_id": key,
            "hold_id": preparation["hold_id"],
            "consent": True,
        },
    )
    assert confirmed.status_code == 200 and confirmed.json()["ok"] is True
    assert (
        len(
            client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()["items"]
        )
        == 1
    )


@pytest.mark.parametrize(
    "change", ["preparation", "text", "language", "expired", "uncertain"]
)
def test_direct_receipt_cannot_authorize_changed_restaurant_preparation(client, change):
    key, preparation = prepared(client)
    assert preparation.get("recap_delivery_id")
    session = client.app.state.demo_sessions.sessions[key]
    if change == "preparation":
        asyncio.run(session.tools.prepare_demo_booking(preparation["hold_id"]))
    elif change == "text":
        session.tools.pending["recap"]["guest_name"] = "Demo Teine"
    elif change == "language":
        session.tools.language = "ru"
    elif change == "expired":
        session.tools.pending["expires_at"] = 0
    else:
        session.tools.mutation_uncertain = True
    response = read(client, key, preparation)
    assert response.status_code == 409
    assert response.headers["Cache-Control"] == "no-store"
    assert not session.busy
    assert (
        client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()["items"]
        == []
    )


def test_receipt_cannot_transfer_to_a_different_direct_session(client):
    key, preparation = prepared(client)
    other, other_preparation = prepared(client)
    assert preparation.get("recap_delivery_id")
    response = read(client, other, other_preparation, preparation["recap_delivery_id"])
    assert response.status_code == 409
    assert (
        client.app.state.demo_sessions.sessions[other].tools.pending["delivery"]
        is False
    )
    assert (
        client.app.state.demo_sessions.sessions[key].tools.pending["delivery"] is False
    )


def test_rejected_direct_request_cannot_preserve_an_incomplete_restaurant_stream(
    client, monkeypatch
):
    from app.browser_audio import AudioEvents
    from tests.test_browser_audio_stream import AsgiExchange, StreamingSpeaker

    async def check():
        waiting, release = asyncio.Event(), asyncio.Event()
        terminal = {}
        original_body = AudioEvents.body

        async def gated_done(events):
            async for chunk in original_body(events):
                data = json.loads(chunk)
                if data["type"] == "done":
                    terminal.update(data)
                    waiting.set()
                    await release.wait()
                yield chunk

        monkeypatch.setattr(AudioEvents, "body", gated_done)
        client.app.state.stack["tts"] = StreamingSpeaker()
        key = start(client, "en")["session_id"]
        session = client.app.state.demo_sessions.sessions[key]
        exchange = await AsgiExchange(
            client.app,
            {
                "session_id": key,
                "language": "en",
                "text": "A table for four tomorrow at 2 pm",
            },
            headers=AUTH,
        ).start()
        try:
            await asyncio.wait_for(waiting.wait(), 2)
            receipt = session.recap_delivery
            assert receipt and receipt["id"] == terminal["recap_delivery_id"]
            assert not session.busy
            count = session.turn_count
            rejected = client.post(
                "/api/booking/recap", headers=AUTH, json={"session_id": key}
            )
            assert rejected.status_code == 400
            assert session.turn_count == count + 1 and session.recap_delivery is receipt
            await exchange.disconnect()
            assert session.recap_delivery is None
            denied = client.post(
                "/api/turn",
                headers=AUTH,
                json={
                    "session_id": key,
                    "language": "en",
                    "text": CONSENT["en"],
                    "recap_delivery_id": receipt["id"],
                },
            )
            assert denied.status_code == 409
            assert (
                client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()[
                    "items"
                ]
                == []
            )
        finally:
            release.set()
            if not exchange.task.done():
                await exchange.disconnect()

    asyncio.run(check())
