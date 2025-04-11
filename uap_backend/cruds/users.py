from typing import Optional

from uaproject_backend_schemas import SortOrder
from uaproject_backend_schemas.users import (
    UserCreate,
    UserFilterParams,
    UserResponse,
    UserSort,
    UserUpdate,
)

from uap_backend.cruds.base import BaseCRUD

__all__ = ["UserCRUDService", "UserCRUDServiceInit"]


class UserCRUDService(BaseCRUD[UserResponse, UserCreate, UserUpdate, UserFilterParams]):
    response_model = UserResponse

    def __init__(self, cache_duration=300):
        super().__init__(cache_duration, "/users")

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
        similar: int = 0.75,
        skip: int = 0,
        limit: int = 10,
        sort_by: UserSort = UserSort.CREATED_AT,
        order: SortOrder = SortOrder.ASC,
        filters: Optional[UserFilterParams] = None,
    ):
        return await self.get_list(
            "/list/search",
            filters=filters,
            params={
                "similar": similar,
                "skip": skip,
                "limit": limit,
                "sort_by": sort_by,
                "order": order,
                "query": nickname,
            },
        )
