from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str
    category: Optional[str] = None
    is_active: bool = True


class ServiceResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
