"""Role CRUD Service based on OpenAPI analysis"""

from typing import TYPE_CHECKING, Dict, List

from uaproject_backend_schemas.models.role import Role
from uaproject_backend_schemas.models.user import User

from uap_backend.cruds.base import BaseCRUD

if TYPE_CHECKING:
    from uaproject_backend_schemas.models.role import (
        RoleFilter,
        RoleSchemaCreate,
        RoleSchemaResponse,
        RoleSchemaUpdate,
    )
    from uaproject_backend_schemas.models.user import UserSchemaResponse
else:
    UserSchemaResponse = User.schemas.response
    RoleSchemaCreate = Role.schemas.create
    RoleSchemaResponse = Role.schemas.response
    RoleSchemaUpdate = Role.schemas.update
    RoleFilter = Role.filter


class RoleCRUDService(BaseCRUD[RoleSchemaResponse, RoleSchemaCreate, RoleSchemaUpdate, RoleFilter]):
    """CRUD service for role management"""

    def __init__(self):
        super().__init__("/roles", "role")

    async def get_assignable(self, **kwargs) -> List[RoleSchemaResponse]:
        """Get roles that can be assigned by current user"""
        return await self._request("GET", "/assignable", **kwargs)

    async def get_users_by_role(self, role_id: int, **kwargs) -> List[UserSchemaResponse]:
        """Get users with specific role"""
        return await self._request("GET", f"/{role_id}/users", **kwargs)

    async def get_users_by_roles(
        self, role_ids: List[int], **kwargs
    ) -> Dict[str, List[UserSchemaResponse]]:
        """Get users grouped by roles"""
        params = {"role_ids": role_ids}
        return await self._request("GET", "/users-by-roles", params=params, **kwargs)
