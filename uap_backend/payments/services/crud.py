from typing import Optional

import aiohttp


class BaseCRUD:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
