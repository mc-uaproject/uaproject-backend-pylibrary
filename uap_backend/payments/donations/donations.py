from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uap_backend.base import BaseBackendModel


class DonationCreate(BaseModel):
    amount: float
    currency: str
    donor_name: str
    donor_email: str
    message: Optional[str] = None
    source: str
    user_id: int
    balance_id: int
    donatello_transaction_id: Optional[str] = None


class DonationResponse(BaseBackendModel):
    amount: str
    currency: str
    donor_name: str
    donor_email: str
    message: Optional[str]
    source: str
    user_id: int
    balance_id: int
    donatello_transaction_id: Optional[str]
