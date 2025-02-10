# uap_backend/payments/transactions/crud.py
from typing import Optional, List, Dict, Any
from uap_backend.base.crud import BaseCRUD
from .schemas import (
    TransactionResponse,
    TransactionFilterParams,
    TransactionType,
    DepositTransaction,
    WithdrawalTransaction,
    TransferTransaction,
    SystemDepositTransaction,
    RefundTransaction,
    AdjustmentTransaction,
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
        return await self.get("/transactions", params=params, is_list=True)

    async def get_transaction_statistics(
        self, transaction_type: Optional[TransactionType] = None
    ) -> Dict[str, Any]:
        """Get transaction statistics"""
        params = {"transaction_type": transaction_type} if transaction_type else {}
        return await self.get("/transactions/statistics", params=params)

    async def get_transaction_details(self, transaction_id: int) -> TransactionResponse:
        """Get details of a specific transaction"""
        return await self.get(f"/transactions/details/{transaction_id}")

    async def get_transaction_service_details(
        self, transaction_id: int
    ) -> Dict[str, Any]:
        """Get service details for a specific transaction"""
        return await self.get(f"/transactions/details/{transaction_id}/service")

    async def create_deposit(self, data: DepositTransaction) -> TransactionResponse:
        """Create a deposit transaction"""
        return await self.post("/transactions/deposit", data=data)

    async def create_withdrawal(
        self, data: WithdrawalTransaction
    ) -> TransactionResponse:
        """Create a withdrawal transaction"""
        return await self.post("/transactions/withdrawal", data=data)

    async def create_transfer(self, data: TransferTransaction) -> TransactionResponse:
        """Create a transfer transaction"""
        return await self.post("/transactions/transfer", data=data)

    async def create_system_deposit(
        self, data: SystemDepositTransaction
    ) -> TransactionResponse:
        """Create a system deposit transaction (admin only)"""
        return await self.post("/transactions/system-deposit", data=data)

    async def create_refund(self, data: RefundTransaction) -> TransactionResponse:
        """Create a refund transaction (admin only)"""
        return await self.post("/transactions/refund", data=data)

    async def create_adjustment(
        self, data: AdjustmentTransaction
    ) -> TransactionResponse:
        """Create an adjustment transaction (admin only)"""
        return await self.post("/transactions/adjustment", data=data)


TransactionCRUDServiceInit = TransactionCRUDService()
