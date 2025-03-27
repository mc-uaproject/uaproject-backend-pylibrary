
from uaproject_backend_schemas.payments import BalanceFilterParams, BalanceResponse, BalanceUpdate

from uap_backend.cruds.base import BaseCRUD


class BalanceCRUDService(BaseCRUD[BalanceResponse, None, BalanceUpdate, BalanceFilterParams]):
    response_model = BalanceResponse

    def __init__(self, cache_duration=300):
        super().__init__(cache_duration, "/payments/balances")

    async def get_by_key(self, identifier: str) -> BalanceResponse:
        """Get balance by key/identifier"""
        return await self._get(f"/key/{identifier}")


BalanceCRUDServiceInit = BalanceCRUDService()
