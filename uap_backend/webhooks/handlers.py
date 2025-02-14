import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Request

from uap_backend.base.schemas import BothPayloadBaseModel, PayloadModels
from uap_backend.webhooks.schemas import WebhookHandlerResponse

from .registry import HandlerInfo, WebhookRegistry

logger = logging.getLogger(__name__)


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
        handler_info: Optional[HandlerInfo] = self.registry.get_handler(data.scope)

        if not handler_info:
            raise HTTPException(
                status_code=404, detail=f"No handler registered for event type: {data.scope}"
            )

        try:
            payload_dict = await request.json()
            payload: PayloadModels = handler_info.model(**payload_dict)

            if isinstance(data, BothPayloadBaseModel):
                if not all(k in payload.payload for k in ("before", "after")):
                    raise ValueError(
                        "Both 'before' and 'after' fields are required for this payload type"
                    )

                result = await handler_info.handler(
                    before=payload.payload["before"], after=payload.payload["after"]
                )
            else:
                result = await handler_info.handler(payload=payload.payload)

            return WebhookHandlerResponse(
                success=True, message=f"Successfully processed {data.scope} event", data=result
            )

        except Exception as e:
            logger.error(f"Error processing webhook {data.scope}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
