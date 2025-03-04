from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, field_validator

from uap_backend.base.schemas import (
    BaseUserBackendModel,
    BothPayloadBaseModel,
    DatetimeMixin,
    PayloadBaseModel,
    PayloadBoth,
    UserDefaultSort,
)


class TransactionType(StrEnum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PURCHASE = "purchase"
    DONATION = "donation"
    SYSTEM = "system"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class TransactionBase(BaseModel):
    amount: Decimal
    recipient_id: int
    type: TransactionType
    description: Optional[str] = None
    transaction_metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None


class TransactionFilterParams(BaseModel):
    user_id: Optional[int] = None
    type: Optional[TransactionType] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    currency: Optional[str] = None


class TransactionSort(StrEnum):
    ID = UserDefaultSort.ID
    CREATED_AT = UserDefaultSort.CREATED_AT
    UPDATED_AT = UserDefaultSort.UPDATED_AT
    AMOUNT = "amount"
    TYPE = "type"


class DepositTransaction(TransactionBase):
    type: TransactionType = TransactionType.DEPOSIT

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != TransactionType.DEPOSIT:
            raise ValueError("Transaction type must be DEPOSIT")
        return v


class TransferTransaction(TransactionBase):
    type: TransactionType = TransactionType.TRANSFER
    recipient_id: int

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != TransactionType.TRANSFER:
            raise ValueError("Transaction type must be TRANSFER")
        return v


class PurchaseTransaction(TransactionBase):
    type: TransactionType = TransactionType.PURCHASE
    amount: Decimal | None = None
    service_id: int

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != TransactionType.PURCHASE:
            raise ValueError("Transaction type must be PURCHASE")
        return v


class WithdrawalTransaction(TransactionBase):
    type: TransactionType = TransactionType.WITHDRAWAL

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != TransactionType.WITHDRAWAL:
            raise ValueError("Transaction type must be WITHDRAWAL")
        return v


class SystemDepositTransaction(TransactionBase):
    type: TransactionType = TransactionType.SYSTEM
    user_id: int
    metadata: Optional[dict] = None


class RefundTransaction(TransactionBase):
    type: TransactionType = TransactionType.REFUND
    original_transaction_id: int
    reason: str
    user_id: int


class AdjustmentTransaction(TransactionBase):
    type: TransactionType = TransactionType.ADJUSTMENT
    user_id: int
    reason: str


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    type: Optional[TransactionType] = None
    description: Optional[str] = None
    service_id: Optional[int] = None
    metadata: Optional[dict] = None


class TransactionResponse(TransactionBase):
    id: int
    recipient_id: int
    service_id: Optional[int] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        from_attributes = True


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
