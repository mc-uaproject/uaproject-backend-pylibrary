import asyncio
from datetime import datetime
from decimal import Decimal
from functools import wraps
from json import JSONEncoder, dumps
from time import time
from types import TracebackType
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

import aiohttp
from pydantic import BaseModel

from uap_backend.config import settings
from uap_backend.exceptions import APIError

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
FilterSchemaType = TypeVar("FilterSchemaType", bound=BaseModel)

class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class SimpleCache:
    _cache: Dict[str, Any] = {}
    _cache_lock = asyncio.Lock()

    @classmethod
    def cached(cls, cache_key: Optional[str] = None, duration: float = 300):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                key = cache_key or f"{func.__module__}.{func.__name__}:{args}:{kwargs}"
                async with cls._cache_lock:
                    cached_result = cls._cache.get(key)
                    if cached_result:
                        result, expiration = cached_result
                        if expiration > time():
                            return result

                result = await func(*args, **kwargs)

                async with cls._cache_lock:
                    cls._cache[key] = (result, time() + duration)

                return result

            return wrapper

        return decorator

    @classmethod
    async def clear_cache(cls, key: Optional[str] = None):
        async with cls._cache_lock:
            if key:
                cls._cache.pop(key, None)
            else:
                cls._cache.clear()


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType, FilterSchemaType]):
    response_model: Type[ModelType]

    def __init__(
        self,
        cache_duration: float = settings.CACHE_DURATION,
        prefix: str = "",
    ) -> None:
        self.prefix = prefix
        self.base_url: str = f"{settings.API_BASE_URL.rstrip('/')}{settings.API_PREFIX}{prefix}"
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache_duration = cache_duration

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.BACKEND_API_KEY}",
                },
                json_serialize=lambda obj: dumps(obj, cls=DateTimeEncoder)
            )
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "BaseCRUD[ModelType]":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    @SimpleCache.cached()
    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] | BaseModel = None,
        response_model: Optional[Type[ModelType]] = None,
        is_list: bool = False,
    ) -> Union[ModelType, List[ModelType], None]:
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"

        if isinstance(json, BaseModel):
            json = json.model_dump(exclude_unset=True)

        try:
            async with session.request(
                method=method, url=url, params=params, json=json
            ) as response:
                if response.status == 404:
                    return [] if is_list else None
                elif response.status >= 400:
                    raise APIError(await response.text(), status_code=response.status)

                data = await response.json()
                model = response_model or self.response_model

                return (
                    [model.model_validate(item) for item in data]
                    if is_list
                    else model.model_validate(data)
                )
        except aiohttp.ClientError as e:
            raise APIError(str(e)) from e

    async def clear_cache(self, key: Optional[str] = None):
        await SimpleCache.clear_cache(key)

    async def create(self, data: CreateSchemaType) -> ModelType:
        return await self._request("POST", "", json=data.model_dump(exclude_none=True))

    async def update(self, id: Union[int, str], data: UpdateSchemaType) -> ModelType:
        return await self._request("PATCH", f"/{id}", json=data.model_dump(exclude_none=True))

    async def delete(self, id: Union[int, str]) -> ModelType:
        return await self._request("DELETE", f"/{id}")

    async def get(self, id: Union[int, str]) -> ModelType:
        return await self._request("GET", f"/{id}")

    async def get_by_user_id(
        self,
        user_id: Union[int, str],
        endpoint: Optional[str] = None,
        *,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[ModelType]] = None,
    ) -> ModelType:
        endpoint = endpoint or f"/users/{user_id}"
        return await self._request(
            "GET",
            endpoint,
            params=params or {"user_id": user_id},
            response_model=response_model,
        )

    async def get_list(
        self,
        endpoint: str = "",
        *,
        filters: Optional[FilterSchemaType] = None,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[ModelType]] = None,
        **kwargs: Any,
    ) -> List[ModelType]:
        if params is None:
            params = {}
        if filters:
            params.update(filters.model_dump(exclude_unset=True))

        if kwargs:
            params.update(kwargs)

        return await self._request(
            "GET",
            endpoint,
            params=params,
            response_model=response_model,
            is_list=True,
        )
