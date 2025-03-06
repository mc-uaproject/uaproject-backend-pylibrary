from __future__ import annotations

import logging
from typing import Any, Callable, Coroutine, Dict, Generic, List, Optional, Set, Type, TypeVar

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
        self.handler_name = handler.__name__
        self.bound_instance = None

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
        instance_class_name = instance.__class__.__name__
        handler_names_seen: Set[str] = set()
        duplicate_handler_names: Set[str] = set()
        bound_handlers = []
        unbound_handlers = []

        for event_type, handler_infos in cls._handlers.items():
            for handler_info in handler_infos:
                handler_name = handler_info.handler_name
                if handler_name in handler_names_seen:
                    duplicate_handler_names.add(handler_name)
                handler_names_seen.add(handler_name)

        if duplicate_handler_names:
            logger.warning(f"Duplicate handler names found: {duplicate_handler_names}")

        for event_type, handler_infos in cls._handlers.items():
            for handler_info in handler_infos:
                if not isinstance(handler_info.handler, staticmethod):
                    handler_name = handler_info.handler_name
                    bound_handler = getattr(instance, handler_name, None)

                    if bound_handler is None:
                        logger.warning(f"Cannot bind handler for {event_type}, method {handler_name} not found in {instance}")
                        unbound_handlers.append((event_type, handler_name))
                    else:
                        if handler_info.bound_instance is not None and handler_info.bound_instance != instance:
                            logger.warning(
                                f"Handler {handler_name} for {event_type} already bound to {handler_info.bound_instance.__class__.__name__}, "
                                f"now binding to {instance_class_name}. This might lead to unexpected behavior."
                            )

                        handler_info.handler = bound_handler
                        handler_info.bound_instance = instance
                        bound_handlers.append((event_type, handler_name))

        if bound_handlers:
            logger.info(f"=== Successfully bound handlers for {instance_class_name} ===")
            for event_type, handler_name in bound_handlers:
                logger.info(f"  ✓ {event_type} -> {instance_class_name}.{handler_name}")

        if unbound_handlers:
            logger.info(f"=== Failed to bind handlers for {instance_class_name} ===")
            for event_type, handler_name in unbound_handlers:
                logger.info(f"  ✗ {event_type} -> {handler_name} (method not found)")

    @classmethod
    def get_handlers(cls, event_type: str) -> List[HandlerInfo[Any]]:
        return cls._handlers.get(event_type, [])

    @classmethod
    def get_all_handlers(cls) -> Dict[str, List[HandlerInfo[Any]]]:
        return cls._handlers

    @classmethod
    def log_registered_scopes(cls):
        logger.info("=== All registered webhook scopes ===")

        instance_handlers = {}
        unbound_scopes = {}

        for scope, handlers in cls._handlers.items():
            for handler in handlers:
                if handler.bound_instance:
                    instance_name = handler.bound_instance.__class__.__name__
                    if instance_name not in instance_handlers:
                        instance_handlers[instance_name] = []
                    instance_handlers[instance_name].append((scope, handler.handler_name))
                else:
                    if scope not in unbound_scopes:
                        unbound_scopes[scope] = []
                    unbound_scopes[scope].append(handler.handler_name)

        for instance_name, handlers in instance_handlers.items():
            logger.info(f"Class: {instance_name}")
            for scope, handler_name in handlers:
                logger.info(f"  - {scope} -> {handler_name}")

        if unbound_scopes:
            logger.info("Unbound scopes:")
            for scope, handlers in unbound_scopes.items():
                logger.info(f"  - {scope}: {', '.join(handlers)}")
