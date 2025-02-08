from pydantic import BaseModel
from typing import Optional
from .base import BaseBackendModel


class BalanceResponse(BaseBackendModel):
    user_id: int
    identifier: str
    amount: str


class BalanceUpdate(BaseModel):
    amount: Optional[float]
