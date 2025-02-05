from typing import Any, Dict, Optional
import aiohttp

from uap_backend.config import settings
from ..exceptions import ServiceError


class BaseCRUD:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.BACKEND_API_KEY}",
                }
            )
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> Dict[str, Any]:
        session = await self.get_session()
        try:
            async with session.request(
                method, settings.API_FULL_URL + endpoint, **kwargs
            ) as response:
                if response.status >= 400:
                    raise ServiceError(
                        f"Service request failed: {response.status}",
                        status_code=response.status,
                    )
                return await response.json()
        except aiohttp.ClientError as e:
            raise ServiceError(f"Service request failed: {str(e)}")
