from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TransactionResponse(BaseModel):
    amount: str
    currency: str
    balance_id: int
    type: str
    description: str
    id: int
    user_id: int
    sender_id: int
    recipient_id: int
    service_id: int
    reference_id: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DepositCreate(BaseModel):
    amount: int
    currency: str
    balance_id: int
    type: str = "deposit"
    description: str


class WithdrawalCreate(BaseModel):
    amount: int
    currency: str
    balance_id: int
    type: str = "withdrawal"
    description: str


class TransferCreate(BaseModel):
    amount: int
    currency: str
    balance_id: int
    type: str = "transfer"
    description: str
    recipient_id: int


class SystemDepositCreate(BaseModel):
    amount: int
    currency: str
    balance_id: int
    type: str = "system"
    description: str
    user_id: int
    reference_id: str
    metadata: Dict[str, Any]


class RefundCreate(BaseModel):
    amount: int
    currency: str
    balance_id: int
    type: str = "refund"
    description: str
    original_transaction_id: int
    reason: str
    user_id: int


class AdjustmentCreate(BaseModel):
    amount: int
    currency: str
    balance_id: int
    type: str = "adjustment"
    description: str
    user_id: int
    reason: str
    reference_id: str


class TransactionFilterParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)
    sort_by: str = Field(
        default="created_at", pattern="^(id|created_at|updated_at|amount|type)$"
    )
    order: str = Field(default="desc", pattern="^(asc|desc)$")
    user_id: Optional[int] = None
    type: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    currency: Optional[str] = None
