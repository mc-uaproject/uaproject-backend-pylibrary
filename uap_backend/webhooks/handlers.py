from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from uaproject_backend_schemas.base import BothPayloadBaseModel, PayloadModels

from uap_backend.logger import get_logger

from .registry import WebhookRegistry

logger = get_logger(__name__)


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
        async def webhook_handler(data: PayloadModels, request: Request) -> WebhookHandlerResponse:
            return await self.handle_webhook(data, request)

    async def handle_webhook(self, data: PayloadModels, request: Request) -> WebhookHandlerResponse:
        handler_infos = self.registry.get_handlers(data.scope)

        if not handler_infos:
            raise HTTPException(
                status_code=404, detail=f"No handler registered for event type: {data.scope}"
            )

        payload_dict = await request.json()
        results = []

        for handler_info in handler_infos:
            payload: PayloadModels = handler_info.model(**payload_dict)

            try:
                if isinstance(payload, BothPayloadBaseModel):
                    result = await handler_info.handler(
                        before=payload.payload["before"], after=payload.payload["after"]
                    )
                else:
                    result = await handler_info.handler(payload=payload.payload)

                results.append(result)

            except Exception as e:
                logger.exception(f"Error processing webhook for {data.scope}: {e}")

        return WebhookHandlerResponse.create(
            success=True, message=f"Successfully processed {data.scope} event", data=results
        )
