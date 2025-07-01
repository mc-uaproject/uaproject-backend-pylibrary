"""Enhanced BaseCRUD following backend patterns without caching"""

import logging
from typing import Any, Dict, Generic, List, Optional, Type, Union

from uaproject_backend_schemas.base import (
    CreateSchemaType,
    FilterSchemaType,
    ModelType,
    UpdateSchemaType,
)

from uap_backend.core.client import HTTPClient
from uap_backend.core.errors import CRUDNotFoundError, CRUDValidationError

logger = logging.getLogger(__name__)


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType, FilterSchemaType]):
    """Enhanced BaseCRUD with singleton pattern like backend"""

    # Singleton pattern - use class type as key (like backend)
    _instances: Dict[Type, "BaseCRUD"] = {}

    def __new__(cls, *args, **kwargs):
        """Singleton pattern implementation like backend BaseCRUD"""
        if cls in cls._instances:
            return cls._instances[cls]

        instance = super().__new__(cls)
        cls._instances[cls] = instance
        return instance

    def __init__(self, endpoint: str = "", model_name: str = ""):
        """Initialize CRUD service"""
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.endpoint = endpoint.rstrip("/")
        self.model_name = model_name or self.__class__.__name__.replace("CRUDService", "").lower()
        self._client: Optional[HTTPClient] = None
        self._initialized = True

        logger.debug(f"Initialized {self.__class__.__name__} for endpoint: {self.endpoint}")

    @property
    def client(self) -> HTTPClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = HTTPClient()
        return self._client

    def _build_endpoint(self, path: str = "") -> str:
        """Build full endpoint path"""
        if path.startswith("/"):
            return path  # Absolute path

        base = self.endpoint
        if path:
            base = f"{base.rstrip('/')}/{path.lstrip('/')}"
        return base

    def _prepare_filters(
        self, filters: Optional[FilterSchemaType] = None, **kwargs
    ) -> Dict[str, Any]:
        """Prepare query parameters from filters"""
        params = {}

        if filters:
            if hasattr(filters, "model_dump"):
                params.update(filters.model_dump(exclude_unset=True, exclude_none=True))
            elif isinstance(filters, dict):
                params.update(filters)

        # Add additional params
        params.update(kwargs)

        # Remove None values
        return {k: v for k, v in params.items() if v is not None}

    def _prepare_data(
        self, data: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare request data"""
        if hasattr(data, "model_dump"):
            return data.model_dump(exclude_unset=True, exclude_none=True)
        elif isinstance(data, dict):
            return data
        else:
            raise CRUDValidationError(f"Invalid data type: {type(data)}")

    # CRUD Operations
    async def get(self, obj_id: Union[int, str], **kwargs) -> Dict[str, Any]:
        """Get single object by ID"""
        endpoint = self._build_endpoint(str(obj_id))

        try:
            return await self.client.get(endpoint, **kwargs)
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise CRUDNotFoundError(self.model_name, obj_id)
            raise

    async def get_many(
        self, filters: Optional[FilterSchemaType] = None, skip: int = 0, limit: int = 50, **kwargs
    ) -> List[Dict[str, Any]]:
        """Get multiple objects with filtering and pagination"""
        params = self._prepare_filters(filters, skip=skip, limit=limit, **kwargs)
        endpoint = self._build_endpoint()

        response = await self.client.get(endpoint, params=params)

        # Handle different response formats
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            # Handle paginated response
            return response.get("items", response.get("data", [response]))
        else:
            return []

    async def create(
        self, data: Union[CreateSchemaType, Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Create new object"""
        endpoint = self._build_endpoint()
        prepared_data = self._prepare_data(data)

        return await self.client.post(endpoint, data=prepared_data, **kwargs)

    async def update(
        self, obj_id: Union[int, str], data: Union[UpdateSchemaType, Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Update existing object"""
        endpoint = self._build_endpoint(str(obj_id))
        prepared_data = self._prepare_data(data)

        try:
            return await self.client.patch(endpoint, data=prepared_data, **kwargs)
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise CRUDNotFoundError(self.model_name, obj_id)
            raise

    async def delete(self, obj_id: Union[int, str], **kwargs) -> bool:
        """Delete object by ID"""
        endpoint = self._build_endpoint(str(obj_id))

        try:
            await self.client.delete(endpoint, **kwargs)
            return True
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise CRUDNotFoundError(self.model_name, obj_id)
            raise

    # Helper methods
    async def exists(self, obj_id: Union[int, str]) -> bool:
        """Check if object exists"""
        try:
            await self.get(obj_id)
            return True
        except CRUDNotFoundError:
            return False

    async def count(self, filters: Optional[FilterSchemaType] = None, **kwargs) -> int:
        """Count objects matching filters"""
        params = self._prepare_filters(filters, **kwargs)
        endpoint = self._build_endpoint("count")

        try:
            response = await self.client.get(endpoint, params=params)
            if isinstance(response, dict):
                return response.get("count", 0)
            return int(response)
        except Exception:
            # Fallback: get all and count
            items = await self.get_many(filters=filters, limit=1000, **kwargs)
            return len(items)

    # Advanced operations
    async def bulk_create(
        self, data_list: List[Union[CreateSchemaType, Dict[str, Any]]], **kwargs
    ) -> List[Dict[str, Any]]:
        """Create multiple objects"""
        endpoint = self._build_endpoint("bulk")
        prepared_data = [self._prepare_data(data) for data in data_list]

        return await self.client.post(endpoint, data={"items": prepared_data}, **kwargs)

    async def bulk_update(
        self,
        updates: List[Dict[str, Any]],  # [{"id": 1, "data": {...}}, ...]
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """Update multiple objects"""
        endpoint = self._build_endpoint("bulk")

        return await self.client.patch(endpoint, data={"items": updates}, **kwargs)

    async def bulk_delete(self, obj_ids: List[Union[int, str]], **kwargs) -> bool:
        """Delete multiple objects"""
        endpoint = self._build_endpoint("bulk")

        await self.client.delete(endpoint, data={"ids": obj_ids}, **kwargs)
        return True

    # Custom request method for specific endpoints
    async def _request(
        self,
        method: str,
        path: str = "",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make custom request to specific endpoint"""
        endpoint = self._build_endpoint(path)

        if method.upper() == "GET":
            return await self.client.get(endpoint, params=params, **kwargs)
        elif method.upper() == "POST":
            return await self.client.post(endpoint, data=data, params=params, **kwargs)
        elif method.upper() == "PUT":
            return await self.client.put(endpoint, data=data, params=params, **kwargs)
        elif method.upper() == "PATCH":
            return await self.client.patch(endpoint, data=data, params=params, **kwargs)
        elif method.upper() == "DELETE":
            return await self.client.delete(endpoint, params=params, **kwargs)
        else:
            raise CRUDValidationError(f"Unsupported HTTP method: {method}")

    # Resource cleanup
    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.close()
            self._client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def get_model_name(self) -> str:
        """Get model name for debugging"""
        return self.model_name
