from typing import TYPE_CHECKING, Any, Dict, List, Optional

from uaproject_backend_schemas.models.schemas.webhook import WebhookAuthType, WebhookStatus
from uaproject_backend_schemas.models.webhook import Webhook

from uap_backend.cruds.base import BaseCRUD

if TYPE_CHECKING:
    from uaproject_backend_schemas.models.webhook import (
        WebhookFilter,
        WebhookSchemaCreate,
        WebhookSchemaResponse,
        WebhookSchemaUpdate,
    )
else:
    WebhookSchemaCreate = Webhook.schemas.create
    WebhookSchemaResponse = Webhook.schemas.response
    WebhookSchemaUpdate = Webhook.schemas.update
    WebhookFilter = Webhook.filter


class WebhookCRUDService(
    BaseCRUD[WebhookSchemaResponse, WebhookSchemaCreate, WebhookSchemaUpdate, WebhookFilter]
):
    def __init__(self):
        super().__init__("/webhooks", "webhook")

    async def stream_webhooks(
        self, skip: int = 0, limit: int = 50, **kwargs
    ) -> List[WebhookSchemaResponse]:
        """Stream webhooks"""
        params = {"skip": skip, "limit": limit}
        return await self._request("GET", "/stream", params=params, **kwargs)

    async def update_webhook_status(
        self, webhook_id: int, status: WebhookStatus, **kwargs
    ) -> WebhookSchemaResponse:
        """Update webhook status"""
        return await self._request("POST", f"/{webhook_id}/status/{status}", **kwargs)

    async def get_my_webhook(self, **kwargs) -> Optional[WebhookSchemaResponse]:
        """Get current application's webhook"""
        try:
            return await self.get("me", **kwargs)
        except Exception:
            return None

    async def ensure_webhook_exists(
        self,
        endpoint_url: str,
        name: str,
        triggers: List[Dict[str, Any]],
        auth_config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> WebhookSchemaResponse:
        """Ensure webhook exists with current configuration"""
        # Check if webhook already exists
        existing_webhook = await self.get_my_webhook(**kwargs)

        webhook_data = {
            "name": name,
            "endpoint_url": endpoint_url,
            "triggers": triggers,
            "status": WebhookStatus.ACTIVE,
            "auth_type": WebhookAuthType.BEARER,
            "auth_config": auth_config or {},
        }

        if existing_webhook:
            # Update existing webhook
            return await self.update(existing_webhook["id"], webhook_data, **kwargs)
        else:
            # Create new webhook
            return await self.create(webhook_data, **kwargs)

    async def activate_webhook(self, webhook_id: int, **kwargs) -> WebhookSchemaResponse:
        """Activate webhook"""
        return await self.update_webhook_status(webhook_id, WebhookStatus.ACTIVE, **kwargs)

    async def pause_webhook(self, webhook_id: int, **kwargs) -> WebhookSchemaResponse:
        """Pause webhook"""
        return await self.update_webhook_status(webhook_id, WebhookStatus.PAUSED, **kwargs)

    async def disable_webhook(self, webhook_id: int, **kwargs) -> WebhookSchemaResponse:
        """Disable webhook"""
        return await self.update_webhook_status(webhook_id, WebhookStatus.DISABLED, **kwargs)

    async def get_webhook_statistics(self, webhook_id: int, **kwargs) -> Dict[str, Any]:
        """Get webhook statistics"""
        return await self._request("GET", f"/{webhook_id}/statistics", **kwargs)

    async def trigger_webhook(self, webhook_id: int, **kwargs) -> Dict[str, Any]:
        """Manually trigger webhook"""
        return await self._request("POST", f"/{webhook_id}/trigger", **kwargs)
