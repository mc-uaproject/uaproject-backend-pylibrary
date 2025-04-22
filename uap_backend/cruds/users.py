from typing import Optional

from uaproject_backend_schemas import SortOrder
from uaproject_backend_schemas.users import (
    SearchMode,
    UserCreate,
    UserFilterParams,
    UserResponse,
    UserSort,
    UserUpdate,
)

from uap_backend.cruds.base import BaseCRUD

__all__ = ["UserCRUDService"]


class UserCRUDService(BaseCRUD[UserResponse, UserCreate, UserUpdate, UserFilterParams]):
    response_model = UserResponse

    def __init__(self):
        super().__init__("/users")

    async def get_by_discord_id(self, user_id: int, **kwargs) -> Optional[UserResponse]:
        """Get details of a specific user"""

        users = await self.get_list(filters=UserFilterParams(discord_id=user_id), **kwargs)
        return users[0] if users else None

    async def get_by_nickname(self, nickname: str, **kwargs) -> Optional[UserResponse]:
        """Get details of a specific user"""

        users = await self.get_list(filter=UserFilterParams(minecraft_nickname=nickname), **kwargs)
        return users[0] if users else None

    async def search_by_nickname(
        self,
        nickname: str,
        similar: Optional[float] = None,
        skip: int = 0,
        limit: int = 10,
        sort_by: UserSort = UserSort.CREATED_AT,
        order: SortOrder = SortOrder.ASC,
        filters: Optional[UserFilterParams] = None,
        search_mode: Optional[SearchMode] = None,
    ):
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

        return await self.get_list(
            "/list/search",
            filters=filters,
            params=params,
        )
