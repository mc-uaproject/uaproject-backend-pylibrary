from typing import TYPE_CHECKING

from uaproject_backend_schemas.models.service import Service

from uap_backend.cruds.base import BaseCRUD

if TYPE_CHECKING:
    from uaproject_backend_schemas.models.service import (
        ServiceFilter,
        ServiceSchemaCreate,
        ServiceSchemaResponse,
        ServiceSchemaUpdate,
    )
else:
    ServiceSchemaCreate = Service.schemas.create
    ServiceSchemaResponse = Service.schemas.response
    ServiceSchemaUpdate = Service.schemas.update
    ServiceFilter = Service.filter


class ServicesCRUDService(
    BaseCRUD[ServiceSchemaResponse, ServiceSchemaCreate, ServiceSchemaUpdate, ServiceFilter]
):
    response_model = ServiceSchemaResponse

    def __init__(self):
        super().__init__("/services")

    async def get_by_name(self, name: str, **kwargs) -> ServiceSchemaResponse:
        """
        Get a service by its name.
        """

        services = await self.get_list(filters=ServiceFilter(name=name), limit=1, **kwargs)
        return services[0]
