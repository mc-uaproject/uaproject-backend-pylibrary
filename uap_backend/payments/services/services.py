from pydantic import BaseModel
from uap_backend.base import BaseBackendModel


class ServiceCreate(BaseModel):
    name: str
    category: str
    is_active: bool


class ServiceResponse(BaseBackendModel):
    name: str
    category: str
    is_active: bool
