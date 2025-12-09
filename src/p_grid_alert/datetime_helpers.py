from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from urllib.parse import quote

_LOGGER = logging.getLogger()


def get_date_range_for_week(weeks_ahead: int = 0) -> tuple[datetime, datetime]:
    """Get start (Monday) and end (Sunday) of week."""
    today = datetime.now()
    days_since_monday = today.weekday()
    start = today - timedelta(days=days_since_monday) + timedelta(weeks=weeks_ahead)
    end = start + timedelta(days=6)
    return start, end


def encode(period: tuple[datetime, datetime]) -> str:
    """Take a tuple of datetimes and encode it in as: 'DD.MM.YYYY - DD.MM.YYYY'"""
    return quote(f'{period[0].strftime("%d.%m.%Y")} - {period[1].strftime("%d.%m.%Y")}')


def parse_event_date(day_str: str) -> datetime | None:
    """Parse day string to datetime (e.g., 'Marți, 09.12.2025')."""
    try:
        date_match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', day_str)
        if date_match:
            day, month, year = date_match.groups()
            return datetime(int(year), int(month), int(day))
    except (ValueError, AttributeError):
        pass
    return None
