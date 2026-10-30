from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final


DEFAULT_HEADERS: Final[dict[str, str]] = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}
HTTP_TIMEOUT_SECONDS: Final = 30
# Any spelling of the day name: 'Marți', 'Marţi' (cedilla), 'Marti' (no diacritics).
RE_DATE_PATTERN: Final[str] = r'(?:[^\W\d_]+,?\s*)?\d{2}\.\d{2}\.\d{4}'
RE_TIME_PATTERN: Final[str] = r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})'
LOG_FORMAT: Final[str] = '%(levelname)s %(asctime)s %(name)s - %(message)s'


@dataclass(frozen=True)
class EmailConfig:
    recipients: tuple[str, ...]
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_pass: str


@dataclass(frozen=True)
class Config:
    target_domain: str
    target_url: str
    street: str
    email: EmailConfig


def load_config() -> Config:
    """Read the configuration from the environment.

    Raises:
        ValueError: if a required variable is missing or has an invalid value.
    """
    recipients = tuple(
        r.strip() for r in _get_required_env('P_GRID_EMAIL_TO').split(',') if r.strip()
    )
    if not recipients:
        raise ValueError('P_GRID_EMAIL_TO contains no email addresses')

    port = _get_required_env('P_GRID_SMTP_PORT')
    if not port.isdigit():
        raise ValueError(f'P_GRID_SMTP_PORT must be a number, got: {port!r}')

    return Config(
        target_domain=_get_required_env('P_GRID_TARGET_DOMAIN'),
        target_url=_get_required_env('P_GRID_TARGET_URL'),
        street=_get_required_env('P_GRID_STREET'),
        email=EmailConfig(
            recipients=recipients,
            smtp_server=_get_required_env('P_GRID_SMTP_SERVER'),
            smtp_port=int(port),
            smtp_user=_get_required_env('P_GRID_SMTP_USER'),
            smtp_pass=_get_required_env('P_GRID_SMTP_PASS'),
        ),
    )


def _get_required_env(key: str) -> str:
    value = getenv(key)
    if not value:
        raise ValueError(f'Missing required environment variable: {key}')
    return value
