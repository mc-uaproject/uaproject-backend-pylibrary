from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uap_backend.base import BaseBackendModel


class DonationCreate(BaseModel):
    amount: float
    currency: str
    user_id: Optional[int] = None
    source: Optional[str] = None


class DonationResponse(BaseBackendModel):
    amount: float
    currency: str
    user_id: Optional[int]
    source: Optional[str]
    status: str
    created_at: str


class DonationUpdate(BaseModel):
    status: str
