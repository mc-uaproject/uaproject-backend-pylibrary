from __future__ import annotations

import asyncio
import inspect
from typing import Any, Callable, Coroutine, Dict, Generic, List, Optional, Set, Type, TypeVar

from pydantic import BaseModel
from uaproject_backend_schemas.base import PayloadModels
from uaproject_backend_schemas.webhooks import WebhookStatus

from uap_backend.cruds.webhooks import WebhookCRUDServiceInit
from uap_backend.logger import get_logger

T = TypeVar("T", bound=BaseModel)
logger = get_logger(__name__)


class HandlerInfo(Generic[T]):
    def __init__(
        self,
        handler: Callable[[T], Coroutine[Any, Any, Dict[str, Any]]],
        model: Optional[Type[T]] = None,
        class_name: str = None,
    ):
        self.handler = handler
        self.model: PayloadModels = model
        self.handler_name = handler.__name__
        self.bound_instance = None
        self.defined_in_class = class_name


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
            frame = inspect.currentframe().f_back
            class_name = None
            while frame:
                if "self" in frame.f_locals and frame.f_code.co_name == func.__name__:
                    class_name = frame.f_locals["self"].__class__.__name__
                    break
                frame = frame.f_back

            if event_type not in cls._handlers:
                cls._handlers[event_type] = []

            cls._handlers[event_type].append(
                HandlerInfo(handler=func, model=validation_model, class_name=class_name)
            )
            return func

        return decorator

    @classmethod
    def bind_handlers(cls, instance):
        instance_class_name = instance.__class__.__name__
        _, duplicate_handler_names = cls._find_duplicate_handlers(instance_class_name)
        cls._log_duplicate_handlers(instance_class_name, duplicate_handler_names)
        bound_handlers = cls._bind_instance_handlers(instance, instance_class_name)
        cls._log_bound_handlers(bound_handlers, instance_class_name)
        cls._include_scopes_to_webhook([event_type for event_type, _ in bound_handlers])

    @classmethod
    def _find_duplicate_handlers(cls, instance_class_name: str) -> tuple[Set[str], Set[str]]:
        handler_names_seen: Set[str] = set()
        duplicate_handler_names: Set[str] = set()

        for handler_infos in cls._handlers.values():
            for handler_info in handler_infos:
                if handler_info.defined_in_class == instance_class_name:
                    handler_name = handler_info.handler_name
                    if handler_name in handler_names_seen:
                        duplicate_handler_names.add(handler_name)
                    handler_names_seen.add(handler_name)

        return handler_names_seen, duplicate_handler_names

    @classmethod
    def _log_duplicate_handlers(cls, instance_class_name: str, duplicate_handler_names: Set[str]):
        if duplicate_handler_names:
            logger.warning(
                f"Duplicate handler names found in {instance_class_name}: {duplicate_handler_names}"
            )

    @classmethod
    def _bind_instance_handlers(cls, instance, instance_class_name: str) -> List[tuple]:
        bound_handlers = []

        for event_type, handler_infos in cls._handlers.items():
            for handler_info in handler_infos:
                if (
                    handler_info.defined_in_class is None
                    or handler_info.defined_in_class == instance_class_name
                ):
                    handler_name = handler_info.handler_name
                    bound_handler = getattr(instance, handler_name, None)

                    if bound_handler is None:
                        logger.warning(
                            f"Cannot bind handler for {event_type}, method {handler_name} not found in {instance}"
                        )
                    else:
                        if (
                            handler_info.bound_instance is not None
                            and handler_info.bound_instance != instance
                        ):
                            logger.warning(
                                f"Handler {handler_name} for {event_type} already bound to {handler_info.bound_instance.__class__.__name__}, "
                                f"now binding to {instance_class_name}. This might lead to unexpected behavior."
                            )

                        handler_info.handler = bound_handler
                        handler_info.bound_instance = instance
                        handler_info.defined_in_class = instance_class_name
                        bound_handlers.append((event_type, handler_name))

        return bound_handlers

    @classmethod
    def _include_scopes_to_webhook(cls, scope: str):
        loop = asyncio.get_running_loop()
        if loop is not None:
            loop.create_task(cls._ainclude_scopes_to_webhook(scope))

    @classmethod
    async def _ainclude_scopes_to_webhook(cls, scopes: List[str]):
        webhook = await WebhookCRUDServiceInit.get("me")

        if not webhook:
            logger.warning("Cant find my webhook")
            return

        webhook.status = WebhookStatus.ACTIVE
        webhook.scopes.update([{scope: True} for scope in scopes])
        await WebhookCRUDServiceInit.update(webhook.id, webhook)

    @classmethod
    def _log_bound_handlers(cls, bound_handlers: List[tuple], instance_class_name: str):
        for event_type, handler_name in bound_handlers:
            logger.info(f"{event_type} -> {instance_class_name}.{handler_name}")

    @classmethod
    def get_handlers(cls, event_type: str) -> List[HandlerInfo[Any]]:
        return cls._handlers.get(event_type, [])

    @classmethod
    def get_all_handlers(cls) -> Dict[str, List[HandlerInfo[Any]]]:
        return cls._handlers
