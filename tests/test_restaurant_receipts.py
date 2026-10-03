"""Reservation details come from committed records, not assistant prose."""

import pytest

from app.restaurant_data import load_restaurant_data, restaurant_booking_details


@pytest.fixture
def booking():
    return {
        "id": 17,
        "table_id": "3",
        "party_size": 4,
        "start": "2026-10-04T14:00:00",
        "end": "2026-10-04T15:30:00",
        "status": "confirmed",
    }


def test_receipt_contains_only_saved_details_and_configured_table_name(booking):
    assert restaurant_booking_details(booking, load_restaurant_data()) == {
        "id": "17",
        "date": "2026-10-04",
        "start_local": booking["start"],
        "end_local": booking["end"],
        "party_size": 4,
        "table_id": "3",
        "table_name": "Table 3",
        "timezone": "Europe/Tallinn",
        "synthetic": True,
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", 0), ("id", True), ("id", "17<script>"),
        ("party_size", True), ("party_size", 0), ("party_size", 7),
        ("party_size", "4"), ("table_id", "unknown"), ("table_id", "1"),
        ("start", "not a date"), ("end", "2026-10-04T13:00:00"),
        ("status", "pending"), ("status", "cancelled"),
    ],
)
def test_invalid_or_uncommitted_records_cannot_make_a_receipt(booking, field, value):
    booking[field] = value
    with pytest.raises((ValueError, TypeError)):
        restaurant_booking_details(booking, load_restaurant_data())
