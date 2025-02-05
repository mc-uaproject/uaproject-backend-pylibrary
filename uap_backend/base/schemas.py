from datetime import datetime
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel

PayloadBoth = Literal["before", "after"]


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class UserSort(str, Enum):
    ROLE = "role"
    NICKNAME = "nickname"
    DISCORD_ID = "discord_id"


class RoleSortField(str, Enum):
    NAME = "name"
    WEIGHT = "weight"
    CREATED_AT = "created_at"


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
