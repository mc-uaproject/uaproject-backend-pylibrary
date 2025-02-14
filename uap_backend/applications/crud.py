from typing import Any, Dict, List, Optional

from uap_backend.base.crud import BaseCRUD

from .schemas import (
    ApplicationCreate,
    ApplicationFilterParams,
    ApplicationResponse,
    ApplicationStatus,
    ApplicationUpdate,
)


class ApplicationCRUDService(BaseCRUD[ApplicationResponse]):
    response_model = ApplicationResponse

    async def get_user_application(
        self,
        user_id: int,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[ApplicationResponse]:
        """Get application for a specific user"""
        params = params or {}
        params['user_id'] = user_id
        try:
            return await self.get(f"/applications/users/{user_id}", params=params)
        except Exception:
            return None

    async def create(
        self,
        data: ApplicationCreate,
        user_id: Optional[int] = None
    ) -> ApplicationResponse:
        """Create a new application"""
        return await self.post("/applications", data=data)

    async def update(
        self,
        application_id: int,
        data: ApplicationUpdate,
        user_id: Optional[int] = None
    ) -> ApplicationResponse:
        """Update an existing application"""
        return await self.patch(f"/applications/{application_id}", data=data)

    async def get_list(
        self,
        filters: Optional[ApplicationFilterParams] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = 'created_at',
        order: str = 'desc'
    ) -> List[ApplicationResponse]:
        """Get list of applications with filtering and pagination"""
        params = {
            'skip': skip,
            'limit': limit,
            'sort_by': sort_by,
            'order': order,
            **(filters.model_dump(exclude_none=True) if filters else {})
        }
        return await self.get("/applications", params=params, is_list=True)

    async def update_status(
        self,
        application_id: int,
        status: ApplicationStatus,
        user_id: Optional[int] = None
    ) -> ApplicationResponse:
        """Update application status"""
        return await self.post(f"/applications/{application_id}/status/{status.value}")

    async def check_field_editable(
        self,
        application_id: int,
        field_name: str,
        user_id: Optional[int] = None
    ) -> bool:
        """Check if a specific field is editable"""
        response = await self.get(f"/applications/{application_id}/field/{field_name}/editable")
        return response.get('editable', False)

    async def get_editable_fields(
        self,
        application_id: int,
        user_id: Optional[int] = None
    ) -> List[str]:
        """Get list of editable fields for an application"""
        response = await self.get(f"/applications/{application_id}/editables")
        return response.get('editable_fields', [])

ApplicationCRUDServiceInit = ApplicationCRUDService()
