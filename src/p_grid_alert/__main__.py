from __future__ import annotations

import logging
from argparse import ArgumentParser

from dotenv import load_dotenv

from .pdf_reader import extract_text, fetch_pdf_urls
from .utils import LOG_FORMAT, STREET

load_dotenv()
_LOGGER = logging.getLogger(__name__)


def _argument_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Power grid outage alert')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    return parser


def process(pdf_urls: list[str]) -> None:
    for url in pdf_urls:
        pdf_id = url.split('?')[0].split('/')[-1]

        _LOGGER.info(f'Processing: {pdf_id} file.')
        text = extract_text(url)

        if STREET.lower() in text.lower():
            idx = text.lower().find(STREET.lower())
            excerpt = '...' + text[max(0, idx - 200) : idx + 200] + '...'
            _LOGGER.warning(excerpt)


def main() -> None:
    args = _argument_parser().parse_args()
    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    pdf_urls = fetch_pdf_urls()
    _LOGGER.info(f'Found {len(pdf_urls)} documents.')

    if not pdf_urls:
        _LOGGER.warning('No PDFs found for current/next week')
        return

    process(pdf_urls)
    _LOGGER.info('Check complete')


if __name__ == '__main__':
    main()
