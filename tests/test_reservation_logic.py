import datetime
from app import is_time_expression, check_overlap, get_default_reservation
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

def test_is_time_expression_valid_examples():
    assert is_time_expression("5 pm")
    assert is_time_expression("9:30 am")
    assert is_time_expression("3 o'clock in the afternoon")

def test_is_time_expression_invalid_examples():
    assert not is_time_expression("tomorrow")
    assert not is_time_expression("meeting with John")

def test_check_overlap_detects_overlap():
    new_event = {
        "start": "2025-10-10T10:00:00",
        "end": "2025-10-10T11:00:00"
    }
    existing_events = [
        {"start": "2025-10-10T10:30:00", "end": "2025-10-10T11:30:00"}
    ]
    assert check_overlap(new_event, existing_events) is True

def test_check_overlap_no_overlap():
    new_event = {
        "start": "2025-10-10T12:00:00",
        "end": "2025-10-10T13:00:00"
    }
    existing_events = [
        {"start": "2025-10-10T10:30:00", "end": "2025-10-10T11:30:00"}
    ]
    assert check_overlap(new_event, existing_events) is False

def test_get_default_reservation_structure():
    reservation = get_default_reservation()
    assert isinstance(reservation, dict)
    assert set(reservation.keys()) == {"title", "start", "end", "allDay", "description"}
