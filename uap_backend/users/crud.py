from typing import List, Optional

from uap_backend.base.crud import BaseCRUD
from uap_backend.base.schemas import RoleSortField, SortOrder, UserSort
from uap_backend.users.schemas import (
    RolePayload,
    UserPayload,
    AccessTokenResponse,
    RedirectUrlResponse,
    UserTokenResponse,
    DiscordUserResponse,
)


class UsersCrudService(BaseCRUD):
    def __init__(self):
        super().__init__()

    # User operations
    async def get_user_by_id(self, user_id: int) -> UserPayload:
        data = await self._request("GET", f"/users/{user_id}")
        return UserPayload.model_validate(data)

    async def get_current_user(self) -> UserPayload:
        data = await self._request("GET", "/users/me")
        return UserPayload.model_validate(data)

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: UserSort = UserSort.ROLE,
        order: SortOrder = SortOrder.ASC,
        minecraft_nickname: Optional[str] = None,
        discord_id: Optional[int] = None,
        role_name: Optional[str] = None,
    ) -> List[UserPayload]:
        params = {"skip": skip, "limit": limit, "sort_by": sort_by, "order": order}
        if minecraft_nickname:
            params["minecraft_nickname"] = minecraft_nickname
        if discord_id:
            params["discord_id"] = discord_id
        if role_name:
            params["role_name"] = role_name

        data = await self._request("GET", "/users", params=params)
        return [UserPayload.model_validate(user) for user in data]

    async def update_minecraft_nickname(self, user_id: int, new_nickname: str) -> dict:
        return await self._request(
            "PATCH",
            f"/users/{user_id}/minecraft-nickname",
            params={"new_nickname": new_nickname},
        )

    async def get_roles(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: RoleSortField = RoleSortField.WEIGHT,
        order: SortOrder = SortOrder.DESC,
    ) -> List[RolePayload]:
        params = {"skip": skip, "limit": limit, "sort_by": sort_by, "order": order}
        data = await self._request("GET", "/users/roles", params=params)
        return [RolePayload.model_validate(role) for role in data]

    async def create_role(self, name: str) -> RolePayload:
        data = await self._request("POST", "/users/roles/create", params={"name": name})
        return RolePayload.model_validate(data)

    async def add_permissions_to_role(
        self, role_id: int, urls: List[str]
    ) -> RolePayload:
        data = await self._request(
            "POST", f"/users/roles/{role_id}/permissions/add", json={"urls": urls}
        )
        return RolePayload.model_validate(data)

    async def assign_role(self, user_id: int, role_id: int) -> dict:
        return await self._request("POST", f"/users/roles/assign/{user_id}/{role_id}")

    async def delete_role(self, role_id: int) -> dict:
        return await self._request("DELETE", f"/users/roles/{role_id}/delete")

    # Discord integration
    async def get_discord_redirect_url(
        self, host: str = "http://localhost"
    ) -> RedirectUrlResponse:
        data = await self._request(
            "GET", "/users/auth/discord/redirect", params={"host": host}
        )
        return RedirectUrlResponse.model_validate(data)

    async def get_discord_access_token(
        self, code: str, redirect_uri: str
    ) -> AccessTokenResponse:
        data = await self._request(
            "GET",
            "/users/auth/discord/token",
            params={"code": code, "redirect_uri": redirect_uri},
        )
        return AccessTokenResponse.model_validate(data)

    async def get_discord_user_info(self, token: str) -> DiscordUserResponse:
        headers = {"Authorization": f"Bearer {token}"}
        data = await self._request("GET", "/users/auth/discord/user", headers=headers)
        return DiscordUserResponse.model_validate(data)

    # Token management
    async def get_current_user_token(self) -> UserTokenResponse:
        data = await self._request("GET", "/users/token/current")
        return UserTokenResponse.model_validate(data)

    async def get_user_token(self, user_id: int) -> UserTokenResponse:
        data = await self._request("GET", f"/users/token/user/{user_id}")
        return UserTokenResponse.model_validate(data)
