from typing import TYPE_CHECKING, Literal

from uaproject_backend_schemas.models.application import Application
from uaproject_backend_schemas.models.schemas.server import ServerAccessStatus

from uap_backend.cruds.base import BaseCRUD

if TYPE_CHECKING:
    from uaproject_backend_schemas.models.application import (
        ApplicationFilter,
        ApplicationSchemaCreate,
        ApplicationSchemaResponse,
        ApplicationSchemaUpdate,
    )
else:
    ApplicationSchemaCreate = Application.schemas.create
    ApplicationSchemaResponse = Application.schemas.response
    ApplicationSchemaUpdate = Application.schemas.update
    ApplicationFilter = Application.filter


class ApplicationCRUDService(
    BaseCRUD[
        ApplicationSchemaResponse,
        ApplicationSchemaCreate,
        ApplicationSchemaUpdate,
        ApplicationFilter,
    ]
):
    def __init__(self):
        super().__init__("/applications", "application")

    async def update_status(
        self, application_id: Literal["me"] | int, status: ServerAccessStatus, **kwargs
    ) -> ApplicationSchemaResponse:
        """Update application status"""
        return await self._request("POST", f"/{application_id}/status/{status.value}", **kwargs)
