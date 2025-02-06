from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from uap_backend.base.schemas import (
    BaseBackendModel,
    BaseUserBackendModel,
    BothPayloadBaseModel,
    DatetimeMixin,
    PayloadBaseModel,
    PayloadBoth,
)


class ApplicationStatus(str, Enum):
    """Enum representing possible application statuses"""

    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    REVIEW = "REVIEW"
    EDITING = "EDITING"
    NOT_SENT = "NOT_SENT"


class ApplicationSort(str, Enum):
    """Enum for sorting application list"""

    CREATED_AT = "created_at"
    STATUS = "status"
    USER_ID = "user_id"


class ApplicationBase(BaseModel):
    """Base model for application creation and update"""

    birth_date: Optional[datetime] = None
    launcher: Optional[str] = Field(default=None, max_length=32)
    server_source: Optional[str] = Field(default=None, max_length=512)
    private_server_experience: Optional[str] = Field(default=None, max_length=1024)
    useful_skills: Optional[str] = Field(default=None, max_length=1024)
    conflict_reaction: Optional[str] = Field(default=None, max_length=1024)
    quiz_answer: Optional[str] = Field(default=None, max_length=1024)


class ApplicationCreate(ApplicationBase):
    """Model for creating a new application"""

    model_config = ConfigDict(extra="forbid")


class ApplicationUpdate(ApplicationBase):
    """Model for updating an existing application"""

    model_config = ConfigDict(extra="forbid")


class ApplicationResponse(ApplicationBase, BaseBackendModel):
    """Full application response model"""

    user_id: int
    status: ApplicationStatus = ApplicationStatus.NOT_SENT
    editable_fields: List[str] = Field(
        default_factory=lambda: [
            "birth_date",
            "launcher",
            "server_source",
            "private_server_experience",
            "useful_skills",
            "conflict_reaction",
            "quiz_answer",
        ]
    )

    class Config:
        from_attributes = True


class ApplicationStatusPayload(BaseUserBackendModel):
    """Payload for application status"""

    status: ApplicationStatus


class ApplicationFormPayload(ApplicationStatusPayload):
    """Detailed form payload"""

    birth_date: Optional[datetime] = None
    launcher: Optional[str] = None
    server_source: Optional[str] = None
    private_server_experience: Optional[str] = None
    useful_skills: Optional[str] = None
    conflict_reaction: Optional[str] = None
    quiz_answer: Optional[str] = None


class ApplicationFormPayloadFull(PayloadBaseModel):
    """Full form payload wrapper"""

    payload: ApplicationFormPayload


class ApplicationStatusPayloadFull(BothPayloadBaseModel):
    """Full status payload wrapper"""

    payload: dict[PayloadBoth, ApplicationStatusPayload]


class ApplicationFullMixins(ApplicationFormPayload, DatetimeMixin):
    """Mixin combining form payload with timestamp"""

    pass


class EditableFieldsResponse(BaseModel):
    """Response for retrieving editable fields"""

    editable_fields: List[str]


class ApplicationFieldEditableResponse(BaseModel):
    """Response for checking if a specific field is editable"""

    editable: bool
