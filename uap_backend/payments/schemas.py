from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DonationBase(BaseModel):
    amount: str
    currency: str
    donor_name: str
    donor_email: str
    message: Optional[str] = None
    source: str


class DonationCreate(DonationBase):
    pass


class DonationUpdate(BaseModel):
    amount: Optional[str] = None
    currency: Optional[str] = None
    donor_name: Optional[str] = None
    donor_email: Optional[str] = None
    message: Optional[str] = None
    source: Optional[str] = None


class Donation(DonationBase):
    id: int
    user_id: int
    balance_id: int
    donatello_transaction_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
