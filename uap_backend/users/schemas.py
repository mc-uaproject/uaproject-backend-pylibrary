from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from uap_backend.base.schemas import (
    BaseUserBackendModel,
    BothPayloadBaseModel,
    PayloadBaseModel,
    PayloadBoth,
)


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
