from pydantic import BaseModel
from typing import Optional
from uap_backend.base import BaseBackendModel


class PurchaseCreate(BaseModel):
    service_id: int
    quantity: int
    user_id: Optional[int] = None


class PurchaseResponse(BaseBackendModel):
    service_id: int
    quantity: int
    user_id: Optional[int]
    status: str
    created_at: str


class PurchaseUpdate(BaseModel):
    status: str
