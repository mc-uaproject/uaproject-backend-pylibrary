from typing import Any, Dict, Optional

from pydantic import BaseModel


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
