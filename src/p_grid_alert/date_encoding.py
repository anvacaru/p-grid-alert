from __future__ import annotations

from datetime import datetime, timedelta
from urllib.parse import quote

# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     pass


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
