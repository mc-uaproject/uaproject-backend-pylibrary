from typing import TypeVar, Optional, Dict, Any, Type, Union, List, Generic
from types import TracebackType
from pydantic import BaseModel
import aiohttp
from uap_backend.exceptions import APIError
from uap_backend.config import settings

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseCRUD(Generic[ModelT]):
    response_model: Type[ModelT]

    def __init__(self) -> None:
        self.base_url: str = f"{settings.API_BASE_URL.rstrip('/')}"
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session or self._session.closed:
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

    async def __aenter__(self) -> "BaseCRUD[ModelT]":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[ModelT]] = None,
        is_list: bool = False,
    ) -> Union[ModelT, List[ModelT]]:
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"

        try:
            async with session.request(
                method=method, url=url, params=params, json=json
            ) as response:
                if response.status >= 400:
                    raise APIError(await response.text(), status_code=response.status)

                data = await response.json()
                model = response_model or self.response_model

                if is_list:
                    return [model.model_validate(item) for item in data]
                return model.model_validate(data)

        except aiohttp.ClientError as e:
            raise APIError(str(e))

    async def get(
        self,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[ModelT]] = None,
        is_list: bool = False,
    ) -> Union[ModelT, List[ModelT]]:
        return await self._request(
            "GET",
            endpoint,
            params=params,
            response_model=response_model,
            is_list=is_list,
        )

    async def post(
        self,
        endpoint: str,
        *,
        data: Optional[BaseModel] = None,
        response_model: Optional[Type[ModelT]] = None,
    ) -> ModelT:
        json_data = data.model_dump(exclude_unset=True) if data else None
        return await self._request(
            "POST", endpoint, json=json_data, response_model=response_model
        )

    async def patch(
        self,
        endpoint: str,
        *,
        data: Optional[BaseModel] = None,
        response_model: Optional[Type[ModelT]] = None,
    ) -> ModelT:
        json_data = data.model_dump(exclude_unset=True) if data else None
        return await self._request(
            "PATCH", endpoint, json=json_data, response_model=response_model
        )

    async def delete(
        self,
        endpoint: str,
        *,
        response_model: Optional[Type[ModelT]] = None,
    ) -> ModelT:
        return await self._request("DELETE", endpoint, response_model=response_model)
