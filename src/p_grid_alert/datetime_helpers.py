from __future__ import annotations

import re
from datetime import datetime, timedelta
from urllib.parse import quote


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
    date_match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', day_str)
    if not date_match:
        return None
    day, month, year = map(int, date_match.groups())
    try:
        return datetime(year, month, day)
    except ValueError:
        return None


def parse_clock(clock: str) -> timedelta:
    """Parse 'HH:MM' into an offset from midnight; '24:00' is the end of the day."""
    hour, minute = map(int, clock.split(':'))
    return timedelta(hours=hour, minutes=minute)
