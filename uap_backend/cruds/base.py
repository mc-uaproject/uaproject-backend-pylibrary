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
from uap_backend.exceptions import APIError, RequestError

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
    _instances: Dict[str, Any] = {}
    _all_sessions: List[aiohttp.ClientSession] = []
    _session_lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        key = f"{cls.__name__}:{args}:{sorted(kwargs.items()) if kwargs else ''}"

        if key not in cls._instances:
            instance = super(BaseCRUD, cls).__new__(cls)
            cls._instances[key] = instance
            instance._initialized = False

        return cls._instances[key]

    def __init__(
        self,
        prefix: str = "",
        cache_duration: float = settings.CACHE_DURATION,
    ) -> None:
        if not hasattr(self, "_initialized") or not self._initialized:
            self.prefix = prefix
            self.base_url: str = f"{settings.API_BASE_URL.rstrip('/')}{settings.API_PREFIX}{prefix}"
            self._session: Optional[aiohttp.ClientSession] = None
            self._cache_duration = cache_duration
            self._initialized = True

    @classmethod
    def _instance(cls, *args, **kwargs):
        """Get the singleton instance without reinitializing if it exists"""
        key = f"{cls.__name__}:{args}:{sorted(kwargs.items()) if kwargs else ''}"

        return cls._instances[key] if key in cls._instances else cls(*args, **kwargs)

    @classmethod
    async def close_all_sessions(cls):
        """Close all sessions created by any BaseCRUD instance"""
        async with cls._session_lock:
            for session in cls._all_sessions:
                if not session.closed:
                    await session.close()
            cls._all_sessions.clear()

    async def _get_session(self) -> aiohttp.ClientSession:
        async with self.__class__._session_lock:
            if not self._session or self._session.closed:
                self._session = aiohttp.ClientSession(
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {settings.BACKEND_API_KEY}",
                    },
                    json_serialize=lambda obj: dumps(obj, cls=DateTimeEncoder),
                )
                self.__class__._all_sessions.append(self._session)
            return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            async with self.__class__._session_lock:
                if self._session in self.__class__._all_sessions:
                    self.__class__._all_sessions.remove(self._session)
            self._session = None

    async def __aenter__(
        self,
    ) -> "BaseCRUD[ModelType, CreateSchemaType, UpdateSchemaType, FilterSchemaType]":
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
        json: Optional[Dict[str, Any]] | BaseModel = None,
        response_model: Optional[Type[ModelType]] = None,
        is_list: bool = False,
        _raise: bool = True,
    ) -> Union[ModelType, List[ModelType], None]:
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"

        if isinstance(json, BaseModel):
            json = json.model_dump(exclude_unset=True)

        try:
            async with session.request(
                method=method, url=url, params=params, json=json
            ) as response:
                data = await response.json()
                if response.status == 404:
                    result = [] if is_list else None
                elif response.status >= 400:
                    raise RequestError(data.get("detail"), url, params)
                else:
                    model = response_model or self.response_model
                    result = (
                        [model.model_validate(item) for item in data]
                        if is_list
                        else model.model_validate(data)
                    )

                if _raise and not result:
                    if isinstance(data, list) and data:
                        data = data[0]

                    error_message = (
                        data.get('detail', None) if isinstance(data, dict)
                        else str(data)
                    )

                    raise RequestError(
                        message=f"Empty or None response received\n```cs\n{error_message}```",
                        endpoint=url,
                        params=params,
                        original_error=None,
                    )

                return result

        except RequestError as e:
            raise e

        except aiohttp.ClientError as e:
            raise APIError(str(e)) from e

    async def clear_cache(self, key: Optional[str] = None):
        await SimpleCache.clear_cache(key)

    async def create(self, data: CreateSchemaType, **kwargs) -> ModelType:
        return await self._request("POST", "", json=data.model_dump(exclude_none=True), **kwargs)

    async def update(self, id: Union[int, str], data: UpdateSchemaType, **kwargs) -> ModelType:
        return await self._request(
            "PATCH", f"/{id}", json=data.model_dump(exclude_none=True), **kwargs
        )

    async def delete(self, id: Union[int, str], **kwargs) -> ModelType:
        return await self._request("DELETE", f"/{id}", **kwargs)

    async def get(self, id: Union[int, str], **kwargs) -> ModelType:
        return await self._request("GET", f"/{id}", **kwargs)

    async def get_by_user_id(
        self,
        user_id: Union[int, str],
        endpoint: Optional[str] = None,
        *,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[ModelType]] = None,
        **kwargs,
    ) -> ModelType:
        endpoint = endpoint or f"/users/{user_id}"
        return await self._request(
            "GET",
            endpoint,
            params=params or {"user_id": user_id},
            response_model=response_model,
            **kwargs,
        )

    async def get_list(
        self,
        endpoint: str = "",
        *,
        filters: Optional[FilterSchemaType] = None,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[ModelType]] = None,
        _raise: bool = True,
        **kwargs: Any,
    ) -> List[ModelType]:
        if params is None:
            params = {}

        if filters := kwargs.pop("filter", filters):
            params.update(filters.model_dump(exclude_unset=True))

        if kwargs:
            params.update(kwargs)

        return await self._request(
            "GET",
            endpoint,
            params=params,
            response_model=response_model,
            is_list=True,
            _raise=_raise,
        )
