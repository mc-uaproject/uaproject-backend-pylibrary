from pydantic import BaseModel
from typing import Optional
from uap_backend.base import BaseBackendModel


class BalanceCreate(BaseModel):
    user_id: int
    currency: str


class BalanceResponse(BaseBackendModel):
    user_id: int
    currency: str
    amount: float


class BalanceUpdate(BaseModel):
    amount: float
