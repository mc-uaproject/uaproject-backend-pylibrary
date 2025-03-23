from typing import Dict, List, Optional

from uaproject_backend_schemas.payments import BalanceFilterParams, BalanceResponse, BalanceUpdate

from uap_backend.base.crud import BaseCRUD


class BalanceCRUDService(BaseCRUD[BalanceResponse]):
    response_model = BalanceResponse

    async def create_balance(self) -> BalanceResponse:
        """Create a new balance for the current user"""
        return await self.post("/payments/balances")

    async def get_balance(self, balance_id: int) -> BalanceResponse:
        """Get a specific balance by ID"""
        return await self.get(f"/payments/balances/{balance_id}")

    async def get_balance_by_key(self, identifier: str) -> BalanceResponse:
        """Get balance by key/identifier"""
        return await self.get(f"/payments/balances/key/{identifier}")

    async def get_user_balance(self, user_id: int) -> BalanceResponse:
        """Get balance for a specific user"""
        return await self.get(f"/payments/balances/users/{user_id}")

    async def get_my_balance(self) -> BalanceResponse:
        """Get current user's balance"""
        return await self.get("/payments/balances/users/me")

    async def list_balances(
        self,
        filters: Optional[BalanceFilterParams] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "amount",
        order: str = "asc",
    ) -> List[BalanceResponse]:
        """Get list of balances with filtering and pagination"""
        params = {
            "skip": skip,
            "limit": limit,
            "sort_by": sort_by,
            "order": order,
            **(filters.model_dump(exclude_none=True) if filters else {}),
        }
        return await self.get("/payments/balances", params=params, is_list=True)

    async def update_balance(
        self, balance_id: int, data: BalanceUpdate
    ) -> BalanceResponse:
        """Update a balance"""
        return await self.patch(f"/payments/balances/{balance_id}", data=data)

    async def delete_balance(self, balance_id: int) -> Dict[str, str]:
        """Delete a balance"""
        return await self.delete(f"/payments/balances/{balance_id}")


BalanceCRUDServiceInit = BalanceCRUDService()
