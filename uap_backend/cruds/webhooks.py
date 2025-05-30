from typing import List

from uaproject_backend_schemas.webhooks import (
    WebhookCreate,
    WebhookFilterParams,
    WebhookResponse,
    WebhookStatus,
    WebhookUpdate,
)

from uap_backend.cruds.base import BaseCRUD


class WebhookCRUDService(
    BaseCRUD[WebhookResponse, WebhookCreate, WebhookUpdate, WebhookFilterParams]
):
    response_model = WebhookResponse

    def __init__(self):
        super().__init__("/webhooks")

    async def stream_webhooks(
        self, skip: int = 0, limit: int = 50, **kwargs
    ) -> List[WebhookResponse]:
        """Stream webhooks"""
        params = {"skip": skip, "limit": limit}
        return await self.get("/stream", params=params, is_list=True, **kwargs)

    async def update_webhook_status(
        self, webhook_id: int, status: WebhookStatus, **kwargs
    ) -> WebhookResponse:
        """Update webhook status"""
        return await self._request("POST", f"/{webhook_id}/status/{status}", **kwargs)
