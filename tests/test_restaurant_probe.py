"""Temporary canonical SQLite and local SDK/process doubles; never live providers."""

import asyncio
import copy
from datetime import datetime, timedelta
import importlib.util
import hashlib
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, Mock
from zoneinfo import ZoneInfo
import wave

import pytest

from app.booking.restaurant import RestaurantAdapter
from app.business import restaurant_dispatcher
from app.demo import load_demo_data, scoped_guest
from app.restaurant_data import load_restaurant_data

ROOT = Path(__file__).resolve().parents[1]
SCOPE, FOREIGN = "a" * 32, "b" * 32
NOW = datetime(2026, 10, 3, 10, tzinfo=ZoneInfo("Europe/Tallinn"))
DAY = (NOW + timedelta(days=14)).date()
NATURAL_CONSENT = {
    "et": "Jah, loomulikult, see sobib, aitäh.",
    "en": "Yes, that works for me.",
    "ru": "Да, подходит.",
}
CONDITIONAL_REPLY = {
    "et": "Jah, kui saame istuda akna ääres.",
    "en": "Yes, if we can sit by the window.",
    "ru": "Да, если мы можем сесть у окна.",
}
PREMATURE_YES = {"et": "Jah.", "en": "Yes.", "ru": "Да."}


def load_probe():
    path = ROOT / "deploy/telephony/restaurant_probe.py"
    assert path.is_file(), "canonical probe missing"
    spec = importlib.util.spec_from_file_location("canonical_probe", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def probe():
    return load_probe()


@pytest.fixture
def transport_probe(monkeypatch):
    from app.restaurant_call import restaurant_spoken_date

    # Only transport fault tests isolate policy. Actual renders below use the
    # real current canonical constructor/COPY, not this deliberately fake text.
    copybook = {
        language: {
            "recap": "Fixture {name}: {question}",
            "confirmation_question": f"Fixture {language} question?",
        }
        for language in ("et", "en", "ru")
    }
    with monkeypatch.context() as local:
        local.setitem(
            sys.modules,
            "app.restaurant_call",
            NS(
                COPY=copybook,
                restaurant_spoken_date=restaurant_spoken_date,
            ),
        )
        return load_probe()


@pytest.fixture
def ledger(tmp_path):
    data = load_restaurant_data()
    data["restaurant_id"] = "probe-fixture-venue"
    path, config = tmp_path / "restaurant-booking.db", tmp_path / "restaurant.json"
    config.write_text(json.dumps(data))
    adapter = RestaurantAdapter(path, data=data, allow_writes=True, now=lambda: NOW)
    return NS(path=path, config=config, data=data, adapter=adapter)


def book(ledger, scope=SCOPE, *, fixture="guest-001", key=None):
    async def create():
        slots = await ledger.adapter.search_tables(DAY.isoformat(), 4)
        slot = next(row for row in slots if row["start"].endswith("T18:00:00"))
        hold = await ledger.adapter.create_hold(slot["slotId"])
        # Independently mirror the read shared-dispatch contract, not a probe
        # helper. Actual dispatched confirmations below corroborate this hash.
        action = hashlib.sha256(
            (
                "confirm_slot_booking"
                + json.dumps({"hold_id": hold.hold_id}, sort_keys=True)
            ).encode()
        ).hexdigest()
        key_used = key or f"tel-{scope}-{action}"
        result = await ledger.adapter.confirm(
            hold.hold_id, scoped_guest(load_demo_data(), fixture, scope), key_used
        )
        assert result["ok"] is True
        return result["booking"]["id"], key_used

    return asyncio.run(create())


@pytest.fixture
def native_confirmation(probe, ledger, monkeypatch):
    from app import restaurant_call

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz) if tz else NOW.replace(tzinfo=None)

    monkeypatch.setattr(restaurant_call, "datetime", FixedDateTime)

    async def confirm(language="en"):
        state = restaurant_call.RestaurantCallTools(
            restaurant_dispatcher(ledger.adapter, ledger.data),
            language=language,
            call_id=SCOPE,
        )
        state.observe_user_text(
            probe.scenario(language, DAY)["request"], language=language
        )
        prepared = await state.dispatch(
            "plan_restaurant_reservation",
            {
                "date": DAY.isoformat(),
                "start_time": "18:00",
                "party_size": 4,
            },
        )
        assert not prepared.get("error")
        hold = prepared["hold_id"]
        assert state.mark_recap_delivered(hold)
        state.observe_user_text(NATURAL_CONSENT[language], language=language)
        arguments = {"hold_id": hold}
        result = await state.dispatch("confirm_slot_booking", arguments)
        assert result.get("ok") is True, result
        with sqlite3.connect(ledger.path) as db:
            actions = db.execute(
                "SELECT key,response_json FROM restaurant_actions WHERE restaurant_id=?",
                (ledger.data["restaurant_id"],),
            ).fetchall()
        (key,) = [
            key
            for key, raw in actions
            if json.loads(raw).get("booking", {}).get("id") == result["booking"]["id"]
        ]
        expected = hashlib.sha256(
            ("confirm_slot_booking" + json.dumps(arguments, sort_keys=True)).encode()
        ).hexdigest()
        assert key == f"tel-{SCOPE}-{expected}"
        return NS(
            state=state, booking_id=result["booking"]["id"], hold_id=hold, key=key
        )

    return confirm


def snapshot(ledger):
    with sqlite3.connect(ledger.path) as db:
        return {
            table: db.execute(f"SELECT * FROM {table} ORDER BY 1,2").fetchall()
            for table in (
                "restaurant_reservations",
                "restaurant_actions",
                "restaurant_holds",
            )
        }


def owned(probe, ledger, scope=SCOPE, *, cleanup=False, writes="1", fallback=False):
    env = {
        "HOME": "/home/arle",
        "PATH": "/usr/bin:/bin",
        "TMPDIR": "/tmp/opencode",
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "PYTHONDONTWRITEBYTECODE": "1",
        "VOICEBOT_BUSINESS_TYPE": "restaurant",
        "RESTAURANT_CONFIG_PATH": str(ledger.config),
        "RESTAURANT_DEMO_WRITES": writes,
    }
    env["EASY_STATE_DB" if fallback else "RESTAURANT_STATE_DB"] = str(
        ledger.path.with_name("easy.db") if fallback else ledger.path
    )
    return subprocess.run(
        [
            sys.executable,
            "-c",
            probe.OWNED_CODE,
            json.dumps({"call_id": scope, "cleanup": cleanup}),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.mark.parametrize("scope", [None, "", "a' OR 1=1 --", "A" * 32, "0" * 33])
def test_scope_validation_precedes_docker_and_sql(probe, ledger, monkeypatch, scope):
    command = Mock()
    monkeypatch.setattr(probe.subprocess, "run", command)
    with pytest.raises(ValueError, match="probe_scope_invalid"):
        probe.read_owned("fixture-worker", scope, cleanup=True)
    command.assert_not_called()
    monkeypatch.undo()
    before = snapshot(ledger)
    result = owned(probe, ledger, scope, cleanup=True)
    assert result.returncode != 0 and "Traceback" not in result.stderr
    assert snapshot(ledger) == before


def test_independent_read_and_cleanup_preserve_baseline_foreign_rows_and_history(
    probe, ledger
):
    mine, _ = book(ledger)
    foreign, _ = book(ledger, FOREIGN)
    baseline, _ = book(ledger, FOREIGN, key="baseline-confirm")
    before = snapshot(ledger)
    result = owned(probe, ledger, fallback=True)
    assert result.returncode == 0, result.stderr
    (item,) = json.loads(result.stdout)["items"]
    assert (
        item["id"] == mine and item["party_size"] == 4 and item["status"] == "confirmed"
    )
    assert item["start"] == DAY.isoformat() + "T18:00:00"
    assert item["end"] == DAY.isoformat() + "T19:30:00"
    assert snapshot(ledger) == before
    result = owned(probe, ledger, cleanup=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["items"][0]["status"] == "cancelled"
    after = snapshot(ledger)
    assert {row[0]: row[-1] for row in after["restaurant_reservations"]} == {
        mine: "cancelled",
        foreign: "confirmed",
        baseline: "confirmed",
    }
    assert set(before["restaurant_actions"]) <= set(after["restaurant_actions"])
    added = set(after["restaurant_actions"]) - set(before["restaurant_actions"])
    assert len(added) == 1 and next(iter(added))[1].startswith(
        f"probe-cleanup-{SCOPE}-{mine}-"
    )
    assert after["restaurant_holds"] == before["restaurant_holds"]
    assert owned(probe, ledger, cleanup=True).returncode == 0
    assert snapshot(ledger) == after


@pytest.mark.parametrize(
    "damage",
    [
        "json",
        "list",
        "boolean_id",
        "string_id",
        "missing_row",
        "fingerprint",
        "guest_hash",
        "fixture",
        "hold_key",
        "restaurant",
        "party",
        "start",
        "end",
        "table",
        "status",
        "not_synthetic",
    ],
)
def test_unproven_malformed_stale_or_foreign_journal_cannot_change_rows(
    probe, ledger, damage
):
    mine, key = book(
        ledger, fixture="guest-002" if damage == "fixture" else "guest-001"
    )
    other, _ = book(ledger, FOREIGN, key="baseline-confirm")
    with sqlite3.connect(ledger.path) as db:
        response = json.loads(
            db.execute(
                "SELECT response_json FROM restaurant_actions WHERE key=?", (key,)
            ).fetchone()[0]
        )
        if damage == "json":
            raw = "PRIVATE malformed"
        elif damage == "list":
            raw = "[]"
        else:
            if damage in {"boolean_id", "string_id", "missing_row"}:
                response["booking"]["id"] = {
                    "boolean_id": True,
                    "string_id": str(mine),
                    "missing_row": 999999,
                }[damage]
            elif damage == "restaurant":
                db.execute(
                    "UPDATE restaurant_reservations SET restaurant_id='other-venue' WHERE id=?",
                    (mine,),
                )
            elif damage == "fingerprint":
                db.execute(
                    "UPDATE restaurant_actions SET request_hash=? WHERE key=?",
                    ("0" * 64, key),
                )
            elif damage == "guest_hash":
                db.execute(
                    "UPDATE restaurant_reservations SET guest_scope_hash=(SELECT guest_scope_hash FROM restaurant_reservations WHERE id=?) WHERE id=?",
                    (other, mine),
                )
            elif damage == "hold_key":
                db.execute(
                    "UPDATE restaurant_reservations SET hold_id=? WHERE id=?",
                    ("restaurant_hold_" + "c" * 32, mine),
                )
            elif damage != "fixture":
                field, value = {
                    "party": ("party_size", 2),
                    "start": ("start", DAY.isoformat() + "T17:00:00"),
                    "end": ("end", DAY.isoformat() + "T20:00:00"),
                    "table": ("table_id", "5"),
                    "status": ("status", "cancelled"),
                    "not_synthetic": ("synthetic", False),
                }[damage]
                response["booking"][field] = value
            raw = json.dumps(response)
        db.execute(
            "UPDATE restaurant_actions SET response_json=? WHERE key=?", (raw, key)
        )
    before = snapshot(ledger)
    result = owned(probe, ledger, cleanup=True)
    assert result.returncode != 0
    assert (
        "PRIVATE" not in result.stdout + result.stderr
        and "Traceback" not in result.stderr
    )
    assert snapshot(ledger) == before


def test_other_venue_native_key_is_not_ownership(probe, ledger):
    data = copy.deepcopy(ledger.data)
    data["restaurant_id"] = "other-venue"
    ledger.adapter = RestaurantAdapter(
        ledger.path, data=data, allow_writes=True, now=lambda: NOW
    )
    book(ledger)
    before = snapshot(ledger)
    result = owned(probe, ledger, cleanup=True)
    assert result.returncode == 0 and json.loads(result.stdout) == {"items": []}
    assert snapshot(ledger) == before


def test_cleanup_respects_opt_in_and_missing_database_is_not_created(probe, ledger):
    book(ledger)
    before = snapshot(ledger)
    assert owned(probe, ledger, cleanup=True, writes="0").returncode != 0
    assert snapshot(ledger) == before
    ledger.path = ledger.path.with_name("absent.db")
    assert owned(probe, ledger).returncode != 0 and not ledger.path.exists()


def test_configured_duration_is_not_replaced_with_old_allocator_facts(probe, ledger):
    ledger.data["reservation_duration_minutes"] = 120
    ledger.config.write_text(json.dumps(ledger.data))
    ledger.adapter = RestaurantAdapter(
        ledger.path, data=ledger.data, allow_writes=True, now=lambda: NOW
    )
    book(ledger)
    result = owned(probe, ledger, cleanup=True)
    assert result.returncode == 0
    assert json.loads(result.stdout)["items"][0]["end"].endswith("T20:00:00")


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_actual_native_confirmation_is_visible_and_cleanup_preserves_other_history(
    probe, ledger, native_confirmation, language
):
    foreign, _ = book(ledger, FOREIGN)
    baseline, _ = book(ledger, FOREIGN, key="baseline-confirm")
    native = asyncio.run(native_confirmation(language))
    before = snapshot(ledger)
    result = owned(probe, ledger)
    assert result.returncode == 0, result.stderr
    items = json.loads(result.stdout)["items"]
    assert [row["id"] for row in items] == [native.booking_id]
    assert items[0]["start"] == DAY.isoformat() + "T18:00:00"
    assert items[0]["party_size"] == 4 and items[0]["status"] == "confirmed"
    assert snapshot(ledger) == before
    result = owned(probe, ledger, cleanup=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["items"][0]["status"] == "cancelled"
    after = snapshot(ledger)
    assert len(after["restaurant_reservations"]) == len(
        before["restaurant_reservations"]
    )
    assert {row[0]: row[-1] for row in after["restaurant_reservations"]} == {
        native.booking_id: "cancelled",
        foreign: "confirmed",
        baseline: "confirmed",
    }
    assert [
        row for row in before["restaurant_reservations"] if row[0] != native.booking_id
    ] == [
        row for row in after["restaurant_reservations"] if row[0] != native.booking_id
    ]
    assert set(before["restaurant_actions"]) <= set(after["restaurant_actions"])
    assert len(after["restaurant_actions"]) == len(before["restaurant_actions"]) + 1
    assert after["restaurant_holds"] == before["restaurant_holds"]


@pytest.mark.parametrize(
    "phase,turn,code",
    [
        ("premature_yes", 1, "probe_premature_yes_write"),
        ("request", 2, "probe_premature_write"),
        ("conditional", 3, "probe_conditional_write"),
        ("decline", 4, "probe_decline_write"),
    ],
)
def test_actual_native_write_cannot_hide_from_zero_write_checks(
    probe, ledger, native_confirmation, phase, turn, code
):
    phrases, spoken = probe.scenario("en", DAY), []

    async def speak(text):
        spoken.append(text)
        if len(spoken) == turn:
            await native_confirmation()
        return rendered("en")

    async def read():
        result = owned(probe, ledger)
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)["items"]

    with pytest.raises(AssertionError, match=code):
        asyncio.run(probe.exercise(speak, read, phrases, "en", DAY))
    assert (
        spoken
        == [
            phrases["premature_yes"],
            phrases["request"],
            phrases["conditional"],
            phrases["decline"],
        ][:turn]
    )
    assert NATURAL_CONSENT["en"] not in spoken


@pytest.mark.parametrize(
    "damage",
    ["missing_action", "invented_key", "malformed_hold", "same_guest_baseline"],
)
def test_scoped_candidate_without_valid_native_proof_fails_closed(
    probe, ledger, native_confirmation, damage
):
    native = asyncio.run(native_confirmation())
    if damage == "same_guest_baseline":
        book(ledger, SCOPE, key="baseline-confirm")
    else:
        with sqlite3.connect(ledger.path) as db:
            if damage == "malformed_hold":
                db.execute(
                    "UPDATE restaurant_reservations SET hold_id='malformed' WHERE id=?",
                    (native.booking_id,),
                )
            else:
                key = (
                    "baseline-hidden-action"
                    if damage == "missing_action"
                    else f"tel-{SCOPE}-confirm_slot_booking-{native.hold_id}"
                )
                db.execute(
                    "UPDATE restaurant_actions SET key=? WHERE key=?", (key, native.key)
                )
    before = snapshot(ledger)
    result = owned(probe, ledger, cleanup=True)
    assert result.returncode != 0, (
        "unproven scoped reservation was silently reported absent"
    )
    assert snapshot(ledger) == before


def test_actual_native_spoken_cancellation_remains_independently_visible(
    probe, ledger, native_confirmation
):
    async def cancel():
        native = await native_confirmation()
        native.state.observe_user_text(
            probe.scenario("en", DAY)["cancel"], language="en"
        )
        result = await native.state.dispatch(
            "cancel_slot_booking", {"booking_id": str(native.booking_id)}
        )
        assert result.get("ok") is True, result
        return native.booking_id

    booking_id = asyncio.run(cancel())
    before = snapshot(ledger)
    result = owned(probe, ledger, cleanup=True)
    assert result.returncode == 0, result.stderr
    assert [
        (row["id"], row["status"]) for row in json.loads(result.stdout)["items"]
    ] == [(booking_id, "cancelled")]
    assert snapshot(ledger) == before


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_actual_natural_consent_exercise_requires_current_delivered_proposal(
    probe, ledger, monkeypatch, language
):
    from app import restaurant_call

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz) if tz else NOW.replace(tzinfo=None)

    monkeypatch.setattr(restaurant_call, "datetime", FixedDateTime)
    foreign, _ = book(ledger, FOREIGN)
    baseline, _ = book(ledger, FOREIGN, key="baseline-confirm")
    before = snapshot(ledger)
    phrases, spoken, delivered = probe.scenario(language, DAY), [], []
    state = restaurant_call.RestaurantCallTools(
        restaurant_dispatcher(ledger.adapter, ledger.data),
        language=language,
        call_id=SCOPE,
    )

    async def read():
        result = owned(probe, ledger)
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)["items"]

    async def prepare():
        proposal = await state.dispatch(
            "plan_restaurant_reservation",
            {
                "date": DAY.isoformat(),
                "start_time": "18:00",
                "party_size": 4,
            },
        )
        assert not proposal.get("error"), proposal
        assert (
            state.pending
            and not state.pending["delivery"]
            and not state.pending["approved"]
        )
        assert not await read(), "preparation alone must not write"
        return proposal["hold_id"]

    async def run():
        # Try confirmation even when a model requests it: native policy must
        # deny an undelivered yes, a delivered condition and a delivered decline.
        for text, delivery in (
            (PREMATURE_YES[language], False),
            (CONDITIONAL_REPLY[language], True),
            (phrases["decline"], True),
        ):
            state.observe_user_text(phrases["request"], language=language)
            hold = await prepare()
            if delivery:
                assert state.mark_recap_delivered(hold)
            snapshot_before = snapshot(ledger)
            state.observe_user_text(text, language=language)
            assert not state.pending or not state.pending["approved"]
            denied = await state.dispatch("confirm_slot_booking", {"hold_id": hold})
            assert denied.get("error") == "consent_required", denied
            assert not await read()
            assert snapshot(ledger) == snapshot_before

        async def speak(text):
            spoken.append(text)
            state.observe_user_text(text, language=language)
            if text == phrases["request"]:
                current_hold = await prepare()
                recap = state.render_recap(current_hold)
                assert recap.endswith(
                    restaurant_call.COPY[language]["confirmation_question"]
                )
                assert state.mark_recap_delivered(current_hold)
                delivered.append(state.pending)
                return recap
            if text == NATURAL_CONSENT[language]:
                assert len(delivered) == 2 and delivered[0] is not delivered[1]
                assert state.pending is delivered[-1]
                assert state.pending["delivery"] and state.pending["approved"]
                result = await state.dispatch(
                    "confirm_slot_booking", {"hold_id": state.pending["hold_id"]}
                )
                assert result.get("ok") is True, result
                assert len(await read()) == 1
                return restaurant_call.COPY[language]["confirmed"]
            if text == phrases["cancel"]:
                assert (
                    state.cancel_approval
                    and state.cancel_approval["booking_id"] == state.last_booking
                )
                result = await state.dispatch(
                    "cancel_slot_booking", {"booking_id": state.last_booking}
                )
                assert result.get("ok") is True, result
                return restaurant_call.COPY[language]["cancelled"]
            assert not state.pending or not state.pending["approved"]
            snapshot_before = snapshot(ledger)
            denied = await state.dispatch("confirm_slot_booking", {"hold_id": hold})
            assert denied.get("error") == "consent_required", denied
            assert not await read()
            assert snapshot(ledger) == snapshot_before
            return state.direct_reply or restaurant_call.COPY[language]["domain"]

        checks = await probe.exercise(speak, read, phrases, language, DAY)
        assert checks["premature_yes_no_write"] and checks["conditional_no_write"]
        assert checks["decline_no_write"] and checks["extra_detail_turns"] == 0
        assert spoken == [
            PREMATURE_YES[language],
            phrases["request"],
            CONDITIONAL_REPLY[language],
            phrases["decline"],
            phrases["request"],
            NATURAL_CONSENT[language],
            phrases["cancel"],
        ]
        assert len(spoken) == 7 and probe.CONVERSATION_TIMEOUT == 240
        (item,) = await read()
        assert item["status"] == "cancelled" and item["party_size"] == 4
        assert item["start"] == DAY.isoformat() + "T18:00:00"
        result = owned(probe, ledger, cleanup=True)
        assert result.returncode == 0
        return item["id"]

    owned_id = asyncio.run(run())
    after = snapshot(ledger)
    assert {row[0]: row[-1] for row in after["restaurant_reservations"]} == {
        foreign: "confirmed",
        baseline: "confirmed",
        owned_id: "cancelled",
    }
    assert [
        row for row in after["restaurant_reservations"] if row[0] != owned_id
    ] == before["restaurant_reservations"]
    assert set(before["restaurant_actions"]) <= set(after["restaurant_actions"])
    assert len(after["restaurant_actions"]) == len(before["restaurant_actions"]) + 2
    assert set(before["restaurant_holds"]) <= set(after["restaurant_holds"])


@pytest.mark.parametrize("failure", ["exit", "json", "timeout"])
def test_docker_errors_do_not_expose_private_output(probe, monkeypatch, failure):
    command = (
        Mock(side_effect=subprocess.TimeoutExpired("PRIVATE", 30))
        if failure == "timeout"
        else Mock(
            return_value=subprocess.CompletedProcess(
                [], 7 if failure == "exit" else 0, "PRIVATE", "PRIVATE"
            )
        )
    )
    monkeypatch.setattr(probe.subprocess, "run", command)
    with pytest.raises(RuntimeError, match="probe_ledger_read_failed") as error:
        probe.read_owned("fixture-worker", SCOPE)
    assert "PRIVATE" not in str(error.value)


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_actual_constructor_render_and_fixed_clock_scenario(
    probe, ledger, monkeypatch, language
):
    from app import restaurant_call

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz) if tz else NOW.replace(tzinfo=None)

    monkeypatch.setattr(restaurant_call, "datetime", FixedDateTime)
    phrases = probe.scenario(language, DAY)
    fields = restaurant_call.parse_restaurant_request(phrases["request"], now=NOW)
    assert fields == {"date": DAY.isoformat(), "start_time": "18:00", "party_size": 4}
    assert phrases["consent"] == NATURAL_CONSENT[language]
    assert phrases["premature_yes"] == PREMATURE_YES[language]
    assert phrases["conditional"] == CONDITIONAL_REPLY[language]
    assert (
        phrases["recap_marker"]
        == restaurant_call.COPY[language]["recap"].split("{", 1)[0]
    )

    async def render():
        state = restaurant_call.RestaurantCallTools(
            restaurant_dispatcher(ledger.adapter, ledger.data), language=language
        )
        state.observe_user_text(phrases["request"], language=language)
        prepared = await state.dispatch("plan_restaurant_reservation", fields)
        assert not prepared.get("error")
        return state.render_recap()

    text = asyncio.run(render())
    assert probe.complete_recap(text, language)
    assert not probe.complete_recap(phrases["recap_marker"] + "unfinished", language)
    question = restaurant_call.COPY[language]["confirmation_question"]
    assert text.endswith(question)
    assert not probe.complete_recap(text[:-1], language)
    assert not probe.complete_recap(text.removesuffix(question), language)
    assert all(
        not probe.complete_recap(text, other)
        for other in ("et", "en", "ru")
        if other != language
    )
    assert probe.diagnostic_counts(["PRIVATE"], [text]) == {
        "final_input_turns": 1,
        "spoken_replies": 1,
        "canonical_recaps": 1,
    }


def rendered(language):
    from app.restaurant_call import COPY

    return COPY[language]["recap"].format(
        name="Fixture",
        date=DAY.isoformat(),
        time="18:00",
        party=4,
        duration=90,
        guest="Fixture Guest",
        question=COPY[language]["confirmation_question"],
    )


@pytest.mark.parametrize("language", ["et", "en", "ru"])
@pytest.mark.parametrize("date_question", ["date", "date_ambiguous"])
def test_dialogue_only_missing_details_later_consent_and_independent_cancellation(
    probe, language, date_question
):
    from app.restaurant_call import COPY

    phrases = probe.scenario(language, DAY)
    replies = iter(
        [
            "no proposal",
            COPY[language][date_question],
            COPY[language]["time"],
            rendered(language),
            rendered(language),
            "declined",
            rendered(language),
            "confirmed",
            "cancelled",
        ]
    )
    spoken, reads = [], []

    async def speak(text):
        spoken.append(text)
        return next(replies)

    async def read():
        reads.append(len(spoken))
        if spoken[-1] not in {phrases["consent"], phrases["cancel"]}:
            return []
        return [
            {
                "id": 1,
                "party_size": 4,
                "start": DAY.isoformat() + "T18:00:00",
                "status": "cancelled"
                if spoken[-1] == phrases["cancel"]
                else "confirmed",
            }
        ]

    result = asyncio.run(probe.exercise(speak, read, phrases, language, DAY))
    assert result["extra_detail_turns"] == 2
    assert spoken == [
        phrases["premature_yes"],
        phrases["request"],
        phrases["details"]["date"],
        phrases["details"]["time"],
        phrases["conditional"],
        phrases["decline"],
        phrases["request"],
        NATURAL_CONSENT[language],
        phrases["cancel"],
    ]
    assert reads == list(range(1, 10))
    assert result["premature_yes_no_write"] and result["conditional_no_write"]
    assert "bare_yes_no_write" not in result


@pytest.mark.parametrize(
    "language,month", [("et", "oktoobril"), ("en", "October"), ("ru", "октября")]
)
def test_spoken_caller_dates_use_one_named_month_and_recover_ambiguous_input(
    probe, language, month
):
    from app.restaurant_call import parse_restaurant_request

    phrases = probe.scenario(language, DAY)
    assert month in phrases["details"]["date"]
    assert month in phrases["request"]
    assert parse_restaurant_request(
        phrases["details"]["date"],
        {"date_issue": "date_ambiguous"},
        now=NOW,
        expected_field="date_ambiguous",
    ) == {"date": "2026-10-17"}


@pytest.mark.parametrize(
    "day_number,ordinal",
    [
        (1, "esimesel"),
        (2, "teisel"),
        (3, "kolmandal"),
        (4, "neljandal"),
        (5, "viiendal"),
        (6, "kuuendal"),
        (7, "seitsmendal"),
        (8, "kaheksandal"),
        (9, "üheksandal"),
        (10, "kümnendal"),
        (11, "üheteistkümnendal"),
        (12, "kaheteistkümnendal"),
        (13, "kolmeteistkümnendal"),
        (14, "neljateistkümnendal"),
        (15, "viieteistkümnendal"),
        (16, "kuueteistkümnendal"),
        (17, "seitsmeteistkümnendal"),
        (18, "kaheksateistkümnendal"),
        (19, "üheksateistkümnendal"),
        (20, "kahekümnendal"),
        (21, "kahekümne esimesel"),
        (22, "kahekümne teisel"),
        (23, "kahekümne kolmandal"),
        (24, "kahekümne neljandal"),
        (25, "kahekümne viiendal"),
        (26, "kahekümne kuuendal"),
        (27, "kahekümne seitsmendal"),
        (28, "kahekümne kaheksandal"),
        (29, "kahekümne üheksandal"),
        (30, "kolmekümnendal"),
        (31, "kolmekümne esimesel"),
    ],
)
def test_estonian_caller_speaks_calendar_day_words(probe, day_number, ordinal):
    from app.restaurant_call import parse_restaurant_request

    day = datetime(2026, 10, day_number).date()
    phrases = probe.scenario("et", day)
    assert phrases["details"]["date"] == f"{ordinal} oktoobril 2026"
    assert parse_restaurant_request(
        phrases["request"],
        now=datetime(2026, 9, 20, 12, tzinfo=ZoneInfo("Europe/Tallinn")),
    ) == {"date": f"2026-10-{day_number:02d}", "start_time": "18:00", "party_size": 4}


def test_estonian_caller_uses_the_recognizable_natural_affirmative(probe):
    from app.restaurant_consent import is_restaurant_confirmation

    assert probe.scenario("et", DAY)["consent"] == "Jah, loomulikult, see sobib, aitäh."
    assert is_restaurant_confirmation(probe.scenario("et", DAY)["consent"], "et")
    assert is_restaurant_confirmation("Jah, olen nõus.", "et")


def test_estonian_caller_declines_with_distinct_supported_language_words(probe):
    from app.languages import select_language
    from app.restaurant_consent import is_restaurant_confirmation

    text = probe.scenario("et", DAY)["decline"]
    assert text == "Ei, mulle see ei sobi. Palun ära kinnita."
    assert select_language(text, None, "") == "et"
    assert not is_restaurant_confirmation(text, "et")


def test_estonian_caller_cancellation_matches_the_qualified_owned_context(probe):
    from app.telephone import CANCELLATIONS

    phrases = probe.scenario("et", DAY)
    assert phrases["voice"] == "et-EE-AnuNeural"
    assert phrases["cancel"] == (
        "Palun tühista broneering, mille just selles kõnes tegime."
    )
    assert (
        " ".join(phrases["cancel"].casefold().replace(",", "").replace(".", "").split())
        in CANCELLATIONS
    )


@pytest.mark.parametrize(
    "mode",
    [
        "absent",
        "partial",
        "stale",
        "limit",
        "premature_yes_write",
        "conditional_write",
        "decline_write",
        "wrong_time",
        "wrong_party",
        "wrong_status",
        "foreign_cancel",
    ],
)
def test_dialogue_failures_do_not_invent_consent_or_accept_unproven_results(
    probe, mode
):
    from app.restaurant_call import COPY

    phrases, spoken = probe.scenario("en", DAY), []

    async def speak(text):
        spoken.append(text)
        if mode == "absent" or (
            mode == "stale" and spoken.count(phrases["request"]) > 1
        ):
            return "PRIVATE no recap"
        if mode == "partial":
            return phrases["recap_marker"] + "incomplete"
        if mode == "limit":
            return COPY["en"]["party"]
        return rendered("en")

    async def read():
        item = {
            "id": 1,
            "party_size": 4,
            "start": DAY.isoformat() + "T18:00:00",
            "status": "confirmed",
        }
        if mode == "premature_yes_write" and spoken[-1] == phrases["premature_yes"]:
            return [item]
        if mode == "conditional_write" and spoken[-1] == phrases["conditional"]:
            return [item]
        if mode == "decline_write" and spoken[-1] == phrases["decline"]:
            return [item]
        if spoken[-1] == phrases["consent"]:
            if mode == "wrong_time":
                item["start"] = DAY.isoformat() + "T19:00:00"
            if mode == "wrong_party":
                item["party_size"] = 6
            if mode == "wrong_status":
                item["status"] = "cancelled"
            return [item]
        if spoken[-1] == phrases["cancel"]:
            return [{**item, "id": 2, "status": "cancelled"}]
        return []

    with pytest.raises(AssertionError, match="probe_"):
        asyncio.run(probe.exercise(speak, read, phrases, "en", DAY))
    if mode not in {"wrong_time", "wrong_party", "wrong_status", "foreign_cancel"}:
        assert NATURAL_CONSENT["en"] not in spoken
    if mode == "limit":
        assert len(spoken) == 5


def test_wait_requires_final_text_audio_and_end_of_playback(probe, monkeypatch):
    monkeypatch.setattr(probe, "REPLY_TIMEOUT", 0.01)

    async def run():
        playback = {"voiced_frames": 21, "last_audio": 0, "last_reply": 0}
        await probe.wait_reply(["complete"], playback, 0, 0)
        for replies, changes in [
            ([], {}),
            (["text only"], {"voiced_frames": 0}),
            (["partial"], {"last_audio": asyncio.get_running_loop().time()}),
        ]:
            with pytest.raises(AssertionError, match="probe_reply_incomplete"):
                await probe.wait_reply(replies, {**playback, **changes}, 0, 0)

    asyncio.run(run())


def test_optional_audio_close_and_closed_diagnostics(probe):
    asynchronous, synchronous = AsyncMock(), Mock()
    asyncio.run(probe.close_audio_source(NS(aclose=asynchronous)))
    asyncio.run(probe.close_audio_source(NS(aclose=synchronous)))
    asyncio.run(probe.close_audio_source(object()))
    asynchronous.assert_awaited_once()
    synchronous.assert_called_once()
    assert "PRIVATE" not in probe.failure_message(RuntimeError("PRIVATE"))
    assert (
        probe.failure_message(TimeoutError("PRIVATE"))
        == "FAIL restaurant native probe: probe_deadline"
    )


@pytest.fixture
def media(transport_probe, monkeypatch):
    probe = transport_probe
    rtc = pytest.importorskip("livekit.rtc")
    from livekit import api

    callbacks = {}
    room = NS(
        on=lambda name: lambda fn: callbacks.update({name: fn}) or fn,
        connect=AsyncMock(),
        disconnect=AsyncMock(),
        remote_participants={"worker": NS(attributes={"voicebot.call_id": SCOPE})},
        local_participant=NS(publish_track=AsyncMock()),
    )
    client = NS(
        room=NS(create_room=AsyncMock(), delete_room=AsyncMock()),
        agent_dispatch=NS(create_dispatch=AsyncMock()),
        aclose=AsyncMock(),
    )
    source, tts = NS(aclose=AsyncMock()), NS(close=Mock())
    monkeypatch.setattr(rtc, "Room", lambda: room)
    monkeypatch.setattr(rtc, "AudioSource", lambda *args, **kwargs: source)
    monkeypatch.setattr(
        rtc.LocalAudioTrack, "create_audio_track", lambda *args: object()
    )
    monkeypatch.setattr(api, "LiveKitAPI", lambda **kwargs: client)
    monkeypatch.setattr(
        probe, "AzureTtsClient", lambda *args, **kwargs: tts, raising=False
    )
    monkeypatch.setattr(probe, "wait_reply", AsyncMock())
    monkeypatch.setattr(probe, "exercise", AsyncMock(return_value={}))
    monkeypatch.setattr(probe, "read_owned", Mock(return_value=[]))
    read = AsyncMock(return_value=[])
    monkeypatch.setattr(probe, "read_owned_async", read, raising=False)
    env = {
        "LIVEKIT_API_KEY": "fixture",
        "LIVEKIT_API_SECRET": "fake-not-a-credential-" + "x" * 32,
        "AZURE_SPEECH_KEY": "fixture",
        "AZURE_REGION": "fixture",
    }
    return NS(
        probe=probe,
        rtc=rtc,
        room=room,
        client=client,
        source=source,
        read=read,
        callbacks=callbacks,
        env=env,
    )


@pytest.mark.parametrize("failure", ["response_error", "deadline"])
def test_ambiguous_creation_deletes_attempted_unique_room(media, failure):
    async def create(request):
        media.created_name = request.name
        if failure == "response_error":
            raise RuntimeError("PRIVATE lost response")
        await asyncio.Event().wait()

    media.client.room.create_room.side_effect = create

    async def run():
        with pytest.raises((RuntimeError, TimeoutError)):
            async with asyncio.timeout(0.02):
                await media.probe.run("fixture-worker", media.env, "en")
        media.client.room.delete_room.assert_awaited_once()
        assert (
            media.client.room.delete_room.call_args.args[0].room == media.created_name
        )
        assert media.created_name.startswith("voicebot-restaurant-probe-")
        media.client.aclose.assert_awaited_once()

    asyncio.run(run())


@pytest.mark.parametrize("stall", ["source", "audio_gather", "disconnect"])
def test_stalled_cleanup_continues_room_ledger_close_and_fails_overall(
    media, monkeypatch, stall
):
    probe = media.probe
    monkeypatch.setattr(probe, "CLEANUP_STEP_TIMEOUT", 0.01, raising=False)

    async def run():
        release = asyncio.Event()

        async def hung(*args, **kwargs):
            await release.wait()

        if stall == "source":
            media.source.aclose.side_effect = hung
        if stall == "disconnect":
            media.room.disconnect.side_effect = hung
        if stall == "audio_gather":

            class Stream:
                def __aiter__(self):
                    return self

                async def __anext__(self):
                    await asyncio.Event().wait()

                async def aclose(self):
                    await release.wait()

            monkeypatch.setattr(
                media.rtc.AudioStream, "from_track", lambda **kwargs: Stream()
            )

            async def exercise(*args):
                media.callbacks["track_subscribed"](
                    NS(kind=media.rtc.TrackKind.KIND_AUDIO),
                    None,
                    NS(identity="fixture-worker"),
                )
                await asyncio.sleep(0)
                return {}

            monkeypatch.setattr(probe, "exercise", exercise)
        task = asyncio.create_task(probe.run("fixture-worker", media.env, "en"))
        try:
            done, _ = await asyncio.wait({task}, timeout=0.15)
            assert task in done, "one stalled cleanup step blocked independent cleanup"
            with pytest.raises(RuntimeError, match="probe_cleanup_failed"):
                task.result()
            media.client.room.delete_room.assert_awaited_once()
            media.read.assert_awaited_once_with("fixture-worker", SCOPE, cleanup=True)
            media.client.aclose.assert_awaited_once()
        finally:
            release.set()
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    asyncio.run(run())


def test_deadline_with_stalled_source_still_cleans_room_and_owned_scope(
    media, monkeypatch
):
    probe = media.probe
    monkeypatch.setattr(probe, "CONVERSATION_TIMEOUT", 0.01, raising=False)
    monkeypatch.setattr(probe, "CLEANUP_STEP_TIMEOUT", 0.01, raising=False)

    async def run():
        release = asyncio.Event()

        async def hung(*args):
            await release.wait()

        monkeypatch.setattr(probe, "exercise", hung)
        media.source.aclose.side_effect = hung
        task = asyncio.create_task(probe.run("fixture-worker", media.env, "ru"))
        try:
            done, _ = await asyncio.wait({task}, timeout=0.15)
            assert task in done, "conversation deadline never reached cleanup"
            with pytest.raises((RuntimeError, TimeoutError)):
                task.result()
            media.client.room.delete_room.assert_awaited_once()
            media.read.assert_awaited_once_with("fixture-worker", SCOPE, cleanup=True)
        finally:
            release.set()
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    asyncio.run(run())


@pytest.mark.parametrize("failure", ["timeout", "cancel", "exit"])
def test_caller_process_is_killable_and_never_exposes_keys_or_private_output(
    transport_probe, monkeypatch, failure
):
    probe = transport_probe
    assert hasattr(probe, "caller_audio"), (
        "caller TTS lacks a killable process boundary"
    )
    monkeypatch.setattr(probe, "CALLER_TTS_TIMEOUT", 0.01)
    monkeypatch.setattr(probe, "PROCESS_STOP_TIMEOUT", 0.01)
    monkeypatch.setattr(
        probe.asyncio,
        "to_thread",
        Mock(side_effect=AssertionError("executor forbidden")),
    )

    async def run():
        started, stopped = asyncio.Event(), asyncio.Event()
        process = NS(returncode=None)

        async def communicate(data):
            process.input = data
            started.set()
            if failure == "exit":
                process.returncode = 9
                return b"PRIVATE body", b"PRIVATE error"
            await asyncio.Event().wait()

        async def wait():
            await stopped.wait()
            return process.returncode

        def kill():
            process.returncode = -9
            stopped.set()

        process.communicate, process.wait = communicate, AsyncMock(side_effect=wait)
        process.terminate, process.kill = Mock(), Mock(side_effect=kill)
        launch = AsyncMock(return_value=process)
        monkeypatch.setattr(probe.asyncio, "create_subprocess_exec", launch)
        env = {
            "AZURE_SPEECH_KEY": "private-fixture-" + "x" * 32,
            "AZURE_REGION": "fixture",
        }
        phrases = probe.scenario("en", DAY)
        task = asyncio.create_task(probe.caller_audio(env, phrases, phrases["request"]))
        if failure == "cancel":
            await started.wait()
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        else:
            with pytest.raises(RuntimeError, match="probe_caller_tts_failed") as error:
                await task
            assert "PRIVATE" not in str(error.value)
        command = launch.call_args
        assert env["AZURE_SPEECH_KEY"] not in repr(command.args)
        assert phrases["request"] not in repr(command.args)
        assert command.kwargs["env"]["AZURE_SPEECH_KEY"] == env["AZURE_SPEECH_KEY"]
        assert (
            command.kwargs["stdout"]
            == command.kwargs["stderr"]
            == asyncio.subprocess.PIPE
        )
        assert json.loads(process.input) == {
            "voice": phrases["voice"],
            "locale": phrases["locale"],
            "text": phrases["request"],
        }
        if failure != "exit":
            process.terminate.assert_called_once()
            process.kill.assert_called_once()
            assert process.wait.await_count == 2

    asyncio.run(run())


def test_cli_never_prints_pass_on_cleanup_failure_and_reserves_total_budget(
    transport_probe, monkeypatch, capsys
):
    probe = transport_probe
    assert hasattr(probe, "worker_credentials"), (
        "credentials still use unbounded executor"
    )
    monkeypatch.setattr(probe, "worker_credentials", AsyncMock(return_value={}))
    monkeypatch.setattr(
        probe, "run", AsyncMock(side_effect=RuntimeError("probe_cleanup_failed"))
    )
    monkeypatch.setattr(
        probe.asyncio,
        "to_thread",
        Mock(side_effect=AssertionError("executor forbidden")),
    )
    with pytest.raises(RuntimeError, match="probe_cleanup_failed"):
        asyncio.run(probe.main("fixture-worker", "en"))
    assert "pass" not in capsys.readouterr().out
    assert (
        probe.CONVERSATION_TIMEOUT
        + 6 * (probe.CLEANUP_STEP_TIMEOUT + 2 * probe.PROCESS_STOP_TIMEOUT)
        + probe.CREDENTIAL_TIMEOUT
        + 2 * probe.PROCESS_STOP_TIMEOUT
        <= 300
    )
    assert (
        probe.failure_message(RuntimeError("probe_cleanup_failed"))
        == "FAIL restaurant native probe: probe_cleanup_failed"
    )


def test_copy_detection_does_not_assume_name_is_first(transport_probe):
    probe = transport_probe
    probe.COPY["et"]["recap"] = (
        "Fixture {date} at {time}, {party} at {name}. {question}!"
    )
    phrases = probe.scenario("et", DAY)
    text = probe.COPY["et"]["recap"].format(
        date=DAY.isoformat(),
        time="18:00",
        party=4,
        name="Fixture",
        question=probe.COPY["et"]["confirmation_question"],
    )
    assert phrases["recap_marker"] == "Fixture "
    assert probe.complete_recap(text, "et")
    assert not probe.complete_recap(text[:-1], "et")


def test_caller_returns_only_wav_bytes_without_executor(transport_probe, monkeypatch):
    probe = transport_probe
    assert hasattr(probe, "caller_audio"), "caller audio lacks bounded process"
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setparams((1, 2, 24000, 0, "NONE", "not compressed"))
        wav.writeframes(bytes(960))
    audio = buffer.getvalue()
    process = NS(
        returncode=0,
        communicate=AsyncMock(return_value=(audio, b"PRIVATE")),
        terminate=Mock(),
        kill=Mock(),
        wait=AsyncMock(return_value=0),
    )
    monkeypatch.setattr(
        probe.asyncio, "create_subprocess_exec", AsyncMock(return_value=process)
    )
    monkeypatch.setattr(
        probe.asyncio,
        "to_thread",
        Mock(side_effect=AssertionError("executor forbidden")),
    )
    phrases = probe.scenario("en", DAY)
    result = asyncio.run(
        probe.caller_audio(
            {"AZURE_SPEECH_KEY": "fixture", "AZURE_REGION": "fixture"},
            phrases,
            phrases["request"],
        )
    )
    assert result == audio
    process.terminate.assert_not_called()
    process.kill.assert_not_called()
