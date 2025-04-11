from uaproject_backend_schemas.payments.donations import (
    DonationCreate,
    DonationFilterParams,
    DonationResponse,
    DonationUpdate,
)

from uap_backend.cruds.base import BaseCRUD


class DonationCRUDService(
    BaseCRUD[DonationResponse, DonationCreate, DonationUpdate, DonationFilterParams]
):
    response_model = DonationResponse

    def __init__(self, cache_duration=300):
        super().__init__(cache_duration, "/payments/donations")

    async def get_statistics(self, **kwargs) -> dict:
        """
        Get statistics for donations.
        """
        return await self._request(method="GET", endpoint="/statistics/summary", **kwargs)
