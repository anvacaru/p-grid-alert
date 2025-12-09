from __future__ import annotations

import logging
from argparse import ArgumentParser

from dotenv import load_dotenv

from .event_processor import process_url
from .pdf_reader import fetch_pdf_urls
from .utils import LOG_FORMAT

load_dotenv()
_LOGGER = logging.getLogger(__name__)


def _argument_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Power grid outage alert')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    return parser


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

    for url in pdf_urls:
        process_url(url)
    _LOGGER.info('Check complete')


if __name__ == '__main__':
    main()
