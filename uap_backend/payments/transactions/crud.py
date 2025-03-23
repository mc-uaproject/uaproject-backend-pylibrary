from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional, overload

from uaproject_backend_schemas.payments import TransactionFilterParams, TransactionResponse

from uap_backend.base.crud import BaseCRUD
from uap_backend.payments.transactions.payload import (
    TransactionType,
)


class TransactionCRUDService(BaseCRUD[TransactionResponse]):
    response_model = TransactionResponse

    async def list_transactions(
        self,
        filters: Optional[TransactionFilterParams] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> List[TransactionResponse]:
        """Get list of transactions with filtering and pagination"""
        params = {
            "skip": skip,
            "limit": limit,
            "sort_by": sort_by,
            "order": order,
            **(filters.model_dump(exclude_none=True) if filters else {}),
        }
        return await self.get("/payments/transactions", params=params, is_list=True)

    async def get_transaction_statistics(
        self, transaction_type: Optional[TransactionType] = None
    ) -> Dict[str, Any]:
        """Get transaction statistics"""
        params = {"transaction_type": transaction_type} if transaction_type else {}
        return await self.get("/payments/transactions/statistics", params=params)

    async def get_transaction_details(self, transaction_id: int) -> TransactionResponse:
        """Get details of a specific transaction"""
        return await self.get(f"/payments/transactions/details/{transaction_id}")

    async def get_transaction_service_details(self, transaction_id: int) -> Dict[str, Any]:
        """Get service details for a specific transaction"""
        return await self.get(f"/payments/transactions/details/{transaction_id}/service")

    @overload
    async def create_transaction(
        self,
        *,
        amount: Decimal,
        type: Literal[TransactionType.DEPOSIT],
        description: Optional[str],
    ) -> TransactionResponse: ...

    @overload
    async def create_transaction(
        self,
        *,
        amount: Decimal,
        type: Literal[TransactionType.WITHDRAWAL],
        description: Optional[str],
    ) -> TransactionResponse: ...

    @overload
    async def create_transaction(
        self,
        *,
        amount: Decimal,
        type: Literal[TransactionType.TRANSFER],
        recipient_id: int,
        description: Optional[str],
    ) -> TransactionResponse: ...

    @overload
    async def create_transaction(
        self,
        *,
        amount: Decimal,
        type: Literal[TransactionType.PURCHASE],
        service_id: int,
        description: Optional[str],
    ) -> TransactionResponse: ...

    @overload
    async def create_transaction(
        self, *, amount: Decimal, type: Literal[TransactionType.SYSTEM], recipient_id
    ): ...

    async def create_transaction(self, **kwargs: Any) -> TransactionResponse:
        """Create a transaction with specific parameters."""
        data = TransactionResponse(id=0, **kwargs)

        return await self.post("/payments/transactions", data=data)


TransactionCRUDServiceInit = TransactionCRUDService()
