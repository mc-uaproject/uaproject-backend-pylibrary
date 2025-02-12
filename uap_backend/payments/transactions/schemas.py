from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, field_validator

from uap_backend.base.schemas import UserDefaultSort


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
    currency: str = "UAH"
    balance_id: int | None = None
    type: TransactionType
    description: Optional[str] = None


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
    reference_id: Optional[str] = None
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
    reference_id: Optional[str] = None


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    type: Optional[TransactionType] = None
    description: Optional[str] = None
    service_id: Optional[int] = None
    metadata: Optional[dict] = None


class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    balance_id: int
    sender_id: Optional[int]
    recipient_id: Optional[int]
    service_id: Optional[int]
    reference_id: Optional[str]
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
