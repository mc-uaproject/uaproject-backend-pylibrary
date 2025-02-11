from pydantic import BaseModel
from typing import Optional
from uap_backend.base import BaseBackendModel


class TransactionCreate(BaseModel):
    amount: float
    currency: str
    user_id: int
    transaction_type: str


class TransactionResponse(BaseBackendModel):
    amount: float
    currency: str
    user_id: int
    transaction_type: str
    status: str
    created_at: str


class TransactionUpdate(BaseModel):
    status: str
