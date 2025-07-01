from typing import TYPE_CHECKING

from uaproject_backend_schemas.models.balance import Balance

from uap_backend.cruds.base import BaseCRUD

if TYPE_CHECKING:
    from uaproject_backend_schemas.models.balance import (
        BalanceFilter,
        BalanceSchemaCreate,
        BalanceSchemaResponse,
        BalanceSchemaUpdate,
    )
else:
    BalanceSchemaCreate = Balance.schemas.create
    BalanceSchemaResponse = Balance.schemas.response
    BalanceSchemaUpdate = Balance.schemas.update
    BalanceFilter = Balance.filter


class BalanceCRUDService(
    BaseCRUD[BalanceSchemaResponse, BalanceSchemaCreate, BalanceSchemaUpdate, BalanceFilter]
):
    def __init__(self):
        super().__init__("/balances", "balance")

    async def get_by_identifier(self, identifier: str, **kwargs) -> BalanceSchemaResponse:
        """Get balance by identifier"""
        return await self._request("GET", f"/identifier/{identifier}", **kwargs)

    async def get_user_total(self, user_id: int, **kwargs) -> BalanceSchemaResponse:
        """Get total balance for user"""
        return await self._request("GET", f"/user/{user_id}/total", **kwargs)
