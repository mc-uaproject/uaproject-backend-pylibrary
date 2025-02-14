from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, HttpUrl


class WebhookStatus(StrEnum):
    ACTIVE = "active"
    UNRESPONSIVE = "unresponsive"
    PROCESSING = "processing"
    ERROR = "error"


class WebhookBase(BaseModel):
    endpoint: HttpUrl
    scopes: Dict[str, bool]
    authorization: Optional[str] = None


class WebhookCreate(WebhookBase):
    status: WebhookStatus = WebhookStatus.ACTIVE


class WebhookUpdate(WebhookBase):
    status: Optional[WebhookStatus] = None


class WebhookResponse(WebhookBase):
    id: int
    status: WebhookStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookFilterParams(BaseModel):
    user_id: Optional[int] = None
    status: Optional[WebhookStatus] = None
    min_created_at: Optional[datetime] = None
    max_created_at: Optional[datetime] = None


class WebhookHandlerResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

    @classmethod
    def create(cls, success: bool, message: str, data: Any = None) -> "WebhookHandlerResponse":
        try:
            return cls(success=success, message=message, data=data)
        except Exception:
            return cls(success=success, message=message, data=None)
