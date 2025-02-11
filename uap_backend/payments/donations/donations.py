from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class DonationCreate(BaseModel):
    amount: Decimal
    user_id: Optional[int] = None
    currency: str = "UAH"
    source: Optional[str] = None


class DonationResponse(BaseModel):
    id: int
    user_id: Optional[int]
    amount: Decimal
    currency: str
    source: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DonationUpdate(BaseModel):
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    source: Optional[str] = None


class DonationFilterParams(BaseModel):
    user_id: Optional[int] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    currency: Optional[str] = None
