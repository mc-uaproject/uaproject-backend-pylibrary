
from uaproject_backend_schemas.applications import (
    ApplicationCreate,
    ApplicationFilterParams,
    ApplicationResponse,
    ApplicationStatus,
    ApplicationUpdate,
)

from uap_backend.cruds.base import BaseCRUD


class ApplicationCRUDService(
    BaseCRUD[ApplicationResponse, ApplicationCreate, ApplicationUpdate, ApplicationFilterParams]
):
    response_model = ApplicationResponse

    async def update_status(
        self, application_id: int, status: ApplicationStatus
    ) -> ApplicationResponse:
        """Update application status"""
        return await self._request("POST", f"/{application_id}/status/{status.value}")


ApplicationCRUDServiceInit = ApplicationCRUDService()
