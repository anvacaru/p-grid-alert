from __future__ import annotations

from os import getenv
from typing import TYPE_CHECKING

from dotenv import load_dotenv

if TYPE_CHECKING:
    from typing import Final

load_dotenv()

DEFAULT_HEADERS: Final[dict[str, str]] = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}
TARGET_DOMAIN: Final[str] = getenv('P_GRID_TARGET_DOMAIN', '')
TARGET_URL: Final[str] = getenv('P_GRID_TARGET_URL', '')
STREET: Final[str] = getenv('P_GRID_STREET', '')
LOG_FORMAT: Final[str] = '%(levelname)s %(asctime)s %(name)s - %(message)s'
