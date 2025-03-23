from decimal import Decimal
from typing import Any, Dict, Optional

from uaproject_backend_schemas.payments import TransactionType

from uap_backend.base.schemas import (
    BaseUserBackendModel,
    BothPayloadBaseModel,
    DatetimeMixin,
    PayloadBaseModel,
    PayloadBoth,
)


class TransactionBasePayload(BaseUserBackendModel):
    """Base payload for transactions"""

    amount: Decimal
    type: TransactionType
    description: Optional[str] = None


class TransactionCreatedPayload(TransactionBasePayload):
    """Payload for transaction creation"""

    id: int
    user_id: int
    recipient_id: Optional[int] = None
    service_id: Optional[int] = None
    transaction_metadata: Optional[Dict[str, Any]] = None


class TransactionTypePayload(TransactionBasePayload):
    """Payload for transaction type updates"""

    id: int
    user_id: int
    amount: Decimal
    type: TransactionType
    description: Optional[str] = None


class TransactionAmountPayload(TransactionBasePayload):
    """Payload for transaction amount updates"""

    id: int
    user_id: int
    amount: Decimal
    type: TransactionType
    description: Optional[str] = None


class TransactionCreatedPayloadFull(PayloadBaseModel):
    """Full transaction created payload wrapper"""

    payload: TransactionCreatedPayload


class TransactionTypePayloadFull(BothPayloadBaseModel):
    """Full transaction type payload wrapper"""

    payload: dict[PayloadBoth, TransactionTypePayload]


class TransactionAmountPayloadFull(BothPayloadBaseModel):
    """Full transaction amount payload wrapper"""

    payload: dict[PayloadBoth, TransactionAmountPayload]


class TransactionFullMixins(TransactionCreatedPayload, DatetimeMixin):
    """Mixin combining transaction payload with timestamp"""

    pass
