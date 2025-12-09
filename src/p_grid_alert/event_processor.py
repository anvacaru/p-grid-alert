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


def extract_event_details(text: str, street: str) -> dict[str, str] | None:
    """Extract day and time from the body of the identified event."""
    idx = text.lower().find(street.lower())
    if idx == -1:
        return None

    # Get surrounding context
    start = max(0, idx - 300)
    end = min(len(text), idx + 300)
    context = text[start:end]

    # Extract day (e.g., "Marți, 09.12.2025")
    day_match = re.search(RE_DATE_PATTERN, context)

    # Extract time (e.g., "09:00 - 17:00")
    time_match = re.search(RE_TIME_PATTERN, context)

    return {
        'day': day_match.group(0) if day_match else 'Unknown',
        'time': f'{time_match.group(1)} - {time_match.group(2)}' if time_match else 'Unknown',
        'excerpt': '...' + text[max(0, idx - 200) : idx + 200] + '...',
    }


def process_url(url: str) -> None:
    pdf_id = url.split('?')[0].split('/')[-1]

    _LOGGER.info(f'Processing: {pdf_id} file.')
    text = extract_text(url)

    details = extract_event_details(text, STREET)
    if details:
        if is_event_in_future(details['day'], details['time']):
            _LOGGER.warning(f'⚠️  OUTAGE FOUND for {STREET}')
            _LOGGER.warning(f'Day: {details["day"]}')
            _LOGGER.warning(f'Time: {details["time"]}')
            send_alert(STREET, url, details['excerpt'], details['day'], details['time'])
        else:
            _LOGGER.info(f'Skipping past outage for {STREET} on {details["day"]}')
