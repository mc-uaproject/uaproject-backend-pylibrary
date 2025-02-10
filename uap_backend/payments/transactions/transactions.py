from pydantic import BaseModel
from typing import Optional
from .base import BaseBackendModel


class TransactionResponse(BaseBackendModel):
    amount: str
    currency: str
    sender_id: Optional[int]
    recipient_id: Optional[int]
    description: Optional[str]


class DepositTransaction(BaseModel):
    amount: float
    currency: str = "UAH"
    balance_id: Optional[int]
    description: Optional[str]
