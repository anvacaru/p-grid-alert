from __future__ import annotations

import logging
from io import BytesIO

import pypdf
import requests
from bs4 import BeautifulSoup

from .datetime_helpers import encode, get_date_range_for_week
from .utils import DEFAULT_HEADERS, TARGET_DOMAIN, TARGET_URL

_LOGGER = logging.getLogger(__name__)


def fetch_pdf_urls() -> list[str]:
    """Fetch all URL's from TARGET_URL that match the TARGET_DOMAIN
    and point to a PDF file."""
    _LOGGER.info(f'Reading page -- {TARGET_URL}')
    resp = requests.get(TARGET_URL, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(resp.content, 'html.parser')

    weeks = [get_date_range_for_week(i) for i in [0, 1]]
    patterns = [encode(week) for week in weeks]
    relevant_urls = []

    for link in soup.find_all('a', href=True):
        href = str(link['href'])
        if TARGET_DOMAIN not in href or '.pdf' not in href:
            continue

        if any(pattern in href for pattern in patterns):
            relevant_urls.append(href)
    return relevant_urls


def extract_text(pdf_url: str) -> str:
    """Fetch a PDF file from an URL and convert it to type 'str'."""
    resp = requests.get(pdf_url)
    reader = pypdf.PdfReader(BytesIO(resp.content))
    return '\n'.join(page.extract_text() for page in reader.pages)
