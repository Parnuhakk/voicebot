"""Calendar grammar and the complete shared booking path, without live providers."""

import asyncio
from datetime import datetime
import json
from unittest.mock import patch

import pytest

from app.booking.tools import Dispatcher
from app.languages import CONSENT, select_language
from app.telephone import CallTools, TEMPORAL_QUESTIONS
from app.temporal import ET_DAYS, ET_MONTHS, EN_DAYS, RU_DAYS, RU_MONTHS, TALLINN, interpret_temporal
from tests.test_demo_plan import LiveSlots
from tests.test_product_demo import client, send, start


NOW = datetime(2026, 10, 3, 12, 15, tzinfo=TALLINN)


class Clock(datetime):
    @classmethod
    def now(cls, tz=None):
        return NOW.astimezone(tz)


@pytest.mark.parametrize("form", [
    "kuues", "kuuenda", "kuuendat", "kuuendasse", "kuuendas", "kuuendast",
    "kuuendale", "kuuendal", "kuuendalt", "kuuendaks", "kuuendani", "kuuendana", "kuuendata", "kuuendaga",
])
def test_estonian_day_in_all_fourteen_cases(form):
    parsed = interpret_temporal(form + " oktoobril 2027", "et", NOW)
    assert parsed.dates == [{"status": "resolved", "date": "2027-10-06"}]
    assert parsed.is_answer and parsed.issue is None


@pytest.mark.parametrize("form,month", list(ET_MONTHS.items()))
def test_every_estonian_month_case_reaches_the_exact_calendar_month(form, month):
    parsed = interpret_temporal("6. " + form + " 2027", "et", NOW)
    assert parsed.dates == [{"status": "resolved", "date": f"2027-{month:02d}-06"}]
    assert parsed.issue is None


@pytest.mark.parametrize("language,forms", [("et", ET_DAYS), ("en", EN_DAYS), ("ru", RU_DAYS)])
def test_all_days_one_to_thirty_one_and_spoken_declensions(language, forms):
    month = {"et": "oktoobril", "en": "October", "ru": "октября"}[language]
    for form, day in forms.items():
        parsed = interpret_temporal(f"{form} {month} 2027", language, NOW)
        assert parsed.dates == [{"status": "resolved", "date": f"2027-10-{day:02d}"}], form
        assert parsed.is_answer and parsed.issue is None, form


@pytest.mark.parametrize("form,month", list(RU_MONTHS.items()))
def test_russian_month_cases_are_calendar_months(form, month):
    parsed = interpret_temporal(f"шестого {form} 2027", "ru", NOW)
    assert parsed.dates == [{"status": "resolved", "date": f"2027-{month:02d}-06"}]


@pytest.mark.parametrize("language,text,day", [
    ("et", "homseks", "2026-10-04"), ("et", "homsel päeval", "2026-10-04"),
    ("et", "ülehomseks", "2026-10-05"), ("et", "kahe päeva pärast", "2026-10-05"),
    ("et", "kahe nädala pärast", "2026-10-17"), ("et", "kuu aja pärast", "2026-11-03"),
    ("et", "teisipäevaks", "2026-10-06"), ("et", "6-ndal oktoobril", "2026-10-06"),
    ("et", "kahekümne kuuendaks oktoobriks", "2026-10-26"),
    ("et", "kuuendal oktoobril kahe tuhande kahekümne seitsmendal aastal", "2027-10-06"),
    ("en", "the day after tomorrow", "2026-10-05"), ("en", "in two weeks", "2026-10-17"),
    ("en", "in a month", "2026-11-03"), ("en", "October the twenty-sixth", "2026-10-26"),
    ("en", "the sixth of October two thousand twenty seven", "2027-10-06"),
    ("en", "October sixth twenty twenty seven", "2027-10-06"),
    ("en", "13/04/2027", "2027-04-13"), ("en", "04/13/2027", "2027-04-13"),
    ("et", "06-10-2027", "2027-10-06"), ("ru", "06-10-2027", "2027-10-06"),
    ("ru", "послезавтра", "2026-10-05"), ("ru", "через две недели", "2026-10-17"),
    ("ru", "через неделю", "2026-10-10"), ("ru", "к шестому октября", "2026-10-06"),
    ("ru", "на шестое октября", "2026-10-06"), ("ru", "во вторник", "2026-10-06"),
    ("ru", "6-го октября", "2026-10-06"), ("ru", "двадцать шестого октября", "2026-10-26"),
    ("ru", "шестого октября две тысячи двадцать седьмого года", "2027-10-06"),
])
def test_relative_dates_weekdays_ordinals_numeric_formats_and_spoken_years(language, text, day):
    parsed = interpret_temporal(text, language, NOW)
    assert parsed.dates == [{"status": "resolved", "date": day}]
    assert parsed.is_answer and parsed.issue is None


@pytest.mark.parametrize("language,text,time", [
    ("et", "kell pool kuus", "05:30"), ("et", "poole kuueks õhtul", "17:30"),
    ("et", "veerand kuus", "05:15"), ("et", "kolmveerand kuus õhtul", "17:45"),
    ("et", "kella kuueks", "06:00"), ("et", "õhtul kell kuus", "18:00"),
    ("et", "kella 18:30-ks", "18:30"), ("et", "kella 18.30ks", "18:30"),
    ("et", "kell kakskümmend üks", "21:00"), ("et", "kell kakskümmendüks", "21:00"),
    ("et", "kella kahekümne üheks", "21:00"),
    ("et", "kell kuus kolmkümmend", "06:30"), ("et", "viis minutit enne kuut", "05:55"),
    ("et", "keskööl", "00:00"), ("et", "keskpäevaks", "12:00"),
    ("en", "at half past six pm", "18:30"), ("en", "at quarter past six pm", "18:15"),
    ("en", "at quarter to six pm", "17:45"), ("en", "at quarter to twelve pm", "11:45"),
    ("en", "at quarter to twelve am", "23:45"), ("en", "at six thirty pm", "18:30"),
    ("en", "at ten minutes to six pm", "17:50"), ("en", "at noon", "12:00"),
    ("en", "at midnight", "00:00"), ("en", "6 a. m.", "06:00"),
    ("ru", "в половине седьмого вечера", "18:30"), ("ru", "к половине седьмого вечера", "18:30"),
    ("ru", "в полседьмого вечера", "18:30"), ("ru", "в четверть седьмого вечера", "18:15"),
    ("ru", "без четверти шесть вечера", "17:45"), ("ru", "без десяти шесть вечера", "17:50"),
    ("ru", "в пять минут седьмого вечера", "18:05"),
    ("ru", "в шесть часов тридцать минут вечера", "18:30"),
    ("ru", "к шести вечера", "18:00"), ("ru", "в полдень", "12:00"),
    ("ru", "к двум дня", "14:00"), ("ru", "к двадцати одному", "21:00"),
])
def test_exact_clocks_colloquial_fractions_and_case_endings(language, text, time):
    parsed = interpret_temporal(text, language, NOW, expected="time")
    assert parsed.times == [{"status": "resolved", "time": time}]
    assert parsed.is_answer and parsed.issue is None


@pytest.mark.parametrize("language,text,issue", [
    ("et", "31. aprill", "invalid_date"), ("en", "February 30", "invalid_date"),
    ("ru", "тридцать первого апреля", "invalid_date"),
    ("en", "06/10/2027", "ambiguous_date"), ("en", "at six", "ambiguous_time"),
    ("ru", "в шесть", "ambiguous_time"), ("ru", "в половине седьмого", "ambiguous_time"),
    ("et", "homme õhtul", "vague_time"), ("en", "tomorrow evening", "vague_time"),
    ("ru", "завтра вечером", "vague_time"), ("en", "next week", "vague_date"),
    ("et", "kell 25:00", "invalid_time"), ("en", "at 9:60", "invalid_time"),
    ("ru", "в 9:5", "invalid_time"), ("et", "kell 10 kuni 11", "ambiguous_time"),
    ("et", "kell 100:00", "invalid_time"), ("en", "at 9:700", "invalid_time"),
    ("en", "between 6 pm and 7 pm", "ambiguous_time"),
    ("en", "at 18:30 GMT", "different_timezone"),
    ("et", "umbes 6. oktoobril", "ambiguous_date"),
    ("en", "around October sixth", "ambiguous_date"),
    ("ru", "примерно шестого октября", "ambiguous_date"),
])
def test_vague_impossible_and_ambiguous_times_need_clarification(language, text, issue):
    assert interpret_temporal(text, language, NOW).issue == issue


@pytest.mark.parametrize("language,text", [("et", "teisipäeval järgmisel nädalal"), ("en", "Tuesday next week"), ("ru", "во вторник на следующей неделе")])
def test_explicit_next_week_does_not_mean_the_upcoming_day_this_week(language, text):
    monday = datetime(2026, 10, 5, 12, tzinfo=TALLINN)
    parsed = interpret_temporal(text, language, monday)
    assert parsed.dates == [{"status": "resolved", "date": "2026-10-13"}]


@pytest.mark.parametrize("language,text", [("et", "kahe tunni pärast"), ("en", "in two hours"), ("ru", "через два часа")])
def test_elapsed_hours_cross_midnight_using_tallinn_clock(language, text):
    now = datetime(2026, 12, 31, 23, 15, tzinfo=TALLINN)
    parsed = interpret_temporal(text, language, now)
    assert parsed.dates == [{"status": "resolved", "date": "2027-01-01"}]
    assert parsed.times == [{"status": "resolved", "time": "01:15"}]


@pytest.mark.parametrize("language,phrase", [("et", "järgmisel päeval"), ("en", "the day after that"), ("ru", "на следующий день")])
def test_next_day_requires_an_anchor_and_preserves_the_previous_absolute_date(language, phrase):
    assert interpret_temporal(phrase, language, NOW).issue == "ambiguous_date"
    assert interpret_temporal(phrase, language, NOW, "2026-10-06").dates == [{"status": "resolved", "date": "2026-10-07"}]


@pytest.mark.parametrize("text,issue", [("2027-03-28T03:30", "invalid_time"), ("2026-10-25T03:30", "timezone")])
def test_daylight_saving_gaps_and_repeated_hours_never_shift_silently(text, issue):
    assert interpret_temporal(text, "et", NOW).issue == issue


def test_utc_timestamp_converts_both_date_and_clock():
    parsed = interpret_temporal("2026-10-06T22:30Z", "en", NOW)
    assert parsed.dates == [{"status": "resolved", "date": "2026-10-07"}]
    assert parsed.times == [{"status": "resolved", "time": "01:30"}]


FLOWS = [
    ("et", "Soovin spaad broneerida.", "kuuendaks oktoobriks", "pool seitse õhtul"),
    ("en", "I'd like to book a spa appointment.", "October sixth", "half past six pm"),
    ("ru", "Хочу записаться в спа.", "шестого октября", "в половине седьмого вечера"),
]


@pytest.mark.parametrize("language,opening,day_answer,time_answer", FLOWS)
def test_full_date_and_time_answer_is_the_exact_prepared_and_confirmed_backend_booking(language, opening, day_answer, time_answer):
    async def run():
        backend = LiveSlots()
        backend.slots[0].update(date="2026-10-06", start="2026-10-06 18:30:00")
        state = CallTools(Dispatcher(slot=backend), language=language)
        state.observe_user_text(opening, language=language)
        state.observe_user_text(day_answer, language=language)
        assert state.booking_inquiry == {"kind": "slot", "date": "2026-10-06"}
        state.observe_user_text(time_answer, language=language)
        assert state.booking_inquiry == {"kind": "slot", "date": "2026-10-06", "start_time": "18:30"}
        prepared = await state.dispatch("plan_demo_booking", {"date": state.booking_inquiry["date"], "start_time": state.booking_inquiry["start_time"]})
        assert prepared["ok"] and state.pending["recap"]["start"] == "2026-10-06 18:30:00"
        assert not state.pending["approved"] and not any(name == "confirm" for name, _ in backend.calls)
        assert state.mark_recap_delivered("backend-hold")
        state.observe_user_text(CONSENT[language], language=language)
        assert (await state.dispatch("confirm_slot_booking", {"hold_id": "backend-hold"}))["ok"]
        assert state.booking_details["42"]["start_local"] == "2026-10-06 18:30:00"
        assert sum(name == "confirm" for name, _ in backend.calls) == 1

    with patch("app.telephone.datetime", Clock):
        asyncio.run(run())


@pytest.mark.parametrize("language,opening,day_answer,time_answer", FLOWS)
def test_http_date_and_time_reach_the_planner_and_identical_audio(client, language, opening, day_answer, time_answer):
    class Planner:
        calls = 0

        def chat(self, messages, tools=None):
            self.calls += 1
            assert '"date":"2026-10-06"' in messages[0]["content"]
            assert '"time":"18:30"' in messages[0]["content"]
            return {"tool_calls": [{"id": "planned", "type": "function", "function": {"name": "plan_demo_booking", "arguments": json.dumps({"date": "2026-10-06", "start_time": "18:30"})}}]}

    backend = LiveSlots()
    backend.slots[0].update(date="2026-10-06", start="2026-10-06 18:30:00")
    planner = Planner()
    client.app.state.stack["llm_primary"] = planner
    session_id = start(client)
    session = client.app.state.demo_sessions.sessions[session_id]
    session.tools = CallTools(Dispatcher(slot=backend), language=language, call_id=session.tools.call_id)
    with patch("app.telephone.datetime", Clock):
        send(client, session_id, opening, language=language)
        send(client, session_id, day_answer, language=language)
        result = send(client, session_id, time_answer, language=language).json()
    assert planner.calls == 1
    assert session.tools.pending["recap"]["date"] == "2026-10-06"
    assert session.tools.pending["recap"]["start"] == "2026-10-06 18:30:00"
    assert client.app.state.stack["tts"].spoken[-1] == result["reply"]
    assert result["booking_changes"] == []


@pytest.mark.parametrize("language,phrase", [("et", "homme õhtul"), ("en", "tomorrow evening"), ("ru", "завтра вечером")])
def test_unclear_hour_cannot_reach_booking_backend(language, phrase):
    async def run():
        backend = LiveSlots()
        state = CallTools(Dispatcher(slot=backend), language=language)
        state.observe_user_text(phrase, language=language)
        assert state.direct_reply == TEMPORAL_QUESTIONS[language]["vague_time"]
        assert await state.dispatch("plan_demo_booking", {"date": "2026-10-04", "start_time": "18:00"}) == {"error": "clarification_required"}
        assert backend.calls == []

    with patch("app.telephone.datetime", Clock):
        asyncio.run(run())


@pytest.mark.parametrize("language,initial,ambiguous,corrected", [
    ("et", "Soovin homme spaad broneerida.", "umbes kell 18", "kell 18:30"),
    ("en", "Book a spa appointment tomorrow.", "at six", "six thirty pm"),
    ("ru", "Хочу записаться в спа завтра.", "в шесть", "в шесть тридцать вечера"),
])
def test_clarifying_the_clock_retains_the_callers_unambiguous_date(language, initial, ambiguous, corrected):
    with patch("app.telephone.datetime", Clock):
        state = CallTools(Dispatcher(slot=LiveSlots()), language=language)
        state.observe_user_text(initial, language=language)
        state.observe_user_text(ambiguous, language=language)
        assert state.booking_inquiry is None
        state.observe_user_text(corrected, language=language)
        assert state.booking_inquiry == {"kind": "slot", "date": "2026-10-04", "start_time": "18:30"}


@pytest.mark.parametrize("language,text,day", [
    ("et", "järgmisel kuul kuuendal", "2026-11-06"),
    ("en", "next month on the sixth", "2026-11-06"),
    ("ru", "шестого числа следующего месяца", "2026-11-06"),
    ("et", "kuuendal sel kuul", "2026-10-06"),
    ("en", "the sixth of this month", "2026-10-06"),
    ("ru", "в этом месяце шестого", "2026-10-06"),
    ("et", "6. oktoobril järgmisel aastal", "2027-10-06"),
    ("en", "October sixth next year", "2027-10-06"),
    ("ru", "шестого октября следующего года", "2027-10-06"),
    ("et", "kuuendal oktoobril kahe tuhande kaheksakümne kuuendal aastal", "2086-10-06"),
    ("en", "October sixth twenty eighty six", "2086-10-06"),
    ("ru", "шестого октября две тысячи восемьдесят шестого года", "2086-10-06"),
    ("ru", "шестого октября две тысячи девяностого года", "2090-10-06"),
])
def test_relative_month_year_and_later_spoken_year(language, text, day):
    parsed = interpret_temporal(text, language, NOW)
    assert parsed.dates == [{"status": "resolved", "date": day}]
    assert parsed.is_answer and parsed.issue is None


@pytest.mark.parametrize("language,text,clock", [
    ("et", "kahe tunni ja kolmekümne minuti pärast", "14:45"),
    ("en", "in two hours and thirty minutes", "14:45"),
    ("ru", "через два часа и тридцать минут", "14:45"),
    ("et", "pooleteise tunni pärast", "13:45"),
    ("en", "in an hour and a half", "13:45"),
    ("en", "in one and a half hours", "13:45"),
    ("ru", "через полтора часа", "13:45"),
    ("et", "kolmekümne minuti pärast", "12:45"),
])
def test_compound_and_fractional_elapsed_time_is_never_truncated(language, text, clock):
    parsed = interpret_temporal(text, language, NOW)
    assert parsed.dates == [{"status": "resolved", "date": "2026-10-03"}]
    assert parsed.times == [{"status": "resolved", "time": clock}]
    assert parsed.is_answer and parsed.issue is None


@pytest.mark.parametrize("language,text,clock", [
    ("et", "kell kaksteist õhtul", "00:00"),
    ("et", "kell kaks päeval", "14:00"),
    ("en", "tonight at six", "18:00"),
    ("en", "at twelve in the morning", "12:00"),
    ("ru", "в половине двенадцатого утра", "11:30"),
    ("ru", "в половине двенадцатого ночи", "23:30"),
])
def test_dayparts_do_not_reverse_noon_and_midnight(language, text, clock):
    assert interpret_temporal(text, language, NOW, expected="time").times == [{"status": "resolved", "time": clock}]


@pytest.mark.parametrize("language,opening,ambiguous,period", [
    ("en", "Book a spa appointment tomorrow.", "at six thirty", "PM"),
    ("en", "Book a spa appointment tomorrow.", "at 6:30", "in the evening"),
    ("ru", "Хочу записаться в спа завтра.", "в шесть тридцать", "вечером"),
])
def test_short_daypart_reply_resolves_the_previous_clock(language, opening, ambiguous, period):
    with patch("app.telephone.datetime", Clock):
        state = CallTools(Dispatcher(slot=LiveSlots()), language=language)
        state.observe_user_text(opening, language=language)
        state.observe_user_text(ambiguous, language=language)
        assert state.booking_inquiry is None
        state.guard_reply(state.direct_reply, [])
        state.observe_user_text(period, language=language)
        assert state.booking_inquiry == {"kind": "slot", "date": "2026-10-04", "start_time": "18:30"}


@pytest.mark.parametrize("language", ["en", "ru"])
def test_twelve_hour_numeric_clock_needs_a_daypart_but_padded_clock_is_twenty_four_hour(language):
    assert interpret_temporal("6:30", language, NOW).issue == "ambiguous_time"
    assert interpret_temporal("06:30", language, NOW).times == [{"status": "resolved", "time": "06:30"}]


@pytest.mark.parametrize("language,text", [("et", "eelmisel teisipäeval"), ("en", "last Tuesday"), ("ru", "в прошлый вторник")])
def test_explicit_previous_weekday_is_not_moved_into_the_future(language, text):
    parsed = interpret_temporal(text, language, NOW)
    assert parsed.dates == [{"status": "past", "date": "2026-09-29"}]
    assert parsed.issue == "past"


@pytest.mark.parametrize("language,text", [("et", "kuuendal"), ("en", "the sixth"), ("ru", "шестого")])
def test_day_without_month_during_a_date_question_needs_clarification(language, text):
    assert interpret_temporal(text, language, NOW, expected="date").issue == "ambiguous_date"


@pytest.mark.parametrize("text,language", [("October sixth", "en"), ("шестого октября", "ru"), ("kuuendaks oktoobriks", "et")])
def test_calendar_words_identify_language_despite_wrong_provider_metadata(text, language):
    assert select_language(text, "unknown", "et") == language


@pytest.mark.parametrize("language", ["et", "en", "ru"])
def test_numeric_time_preserves_selected_language(language):
    assert select_language("18:30", "english", language) == language


@pytest.mark.parametrize("day,clock,error", [
    ("2027-03-28", "03:30", "invalid_local_datetime"),
    ("2026-10-25", "03:30", "ambiguous_datetime"),
])
def test_direct_tool_cannot_bypass_daylight_saving_validation(day, clock, error):
    async def run():
        backend = LiveSlots()
        state = CallTools(Dispatcher(slot=backend))
        assert await state.dispatch("plan_demo_booking", {"date": day, "start_time": clock}) == {"error": error}
        assert backend.calls == []
    with patch("app.telephone.datetime", Clock):
        asyncio.run(run())


@pytest.mark.parametrize("day,issue", [("2027-03-28", "invalid_time"), ("2026-10-25", "timezone")])
def test_date_and_time_on_separate_turns_still_check_the_daylight_saving_boundary(day, issue):
    with patch("app.telephone.datetime", Clock):
        state = CallTools(Dispatcher(slot=LiveSlots()))
        state.observe_user_text("Soovin spaad broneerida.")
        state.observe_user_text(day)
        state.observe_user_text("kell 03:30")
        assert state.booking_inquiry is None
        assert state.direct_reply == TEMPORAL_QUESTIONS["et"][issue]


@pytest.mark.parametrize("language,opening,day_answer,time_answer", FLOWS)
def test_native_final_turn_injects_both_exact_booking_fields(language, opening, day_answer, time_answer):
    pytest.importorskip("livekit.agents")
    from livekit.agents import llm
    from livekit.agents.voice.agent import ModelSettings
    from app.worker import TelephoneAgent
    from tests.test_native_booking_terminals import tool_chunk

    async def run():
        state = CallTools(Dispatcher(slot=LiveSlots()), language=language)
        agent = TelephoneAgent(state)
        context = llm.ChatContext()
        for text in (opening, day_answer, time_answer):
            message = llm.ChatMessage(role="user", content=[text])
            context.items.append(message)
            await agent.on_user_turn_completed(context.copy(), message)

        async def planner(agent, chat_ctx, tools, settings):
            current = [m.text_content for m in chat_ctx.items if isinstance(m, llm.ChatMessage) and m.role == "system"]
            assert any('"requested_times": [{"status": "resolved", "time": "18:30"}]' in text for text in current)
            assert any('"booking_inquiry": {"kind": "slot", "date": "2026-10-06", "start_time": "18:30"}' in text for text in current)
            yield tool_chunk("plan_demo_booking", {"date": "2026-10-06", "start_time": "18:30"})

        with patch("livekit.agents.Agent.default.llm_node", planner):
            chunks = [chunk async for chunk in agent.llm_node(context, [], ModelSettings())]
        assert chunks[0].delta.tool_calls[0].name == "plan_demo_booking"
        assert json.loads(chunks[0].delta.tool_calls[0].arguments)["start_time"] == "18:30"
    with patch("app.telephone.datetime", Clock):
        asyncio.run(run())
