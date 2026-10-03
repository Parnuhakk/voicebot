"""Restaurant web controls; authorization and shared consent precede writes."""

from __future__ import annotations

import copy
import time

from fastapi import Header, HTTPException, Request

from .booking_web import _body, _fields, _remember_booking, _result
from .dashboard.api import _require_operator
from .hackathon import operator_scope, read_session_language
from .languages import CONSENT
from .restaurant_answers import format_schedule
from .restaurant_family import family_reply
from .restaurant_reasoning import reasoning_enabled
from .restaurant_times import TIME_INPUT_EXAMPLES

CANCEL = {"et": "Jah, tühista.", "en": "Yes, cancel.", "ru": "Да, отмените."}


def add_restaurant_routes(app, sessions):
    def proposal_result(session, result):
        if not isinstance(result, dict) or result.get("ok") is not True:
            return _result(result)
        pending = session.tools.pending
        recap = session.tools.render_recap()
        if not pending or not recap:
            return _result({"error": "hold_expired_or_unknown"})
        return _result({
            **result,
            "recap_text": recap,
            "recap_expires_in_s": max(
                0.0, min(pending["expires_at"], session.expires_at) - time.monotonic()
            ),
            "kind": "slot",
            "business_type": "restaurant",
        })

    @app.get("/api/public/restaurant")
    @app.get("/api/public/property")
    async def restaurant_information():
        data = copy.deepcopy(app.state.stack["restaurant_data"])
        return {
            "synthetic": True,
            "business_type": "restaurant",
            "restaurant": data,
            "supported_languages": ["et", "en", "ru"],
            "family_facilities_summary": {
                language: family_reply(data, language) for language in ("et", "en", "ru")
            },
            "booking_time_examples": copy.deepcopy(TIME_INPUT_EXAMPLES),
            "opening_hours_summary": {
                language: format_schedule(data, language) + "."
                for language in ("et", "en", "ru")
            },
            "kitchen_hours_summary": {
                language: format_schedule(data, language, kitchen=True) + "."
                for language in ("et", "en", "ru")
            },
            "table_booking_ready": app.state.capabilities["slot_booking_ready"],
            "answer_policy_version": "grounded-restaurant-v1",
            "booking_interruption_version": "resume-booking-v1",
            "grounded_answers_ready": reasoning_enabled(app.state.stack["llm_primary"]),
            "booking_access": "operator_demo",
            "allergy_safety_verified": False,
        }

    @app.get("/api/public/catalogue")
    async def menu():
        data = app.state.stack["restaurant_data"]
        return {
            "synthetic": True,
            "business_type": "restaurant",
            "menu": copy.deepcopy(data["menu"]),
        }

    @app.post("/api/booking/session")
    async def start(request: Request, authorization: str | None = Header(default=None)):
        _require_operator(authorization)
        language = await read_session_language(request)
        return sessions.create(
            app.state.stack["dispatcher"],
            operator_scope(authorization),
            language=language,
        )

    async def owned(request, authorization):
        _require_operator(authorization)
        body = await _body(request)
        return body, sessions.acquire(
            body.get("session_id"), operator_scope(authorization)
        )

    @app.post("/api/restaurant/reservation/prepare")
    async def prepare(
        request: Request, authorization: str | None = Header(default=None)
    ):
        body, session = await owned(request, authorization)
        try:
            _fields(
                body,
                {"session_id", "date", "start_time", "party_size", "guest_fixture_id"},
                {"date", "start_time", "party_size"},
            )
            session.tools.observe_user_text(
                "Prepare this restaurant table reservation.",
                language=session.tools.language,
            )
            result = await session.tools.dispatch(
                "plan_restaurant_reservation",
                {
                    key: body[key]
                    for key in ("date", "start_time", "party_size", "guest_fixture_id")
                    if key in body
                },
            )
            return proposal_result(session, result)
        finally:
            sessions.release(session)

    @app.post("/api/restaurant/reservation/renew")
    async def renew(
        request: Request, authorization: str | None = Header(default=None)
    ):
        body, session = await owned(request, authorization)
        try:
            _fields(body, {"session_id", "hold_id"}, {"hold_id"})
            hold_id = body["hold_id"]
            pending = session.tools.pending
            if (
                not isinstance(hold_id, str)
                or hold_id not in session.tools.held_slots
                or hold_id in session.tools.confirmed_holds
                or session.tools.mutation_uncertain
                or not pending
                or pending.get("hold_id") != hold_id
            ):
                raise HTTPException(409, "booking_proposal_unavailable")
            guest = pending["guest_fixture_id"]
            session.tools.observe_user_text(
                "Prepare this restaurant table reservation.",
                language=session.tools.language,
            )
            result = await session.tools.dispatch(
                "prepare_demo_booking",
                {"hold_id": hold_id, "guest_fixture_id": guest},
            )
            return proposal_result(session, result)
        finally:
            sessions.release(session)

    @app.post("/api/booking/recap")
    async def recap(request: Request, authorization: str | None = Header(default=None)):
        body, session = await owned(request, authorization)
        try:
            _fields(body, {"session_id", "hold_id"}, {"hold_id"})
            if not session.tools.mark_recap_delivered(body["hold_id"]):
                raise HTTPException(409, "booking_recap_expired_or_unknown")
            return {"acknowledged": True, "hold_id": body["hold_id"]}
        finally:
            sessions.release(session)

    async def mutate(request, authorization, *, cancel=False):
        body, session = await owned(request, authorization)
        try:
            identifier = "booking_id" if cancel else "hold_id"
            _fields(
                body, {"session_id", identifier, "consent"}, {identifier, "consent"}
            )
            if body["consent"] is not True:
                raise HTTPException(400, "explicit_consent_required")
            language = session.tools.language
            session.tools.observe_user_text(
                CANCEL[language] if cancel else CONSENT[language], language=language
            )
            if cancel and not session.tools.authorize_cancellation(body[identifier]):
                raise HTTPException(
                    409, "booking_not_owned_or_cancellation_unavailable"
                )
            result = await session.tools.dispatch(
                "cancel_slot_booking" if cancel else "confirm_slot_booking",
                {identifier: body[identifier]},
            )
            if (
                isinstance(result, dict)
                and result.get("ok") is True
                and not result.get("error")
            ):
                _remember_booking(session, body, result, "slot", cancel)
            return _result(result)
        finally:
            sessions.release(session)

    @app.post("/api/booking/confirm")
    async def confirm(
        request: Request, authorization: str | None = Header(default=None)
    ):
        return await mutate(request, authorization)

    @app.post("/api/booking/cancel")
    async def cancel(
        request: Request, authorization: str | None = Header(default=None)
    ):
        return await mutate(request, authorization, cancel=True)
