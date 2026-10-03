"""Missing adapter and RTC state must fail before an external write or audio call."""

import asyncio
from types import SimpleNamespace

import pytest

from app.booking_response import trusted_booking_response
from app.booking_web import _read_adapter
from app.dashboard import demo
from app.providers.errors import ProviderError
from tests.test_adversarial_adapter import Backend, DAY, GUEST, adapter


@pytest.mark.parametrize("operation", ["confirm", "cancel"])
@pytest.mark.parametrize("missing", ["_journal", "_lock_path"])
def test_missing_write_state_never_contacts_the_provider(tmp_path, operation, missing):
    async def run():
        backend = Backend()
        api = adapter(backend, tmp_path / "journal.db")
        setattr(api, missing, None)
        try:
            with pytest.raises(ProviderError):
                if operation == "confirm":
                    await api.confirm("hold-not-sent", GUEST, "missing-state")
                else:
                    await api.cancel("42", "missing-state")
            assert backend.calls == []
        finally:
            await api._http.aclose()

    asyncio.run(run())


def test_missing_pending_record_blocks_a_new_write(tmp_path, monkeypatch):
    async def run():
        backend = Backend()
        api = adapter(backend, tmp_path / "journal.db")
        try:
            slots = await api.search_slots("6", DAY, "2")
            hold = await api.create_hold(slots[0]["slotId"])
            monkeypatch.setattr(api._journal, "pending_appointments", lambda key: [("missing", "opaque")])
            result = await api.confirm(hold.hold_id, GUEST, "new-attempt")
            assert result == {"ok": False, "error": "write_outcome_unknown"}
            assert backend.posts == backend.customers == 0
        finally:
            await api._http.aclose()

    asyncio.run(run())


def test_adapter_read_rejects_a_synchronous_result():
    with pytest.raises(TypeError, match="must be asynchronous"):
        asyncio.run(_read_adapter(lambda: {"synthetic": True}))


def test_invalid_trusted_response_cannot_fall_through_to_another_action():
    state = SimpleNamespace(
        mutation_uncertain=False,
        trusted_restaurant_response=lambda **kwargs: object(),
    )
    with pytest.raises(ValueError, match="invalid trusted restaurant response"):
        trusted_booking_response(state)


def test_demo_reset_preserves_the_store_reference():
    original = demo.STORE
    original["quality-check"] = True
    demo.reset()
    assert demo.STORE is original
    assert "quality-check" not in original
    assert original["holds"]


def test_missing_native_track_fails_before_subscribing():
    pytest.importorskip("livekit.rtc")
    from app.twilio_bridge import LiveKitCall
    from app.twilio_security import BridgeError

    call = LiveKitCall(None, None)
    with pytest.raises(BridgeError) as caught:
        call._subscribe_audio()
    assert caught.value.code == "output_invalid"
    assert call.stream is call.output is None


def test_missing_native_source_fails_before_feeding_audio():
    pytest.importorskip("livekit.rtc")
    from app.twilio_bridge import LiveKitCall
    from app.twilio_security import BridgeError

    async def run():
        call = LiveKitCall(None, None)
        with pytest.raises(BridgeError) as caught:
            await call.feed(b"\0" * 320)
        assert caught.value.code == "bridge_unavailable"
        assert call.source is None

    asyncio.run(run())


def test_missing_output_stream_finishes_the_call_with_a_closed_failure():
    pytest.importorskip("livekit.rtc")
    from app.twilio_bridge import LiveKitCall

    async def run():
        call = LiveKitCall(None, None)
        await call._output()
        assert call.failed and call.ended.is_set()

    asyncio.run(run())
