from typing import Dict, List, Optional

from uaproject_backend_schemas import SortOrder
from uaproject_backend_schemas.users import UserFilterParams, UserResponse, UserSort, UserUpdate

from uap_backend.base.crud import BaseCRUD

__all__ = ["UserCRUDService", "UserCRUDServiceInit"]


class UserCRUDService(BaseCRUD[UserResponse]):
    response_model = UserResponse

    async def get_user_details(self, user_id: int) -> Optional[UserResponse]:
        """Get details of a specific user"""
        return await self.get(f"/users/details/{user_id}")

    async def get_user_details_by_discord_id(self, user_id: int) -> Optional[UserResponse]:
        """Get details of a specific user"""

        users = await self.list_users(UserFilterParams(discord_id=user_id))
        if users:
            return users[0]

    async def list_users(
        self,
        filters: Optional[UserFilterParams] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: UserSort = UserSort.CREATED_AT,
        order: SortOrder = SortOrder.DESC,
    ) -> List[UserResponse]:
        """Get list of users with filtering and pagination"""
        params = {
            "skip": skip,
            "limit": limit,
            "sort_by": sort_by,
            "order": order,
            **(filters.model_dump(exclude_none=True) if filters else {}),
        }
        return await self.get("/users", params=params, is_list=True)

    async def update_user(self, user_id: int, data: UserUpdate) -> UserResponse:
        """Update user details"""
        return await self.patch(f"/users/{user_id}", data=data)

    async def delete_user(self, user_id: int) -> Dict[str, str]:
        """Delete a user"""
        return await self.delete(f"/users/{user_id}")

    async def search_users_by_nickname(
        self, minecraft_nickname: str, limit: int = 50
    ) -> List[UserResponse]:
        """Search users by Minecraft nickname"""
        params = {"minecraft_nickname": minecraft_nickname, "limit": limit, "skip": 0}
        return await self.get("/users/search", params=params, is_list=True)


UserCRUDServiceInit = UserCRUDService()
