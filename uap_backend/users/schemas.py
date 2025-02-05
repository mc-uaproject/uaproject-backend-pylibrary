from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from uap_backend.base.schemas import BaseBackendModel


class DiscordUserResponse(BaseModel):
    id: int
    username: str
    discriminator: str
    avatar: Optional[str] = None
    email: Optional[str] = None
    verified: bool
    locale: str
    flags: int
    premium_type: Optional[int] = None
    public_flags: int


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(default=604800)
    refresh_token: Optional[str] = None
    scope: str = "identify email"


class RedirectUrlResponse(BaseModel):
    url: str
    state: Optional[str] = None


class UserTokenResponse(BaseModel):
    token: UUID
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


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
