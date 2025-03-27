import asyncio
from functools import wraps
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


class CacheEntry:
    def __init__(self, value, expiration: float):
        self.value = value
        self.expiration = expiration


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType, FilterSchemaType]):
    response_model: Type[ModelType]

    def __init__(
        self,
        cache_duration: float = 300,
        prefix: str = "",
    ) -> None:
        self.prefix = prefix
        self.base_url: str = f"{settings.API_BASE_URL.rstrip('/')}{settings.API_PREFIX}{prefix}"
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, CacheEntry] = {}
        self._cache_lock = asyncio.Lock()
        self._default_cache_duration = cache_duration

    def cached(self, cache_key: Optional[str] = None, duration: Optional[float] = None):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                key = cache_key or f"{func.__module__}.{func.__name__}:{args}:{kwargs}"

                async with self._cache_lock:
                    cache_entry = self._cache.get(key)
                    if cache_entry and cache_entry.expiration > asyncio.get_event_loop().time():
                        return cache_entry.value

                result = await func(*args, **kwargs)

                async with self._cache_lock:
                    cache_duration_to_use = duration or self._default_cache_duration
                    self._cache[key] = CacheEntry(
                        result, asyncio.get_event_loop().time() + cache_duration_to_use
                    )

                return result

            return wrapper

        return decorator

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

        async with self._cache_lock:
            current_time = asyncio.get_event_loop().time()
            self._cache = {k: v for k, v in self._cache.items() if v.expiration > current_time}

    async def __aenter__(self) -> "BaseCRUD[ModelType]":
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
        response_model: Optional[Type[ModelType]] = None,
        is_list: bool = False,
        cache_duration: Optional[float] = None,
    ) -> Union[ModelType, List[ModelType], None]:
        cache_key = f"{method}:{endpoint}:{params}:{json}"

        if method == "GET":
            async with self._cache_lock:
                cache_entry = self._cache.get(cache_key)
                if cache_entry and cache_entry.expiration > asyncio.get_event_loop().time():
                    return cache_entry.value

        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
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

                result = (
                    [model.model_validate(item) for item in data]
                    if is_list
                    else model.model_validate(data)
                )

                if method == "GET":
                    async with self._cache_lock:
                        self._cache[cache_key] = CacheEntry(
                            result,
                            asyncio.get_event_loop().time()
                            + (cache_duration or self._default_cache_duration),
                        )

                return result

        except aiohttp.ClientError as e:
            raise APIError(str(e))

    @cached()
    async def _get(
        self,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[ModelType]] = None,
        is_list: bool = False,
        cache_duration: Optional[float] = None,
    ) -> Union[ModelType, List[ModelType]]:
        return await self._request(
            "GET",
            endpoint,
            params=params,
            response_model=response_model,
            is_list=is_list,
            cache_duration=cache_duration,
        )

    async def _post(
        self,
        endpoint: str,
        *,
        data: Optional[BaseModel] = None,
        response_model: Optional[Type[ModelType]] = None,
    ) -> ModelType:
        json_data = data.model_dump(exclude_unset=True) if data else None
        return await self._request("POST", endpoint, json=json_data, response_model=response_model)

    async def _patch(
        self,
        endpoint: str,
        *,
        data: Optional[BaseModel] = None,
        response_model: Optional[Type[ModelType]] = None,
    ) -> ModelType:
        json_data = data.model_dump(exclude_unset=True) if data else None
        return await self._request("PATCH", endpoint, json=json_data, response_model=response_model)

    async def _delete(
        self,
        endpoint: str,
        *,
        response_model: Optional[Type[ModelType]] = None,
    ) -> ModelType:
        return await self._request("DELETE", endpoint, response_model=response_model)

    async def clear_cache(self, key: Optional[str] = None):
        async with self._cache_lock:
            if key:
                self._cache.pop(key, None)
            else:
                self._cache.clear()

    async def create(self, data: CreateSchemaType) -> ModelType:
        return await self._post("", data)

    async def update(self, id: Union[int, str], data: UpdateSchemaType) -> ModelType:
        return await self._patch(f"/{id}", data)

    async def delete(self, id: Union[int, str]) -> ModelType:
        return await self._delete(f"/{id}")

    async def get(self, id: Union[int, str]) -> ModelType:
        return await self._get(id)

    async def get_by_user_id(
        self,
        user_id: Union[int, str],
        endpoint: Optional[str] = None,
        *,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[ModelType]] = None,
        cache_duration: Optional[float] = None,
    ) -> ModelType:
        endpoint = endpoint or f"/users/{user_id}"
        return await self._get(
            endpoint,
            params=params or {"user_id": user_id},
            response_model=response_model,
            cache_duration=cache_duration,
        )

    async def get_list(
        self,
        endpoint: str,
        *,
        filters: Optional[FilterSchemaType] = None,
        params: Optional[Dict[str, Any]] = {},
        response_model: Optional[Type[ModelType]] = None,
        cache_duration: Optional[float] = None,
        **kwargs: Any,
    ) -> List[ModelType]:
        if filters:
            params.update(filters.model_dump(exclude_unset=True))

        if kwargs:
            params.update(kwargs)

        return await self._get(
            endpoint,
            params=params,
            response_model=response_model,
            is_list=True,
            cache_duration=cache_duration,
        )
