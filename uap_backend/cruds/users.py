from typing import TYPE_CHECKING, Optional

from uaproject_backend_schemas.base import SortOrder
from uaproject_backend_schemas.models.schemas.user import SearchMode
from uaproject_backend_schemas.models.user import User

from uap_backend.cruds.base import BaseCRUD

if TYPE_CHECKING:
    from uaproject_backend_schemas.models.user import (
        UserFilter,
        UserSchemaCreate,
        UserSchemaResponse,
        UserSchemaUpdate,
        UserSort,
    )
else:
    UserSchemaCreate = User.schemas.create
    UserSchemaResponse = User.schemas.response
    UserSchemaUpdate = User.schemas.update
    UserFilter = User.filter
    UserSort = User.sort

__all__ = ["UserCRUDService"]


class UserCRUDService(BaseCRUD[UserSchemaResponse, UserSchemaCreate, UserSchemaUpdate, UserFilter]):
    def __init__(self):
        super().__init__("/users", "user")

    async def get_by_discord_id(self, user_id: int, **kwargs) -> Optional[UserSchemaResponse]:
        """Get user by Discord ID"""
        users = await self.get_many(filters=UserFilter(discord_id=user_id), **kwargs)
        return users[0] if users else None

    async def get_by_nickname(self, nickname: str, **kwargs) -> Optional[UserSchemaResponse]:
        """Get user by Minecraft nickname"""
        users = await self.get_many(filters=UserFilter(minecraft_nickname=nickname), **kwargs)
        return users[0] if users else None

    async def search_by_nickname(
        self,
        nickname: str,
        similar: Optional[float] = None,
        skip: int = 0,
        limit: int = 10,
        sort_by: UserSort = UserSort.CREATED_AT,
        order: SortOrder = SortOrder.ASC,
        filters: Optional[UserFilter] = None,
        search_mode: Optional[SearchMode] = None,
        **kwargs,
    ):
        """Search users by nickname with advanced options"""
        params = {
            "skip": skip,
            "limit": limit,
            "sort_by": sort_by,
            "order": order,
            "query": nickname,
        }

        if search_mode == SearchMode.ANY:
            params["search_mode"] = search_mode
        elif similar is not None:
            params["similar"] = similar

        return await self._request("GET", "/list/search", params=params, **kwargs)
