from __future__ import annotations

import logging
from io import BytesIO

import pypdf
import requests
from bs4 import BeautifulSoup

from p_grid_alert.datetime_helpers import encode, get_date_range_for_week
from p_grid_alert.utils import DEFAULT_HEADERS, HTTP_TIMEOUT_SECONDS

_LOGGER = logging.getLogger(__name__)


def fetch_pdf_urls(target_url: str, target_domain: str) -> list[str]:
    """Return the PDF links on `target_url`, hosted on `target_domain`, for the current
    and next week, without duplicates."""
    _LOGGER.info(f'Reading page -- {target_url}')
    resp = requests.get(target_url, headers=DEFAULT_HEADERS, timeout=HTTP_TIMEOUT_SECONDS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, 'html.parser')

    weeks = [get_date_range_for_week(i) for i in [0, 1]]
    patterns = [encode(week) for week in weeks]
    # Keyed by path: the same PDF may be linked twice with different signed query strings.
    relevant_urls: dict[str, str] = {}

    for link in soup.find_all('a', href=True):
        href = str(link['href'])
        if target_domain not in href or '.pdf' not in href:
            continue

        if any(pattern in href for pattern in patterns):
            relevant_urls.setdefault(href.split('?')[0], href)
    return list(relevant_urls.values())


def extract_text(pdf_url: str) -> str:
    """Fetch a PDF file from an URL and convert it to type 'str'."""
    resp = requests.get(pdf_url, headers=DEFAULT_HEADERS, timeout=HTTP_TIMEOUT_SECONDS)
    resp.raise_for_status()
    reader = pypdf.PdfReader(BytesIO(resp.content))
    return '\n'.join(page.extract_text() for page in reader.pages)
