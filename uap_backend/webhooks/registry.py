from typing import Dict, Any, Callable, Type, Optional, TypeVar, Generic, Coroutine
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class PayloadModels(BaseModel):
    scope: str

class HandlerInfo(Generic[T]):
    handler: Callable[[T], Coroutine[Any, Any, Dict[str, Any]]]
    model: Optional[Type[T]] = None

class WebhookRegistry:
    _instance: Optional['WebhookRegistry'] = None
    _handlers: Dict[str, HandlerInfo[Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register_handler(
        cls, 
        event_type: str, 
        validation_model: Optional[Type[T]] = None
    ):
        def decorator(func: Callable[[T], Coroutine[Any, Any, Dict[str, Any]]]):
            cls._handlers[event_type] = HandlerInfo(
                handler=func, 
                model=validation_model
            )
            return func
        return decorator

    @classmethod
    def bind_handlers(cls, instance):
        for event_type, handler_info in cls._handlers.items():
            if not isinstance(handler_info.handler, staticmethod):
                bound_handler = getattr(
                    instance, 
                    handler_info.handler.__name__, 
                    None
                )
                if bound_handler is None:
                    raise ValueError(
                        f"Cannot bind handler for {event_type}, "
                        f"method not found in {instance}"
                    )
                handler_info.handler = bound_handler

    @classmethod
    def get_handler(cls, event_type: str) -> Optional[HandlerInfo[Any]]:
        return cls._handlers.get(event_type)

    @classmethod
    def get_all_handlers(cls) -> Dict[str, HandlerInfo[Any]]:
        return cls._handlers
