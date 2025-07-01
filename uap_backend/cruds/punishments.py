from typing import TYPE_CHECKING, Literal

from uaproject_backend_schemas.models.punishment import Punishment
from uaproject_backend_schemas.models.schemas.punishment import PunishmentStatus

from uap_backend.cruds.base import BaseCRUD

if TYPE_CHECKING:
    from uaproject_backend_schemas.models.punishment import (
        PunishmentFilter,
        PunishmentSchemaCreate,
        PunishmentSchemaResponse,
        PunishmentSchemaUpdate,
    )
else:
    PunishmentSchemaCreate = Punishment.schemas.create
    PunishmentSchemaResponse = Punishment.schemas.response
    PunishmentSchemaUpdate = Punishment.schemas.update
    PunishmentFilter = Punishment.filter


class PunishmentsCRUDService(
    BaseCRUD[
        PunishmentSchemaResponse, PunishmentSchemaCreate, PunishmentSchemaUpdate, PunishmentFilter
    ]
):
    def __init__(self):
        super().__init__("/punishments", "punishment")

    async def update_status(
        self, punishment_id: Literal["me"] | int, status: PunishmentStatus, **kwargs
    ) -> PunishmentSchemaResponse:
        """Update the status of a punishment"""
        return await self._request("POST", f"/{punishment_id}/status/{status}", **kwargs)
