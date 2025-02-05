from fastapi import FastAPI, Request, HTTPException
from typing import Dict, Any
import logging

from uap_backend.base.schemas import PayloadModels
from .registry import WebhookRegistry

logger = logging.getLogger(__name__)


class WebhookManager:
    def __init__(self, app: FastAPI):
        self.app = app
        self.registry = WebhookRegistry()

        @app.post("/webhook")
        async def webhook_handler(data: PayloadModels, request: Request) -> Dict[str, Any]:
            return await self.handle_webhook(data.scope, request)

    async def handle_webhook(self, event_type: str, request: Request) -> Dict[str, Any]:
        handler_info = self.registry.get_handler(event_type)

        if not handler_info:
            raise HTTPException(
                status_code=404,
                detail=f"No handler registered for event type: {event_type}",
            )

        try:
            payload = await request.json()

            if handler_info["model"]:
                payload = handler_info["model"](**payload)
                payload = payload.model_dump()

            result = await handler_info["handler"](payload)

            return {
                "success": True,
                "message": f"Successfully processed {event_type} event",
                "data": result,
            }

        except Exception as e:
            logger.error(f"Error processing webhook {event_type}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
