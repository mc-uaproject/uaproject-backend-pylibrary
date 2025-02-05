from typing import Dict, Callable, Type, Any, Optional
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class WebhookRegistry:
    _instance = None
    _handlers: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register_handler(
        cls, event_type: str, validation_model: Optional[Type[BaseModel]] = None
    ):
        def decorator(func: Callable):
            cls._handlers[event_type] = {"handler": func, "model": validation_model}
            return func

        return decorator

    @classmethod
    def get_handler(cls, event_type: str) -> Optional[Dict[str, Any]]:
        return cls._handlers.get(event_type)

    @classmethod
    def get_all_handlers(cls) -> Dict[str, Dict[str, Any]]:
        return cls._handlers
