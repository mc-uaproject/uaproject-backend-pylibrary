from uaproject_backend_schemas.payments.balances import (
    BalanceFilterParams,
    BalanceResponse,
    BalanceUpdate,
)

from uap_backend.cruds.base import BaseCRUD


class BalanceCRUDService(BaseCRUD[BalanceResponse, None, BalanceUpdate, BalanceFilterParams]):
    response_model = BalanceResponse

    def __init__(self):
        super().__init__("/payments/balances")

    async def get_by_key(self, identifier: str, **kwargs) -> BalanceResponse:
        """Get balance by key/identifier"""
        return await self._request("GET", f"/key/{identifier}", **kwargs)
