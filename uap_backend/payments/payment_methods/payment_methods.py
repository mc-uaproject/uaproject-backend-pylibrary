from pydantic import BaseModel
from typing import Optional
from .base import BaseBackendModel


class PaymentMethodCreate(BaseModel):
    name: str
    method_type: str
    is_active: bool


class PaymentMethodResponse(BaseBackendModel):
    name: str
    method_type: str
    is_active: bool
