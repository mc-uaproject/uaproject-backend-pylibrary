"""Enhanced webhook decorators for automatic registration"""

from typing import Any, Callable, Dict, List, Optional, Type

from .registry import WebhookRegistry


def webhook_handler(
    event_type: str,
    model_name: Optional[str] = None,
    conditions: Optional[Dict[str, Any]] = None,
    field_mapping: Optional[List[Dict[str, str]]] = None,
    auto_register: bool = True,
    include_all_fields: bool = True,
    include_metadata: bool = True,
    respect_permissions: bool = True,
    validation_model: Optional[Type] = None,
):
    """
    Enhanced decorator for webhook handlers with auto-registration support.

    Args:
        event_type: Event type to handle (e.g., "user.create", "transaction.update")
        model_name: Model name for webhook trigger (auto-extracted if not provided)
        conditions: Webhook conditions for filtering events
        field_mapping: Field mapping configuration for webhook payload
        auto_register: Whether to include this handler in auto-registration
        include_all_fields: Include all fields in webhook payload
        include_metadata: Include metadata in webhook payload
        respect_permissions: Respect permissions when triggering webhook
        validation_model: Pydantic model for payload validation

    Example:
        @webhook_handler(
            event_type="purchased_item.create",
            model_name="PurchasedItem",
            conditions={
                "operator": "AND",
                "conditions": [
                    {"field": "status", "operator": "eq", "value": "active"}
                ]
            },
            field_mapping=[
                {"source_path": "user.id", "target_field": "recipient_id"},
                {"source_path": "user.minecraft_nickname", "target_field": "recipient_nickname"}
            ]
        )
        async def handle_purchase_created(self, payload):
            # Process purchase webhook
            pass
    """

    def decorator(func: Callable) -> Callable:
        # Store webhook metadata for auto-registration
        func._webhook_metadata = {
            "event_type": event_type,
            "model_name": model_name,
            "conditions": conditions,
            "field_mapping": field_mapping,
            "auto_register": auto_register,
            "include_all_fields": include_all_fields,
            "include_metadata": include_metadata,
            "respect_permissions": respect_permissions,
        }

        # Register with the webhook registry
        return WebhookRegistry.register_handler(event_type, validation_model)(func)

    return decorator


# Convenience decorators for common events
def on_create(model_name: str = None, **kwargs):
    """
    Decorator for CREATE events

    Args:
        model_name: Model name (e.g., "User", "Transaction", "PurchasedItem")
        **kwargs: Additional webhook handler options

    Examples:
        @on_create("User")
        async def handle_user_created(self, payload):
            pass

        @on_create("Transaction", conditions={...})
        async def handle_transaction_created(self, payload):
            pass
    """
    if model_name is None:
        raise ValueError("model_name is required for on_create decorator")
    event_type = f"{model_name.lower()}.create"
    return webhook_handler(event_type, model_name, **kwargs)


def on_update(model_name: str = None, **kwargs):
    """
    Decorator for UPDATE events

    Args:
        model_name: Model name (e.g., "User", "Transaction", "PurchasedItem")
        **kwargs: Additional webhook handler options
    """
    if model_name is None:
        raise ValueError("model_name is required for on_update decorator")
    event_type = f"{model_name.lower()}.update"
    return webhook_handler(event_type, model_name, **kwargs)


def on_delete(model_name: str = None, **kwargs):
    """
    Decorator for DELETE events

    Args:
        model_name: Model name (e.g., "User", "Transaction", "PurchasedItem")
        **kwargs: Additional webhook handler options
    """
    if model_name is None:
        raise ValueError("model_name is required for on_delete decorator")
    event_type = f"{model_name.lower()}.delete"
    return webhook_handler(event_type, model_name, **kwargs)
