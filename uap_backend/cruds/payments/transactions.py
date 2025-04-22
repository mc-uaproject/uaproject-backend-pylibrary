from typing import Any, Dict, Optional

from uaproject_backend_schemas.payments import (
    TransactionBase,
    TransactionFilterParams,
    TransactionResponse,
    TransactionUpdate,
)
from uaproject_backend_schemas.payments.transactions import TransactionType

from uap_backend.cruds.base import BaseCRUD


class TransactionCRUDService(
    BaseCRUD[TransactionResponse, TransactionBase, TransactionUpdate, TransactionFilterParams]
):
    response_model = TransactionResponse

    def __init__(self):
        super().__init__("/payments/transactions")

    async def get_transaction_statistics(
        self, transaction_type: Optional[TransactionType] = None, **kwargs
    ) -> Dict[str, Any]:
        """Get transaction statistics"""
        params = {"transaction_type": transaction_type} if transaction_type else {}
        return await self._request("/statistics", params=params, **kwargs)

    async def get_service_details(self, transaction_id: int, **kwargs) -> Dict[str, Any]:
        """Get service details for a specific transaction"""
        return await self.get(f"/details/{transaction_id}/service", **kwargs)
