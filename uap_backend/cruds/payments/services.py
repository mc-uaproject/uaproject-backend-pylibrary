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

    async def get_by_name(
        self,
        name: str,
    ) -> ServiceResponse:
        """
        Get a service by its name.
        """
        return await self._request(
            method="GET",
            endpoint="/",
            params={"service_name": name},
        )


ServicesCRUDServiceInit = ServicesCRUDService()
