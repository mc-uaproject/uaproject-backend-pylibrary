"""HTTP Client for UAProject API"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import aiohttp
from pydantic import BaseModel

from .config import settings
from .errors import (
    APIAuthenticationError,
    APIConnectionError,
    APIPermissionError,
    APIRateLimitError,
    APIServerError,
    ConfigurationError,
)

logger = logging.getLogger(__name__)


class HTTPClient:
    """Enhanced HTTP client with retry logic and proper error handling"""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or settings.FULL_API_URL
        self.api_key = api_key or settings.BACKEND_API_KEY
        self._session: Optional[aiohttp.ClientSession] = None

        if not self.api_key:
            raise ConfigurationError("BACKEND_API_KEY is required")

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
            connector = aiohttp.TCPConnector(
                limit=settings.MAX_CONNECTIONS,
                keepalive_timeout=settings.KEEPALIVE_TIMEOUT,
            )

            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self._get_default_headers(),
            )
        return self._session

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests"""
        return {
            "User-Agent": settings.USER_AGENT,
            "Content-Type": "application/json",
            "Accept": "application/json",
            settings.API_KEY_HEADER: f"{settings.BEARER_TOKEN_PREFIX} {self.api_key}",
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], BaseModel]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = urljoin(self.base_url, endpoint.lstrip("/"))

        # Prepare request data
        request_headers = headers or {}
        request_data = None

        if data is not None:
            if isinstance(data, BaseModel):
                request_data = data.model_dump(exclude_unset=True, exclude_none=True)
            else:
                request_data = data

        # Retry logic
        last_exception = None
        for attempt in range(settings.MAX_RETRIES + 1):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    json=request_data,
                    params=params,
                    headers=request_headers,
                    **kwargs,
                ) as response:
                    return await self._handle_response(response, endpoint)

            except aiohttp.ClientError as e:
                last_exception = APIConnectionError(
                    message=str(e),
                    endpoint=endpoint,
                )

                if attempt < settings.MAX_RETRIES:
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(f"Request failed, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    break

            except (APIRateLimitError, APIServerError) as e:
                # These errors are retryable
                last_exception = e

                if attempt < settings.MAX_RETRIES:
                    if isinstance(e, APIRateLimitError) and e.retry_after:
                        delay = min(e.retry_after, settings.MAX_RETRY_DELAY)
                    else:
                        delay = self._calculate_retry_delay(attempt)

                    logger.warning(f"API error, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    break

            except (APIAuthenticationError, APIPermissionError):
                # These errors are not retryable
                raise

        # If we get here, all retries failed
        raise last_exception or APIConnectionError("All retries failed", endpoint)

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = settings.RETRY_DELAY * (settings.RETRY_BACKOFF_FACTOR**attempt)
        return min(delay, settings.MAX_RETRY_DELAY)

    async def _handle_response(
        self, response: aiohttp.ClientResponse, endpoint: str
    ) -> Dict[str, Any]:
        """Handle HTTP response and convert to appropriate exception if needed"""
        try:
            response_data = await response.json()
        except Exception:
            response_data = {"detail": await response.text()}

        if response.status in (200, 201):
            return response_data
        if response.status == 204:
            return {}
        self._raise_for_status(response, endpoint, response_data)

    def _raise_for_status(
        self, response: aiohttp.ClientResponse, endpoint: str, response_data: dict
    ):
        if response.status == 401:
            raise APIAuthenticationError(
                endpoint, response_data.get("detail", "Authentication failed")
            )
        if response.status == 403:
            raise APIPermissionError(endpoint, response_data.get("detail", "Permission denied"))
        if response.status == 404:
            raise APIConnectionError("Not found", endpoint, 404, response_data)
        if response.status == 422:
            detail = response_data.get("detail", "Validation error")
            raise APIConnectionError(f"Validation error: {detail}", endpoint, 422, response_data)
        if response.status == 429:
            retry_after = None
            if "Retry-After" in response.headers:
                try:
                    retry_after = int(response.headers["Retry-After"])
                except ValueError:
                    pass
            raise APIRateLimitError(endpoint, retry_after)
        if response.status >= 500:
            raise APIServerError(
                endpoint, response.status, response_data.get("detail", "Server error")
            )
        raise APIConnectionError(
            f"Unexpected status code: {response.status}",
            endpoint,
            response.status,
            response_data,
        )

    # HTTP Methods
    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """GET request"""
        return await self._make_request("GET", endpoint, params=params, **kwargs)

    async def post(
        self, endpoint: str, data: Optional[Union[Dict[str, Any], BaseModel]] = None, **kwargs
    ) -> Dict[str, Any]:
        """POST request"""
        return await self._make_request("POST", endpoint, data=data, **kwargs)

    async def put(
        self, endpoint: str, data: Optional[Union[Dict[str, Any], BaseModel]] = None, **kwargs
    ) -> Dict[str, Any]:
        """PUT request"""
        return await self._make_request("PUT", endpoint, data=data, **kwargs)

    async def patch(
        self, endpoint: str, data: Optional[Union[Dict[str, Any], BaseModel]] = None, **kwargs
    ) -> Dict[str, Any]:
        """PATCH request"""
        return await self._make_request("PATCH", endpoint, data=data, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE request"""
        return await self._make_request("DELETE", endpoint, **kwargs)

    @asynccontextmanager
    async def _session_context(self):
        """Async context manager for session lifecycle"""
        try:
            yield self.session
        finally:
            pass  # Session will be closed by close() method

    async def close(self):
        """Close the HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
