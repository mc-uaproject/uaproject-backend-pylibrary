from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str
    description: str
    price: float
    currency: str = "UAH"
    category: Optional[str] = None
    is_active: bool = True


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str
    price: str
    currency: str
    category: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
