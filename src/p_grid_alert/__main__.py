from __future__ import annotations

import logging
import sys
from argparse import ArgumentParser

from dotenv import load_dotenv

from p_grid_alert.event_processor import process_url
from p_grid_alert.pdf_reader import fetch_pdf_urls
from p_grid_alert.utils import LOG_FORMAT, load_config

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

    load_dotenv()
    config = load_config()

    pdf_urls = fetch_pdf_urls(config.target_url, config.target_domain)
    _LOGGER.info(f'Found {len(pdf_urls)} documents.')

    if not pdf_urls:
        _LOGGER.warning('No PDFs found for current/next week')
        return

    # One bad PDF must not stop the others from being checked; failures still fail the run.
    failed = 0
    for url in pdf_urls:
        try:
            process_url(url, config.street, config.email)
        except Exception:
            _LOGGER.exception(f'Failed to process {url}')
            failed += 1

    if failed:
        sys.exit(f'{failed} of {len(pdf_urls)} document(s) failed')
    _LOGGER.info('Check complete')


if __name__ == '__main__':
    main()
