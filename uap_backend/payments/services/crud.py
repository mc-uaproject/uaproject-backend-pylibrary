from typing import Any, Dict, Optional

import aiohttp

from uap_backend.config import settings
from uap_backend.exceptions import ServiceError


class BaseCRUD:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
