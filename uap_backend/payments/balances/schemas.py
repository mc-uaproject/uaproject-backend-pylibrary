from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class BalanceUpdate(BaseModel):
    amount: Optional[Decimal] = None


class BalanceResponse(BaseModel):
    id: int
    user_id: int
    identifier: UUID
    amount: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {UUID: str}


class BalanceFilterParams(BaseModel):
    user_id: Optional[int] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
