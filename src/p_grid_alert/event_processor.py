from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from p_grid_alert.datetime_helpers import parse_clock, parse_event_date
from p_grid_alert.pdf_reader import extract_text
from p_grid_alert.smtp_driver import send_alert
from p_grid_alert.utils import RE_DATE_PATTERN, RE_TIME_PATTERN

if TYPE_CHECKING:
    from p_grid_alert.utils import EmailConfig

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class OutageEvent:
    day: str  # as printed in the PDF, e.g. 'Marți, 09.12.2025'
    hours: str | None  # e.g. '09:00 - 17:00'; None if the row has no time range
    excerpt: str


def process_url(url: str, street: str, email: EmailConfig) -> None:
    pdf_id = url.split('?')[0].split('/')[-1]

    _LOGGER.info(f'Processing: {pdf_id} file.')
    text = extract_text(url)

    all_events = extract_all_events(text, street)

    if not all_events:
        _LOGGER.info(f'✓ No outages for {street}')
        return

    now = datetime.now()
    future_events = [event for event in all_events if is_event_in_future(event, now)]

    if not future_events:
        _LOGGER.info(f'Skipping {len(all_events)} past outage(s) for {street}')
        return

    _LOGGER.warning(f'⚠️  Found {len(future_events)} outage(s) for {street}')
    for event in future_events:
        _LOGGER.warning(f'  - {event.day} at {event.hours}')

    send_alert(street, url, future_events, email)


def extract_all_events(text: str, street: str) -> list[OutageEvent]:
    """Return one event per schedule row that mentions `street`.

    The PDF lists one outage per row: 'Day, DD.MM.YYYY Locality Streets HH:MM - HH:MM',
    so a row spans from one date to the next. Text before the first date is not a row.
    Matching ignores case and diacritics.
    """
    street_key = _fold(street)
    date_starts = [m.start() for m in re.finditer(RE_DATE_PATTERN, text)]
    row_bounds = zip(date_starts, date_starts[1:] + [len(text)], strict=True)
    rows = [text[start:end].strip() for start, end in row_bounds]
    return [_parse_row(row) for row in rows if street_key in _fold(row)]


def is_event_in_future(event: OutageEvent, now: datetime) -> bool:
    """Whether the outage has not ended yet; unparseable dates count as future."""
    end = outage_end(event)
    if end is None:
        _LOGGER.warning(f'Could not parse date from: {event.day}')
        return True  # Send alert if unsure
    return end > now


def outage_end(event: OutageEvent) -> datetime | None:
    """End of the outage; a row without hours lasts the whole day."""
    event_date = parse_event_date(event.day)
    if event_date is None:
        return None

    time_match = re.search(RE_TIME_PATTERN, event.hours) if event.hours else None
    if time_match is None:
        return event_date + timedelta(days=1)

    start, end = (parse_clock(clock) for clock in time_match.groups())
    if end <= start:  # overnight, e.g. '22:00 - 02:00'
        end += timedelta(days=1)
    return event_date + end


def _parse_row(row: str) -> OutageEvent:
    day_match = re.match(RE_DATE_PATTERN, row)
    assert day_match is not None, 'rows start at a date by construction'
    time_match = re.search(RE_TIME_PATTERN, row)
    return OutageEvent(
        day=day_match.group(0),
        hours=f'{time_match.group(1)} - {time_match.group(2)}' if time_match else None,
        excerpt=row,
    )


def _fold(text: str) -> str:
    """Lowercase and strip diacritics, so 'Mărăşeşti' matches 'marasesti'."""
    decomposed = unicodedata.normalize('NFKD', text.lower())
    return ''.join(c for c in decomposed if not unicodedata.combining(c))
