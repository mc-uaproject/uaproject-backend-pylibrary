from typing import Any, Dict, Optional, Union
import aiohttp
from uap_backend.config import settings
from uap_backend.exceptions import ServiceError


class BaseCRUD:
    def __init__(self, resource: str):
        self._session: Optional[aiohttp.ClientSession] = None
        self.resource = resource

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
        url = f"{settings.API_FULL_URL}/api/v1/payments/{self.resource}{endpoint}"
        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status >= 400:
                    raise ServiceError(
                        f"Service request failed: {response.status}",
                        status_code=response.status,
                    )
                return await response.json()
        except aiohttp.ClientError as e:
            raise ServiceError(f"Service request failed: {str(e)}")

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "", json=data)

    async def get_list(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._request("GET", "", params=params)

    async def get(self, item_id: Union[int, str]) -> Dict[str, Any]:
        return await self._request("GET", f"/{item_id}")

    async def update(
        self, item_id: Union[int, str], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._request("PATCH", f"/{item_id}", json=data)

    async def delete(self, item_id: Union[int, str]) -> Dict[str, Any]:
        return await self._request("DELETE", f"/{item_id}")
