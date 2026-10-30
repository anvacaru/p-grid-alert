from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from p_grid_alert.event_processor import OutageEvent, extract_all_events, is_event_in_future

if TYPE_CHECKING:
    from typing import Final

import pytest

NOW: Final = datetime(2025, 12, 10, 12, 0)

IS_EVENT_IN_FUTURE_TEST_DATA: Final = [
    ('future-event', 'Marți, 15.12.2025', '09:00 - 17:00', True),
    ('past-event', 'Marți, 09.12.2025', '09:00 - 17:00', False),
    ('today-future', 'Marți, 10.12.2025', '18:00 - 20:00', True),
    ('today-past', 'Marți, 10.12.2025', '08:00 - 10:00', False),
    ('today-ongoing', 'Marți, 10.12.2025', '08:00 - 14:00', True),
    ('no-time-range-today', 'Marți, 10.12.2025', None, True),
    ('no-time-range-past', 'Marți, 09.12.2025', None, False),
    ('invalid-date', '32.13.2025', '09:00 - 17:00', True),
    ('ends-at-midnight', 'Marți, 10.12.2025', '20:00 - 24:00', True),
    ('ended-at-midnight', 'Marți, 09.12.2025', '20:00 - 24:00', False),
    ('overnight-ongoing', 'Marți, 09.12.2025', '22:00 - 14:00', True),
    ('overnight-past', 'Marți, 09.12.2025', '22:00 - 02:00', False),
]


@pytest.mark.parametrize(
    'test_id,day,hours,expected',
    IS_EVENT_IN_FUTURE_TEST_DATA,
    ids=[test_id for test_id, *_ in IS_EVENT_IN_FUTURE_TEST_DATA],
)
def test_is_event_in_future(test_id: str, day: str, hours: str | None, expected: bool) -> None:
    # Given
    event = OutageEvent(day=day, hours=hours, excerpt='')

    # When
    actual = is_event_in_future(event, NOW)

    # Then
    assert actual == expected


EXTRACT_ALL_EVENTS_TEST_DATA: Final = [
    (
        'single-event',
        'Header text\nMarți, 09.12.2025 București Strada Principala 09:00 - 17:00\n',
        'Principala',
        [('Marți, 09.12.2025', '09:00 - 17:00')],
    ),
    (
        'each-row-keeps-its-own-date-and-time',
        'Marți, 09.12.2025 Strada Principala 09:00 - 12:00\n'
        'Miercuri, 10.12.2025 Strada Principala 14:00 - 18:00\n',
        'Principala',
        [('Marți, 09.12.2025', '09:00 - 12:00'), ('Miercuri, 10.12.2025', '14:00 - 18:00')],
    ),
    (
        'no-bleed-from-neighbour-rows',
        'Luni, 08.12.2025 Arad Strada Altceva 08:00 - 10:00\n'
        'Marți, 09.12.2025 Arad Strada Principala\n'
        'Miercuri, 10.12.2025 Arad Strada Alta 14:00 - 18:00\n',
        'Principala',
        [('Marți, 09.12.2025', None)],
    ),
    (
        'street-repeated-in-one-row',
        'Joi, 11.12.2025 Str Principala nr 1-5, Str Principala nr 9 09:00 - 12:00\n',
        'Principala',
        [('Joi, 11.12.2025', '09:00 - 12:00')],
    ),
    (
        'street-not-found',
        'Marți, 09.12.2025 București Strada Altceva 09:00 - 17:00',
        'Principala',
        [],
    ),
    (
        'day-without-diacritics',
        'Marti, 09.12.2025 Strada Principala 09:00 - 12:00',
        'Principala',
        [('Marti, 09.12.2025', '09:00 - 12:00')],
    ),
    (
        'day-with-cedilla',
        'Marţi, 09.12.2025 Strada Principala 09:00 - 12:00',
        'Principala',
        [('Marţi, 09.12.2025', '09:00 - 12:00')],
    ),
    (
        'street-matches-ignoring-diacritics-and-case',
        'Marți, 09.12.2025 Strada Dâmboviței 09:00 - 12:00',
        'dambovitei',
        [('Marți, 09.12.2025', '09:00 - 12:00')],
    ),
    (
        'street-before-first-date-is-ignored',
        'Cuprins Principala\nMarți, 09.12.2025 Strada Altceva 09:00 - 17:00',
        'Principala',
        [],
    ),
]


@pytest.mark.parametrize(
    'test_id,text,street,expected',
    EXTRACT_ALL_EVENTS_TEST_DATA,
    ids=[test_id for test_id, *_ in EXTRACT_ALL_EVENTS_TEST_DATA],
)
def test_extract_all_events(
    test_id: str, text: str, street: str, expected: list[tuple[str, str | None]]
) -> None:
    # When
    actual = extract_all_events(text, street)

    # Then
    assert [(event.day, event.hours) for event in actual] == expected
