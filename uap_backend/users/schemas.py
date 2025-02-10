from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, model_validator
from uap_backend.base.schemas import BaseBackendModel


class TokenResponse(BaseModel):
    token: UUID


class RolePayload(BaseBackendModel):
    name: str
    display_name: str | None
    permissions: list[str]
    weight: int


class UserPayload(BaseBackendModel):
    discord_id: str
    minecraft_nickname: str | None
    is_superuser: bool | None

    roles: list


class UserUpdate(BaseModel):
    minecraft_nickname: Optional[str] = None
    discord_id: Optional[int] = None
    is_superuser: Optional[bool] = None

    @model_validator(mode="before")
    def validate_minecraft_nickname(cls, values):
        nickname = values.get("minecraft_nickname")
        if nickname is not None:
            if not 3 <= len(nickname) <= 16:
                raise ValueError(
                    "Minecraft nickname must be between 3 and 16 characters."
                )
            if not nickname.isalnum() and "_" not in nickname:
                raise ValueError(
                    "Minecraft nickname can only contain letters, numbers, and underscores."
                )
        return values


class UserResponse(BaseModel):
    id: int
    discord_id: Optional[int] = None
    minecraft_nickname: Optional[str] = None
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime
    token: Optional[TokenResponse] = None

    class Config:
        from_attributes = True


class UserFilterParams(BaseModel):
    user_id: Optional[int] = None
    discord_id: Optional[int] = None
    minecraft_nickname: Optional[str] = None
    is_superuser: Optional[bool] = None
    role_name: Optional[str] = None
