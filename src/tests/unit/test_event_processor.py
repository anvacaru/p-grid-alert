from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

from p_grid_alert.event_processor import extract_event_details, is_event_in_future

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

EXTRACT_EVENT_DETAILS_TEST_DATA: Final = [
    (
        'valid-event',
        'Some text Marți, 09.12.2025 București, Sector 1 Strada Principala 09:00 - 17:00 more text',
        'Principala',
        {'day': 'Marți, 09.12.2025', 'time': '09:00 - 17:00'},
    ),
    (
        'street-not-found',
        'Some text Marți, 09.12.2025 București, Sector 1 Strada Altceva 09:00 - 17:00',
        'Principala',
        None,
    ),
    (
        'no-time',
        'Some text Marți, 09.12.2025 București, Sector 1 Strada Principala more text',
        'Principala',
        {'day': 'Marți, 09.12.2025', 'time': 'Unknown'},
    ),
    (
        'no-date',
        'Some text București, Sector 1 Strada Principala 09:00 - 17:00 more text',
        'Principala',
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
    'test_id,text,street,expected',
    EXTRACT_EVENT_DETAILS_TEST_DATA,
    ids=[test_id for test_id, *_ in EXTRACT_EVENT_DETAILS_TEST_DATA],
)
def test_extract_event_details(
    test_id: str, text: str, street: str, expected: dict[str, str] | None
) -> None:
    # When
    actual = extract_event_details(text, street)

    # Then
    if expected is None:
        assert actual is None
    else:
        assert actual is not None
        assert actual['day'] == expected['day']
        assert actual['time'] == expected['time']
        assert 'excerpt' in actual
