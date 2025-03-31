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

    def __init__(self, cache_duration=300):
        super().__init__(cache_duration, "/webhooks")

    async def stream_webhooks(self, skip: int = 0, limit: int = 50) -> List[WebhookResponse]:
        """Stream webhooks"""
        params = {"skip": skip, "limit": limit}
        return await self.get("/stream", params=params, is_list=True)

    async def update_webhook_status(
        self, webhook_id: int, status: WebhookStatus
    ) -> WebhookResponse:
        """Update webhook status"""
        return await self.post(f"/{webhook_id}/status/{status}")


WebhookCRUDServiceInit = WebhookCRUDService()
