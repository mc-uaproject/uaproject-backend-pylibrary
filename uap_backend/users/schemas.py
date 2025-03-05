from datetime import datetime
from enum import StrEnum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, model_validator

from uap_backend.base.schemas import (
    BaseBackendModel,
    BaseUserBackendModel,
    BothPayloadBaseModel,
    PayloadBaseModel,
    PayloadBoth,
    UserDefaultSort,
)


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

    class Config:
        from_attributes = True


class UserFilterParams(BaseModel):
    user_id: Optional[int] = None
    discord_id: Optional[int] = None
    minecraft_nickname: Optional[str] = None
    is_superuser: Optional[bool] = None
    role_name: Optional[str] = None


class UserSort(StrEnum):
    ID = UserDefaultSort.ID
    CREATED_AT = UserDefaultSort.CREATED_AT
    UPDATED_AT = UserDefaultSort.UPDATED_AT
    MINECRAFT_NICKNAME = "minecraft_nickname"
    DISCORD_ID = "discord_id"
    ROLE_WEIGHT = "role_weight"


class BaseUserPayload(BaseUserBackendModel):
    """Base payload for user-related operations"""
    discord_id: Optional[int] = None
    minecraft_nickname: Optional[str] = None
    is_superuser: Optional[bool] = False


class UserCreatedPayload(BaseUserPayload):
    """Payload for user creation"""
    id: int
    created_at: datetime
    roles: List[int] = []


class UserUpdatedPayload(BaseModel):
    """Payload for user updates"""
    id: int
    discord_id: Optional[int] = None
    minecraft_nickname: Optional[str] = None
    is_superuser: Optional[bool] = None


class UserRolesPayload(BaseModel):
    """Payload for user roles management"""
    id: int
    roles: List[int]
    updated_at: datetime


class UserCreatedPayloadFull(PayloadBaseModel):
    """Full user created payload wrapper"""
    payload: UserCreatedPayload


class UserUpdatedPayloadFull(BothPayloadBaseModel):
    """Full user updated payload wrapper"""
    payload: dict[PayloadBoth, UserUpdatedPayload]


class UserRolesPayloadFull(BothPayloadBaseModel):
    """Full user roles update payload wrapper"""
    payload: dict[PayloadBoth, UserRolesPayload]


class MinecraftNicknamePayload(BaseModel):
    """Payload for Minecraft nickname scope"""
    id: int
    discord_id: Optional[int] = None
    minecraft_nickname: Optional[str] = None


class DiscordIdPayload(BaseModel):
    """Payload for Discord ID scope"""
    id: int
    discord_id: int
    minecraft_nickname: Optional[str] = None


class MinecraftNicknamePayloadFull(BothPayloadBaseModel):
    """Full payload wrapper for Minecraft nickname scope"""
    payload: dict[PayloadBoth, MinecraftNicknamePayload]


class DiscordIdPayloadFull(BothPayloadBaseModel):
    """Full payload wrapper for Discord ID scope"""
    payload: dict[PayloadBoth, DiscordIdPayload]
