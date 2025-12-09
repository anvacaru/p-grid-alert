from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

from p_grid_alert.event_processor import extract_all_events, is_event_in_future

if TYPE_CHECKING:
    from typing import Final

import pytest

IS_EVENT_IN_FUTURE_TEST_DATA: Final = [
    ('future-event', 'Marți, 15.12.2025', '09:00 - 17:00', datetime(2025, 12, 10, 12, 0), True),
    ('past-event', 'Marți, 09.12.2025', '09:00 - 17:00', datetime(2025, 12, 10, 12, 0), False),
    ('today-future', 'Marți, 10.12.2025', '18:00 - 20:00', datetime(2025, 12, 10, 12, 0), True),
    ('today-past', 'Marți, 10.12.2025', '08:00 - 10:00', datetime(2025, 12, 10, 12, 0), False),
    ('no-time-range', 'Marți, 15.12.2025', 'All day', datetime(2025, 12, 10, 12, 0), True),
    ('invalid-date', 'Invalid date', '09:00 - 17:00', datetime(2025, 12, 10, 12, 0), True),
]

EXTRACT_ALL_EVENTS_TEST_DATA: Final = [
    (
        'single-event',
        'Some text Marți, 09.12.2025 București, Sector 1 Strada Principala 09:00 - 17:00 more text',
        'Principala',
        1,
        {'day': 'Marți, 09.12.2025', 'time': '09:00 - 17:00'},
    ),
    (
        'multiple-events',
        'Marți, 09.12.2025 Strada Principala 09:00 - 12:00 and Miercuri, 10.12.2025 Strada Principala 14:00 - 18:00',
        'Principala',
        2,
        None,
    ),
    (
        'street-not-found',
        'Some text Marți, 09.12.2025 București, Sector 1 Strada Altceva 09:00 - 17:00',
        'Principala',
        0,
        None,
    ),
    (
        'no-time',
        'Some text Marți, 09.12.2025 București, Sector 1 Strada Principala more text',
        'Principala',
        1,
        {'day': 'Marți, 09.12.2025', 'time': 'Unknown'},
    ),
    (
        'no-date',
        'Some text București, Sector 1 Strada Principala 09:00 - 17:00 more text',
        'Principala',
        1,
        {'day': 'Unknown', 'time': '09:00 - 17:00'},
    ),
]


@pytest.mark.parametrize(
    'test_id,day_str,time_str,mock_now,expected',
    IS_EVENT_IN_FUTURE_TEST_DATA,
    ids=[test_id for test_id, *_ in IS_EVENT_IN_FUTURE_TEST_DATA],
)
def test_is_event_in_future(
    test_id: str, day_str: str, time_str: str, mock_now: datetime, expected: bool
) -> None:
    # Given
    with patch('p_grid_alert.event_processor.datetime') as mock_dt:
        mock_dt.now.return_value = mock_now
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # When
        actual = is_event_in_future(day_str, time_str)

        # Then
        assert actual == expected


@pytest.mark.parametrize(
    'test_id,text,street,expected_count,expected_first',
    EXTRACT_ALL_EVENTS_TEST_DATA,
    ids=[test_id for test_id, *_ in EXTRACT_ALL_EVENTS_TEST_DATA],
)
def test_extract_all_events(
    test_id: str,
    text: str,
    street: str,
    expected_count: int,
    expected_first: dict[str, str] | None,
) -> None:
    # When
    actual = extract_all_events(text, street)

    # Then
    assert len(actual) == expected_count

    if expected_count > 0 and expected_first:
        assert actual[0]['day'] == expected_first['day']
        assert actual[0]['time'] == expected_first['time']
        assert 'excerpt' in actual[0]
