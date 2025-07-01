import hashlib
import hmac
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from uap_backend.core.config import settings
from uap_backend.logger import get_logger

from .registry import WebhookRegistry

logger = get_logger(__name__)

security = HTTPBearer()


class WebhookHandlerResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

    @classmethod
    def create(cls, success: bool, message: str, data: Any = None) -> "WebhookHandlerResponse":
        try:
            return cls(success=success, message=message, data=data)
        except Exception:
            return cls(success=success, message=message, data=None)


class WebhookManager:
    def __init__(self, app: FastAPI):
        self.app = app
        self.registry = WebhookRegistry()
        self._setup_webhook_handler()

    def _setup_webhook_handler(self) -> None:
        @self.app.post("/webhook", response_model=WebhookHandlerResponse)
        async def webhook_handler(
            request: Request,
            credentials: HTTPAuthorizationCredentials = Depends(security),
        ) -> WebhookHandlerResponse:
            if credentials.credentials != settings.CALLBACK_SECRET:
                raise HTTPException(status_code=401, detail="Invalid authorization token")
            return await self.handle_webhook(request)

    async def handle_webhook(self, request: Request) -> WebhookHandlerResponse:
        payload_dict = await request.json()

        # Extract scope/event type from payload
        scope = payload_dict.get("scope")
        if not scope:
            raise HTTPException(status_code=400, detail="Missing 'scope' in webhook payload")

        handler_infos = self.registry.get_handlers(scope)

        if not handler_infos:
            raise HTTPException(
                status_code=404, detail=f"No handler registered for event type: {scope}"
            )

        results = []

        for handler_info in handler_infos:
            try:
                # Check if payload has before/after structure (update events)
                payload_data = payload_dict.get("payload", {})

                if (
                    isinstance(payload_data, dict)
                    and "before" in payload_data
                    and "after" in payload_data
                ):
                    # Handle before/after payload (update events)
                    result = await handler_info.handler(
                        before=payload_data["before"], after=payload_data["after"]
                    )
                else:
                    # Handle single payload (create/delete events)
                    result = await handler_info.handler(payload=payload_data)

                results.append(result)

            except Exception as e:
                logger.exception(f"Error processing webhook for {scope}: {e}")

        return WebhookHandlerResponse.create(
            success=True, message=f"Successfully processed {scope} event", data=results
        )

    async def _auto_register_webhook(self):
        """Auto-register webhook on startup"""
        if hasattr(self.app, "webhook_endpoint_url") and self.app.webhook_endpoint_url:
            endpoint_url = self.app.webhook_endpoint_url
            if not endpoint_url.endswith(self.endpoint_path):
                endpoint_url = endpoint_url.rstrip("/") + self.endpoint_path

            success = await self.registry.auto_register_webhook(
                endpoint_url=endpoint_url, auth_config={"token": settings.CALLBACK_SECRET}
            )

            if success:
                logger.info(f"Webhook auto-registered at {endpoint_url}")
            else:
                logger.warning(f"Failed to auto-register webhook at {endpoint_url}")
        else:
            logger.info("No webhook endpoint URL configured, skipping auto-registration")

    async def _verify_webhook_signature(self, request: Request) -> None:
        """Verify HMAC signature for webhook security"""
        signature = request.headers.get(settings.WEBHOOK_SIGNATURE_HEADER)
        if not signature:
            raise HTTPException(status_code=401, detail="Missing webhook signature")

        payload = await request.body()
        secret = settings.WEBHOOK_SECRET or settings.CALLBACK_SECRET

        if not self._verify_hmac_signature(payload, signature, secret):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    def _verify_hmac_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify HMAC signature"""
        try:
            expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

            # Handle different signature formats
            if signature.startswith("sha256="):
                signature = signature[7:]

            return hmac.compare_digest(expected, signature)
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
