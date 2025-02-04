from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApplicationBase(BaseModel):
    user_id: int
    form_data: Dict[str, Any]
    status: ApplicationStatus = ApplicationStatus.PENDING


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    form_data: Optional[Dict[str, Any]] = None
    status: Optional[ApplicationStatus] = None


class Application(ApplicationBase):
    id: int
    created_at: datetime
    updated_at: datetime
