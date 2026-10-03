"""Restaurant corrections and recap recovery against isolated SQLite inventory."""

import asyncio
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from app import restaurant_call
from app.booking.restaurant import RestaurantAdapter
from app.booking_response import trusted_booking_response
from app.business import restaurant_dispatcher
from app.call_factory import make_call_tools
from app.languages import CONSENT
from app.restaurant_call import COPY, parse_restaurant_request
from app.restaurant_data import load_restaurant_data

NOW = datetime(2026, 10, 3, 12, tzinfo=ZoneInfo("Europe/Tallinn"))
DAY = "2026-10-04"
REQUESTS = {
    "et": "Soovin homme lauda kuuele kell 14.00",
    "en": "A table tomorrow at 14:00 for six",
    "ru": "Столик завтра в 14:00 на шестерых",
}


@pytest.fixture
def make_state(tmp_path, monkeypatch):
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz) if tz else NOW.replace(tzinfo=None)

    monkeypatch.setattr(restaurant_call, "datetime", FixedDatetime)
    data = load_restaurant_data()
    adapter = RestaurantAdapter(
        str(tmp_path / "restaurant.db"),
        data=data,
        allow_writes=True,
        now=lambda: NOW,
    )

    def create(language="en"):
        return make_call_tools(restaurant_dispatcher(adapter, data), language=language)

    return create


async def plan_turn(state, text):
    state.observe_user_text(text, language=state.language)
    response = trusted_booking_response(state)
    assert response["name"] == "plan_restaurant_reservation", response
    result = await state.dispatch(response["name"], response["arguments"])
    reply = trusted_booking_response(state, after_tool=True)
    assert reply == {"content": state.guard_reply("", state.results)}
    return result


def inventory(adapter):
    with sqlite3.connect(adapter.state_db) as connection:
        holds = {
            row[0] for row in connection.execute("SELECT id FROM restaurant_holds")
        }
        bookings = connection.execute(
            "SELECT status FROM restaurant_reservations ORDER BY id"
        ).fetchall()
        actions = connection.execute(
            "SELECT COUNT(*) FROM restaurant_actions"
        ).fetchone()[0]
    return holds, bookings, actions


@pytest.mark.parametrize(
    "language,initial,correction",
    [
        ("en", "A table Monday", "Actually Friday at 19:00 for four"),
        ("et", "Laud esmaspäeval", "Hoopis reedel kell 19:00 neljale"),
        ("ru", "Столик в понедельник", "Лучше в пятницу в 19:00 на четверых"),
    ],
)
def test_weekday_correction_before_hold_updates_trusted_plan(
    make_state, language, initial, correction
):
    state = make_state(language)
    state.observe_user_text(initial, language=language)
    assert state.booking_inquiry["date"] == "2026-10-05"
    state.observe_user_text(correction, language=language)
    assert trusted_booking_response(state) == {
        "name": "plan_restaurant_reservation",
        "arguments": {
            "date": "2026-10-09",
            "start_time": "19:00",
            "party_size": 4,
        },
    }
    assert state.holds == set()


@pytest.mark.parametrize(
    "correction,expected",
    [
        ("Actually at 19:00 for four", "2026-10-05"),
        ("Actually tomorrow Friday at 19:00 for four", DAY),
        ("Actually day after tomorrow Friday at 19:00 for four", "2026-10-05"),
        ("Actually today Friday at 19:00 for four", "2026-10-03"),
        ("Actually Friday on 2026-10-12 at 19:00 for four", "2026-10-12"),
        ("Actually tomorrow on 2026-10-12 at 19:00 for four", "2026-10-12"),
        ("Actually Friday on 12.10.2026 at 19:00 for four", "2026-10-12"),
    ],
)
def test_date_correction_preserves_current_relative_and_explicit_precedence(
    correction, expected
):
    previous = {"date": "2026-10-05", "start_time": "14:00", "party_size": 6}
    assert parse_restaurant_request(correction, previous, now=NOW) == {
        "date": expected,
        "start_time": "19:00",
        "party_size": 4,
    }
    assert previous == {"date": "2026-10-05", "start_time": "14:00", "party_size": 6}


@pytest.mark.parametrize(
    "language,correction",
    [
        ("en", "Friday or Saturday at 19:00 for four"),
        ("et", "Reedel või laupäeval kell 19:00 neljale"),
        ("ru", "В пятницу или субботу в 19:00 на четверых"),
    ],
)
def test_ambiguous_weekday_correction_asks_date_instead_of_retaining_or_guessing(
    make_state, language, correction
):
    state = make_state(language)
    state.observe_user_text("A table Monday", language=language)
    state.observe_user_text(correction, language=language)
    assert state.booking_inquiry == {"start_time": "19:00", "party_size": 4}
    assert trusted_booking_response(state) == {"content": COPY[language]["date"]}
    assert state.pending is None


@pytest.mark.parametrize(
    "language,ambiguous", [("et", "jah"), ("en", "yes"), ("ru", "да")]
)
def test_ambiguous_consent_reprepares_same_live_owned_hold_without_auto_write(
    make_state, language, ambiguous
):
    async def run():
        state = make_state(language)
        first = await plan_turn(state, REQUESTS[language])
        assert first.get("ok"), first
        original = state.pending
        assert state.mark_recap_delivered(first["hold_id"])
        before = inventory(state.dispatcher._slot)
        assert before == ({first["hold_id"]}, [], 0)
        for _ in range(3):
            recovered = await plan_turn(state, ambiguous)
            assert recovered.get("ok"), recovered
            assert recovered["hold_id"] == first["hold_id"]
            assert recovered["recap"] == first["recap"]
            assert state.pending is not original
            assert state.pending["delivery"] is False
            assert state.pending["approved"] is False
            assert state.bookings == set()
            assert inventory(state.dispatcher._slot) == before
            original = state.pending
            assert state.mark_recap_delivered(first["hold_id"])

    asyncio.run(run())


def test_recovered_hold_requires_fresh_delivery_and_later_exact_consent(make_state):
    async def run():
        state = make_state()
        first = await plan_turn(state, REQUESTS["en"])
        assert first.get("ok"), first
        assert state.mark_recap_delivered(first["hold_id"])
        recovered = await plan_turn(state, "yes")
        assert recovered.get("ok"), recovered
        state.observe_user_text(CONSENT["en"], language="en")
        response = trusted_booking_response(state)
        assert response["name"] == "plan_restaurant_reservation"
        assert inventory(state.dispatcher._slot) == ({first["hold_id"]}, [], 0)
        prepared = await state.dispatch(response["name"], response["arguments"])
        assert prepared["hold_id"] == first["hold_id"]
        assert state.mark_recap_delivered(prepared["hold_id"])
        state.observe_user_text(CONSENT["en"], language="en")
        response = trusted_booking_response(state)
        assert response == {
            "name": "confirm_slot_booking",
            "arguments": {"hold_id": first["hold_id"]},
        }
        confirmed = await state.dispatch(response["name"], response["arguments"])
        assert confirmed.get("ok"), confirmed
        assert inventory(state.dispatcher._slot) == (set(), [("confirmed",)], 1)

    asyncio.run(run())


@pytest.mark.parametrize(
    "invalidated", ["expired", "released", "cancelled", "confirmed"]
)
def test_recovery_rechecks_durable_hold_instead_of_replaying_local_snapshot(
    make_state, invalidated
):
    async def run():
        state = make_state()
        first = await plan_turn(state, REQUESTS["en"])
        assert first.get("ok"), first
        assert state.mark_recap_delivered(first["hold_id"])
        adapter = state.dispatcher._slot
        if invalidated == "expired":
            adapter._now = lambda: NOW + timedelta(seconds=121)
        elif invalidated == "released":
            with sqlite3.connect(adapter.state_db) as connection:
                connection.execute(
                    "DELETE FROM restaurant_holds WHERE id=?", (first["hold_id"],)
                )
        else:
            other = RestaurantAdapter(
                adapter.state_db, allow_writes=True, now=lambda: NOW
            )
            confirmed = await other.confirm(
                first["hold_id"], first["guest"], "other-confirm"
            )
            assert confirmed.get("ok"), confirmed
            if invalidated == "cancelled":
                cancelled = await other.cancel(
                    str(confirmed["booking"]["id"]), "other-cancel"
                )
                assert cancelled.get("ok"), cancelled
        assert first["hold_id"] in state.held_slots
        assert first["hold_id"] not in state.confirmed_holds
        assert await adapter.get_hold(first["hold_id"]) is None
        recovered = await plan_turn(state, "yes")
        if invalidated == "confirmed":
            assert recovered.get("restaurant_unavailable"), recovered
            assert state.pending is None
        else:
            assert recovered.get("ok"), recovered
            assert recovered["hold_id"] != first["hold_id"]
            assert state.pending["delivery"] is False
            assert state.pending["approved"] is False
        assert state.bookings == set()

    asyncio.run(run())


def test_recovery_revalidates_current_restaurant_rules(make_state):
    async def run():
        state = make_state()
        first = await plan_turn(state, REQUESTS["en"])
        assert first.get("ok"), first
        assert state.mark_recap_delivered(first["hold_id"])
        adapter = state.dispatcher._slot
        adapter.data["closures"][DAY] = {
            language: "Closed fixture" for language in ("et", "en", "ru")
        }
        recovered = await plan_turn(state, "yes")
        assert not recovered.get("ok"), recovered
        assert state.pending is None
        assert state.render_recap() is None
        assert inventory(adapter) == ({first["hold_id"]}, [], 0)

    asyncio.run(run())


@pytest.mark.parametrize(
    "correction,date,start_time,party_size",
    [
        ("Actually on 2026-10-05", "2026-10-05", "14:00", 6),
        ("Actually at 17:00", DAY, "17:00", 6),
        ("Actually for four", DAY, "14:00", 4),
    ],
)
def test_changed_request_does_not_reuse_previous_hold(
    make_state, correction, date, start_time, party_size
):
    async def run():
        state = make_state()
        first = await plan_turn(state, REQUESTS["en"])
        assert first.get("ok"), first
        assert state.mark_recap_delivered(first["hold_id"])
        changed = await plan_turn(state, correction)
        assert changed.get("ok"), changed
        assert changed["hold_id"] != first["hold_id"]
        assert changed["recap"]["date"] == date
        assert changed["recap"]["start"][11:16] == start_time
        assert changed["recap"]["party_size"] == party_size
        assert inventory(state.dispatcher._slot) == (
            {first["hold_id"], changed["hold_id"]},
            [],
            0,
        )

    asyncio.run(run())


@pytest.mark.parametrize(
    "language,question",
    [
        ("et", "Mis on lõhe hind?"),
        ("et", "Millised on menüü hinnad?"),
        ("en", "What is the price of salmon?"),
        ("en", "What are the menu prices?"),
        ("ru", "Какая цена лосося?"),
        ("ru", "Какие цены в меню?"),
    ],
)
def test_dish_and_menu_price_questions_use_exact_unknown_price_copy(
    make_state, language, question
):
    state = make_state(language)
    state.observe_user_text(question, language=language)
    assert trusted_booking_response(state) == {"content": COPY[language]["price"]}
    assert (
        state.guard_reply("Invented menu price: 20 EUR", []) == COPY[language]["price"]
    )
    assert inventory(state.dispatcher._slot) == (set(), [], 0)


@pytest.mark.parametrize(
    "language,question",
    [
        ("et", "Mul on raske allergia. Mis on lõhe hind?"),
        ("en", "I have a severe allergy. What is the price of salmon?"),
        ("ru", "У меня сильная аллергия. Какая цена лосося?"),
    ],
)
def test_serious_allergy_guidance_still_precedes_price(make_state, language, question):
    state = make_state(language)
    state.observe_user_text(question, language=language)
    response = trusted_booking_response(state)
    assert response == {"content": state.information_reply("allergens")}
    assert state.restaurant["allergy_notice"][language] in response["content"]
    assert inventory(state.dispatcher._slot) == (set(), [], 0)


@pytest.mark.parametrize(
    "language,cancellation,expected",
    [
        (
            "et",
            "Jah, tühista.",
            "Toimingu tulemus jäi ebaselgeks. Ära korda seda; kontrolli saidilt või küsi töötajalt.",
        ),
        (
            "en",
            "Yes, cancel.",
            "The action result is uncertain. Don't repeat it; check the website or ask staff.",
        ),
        (
            "ru",
            "Да, отмените.",
            "Результат действия неизвестен. Не повторяйте его; проверьте на сайте или спросите сотрудника.",
        ),
    ],
)
def test_committed_cancellation_lost_result_uses_neutral_sticky_uncertainty(
    make_state, language, cancellation, expected
):
    from app.providers.errors import ProviderError

    async def run():
        state = make_state(language)
        prepared = await plan_turn(state, REQUESTS[language])
        assert prepared.get("ok"), prepared
        assert state.mark_recap_delivered(prepared["hold_id"])
        state.observe_user_text(CONSENT[language], language=language)
        response = trusted_booking_response(state)
        assert response == {
            "name": "confirm_slot_booking",
            "arguments": {"hold_id": prepared["hold_id"]},
        }
        confirmed = await state.dispatch(response["name"], response["arguments"])
        assert confirmed.get("ok"), confirmed
        identifier = str(confirmed["booking"]["id"])
        assert trusted_booking_response(state, after_tool=True) == {
            "content": COPY[language]["confirmed"]
        }
        original = state.dispatcher.dispatch
        committed_cancellations = []

        async def lost_result(name, arguments):
            result = await original(name, arguments)
            if name == "cancel_slot_booking":
                committed_cancellations.append(result)
                raise ProviderError(
                    "Cancellation response lost", reason="transport_error"
                )
            return result

        state.dispatcher.dispatch = lost_result
        state.observe_user_text(cancellation, language=language)
        response = trusted_booking_response(state)
        assert response == {
            "name": "cancel_slot_booking",
            "arguments": {"booking_id": identifier},
        }
        result = await state.dispatch(response["name"], response["arguments"])
        assert result == {"error": "cancel_outcome_unknown"}
        assert committed_cancellations == [
            {"ok": True, "booking_id": identifier, "status": "cancelled"}
        ]
        assert inventory(state.dispatcher._slot) == (set(), [("cancelled",)], 2)
        assert state.mutation_uncertain is True
        assert state.outcome == "write_outcome_unknown"
        first_reply = trusted_booking_response(state, after_tool=True)

        state.observe_user_text(cancellation, language=language)
        assert state.mutation_uncertain is True
        assert await state.dispatch(
            "cancel_slot_booking", {"booking_id": identifier}
        ) == {"error": "cancel_outcome_unknown"}
        assert len(committed_cancellations) == 1
        assert inventory(state.dispatcher._slot) == (set(), [("cancelled",)], 2)
        assert state.pending is None and state.cancel_approval is None
        assert first_reply == {"content": expected}
        assert trusted_booking_response(state) == {"content": expected}
        assert state.guard_reply(COPY[language]["confirmed"], [confirmed]) == expected
        assert COPY[language]["unknown"] == expected

    asyncio.run(run())
