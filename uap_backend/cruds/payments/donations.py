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

    def __init__(self):
        super().__init__("/payments/donations")

    async def get_statistics(self, **kwargs) -> dict:
        """
        Get statistics for donations.
        """
        return await self._request(method="GET", endpoint="/statistics/summary", **kwargs)
