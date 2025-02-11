from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PurchaseCreate(BaseModel):
    service_id: int
    quantity: int
    user_id: Optional[int] = None


class PurchasedItemResponse(BaseModel):
    id: int
    user_id: Optional[int]
    service_id: int
    quantity: int
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseFilterParams(BaseModel):
    user_id: Optional[int] = None
    service_id: Optional[int] = None
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
