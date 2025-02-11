from pydantic import BaseModel
from uap_backend.base import BaseBackendModel


class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: str
    is_active: bool


class ServiceResponse(BaseBackendModel):
    name: str
    description: Optional[str]
    price: float
    currency: str
    is_active: bool


class ServiceUpdate(BaseModel):
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None
