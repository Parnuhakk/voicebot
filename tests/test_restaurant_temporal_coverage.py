"""Independent ET/EN/RU booking vocabulary and multi-turn acceptance cases.

These fixtures check text after recognition, not live acoustic accuracy.
"""

import asyncio
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from app.booking_response import trusted_booking_response
from app.restaurant_call import COPY, parse_restaurant_request
from app.restaurant_dates import resolve_restaurant_date
from app.restaurant_times import parse_spoken_time
from tests.test_restaurant_http import start, turn

pytest_plugins = ["tests.test_restaurant_conversation", "tests.test_restaurant_http"]

NOW = datetime(2026, 10, 3, 12, tzinfo=ZoneInfo("Europe/Tallinn"))
MONTHS = {
    "et": "jaanuar veebruar märts aprill mai juuni juuli august september oktoober november detsember".split(),
    "en": "January February March April May June July August September October November December".split(),
    "ru": "января февраля марта апреля мая июня июля августа сентября октября ноября декабря".split(),
}


@pytest.mark.parametrize("language", ["et", "en", "ru"])
@pytest.mark.parametrize("day", range(1, 32))
@pytest.mark.parametrize("month", range(1, 13))
def test_all_calendar_days_all_months_all_languages(language, day, month):
    result = resolve_restaurant_date(f"{day} {MONTHS[language][month - 1]} 2028", NOW)
    try:
        expected = date(2028, month, day).isoformat()
    except ValueError:
        assert result.value is None and result.issue == "date_invalid"
    else:
        assert result.value == expected and result.issue is None


@pytest.mark.parametrize("prefix", ["kell", "at", "в"])
@pytest.mark.parametrize("hour", range(24))
@pytest.mark.parametrize("minute", range(60))
def test_every_minute_in_a_24_hour_day(prefix, hour, minute):
    expected = f"{hour:02d}:{minute:02d}"
    period = ""
    if 10 <= hour <= 12:
        period = {"kell": "hommikul" if hour < 12 else "päeval", "at": "AM" if hour < 12 else "PM", "в": "утра" if hour < 12 else "дня"}[prefix]
    assert parse_spoken_time(f"{prefix} {expected} {period}").value == expected


@pytest.mark.parametrize("text,days", [
    ("kahe päeva pärast", 2), ("2 päeva pärast", 2), ("kolme päeva pärast", 3),
    ("ühe nädala pärast", 7), ("kahe nädala pärast", 14),
    ("in two days", 2), ("in 2 days", 2), ("two days from now", 2),
    ("in a week", 7), ("in two weeks", 14), ("a week from today", 7),
    ("через два дня", 2), ("через три дня", 3), ("через неделю", 7),
    ("через две недели", 14), ("через 2 дня", 2),
    ("tonight", 0), ("täna õhtul", 0), ("сегодня вечером", 0),
])
def test_relative_offsets_and_tonight(text, days):
    result = resolve_restaurant_date(text, NOW)
    assert result.value == (NOW.date() + timedelta(days=days)).isoformat()
    assert result.issue is None


@pytest.mark.parametrize("text,expected", [
    ("selle nädala pühapäeval", "2026-10-04"),
    ("järgmise nädala reedel", "2026-10-09"),
    ("ülejärgmise nädala reedel", "2026-10-16"),
    ("this Sunday", "2026-10-04"),
    ("this week's Friday", "2026-10-02"),
    ("next week on Friday", "2026-10-09"),
    ("Friday next week", "2026-10-09"),
    ("the week after next on Friday", "2026-10-16"),
    ("в это воскресенье", "2026-10-04"),
    ("на этой неделе в пятницу", "2026-10-02"),
    ("на следующей неделе в пятницу", "2026-10-09"),
    ("в пятницу на следующей неделе", "2026-10-09"),
    ("через неделю в пятницу", "2026-10-09"),
])
def test_explicit_calendar_week_qualifiers(text, expected):
    assert resolve_restaurant_date(text, NOW).value == expected


@pytest.mark.parametrize("text", ["this Sunday", "sel pühapäeval", "в это воскресенье"])
def test_this_weekday_on_the_same_day_means_today(text):
    sunday = NOW + timedelta(days=1)
    assert resolve_restaurant_date(text, sunday).value == sunday.date().isoformat()


@pytest.mark.parametrize("initial,reply", [
    ("oktoober", "neljas"), ("October", "the fourth"), ("октябрь", "четвертого"),
    ("neljandal", "oktoobril"), ("fourth", "October"), ("четвертого", "октября"),
])
def test_month_and_day_in_separate_answers_never_become_guest_counts(initial, reply):
    previous = {"start_time": "18:00", "party_size": 4}
    first = parse_restaurant_request(initial, previous, now=NOW, expected_field="date")
    assert "date" not in first and first["date_issue"] == "date_incomplete"
    assert first["party_size"] == 4
    second = parse_restaurant_request(reply, first, now=NOW, expected_field="date_incomplete")
    assert second == {"date": "2026-10-04", "start_time": "18:00", "party_size": 4}


@pytest.mark.parametrize("text", ["4", "4.", "4th", "neljandal", "четвёртого"])
def test_day_only_reply_requires_a_month_and_preserves_party(text):
    result = parse_restaurant_request(text, {"start_time": "18:00", "party_size": 2}, now=NOW, expected_field="date")
    assert result["date_issue"] == "date_incomplete" and result["date_day"] == 4
    assert result["party_size"] == 2


@pytest.mark.parametrize("text", ["4.10", "10/4", "4-10"])
def test_short_numeric_date_reply_is_never_a_clock(text):
    result = parse_restaurant_request(text, {}, now=NOW, expected_field="date")
    assert result == {"date_issue": "date_ambiguous"}


@pytest.mark.parametrize("initial,reply", [("October 2028", "fourth"), ("oktoober 2028", "neljas"), ("октябрь 2028", "четвертого")])
def test_partial_month_keeps_explicit_year(initial, reply):
    first = parse_restaurant_request(initial, {}, now=NOW, expected_field="date")
    second = parse_restaurant_request(reply, first, now=NOW, expected_field="date_incomplete")
    assert second == {"date": "2028-10-04"}


@pytest.mark.parametrize("text", [
    "next week", "järgmisel nädalal", "на следующей неделе", "next month",
    "järgmisel kuul", "в следующем месяце", "in two months", "kahe kuu pärast",
])
def test_incomplete_relative_dates_clear_previous_date(text):
    previous = {"date": "2026-10-06", "start_time": "18:00", "party_size": 4}
    result = parse_restaurant_request(text, previous, now=NOW)
    assert "date" not in result and result["date_issue"] == "date_incomplete"
    assert result["start_time"] == "18:00" and result["party_size"] == 4


@pytest.mark.parametrize("text,expected", [
    ("kell kuueks õhtul", "18:00"), ("kella kuue ajal õhtul", "18:00"),
    ("kell kaheksateistkümneks", "18:00"),
    ("kell kuus läbi viisteist õhtul", "18:15"),
    ("viisteist minutit enne seitset õhtul", "18:45"),
    ("at six fifteen in the evening", "18:15"),
    ("quarter after six PM", "18:15"), ("a quarter before seven PM", "18:45"),
    ("at six and a half in the evening", "18:30"),
    ("at six hours and thirty minutes in the evening", "18:30"),
    ("в половине седьмого вечера", "18:30"),
    ("в шесть с половиной вечера", "18:30"),
    ("в шесть часов пятнадцать минут вечера", "18:15"),
    ("без пятнадцати семь вечера", "18:45"),
    ("at eighteen hours and thirty minutes", "18:30"),
])
def test_additional_spoken_time_forms(text, expected):
    result = parse_spoken_time(text)
    assert result and result.value == expected


@pytest.mark.parametrize("text", [
    "around six in the evening", "at about six PM", "kella kuue paiku õhtul",
    "около шести вечера", "примерно в шесть вечера", "between six and seven PM",
    "kell kuus kuni seitse õhtul", "с шести до семи вечера", "at -6 PM",
    "at 24:00", "kell 18:60", "в 25 часов", "at six or seven PM",
    "at noon AM", "at midnight PM",
])
def test_unclear_invalid_and_approximate_times_never_select_a_clock(text):
    result = parse_restaurant_request(text, {"date": "2026-10-06", "start_time": "18:00", "party_size": 4}, now=NOW)
    assert "start_time" not in result and result["time_invalid"]
    assert result["party_size"] == 4


@pytest.mark.parametrize("language,quantity", [
    ("et", "meid on neli"), ("et", "meid tuleb neli"),
    ("en", "there will be four of us"), ("en", "for a party of four"),
    ("ru", "нас будет четверо"), ("ru", "нас четверо"), ("ru", "нас будет четыре"),
])
def test_guest_count_answers_keep_date_and_time(language, quantity):
    result = parse_restaurant_request(quantity, {"date": "2026-10-06", "start_time": "18:00"}, now=NOW, expected_field="party")
    assert result == {"date": "2026-10-06", "start_time": "18:00", "party_size": 4}


@pytest.mark.parametrize("text", [
    "Soovin lauda neljas oktoober kell 14 nelja külalisega",
    "A table on October fourth at fourteen four guests",
    "Столик четвертого октября в четырнадцать четыре гостя",
])
def test_adjacent_guest_count_is_never_a_clock_minute(text):
    assert parse_restaurant_request(text, now=NOW) == {"date": "2026-10-04", "start_time": "14:00", "party_size": 4}


@pytest.mark.parametrize("text", ["around four guests", "between four and five guests", "umbes nelja inimesega", "около четырех гостей"])
def test_approximate_guest_quantity_keeps_time_but_requires_exact_count(text):
    result = parse_restaurant_request(text, {"date": "2026-10-06", "start_time": "18:00", "party_size": 4}, now=NOW)
    assert result == {"date": "2026-10-06", "start_time": "18:00", "party_invalid": True}


@pytest.mark.parametrize("quantity,expected", [
    ("eleven guests", 11), ("twenty people", 20), ("twenty-one people", 21),
    ("üksteist inimest", 11), ("kakskümmend inimest", 20), ("kakskümmend üks inimest", 21),
    ("одиннадцать гостей", 11), ("двадцать гостей", 20), ("двадцать один человек", 21),
])
def test_larger_party_words_never_become_their_units(quantity, expected):
    result = parse_restaurant_request(quantity, {}, now=NOW, expected_field="party")
    assert result == {"party_size": expected}


@pytest.mark.parametrize("text", [
    "for four or five guests", "neljale või viiele inimesele", "на четверых или пятерых",
    "four guests and two guests", "kokku neli, kaks täiskasvanut ja kolm last",
    "four in total, two adults and three children", "всего четыре, двое взрослых и трое детей",
    "not for four guests", "mitte neljale inimesele", "не на четверых",
])
def test_unclear_or_conflicting_guest_counts_clear_old_count(text):
    result = parse_restaurant_request(text, {"date": "2026-10-06", "start_time": "18:00", "party_size": 4}, now=NOW)
    assert "party_size" not in result


@pytest.mark.parametrize("language,initial,date_reply,time_reply,party_reply", [
    ("et", "Soovin lauda", "kahe päeva pärast", "kell kuueks õhtul", "meid tuleb neli"),
    ("en", "I'd like to book a table", "in two days", "at six and a half PM", "for a party of four"),
    ("ru", "Хочу забронировать столик", "через два дня", "в шесть с половиной вечера", "нас будет четверо"),
])
def test_http_stepwise_answers_have_exact_recap_without_a_model(client, language, initial, date_reply, time_reply, party_reply):
    session_id = start(client, language)["session_id"]
    for text, question in [(initial, "date"), (date_reply, "time"), (time_reply, "party")]:
        response = turn(client, session_id, text, language=language)
        assert response["reply"] == COPY[language][question]
        assert response["booking_changes"] == [] and not response.get("recap_delivery_id")
    response = turn(client, session_id, party_reply, language=language)
    state = client.app.state.demo_sessions.sessions[session_id].tools
    assert response["recap_delivery_id"] and state.pending
    recap = state.pending["recap"]
    assert datetime.fromisoformat(recap["start"]).date() == datetime.now(ZoneInfo("Europe/Tallinn")).date() + timedelta(days=2)
    assert datetime.fromisoformat(recap["start"]).strftime("%H:%M") == ("18:00" if language == "et" else "18:30")
    assert recap["party_size"] == 4 and response["booking_changes"] == []


@pytest.mark.parametrize("language,bad_date", [("et", "järgmisel nädalal"), ("en", "next week"), ("ru", "на следующей неделе")])
def test_incomplete_date_cannot_dispatch_a_stale_booking(make_state, language, bad_date):
    state = make_state(language)
    state.observe_user_text("table tomorrow at 18:00 for four", language=language)
    state.observe_user_text(bad_date, language=language)
    assert trusted_booking_response(state) == {"content": COPY[language]["date_incomplete"]}
    result = asyncio.run(state.dispatch("plan_restaurant_reservation", {"date": "2026-10-06", "start_time": "18:00", "party_size": 4}))
    assert not result.get("ok") and state.pending is None


@pytest.mark.parametrize("language,month,day", [("et", "oktoober", "neljas"), ("en", "October", "fourth"), ("ru", "октябрь", "четвертого")])
def test_http_month_and_day_followups_retain_context(client, language, month, day):
    session_id = start(client, language)["session_id"]
    for text, key in [("table at 18:00 for four", "date"), (month, "date_incomplete")]:
        response = turn(client, session_id, text, language=language)
        assert response["reply"] == COPY[language][key] and response["booking_changes"] == []
    response = turn(client, session_id, day, language=language)
    state = client.app.state.demo_sessions.sessions[session_id].tools
    assert response.get("recap_delivery_id")
    assert state.booking_inquiry == {"date": "2026-10-04", "start_time": "18:00", "party_size": 4}


@pytest.mark.parametrize("language,range_reply,exact", [("et", "neljale või viiele inimesele", "viiele"), ("en", "for four or five guests", "five"), ("ru", "на четверых или пятерых", "пять")])
def test_unclear_party_blocks_dispatch_until_resolved(make_state, language, range_reply, exact):
    state = make_state(language)
    state.observe_user_text("table tomorrow at 18:00 for four", language=language)
    state.observe_user_text(range_reply, language=language)
    assert trusted_booking_response(state) == {"content": COPY[language]["party"]}
    assert state.booking_inquiry["party_invalid"]
    result = asyncio.run(state.dispatch("plan_restaurant_reservation", {"date": "2026-10-06", "start_time": "18:00", "party_size": 4}))
    assert result.get("error") == "clarification_required" and state.pending is None
    state.observe_user_text(exact, language=language)
    assert state.booking_inquiry["party_size"] == 5 and "party_invalid" not in state.booking_inquiry


@pytest.mark.parametrize("text", [
    "not next week on Friday", "mitte järgmise nädala reedel", "не на следующей неделе в пятницу",
    "October or November", "oktoober või november", "октябрь или ноябрь",
    "in -2 days", "-2 päeva pärast", "через -2 дня", "2026-02-30", "0000-10-04",
])
def test_invalid_relative_and_partial_dates_cannot_reuse_previous_date(text):
    result = parse_restaurant_request(text, {"date": "2026-10-06", "start_time": "18:00", "party_size": 4}, now=NOW)
    assert "date" not in result and result.get("date_issue")


@pytest.mark.parametrize("language,template", [("et", "{n} päeva pärast"), ("en", "in {n} days"), ("ru", "через {n} дней")])
@pytest.mark.parametrize("days", range(32))
@pytest.mark.parametrize("today", [date(2026, 12, 31), date(2028, 2, 28), date(2026, 3, 28), date(2026, 10, 24)])
def test_relative_days_across_year_leap_day_and_dst(language, template, days, today):
    now = datetime.combine(today, datetime.min.time(), tzinfo=ZoneInfo("Europe/Tallinn"))
    result = resolve_restaurant_date(template.format(n=days), now)
    assert result.value == (today + timedelta(days=days)).isoformat() and result.issue is None
