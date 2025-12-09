from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from p_grid_alert.date_encoding import encode

if TYPE_CHECKING:
    from typing import Final

import pytest

ENCODING_TEST_DATA: Final = [
    ('encode-01', (datetime(2025, 12, 9), datetime(2025, 12, 16)), '09.12.2025%20-%2016.12.2025')
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
