"""Proposal lifetimes and renewal use the real owned restaurant HTTP workflow."""

import sqlite3
import time

import pytest

from tests.test_restaurant_http import AUTH, prepared, start, tomorrow

pytest_plugins = ["tests.test_restaurant_http"]


def renew(client, session, hold_id):
    return client.post(
        "/api/restaurant/reservation/renew",
        json={"session_id": session, "hold_id": hold_id},
        headers=AUTH,
    )


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_proposal_lifetime_is_server_owned_and_bounded_by_the_session(client, language):
    session_id = start(client, language, direct=True)["session_id"]
    session = client.app.state.demo_sessions.sessions[session_id]
    session.expires_at = time.monotonic() + 5
    result = client.post(
        "/api/restaurant/reservation/prepare",
        json={"session_id": session_id, "date": tomorrow(), "start_time": "14:00", "party_size": 2},
        headers=AUTH,
    )
    assert result.status_code == 200 and result.json()["ok"]
    assert 0 < result.json()["recap_expires_in_s"] <= 5
    assert session.tools.pending["expires_at"] > session.expires_at


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_renew_preserves_the_owned_table_guest_and_releases_old_consent(client, language):
    session_id = start(client, language, direct=True)["session_id"]
    original = client.post(
        "/api/restaurant/reservation/prepare",
        json={"session_id": session_id, "date": tomorrow(), "start_time": "14:00", "party_size": 2, "guest_fixture_id": "guest-002"},
        headers=AUTH,
    ).json()
    hold_id = original["hold_id"]
    assert client.post("/api/booking/recap", json={"session_id": session_id, "hold_id": hold_id}, headers=AUTH).status_code == 200
    state = client.app.state.demo_sessions.sessions[session_id].tools
    assert state.pending["delivery"]
    state.pending["expires_at"] = time.monotonic() - 1
    result = renew(client, session_id, hold_id)
    assert result.status_code == 200 and result.json()["ok"], result.text
    assert result.json()["hold_id"] == hold_id
    assert result.json()["recap"] == original["recap"]
    assert result.json()["recap_text"] == original["recap_text"]
    assert 0 < result.json()["recap_expires_in_s"] <= 60
    assert state.pending["guest_fixture_id"] == "guest-002"
    assert not state.pending["delivery"] and not state.pending["approved"]
    with sqlite3.connect(state.dispatcher._slot.state_db) as database:
        assert database.execute("SELECT COUNT(*) FROM restaurant_holds").fetchone()[0] == 1
        assert database.execute("SELECT COUNT(*) FROM restaurant_reservations").fetchone()[0] == 0
    denied = client.post("/api/booking/confirm", json={"session_id": session_id, "hold_id": hold_id, "consent": True}, headers=AUTH)
    assert denied.status_code == 409
    assert not state.bookings


def test_renewed_proposal_can_be_confirmed_only_after_its_new_read_acknowledgement(client):
    session_id, original = prepared(client)
    renewed = renew(client, session_id, original["hold_id"])
    assert renewed.status_code == 200 and renewed.json()["ok"]
    body = {"session_id": session_id, "hold_id": original["hold_id"]}
    assert client.post("/api/booking/recap", json=body, headers=AUTH).status_code == 200
    confirmed = client.post("/api/booking/confirm", json={**body, "consent": True}, headers=AUTH)
    assert confirmed.status_code == 200 and confirmed.json()["ok"]
    assert renew(client, session_id, original["hold_id"]).status_code == 409


def test_renew_rejects_foreign_and_unknown_holds_without_writes(client):
    owner, original = prepared(client)
    other = start(client, "en", direct=True)["session_id"]
    assert renew(client, other, original["hold_id"]).status_code == 409
    assert renew(client, owner, "unknown").status_code == 409
    assert client.get("/api/bookings?date=" + tomorrow(), headers=AUTH).json()["items"] == []


def test_renew_cannot_resurrect_an_expired_database_hold(client):
    session_id, original = prepared(client)
    state = client.app.state.demo_sessions.sessions[session_id].tools
    with sqlite3.connect(state.dispatcher._slot.state_db) as database:
        database.execute("UPDATE restaurant_holds SET expires_epoch=0 WHERE id=?", (original["hold_id"],))
    result = renew(client, session_id, original["hold_id"])
    assert result.status_code == 409 and result.json()["error"] == "hold_expired_or_unknown"
    assert state.pending is None and not state.bookings


def test_renew_is_denied_after_an_uncertain_mutation(client):
    session_id, original = prepared(client)
    state = client.app.state.demo_sessions.sessions[session_id].tools
    state.mutation_uncertain = True
    assert renew(client, session_id, original["hold_id"]).status_code == 409
    assert not state.bookings


def test_expired_read_can_recover_by_checking_current_availability(client):
    session_id, original = prepared(client)
    state = client.app.state.demo_sessions.sessions[session_id].tools
    state.pending["expires_at"] = time.monotonic() - 1
    body = {"session_id": session_id, "hold_id": original["hold_id"]}
    assert client.post("/api/booking/recap", json=body, headers=AUTH).status_code == 409
    assert state.pending is None
    result = renew(client, session_id, original["hold_id"])
    assert result.status_code == 409 and result.json()["error"] == "hold_expired_or_unknown"
    fresh = client.post(
        "/api/restaurant/reservation/prepare",
        json={"session_id": session_id, "date": tomorrow(), "start_time": "14:00", "party_size": 4},
        headers=AUTH,
    )
    assert fresh.status_code == 200 and fresh.json()["ok"]
    assert fresh.json()["hold_id"] != original["hold_id"]
    assert not state.pending["delivery"] and not state.bookings


@pytest.mark.parametrize("hold_id", [None, 1, True, [], {}])
def test_renew_validates_hold_identity(client, hold_id):
    session_id, _ = prepared(client)
    assert renew(client, session_id, hold_id).status_code == 409


def test_renew_requires_operator_authentication(client):
    assert client.post("/api/restaurant/reservation/renew", json={}).status_code == 403
