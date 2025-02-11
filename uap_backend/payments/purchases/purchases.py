from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class PurchaseCreate(BaseModel):
    service_id: int
    quantity: int
    user_id: Optional[int] = None
    status: str
    time_spent: Optional[int] = None
    transaction_id: Optional[int] = None


class PurchasedItemResponse(BaseModel):
    id: int
    user_id: Optional[int]
    service_id: int
    quantity: int
    created_at: datetime
    status: str
    time_spent: int
    transaction_id: int
    updated_at: datetime

    class Config:
        from_attributes = True


class PurchaseFilterParams(BaseModel):
    user_id: Optional[int] = None
    service_id: Optional[int] = None
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    min_time_spent: Optional[int] = None
    max_time_spent: Optional[int] = None


class PurchaseTimeUpdate(BaseModel):
    time_spent: int


class UserPurchaseStatisticsResponse(BaseModel):
    total_purchases: int
    total_time_spent: int
    active_purchases: int
    cancelled_purchases: int


class UserTotalTimeResponse(BaseModel):
    total_time_spent: int
