from typing import TYPE_CHECKING, List

from uaproject_backend_schemas.models.schemas import WebhookStatus

from uap_backend.cruds.base import BaseCRUD

if TYPE_CHECKING:
    from uaproject_backend_schemas.models.webhook import (
        WebhookSchemaCreate,
        WebhookFilter,
        WebhookSchemaResponse,
        WebhookSchemaUpdate,
    )


class WebhookCRUDService(
    BaseCRUD[
        WebhookSchemaResponse,
        WebhookSchemaCreate,
        WebhookSchemaUpdate,
        WebhookFilter,
    ]
):
    response_model = WebhookSchemaResponse

    def __init__(self):
        super().__init__("/webhooks")

    async def stream_webhooks(
        self, skip: int = 0, limit: int = 50, **kwargs
    ) -> List["WebhookSchemaResponse"]:
        """Stream webhooks"""
        params = {"skip": skip, "limit": limit}
        return await self.get("/stream", params=params, is_list=True, **kwargs)

    async def update_webhook_status(
        self, webhook_id: int, status: WebhookStatus, **kwargs
    ) -> "WebhookSchemaResponse":
        """Update webhook status"""
        return await self._request("POST", f"/{webhook_id}/status/{status}", **kwargs)
