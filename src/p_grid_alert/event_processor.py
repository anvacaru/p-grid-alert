from __future__ import annotations

import logging
import re
from datetime import datetime

from .datetime_helpers import parse_event_date
from .pdf_reader import extract_text
from .smtp_driver import send_alert
from .utils import RE_DATE_PATTERN, RE_TIME_PATTERN, STREET

_LOGGER = logging.getLogger()


def is_event_in_future(day_str: str, time_str: str) -> bool:
    """Check if the identified event is in the future."""
    event_date = parse_event_date(day_str)
    if not event_date:
        _LOGGER.warning(f'Could not parse date from: {day_str}')
        return True  # Send alert if unsure

    # Extract end time (e.g., "17:00" from "09:00 - 17:00")
    time_match = re.search(r'-\s*(\d{1,2}):(\d{2})', time_str)
    if time_match:
        hour, minute = map(int, time_match.groups())
        outage_end = event_date.replace(hour=hour, minute=minute)
    else:
        outage_end = event_date.replace(hour=23, minute=59)

    now = datetime.now()
    return outage_end > now


def extract_all_events(text: str, street: str) -> list[dict[str, str]]:
    """Extract all occurrences of street with day and time."""
    events = []
    text_lower = text.lower()
    street_lower = street.lower()

    idx = 0
    while True:
        idx = text_lower.find(street_lower, idx)
        if idx == -1:
            break

        # Get surrounding context
        start = max(0, idx - 300)
        end = min(len(text), idx + 300)
        context = text[start:end]

        # Extract day and time
        day_match = re.search(RE_DATE_PATTERN, context)
        time_match = re.search(RE_TIME_PATTERN, context)

        event = {
            'day': day_match.group(0) if day_match else 'Unknown',
            'time': f'{time_match.group(1)} - {time_match.group(2)}' if time_match else 'Unknown',
            'excerpt': '...' + text[max(0, idx - 200) : idx + 200] + '...',
        }

        events.append(event)
        idx += len(street)

    return events


def process_url(url: str) -> None:
    pdf_id = url.split('?')[0].split('/')[-1]

    _LOGGER.info(f'Processing: {pdf_id} file.')
    text = extract_text(url)

    all_events = extract_all_events(text, STREET)

    if not all_events:
        _LOGGER.info(f'✓ No outages for {STREET}')
        return

    # Filter future events
    future_events = [
        event for event in all_events if is_event_in_future(event['day'], event['time'])
    ]

    if not future_events:
        _LOGGER.info(f'Skipping {len(all_events)} past outage(s) for {STREET}')
        return

    _LOGGER.warning(f'⚠️  Found {len(future_events)} outage(s) for {STREET}')
    for event in future_events:
        _LOGGER.warning(f'  - {event["day"]} at {event["time"]}')

    # Send single email with all events
    send_alert(STREET, url, future_events)
