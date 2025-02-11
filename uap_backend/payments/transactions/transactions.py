from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class TransactionResponse(BaseModel):
    id: int
    user_id: Optional[int]
    amount: Decimal
    currency: str
    type: str
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    amount: Decimal
    currency: str
    type: str
    user_id: Optional[int] = None


class TransactionFilterParams(BaseModel):
    user_id: Optional[int] = None
    type: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    currency: Optional[str] = None
