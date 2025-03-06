from __future__ import annotations

import logging
from typing import Any, Callable, Coroutine, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel

from uap_backend.base.schemas import PayloadModels

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)

class HandlerInfo(Generic[T]):
    def __init__(
        self,
        handler: Callable[[T], Coroutine[Any, Any, Dict[str, Any]]],
        model: Optional[Type[T]] = None,
    ):
        self.handler = handler
        self.model: PayloadModels = model

class WebhookRegistry:
    _instance: Optional["WebhookRegistry"] = None
    _handlers: Dict[str, List[HandlerInfo[Any]]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register_handler(cls, event_type: str, validation_model: Optional[Type[T]] = None):
        def decorator(func: Callable[[T], Coroutine[Any, Any, Dict[str, Any]]]):
            if event_type not in cls._handlers:
                cls._handlers[event_type] = []
            cls._handlers[event_type].append(HandlerInfo(handler=func, model=validation_model))
            return func
        return decorator

    @classmethod
    def bind_handlers(cls, instance):
        for event_type, handler_infos in cls._handlers.items():
            for handler_info in handler_infos:
                if not isinstance(handler_info.handler, staticmethod):
                    bound_handler = getattr(instance, handler_info.handler.__name__, None)
                    if bound_handler is None:
                        # Optionally, you can log a warning instead of raising an error
                        logger.warn(f"Cannot bind handler for {event_type}, method not found in {instance}")
                    else:
                        handler_info.handler = bound_handler

    @classmethod
    def get_handlers(cls, event_type: str) -> List[HandlerInfo[Any]]:
        return cls._handlers.get(event_type, [])

    @classmethod
    def get_all_handlers(cls) -> Dict[str, List[HandlerInfo[Any]]]:
        return cls._handlers
