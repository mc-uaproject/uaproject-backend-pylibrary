from typing import TYPE_CHECKING, Any, Dict, List, Optional

from uaproject_backend_schemas.models.schemas.transaction import TransactionType
from uaproject_backend_schemas.models.transaction import Transaction

from uap_backend.cruds.base import BaseCRUD

if TYPE_CHECKING:
    from uaproject_backend_schemas.models.transaction import (
        TransactionFilter,
        TransactionSchemaCreate,
        TransactionSchemaResponse,
        TransactionSchemaUpdate,
    )
else:
    TransactionSchemaCreate = Transaction.schemas.create
    TransactionSchemaResponse = Transaction.schemas.response
    TransactionSchemaUpdate = Transaction.schemas.update
    TransactionFilter = Transaction.filter


class TransactionCRUDService(
    BaseCRUD[
        TransactionSchemaResponse,
        TransactionSchemaCreate,
        TransactionSchemaUpdate,
        TransactionFilter,
    ]
):
    def __init__(self):
        super().__init__("/transactions", "transaction")

    async def get_transaction_statistics(
        self, transaction_type: Optional[TransactionType] = None, **kwargs
    ) -> Dict[str, Any]:
        """Get transaction statistics"""
        params = {"transaction_type": transaction_type} if transaction_type else {}
        return await self._request("GET", "/statistics", params=params, **kwargs)

    async def get_service_details(self, transaction_id: int, **kwargs) -> Dict[str, Any]:
        """Get service details for a specific transaction"""
        return await self._request("GET", f"/details/{transaction_id}/service", **kwargs)

    async def get_user_summary(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Get transaction summary for user"""
        return await self._request("GET", f"/{user_id}/summary", **kwargs)

    async def get_by_service(self, service_id: int, **kwargs) -> List[Dict[str, Any]]:
        """Get transactions by service ID"""
        return await self._request("GET", f"/service/{service_id}", **kwargs)

    async def get_by_type(self, transaction_type: str, **kwargs) -> List[Dict[str, Any]]:
        """Get transactions by type"""
        return await self._request("GET", f"/type/{transaction_type}", **kwargs)

    async def create_donatello_transaction(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create transaction from Donatello webhook"""
        return await self._request("POST", "/donatello", data=data, **kwargs)
