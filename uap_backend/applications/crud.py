from typing import List, Optional
from .schemas import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationStatus,
)
from uap_backend.base.crud import BaseCRUD


class ApplicationsCrudService(BaseCRUD):
    def __init__(self):
        super().__init__()
        self.base_url = "/applications"

    async def create_application(
        self, application: ApplicationCreate
    ) -> ApplicationResponse:
        """Create a new application"""
        data = await self._request(
            "POST", self.base_url, json=application.model_dump(exclude_unset=True)
        )
        return ApplicationResponse.model_validate(data)

    async def get_current_user_application(self) -> ApplicationResponse:
        """Get the current user's application"""
        data = await self._request("GET", f"{self.base_url}/me")
        return ApplicationResponse.model_validate(data)

    async def get_application_by_id(self, application_id: int) -> ApplicationResponse:
        """Get an application by its ID"""
        data = await self._request("GET", f"{self.base_url}/{application_id}")
        return ApplicationResponse.model_validate(data)

    async def get_application_by_user_id(self, user_id: int) -> ApplicationResponse:
        """Get an application by user ID"""
        data = await self._request("GET", f"{self.base_url}/by-user/{user_id}")
        return ApplicationResponse.model_validate(data)

    async def get_applications(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        order: str = "desc",
        status: Optional[ApplicationStatus] = None,
        user_id: Optional[int] = None,
    ) -> List[ApplicationResponse]:
        """
        Get a list of applications with optional filtering and sorting

        :param skip: Number of records to skip
        :param limit: Maximum number of records to return
        :param sort_by: Field to sort by (created_at, status, user_id)
        :param order: Sort order (asc or desc)
        :param status: Filter by application status
        :param user_id: Filter by specific user ID
        """
        params = {"skip": skip, "limit": limit, "sort_by": sort_by, "order": order}

        if status is not None:
            params["status"] = status
        if user_id is not None:
            params["user_id"] = user_id

        data = await self._request("GET", self.base_url, params=params)
        return [ApplicationResponse.model_validate(app) for app in data]

    async def update_application(
        self, application_id: int, application_update: ApplicationUpdate
    ) -> ApplicationResponse:
        """Update an existing application"""
        data = await self._request(
            "PATCH",
            f"{self.base_url}/{application_id}",
            json=application_update.model_dump(exclude_unset=True),
        )
        return ApplicationResponse.model_validate(data)

    async def delete_application(self, application_id: int) -> dict:
        """Delete an application"""
        return await self._request("DELETE", f"{self.base_url}/{application_id}")

    async def update_application_status(
        self, application_id: int, status: ApplicationStatus
    ) -> ApplicationResponse:
        """Update the status of an application"""
        data = await self._request(
            "POST", f"{self.base_url}/{application_id}/status/{status}"
        )
        return ApplicationResponse.model_validate(data)

    async def check_field_editable(self, application_id: int, field_name: str) -> bool:
        """Check if a specific field is editable"""
        data = await self._request(
            "GET", f"{self.base_url}/{application_id}/field/{field_name}/editable"
        )
        return data.get("editable", False)

    async def get_editable_fields(self, application_id: int) -> List[str]:
        """Get all editable fields for a specific application"""
        data = await self._request("GET", f"{self.base_url}/{application_id}/editables")
        return data.get("editable_fields", [])
