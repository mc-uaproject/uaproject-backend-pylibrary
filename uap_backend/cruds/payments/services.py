from uaproject_backend_schemas.payments.services import (
    ServiceCreate,
    ServiceFilterParams,
    ServiceResponse,
    ServiceUpdate,
)

from uap_backend.cruds.base import BaseCRUD


class ServicesCRUDService(
    BaseCRUD[ServiceResponse, ServiceCreate, ServiceUpdate, ServiceFilterParams]
):
    response_model = ServiceResponse

    def __init__(self, cache_duration=300):
        super().__init__(cache_duration, "/payments/services")

    async def get_by_name(self, name: str, **kwargs) -> ServiceResponse:
        """
        Get a service by its name.
        """

        services = await self.get_list(filters=ServiceFilterParams(name=name), limit=1, **kwargs)
        return services[0]
