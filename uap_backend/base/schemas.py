from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from pydantic import BaseModel

PayloadBoth = Literal["before", "after"]


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class DefaultSort(StrEnum):
    ID = "id"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class UserDefaultSort(StrEnum):
    ID = DefaultSort.ID
    CREATED_AT = DefaultSort.CREATED_AT
    UPDATED_AT = DefaultSort.UPDATED_AT
    USER_ID = "user_id"


class DatetimeMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class BaseBackendModel(BaseModel):
    id: int


class BaseUserBackendModel(BaseBackendModel):
    user_id: int


class PayloadBaseModel(BaseModel):
    action: str
    scope: str
    payload: dict[str, Any]


class BothPayloadBaseModel(BaseModel):
    payload: dict[Literal["before", "after"], dict[str, Any]]


PayloadModels = PayloadBaseModel | BothPayloadBaseModel
