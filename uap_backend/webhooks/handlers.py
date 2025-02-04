from typing import Any, Callable, Dict, Optional
from fastapi import FastAPI, Request, HTTPException
import asyncio
import logging
from ..config import settings

logger = logging.getLogger(__name__)


class WebhookHandler:
    def __init__(self, app: FastAPI):
        self.app = app
        self.handlers: Dict[str, Callable] = {}
        self.retries: Dict[str, int] = {}

        @app.post("/webhook/{event_type}")
        async def handle_webhook(event_type: str, request: Request) -> Dict[str, Any]:
            try:
                payload = await request.json()
                return await self.process_event(event_type, payload)
            except Exception as e:
                logger.error(f"Webhook error: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))

    async def process_event(
        self, event_type: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        if event_type not in self.handlers:
            raise HTTPException(
                status_code=404, detail=f"No handler for event type: {event_type}"
            )

        retries = self.retries.get(event_type, settings.MAX_RETRIES)
        for attempt in range(retries):
            try:
                result = await self.handlers[event_type](payload)
                return {
                    "success": True,
                    "message": "Event processed successfully",
                    "data": result,
                }
            except Exception as e:
                if attempt == retries - 1:
                    raise
                logger.warning(
                    f"Retry {attempt + 1}/{retries} for {event_type}: {str(e)}"
                )
                await asyncio.sleep(settings.RETRY_DELAY)

    def register(
        self, event_type: str, handler: Callable, retries: Optional[int] = None
    ) -> None:
        self.handlers[event_type] = handler
        if retries is not None:
            self.retries[event_type] = retries
