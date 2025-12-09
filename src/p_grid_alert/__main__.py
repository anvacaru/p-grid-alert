from __future__ import annotations

import logging
from io import BytesIO

import PyPDF2
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from .date_encoding import encode, get_date_range_for_week
from .utils import DEFAULT_HEADERS, LOG_FORMAT, STREET, TARGET_DOMAIN, TARGET_URL

load_dotenv()
logging.basicConfig(
    level=logging.WARNING,
    format=LOG_FORMAT,
    datefmt='%Y-%m-%d %H:%M:%S',
)
_LOGGER = logging.getLogger(__name__)


def get_relevant_pdf_urls() -> list[str]:
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
    resp = requests.get(pdf_url)
    reader = PyPDF2.PdfReader(BytesIO(resp.content))
    return '\n'.join(page.extract_text() for page in reader.pages)


def main() -> None:
    pdf_urls = get_relevant_pdf_urls()
    _LOGGER.info(f'Found {len(pdf_urls)} documents.')

    if not pdf_urls:
        _LOGGER.warning('No PDFs found for current/next week')
        return

    for pdf_url in pdf_urls:
        pdf_id = pdf_url.split('?')[0].split('/')[-1]

        _LOGGER.info(f'Processing: {pdf_id}')
        text = extract_text(pdf_url)

        if STREET.lower() in text.lower():
            idx = text.lower().find(STREET.lower())
            excerpt = '...' + text[max(0, idx - 200) : idx + 200] + '...'
            _LOGGER.warning(excerpt)

    _LOGGER.info('Check complete')


if __name__ == '__main__':
    main()
