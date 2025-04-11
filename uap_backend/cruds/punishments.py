from typing import Literal

from uaproject_backend_schemas.punishments import (
    PunishmentCreate,
    PunishmentFilterParams,
    PunishmentResponse,
    PunishmentStatus,
    PunishmentUpdate,
)

from uap_backend.cruds.base import BaseCRUD


class PunishmentsCRUDService(
    BaseCRUD[PunishmentResponse, PunishmentCreate, PunishmentUpdate, PunishmentFilterParams]
):
    response_model = PunishmentResponse

    def __init__(self, cache_duration=300):
        super().__init__(cache_duration, "/punishments")

    async def update_status(
        self, punishment_id: Literal["me"] | int, status: PunishmentStatus, **kwargs
    ) -> PunishmentResponse:
        """
        Update the status of a punishment.
        """
        return await self._request(
            method="POST", endpoint=f"/{punishment_id}/status/{status}", **kwargs
        )
