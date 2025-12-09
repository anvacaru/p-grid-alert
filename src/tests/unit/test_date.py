from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

from p_grid_alert.date_encoding import encode, get_date_range_for_week

if TYPE_CHECKING:
    from typing import Final

import pytest

ENCODING_TEST_DATA: Final = [
    ('encode-01', (datetime(2025, 12, 9), datetime(2025, 12, 16)), '09.12.2025%20-%2016.12.2025')
]
DATE_RANGE_TEST_DATA: Final = [
    ('tuesday-current', datetime(2025, 12, 9), 0, datetime(2025, 12, 8), datetime(2025, 12, 14)),
    ('tuesday-next', datetime(2025, 12, 9), 1, datetime(2025, 12, 15), datetime(2025, 12, 21)),
    ('monday-current', datetime(2025, 12, 8), 0, datetime(2025, 12, 8), datetime(2025, 12, 14)),
    ('sunday-current', datetime(2025, 12, 14), 0, datetime(2025, 12, 8), datetime(2025, 12, 14)),
]


@pytest.mark.parametrize(
    'test_id,datetime_tuple,expected',
    ENCODING_TEST_DATA,
    ids=[test_id for test_id, *_ in ENCODING_TEST_DATA],
)
def test_datetime_encoding(
    test_id: str, datetime_tuple: tuple[datetime, datetime], expected: str
) -> None:
    # When
    actual = encode(datetime_tuple)
    # Then
    assert actual == expected


@pytest.mark.parametrize(
    'test_id,mock_now,weeks_ahead,expected_start,expected_end',
    DATE_RANGE_TEST_DATA,
    ids=[test_id for test_id, *_ in DATE_RANGE_TEST_DATA],
)
def test_get_date_range_for_week(
    test_id: str,
    mock_now: datetime,
    weeks_ahead: int,
    expected_start: datetime,
    expected_end: datetime,
) -> None:
    # Given
    with patch('p_grid_alert.date_encoding.datetime') as mock_dt:
        mock_dt.now.return_value = mock_now
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # When
        actual_start, actual_end = get_date_range_for_week(weeks_ahead)

        # Then
        assert actual_start == expected_start
        assert actual_end == expected_end
