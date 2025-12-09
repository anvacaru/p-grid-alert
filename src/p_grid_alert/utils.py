from __future__ import annotations

from os import getenv
from typing import TYPE_CHECKING

from dotenv import load_dotenv

if TYPE_CHECKING:
    from typing import Any, Final

load_dotenv()


def _get_required_env(key: str) -> str:
    """Get required environment variable or raise error."""
    value = getenv(key)
    if not value:
        raise ValueError(f'Missing required environment variable: {key}')
    return value


DEFAULT_HEADERS: Final[dict[str, str]] = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}
TARGET_DOMAIN: Final[str] = _get_required_env('P_GRID_TARGET_DOMAIN')
TARGET_URL: Final[str] = _get_required_env('P_GRID_TARGET_URL')
STREET: Final[str] = _get_required_env('P_GRID_STREET')
LOG_FORMAT: Final[str] = '%(levelname)s %(asctime)s %(name)s - %(message)s'

EMAIL_CONFIG: Final[dict[str, Any]] = {
    'email_to': _get_required_env('P_GRID_EMAIL_TO'),
    'smtp_server': _get_required_env('P_GRID_SMTP_SERVER'),
    'smtp_port': int(_get_required_env('P_GRID_SMTP_PORT')),
    'smtp_user': _get_required_env('P_GRID_SMTP_USER'),
    'smtp_pass': _get_required_env('P_GRID_SMTP_PASS'),
}
