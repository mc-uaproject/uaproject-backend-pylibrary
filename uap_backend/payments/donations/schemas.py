from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr


class DonationCreate(BaseModel):
    amount: Decimal
    currency: str = "UAH"
    donor_name: Optional[str] = None
    donor_email: Optional[EmailStr] = None
    message: Optional[str] = None
    source: Optional[str] = None
    user_id: Optional[int] = None
    balance_id: Optional[int] = None
    donatello_transaction_id: Optional[str] = None


class DonationResponse(BaseModel):
    id: int
    amount: Decimal
    currency: str
    donor_name: Optional[str]
    donor_email: Optional[EmailStr]
    message: Optional[str]
    source: Optional[str]
    user_id: Optional[int]
    balance_id: Optional[int]
    donatello_transaction_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DonationUpdate(BaseModel):
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    donor_name: Optional[str] = None
    donor_email: Optional[EmailStr] = None
    message: Optional[str] = None
    source: Optional[str] = None


class DonationFilterParams(BaseModel):
    sort_by: Optional[str] = "amount"
    skip: int = 0
    limit: int = 50
    user_id: Optional[int] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    source: Optional[str] = None
