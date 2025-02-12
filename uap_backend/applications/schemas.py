from datetime import datetime
from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator
from uap_backend.base.schemas import (
    BaseUserBackendModel,
    BothPayloadBaseModel,
    DatetimeMixin,
    PayloadBaseModel,
    PayloadBoth,
)
from uap_backend.base.schemas import UserDefaultSort


class ApplicationStatus(StrEnum):
    ACCEPTED = "accepted"
    DECLINED = "declined"
    REVIEW = "review"
    EDITING = "editing"
    NOT_SENT = "not_sent"


class ApplicationSort(StrEnum):
    ID = UserDefaultSort.ID
    CREATED_AT = UserDefaultSort.CREATED_AT
    UPDATED_AT = UserDefaultSort.UPDATED_AT
    STATUS = "status"
    USER_ID = "user_id"


class ApplicationBase(BaseModel):
    birth_date: Optional[datetime] = None
    launcher: Optional[str] = Field(None, max_length=32)
    server_source: Optional[str] = Field(None, max_length=512)
    private_server_experience: Optional[str] = Field(None, max_length=1024)
    useful_skills: Optional[str] = Field(None, max_length=1024)
    conflict_reaction: Optional[str] = Field(None, max_length=1024)
    quiz_answer: Optional[str] = Field(None, max_length=1024)

    @model_validator(mode="before")
    @classmethod
    def truncate_fields(cls, values):
        max_lengths = {
            "launcher": 32,
            "server_source": 512,
            "private_server_experience": 1024,
            "useful_skills": 1024,
            "conflict_reaction": 1024,
            "quiz_answer": 1024,
        }
        for field, max_length in max_lengths.items():
            if field in values and values[field] and isinstance(values[field], str):
                values[field] = values[field][:max_length]
        return values


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(ApplicationBase):
    status: Optional[ApplicationStatus] = None
    editable_fields: Optional[List[str]] = None


class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int
    status: ApplicationStatus
    editable_fields: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationFilterParams(BaseModel):
    user_id: Optional[int] = None
    status: Optional[ApplicationStatus] = None
    min_created_at: Optional[datetime] = None
    max_created_at: Optional[datetime] = None
    min_updated_at: Optional[datetime] = None
    max_updated_at: Optional[datetime] = None


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
