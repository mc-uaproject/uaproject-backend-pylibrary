from typing import Dict, List, Optional

from uap_backend.base.crud import BaseCRUD

from .schemas import (
    WebhookCreate,
    WebhookFilterParams,
    WebhookResponse,
    WebhookStatus,
    WebhookUpdate,
)


class WebhookCRUDService(BaseCRUD[WebhookResponse]):
    response_model = WebhookResponse

    async def create_webhook(
        self,
        data: WebhookCreate
    ) -> WebhookResponse:
        """Create a new webhook"""
        return await self.post("/webhooks", data=data)

    async def list_webhooks(
        self,
        filters: Optional[WebhookFilterParams] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = 'created_at',
        order: str = 'desc'
    ) -> List[WebhookResponse]:
        """Get list of webhooks with filtering and pagination"""
        params = {
            'skip': skip,
            'limit': limit,
            'sort_by': sort_by,
            'order': order,
            **(filters.model_dump(exclude_none=True) if filters else {})
        }
        return await self.get("/webhooks", params=params, is_list=True)

    async def stream_webhooks(
        self,
        skip: int = 0,
        limit: int = 50
    ) -> List[WebhookResponse]:
        """Stream webhooks"""
        params = {
            'skip': skip,
            'limit': limit
        }
        return await self.get("/webhooks/stream", params=params, is_list=True)

    async def get_webhook(
        self,
        webhook_id: int
    ) -> WebhookResponse:
        """Get a specific webhook by ID"""
        return await self.get(f"/webhooks/{webhook_id}")

    async def update_webhook(
        self,
        webhook_id: int,
        data: WebhookUpdate
    ) -> WebhookResponse:
        """Update a webhook"""
        return await self.patch(f"/webhooks/{webhook_id}", data=data)

    async def update_webhook_status(
        self,
        webhook_id: int,
        status: WebhookStatus
    ) -> WebhookResponse:
        """Update webhook status"""
        return await self.post(f"/webhooks/{webhook_id}/status/{status}")

    async def delete_webhook(
        self,
        webhook_id: int
    ) -> Dict[str, str]:
        """Delete a webhook"""
        return await self.delete(f"/webhooks/{webhook_id}")

WebhookCRUDServiceInit = WebhookCRUDService()
