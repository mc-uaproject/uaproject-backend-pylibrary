from typing import Any, Dict, Generic, Optional, Type, TypeVar
from pydantic import BaseModel
import aiohttp
from ..exceptions import ServiceError

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"Content-Type": "application/json"}
            )
        return self._session
    
    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        session = await self.get_session()
        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status >= 400:
                    raise ServiceError(
                        f"Service request failed: {response.status}",
                        status_code=response.status
                    )
                return await response.json()
        except aiohttp.ClientError as e:
            raise ServiceError(f"Service request failed: {str(e)}")