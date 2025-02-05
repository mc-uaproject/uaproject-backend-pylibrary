from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel

PayloadBoth = Literal["before", "after"]

class BaseBackendModel(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime


class BaseUserBackendModel(BaseBackendModel):
    user_id: int


class PayloadBaseModel(BaseModel):
    action: str
    scope: str
    payload: dict[str, Any]


class BothPayloadBaseModel(BaseModel):
    payload: dict[Literal["before", "after"], dict[str, Any]]


PayloadModels = PayloadBaseModel | BothPayloadBaseModel