"""
Enhanced webhook system for UAProject Backend Library.

Provides automatic webhook registration, handler management, and security features.
"""

from .decorators import (
    on_create,
    on_delete,
    on_update,
    webhook_handler,
)
from .handlers import WebhookHandlerResponse, WebhookManager
from .registry import HandlerInfo, WebhookRegistry

__all__ = [
    # Core classes
    "WebhookRegistry",
    "WebhookManager",
    "HandlerInfo",
    "WebhookHandlerResponse",
    
    # Decorators
    "webhook_handler",
    "on_create",
    "on_update", 
    "on_delete",
]


# Convenience functions for setup
async def setup_webhooks(app, endpoint_url: str = None, auto_register: bool = True):
    """
    Setup webhook system for FastAPI application.
    
    Args:
        app: FastAPI application instance
        endpoint_url: Public URL for webhook endpoint (for auto-registration)
        auto_register: Whether to automatically register webhooks
    
    Example:
        from fastapi import FastAPI
        from uap_backend.webhooks import setup_webhooks
        
        app = FastAPI()
        
        # Setup webhooks with auto-registration
        await setup_webhooks(
            app, 
            endpoint_url="https://your-app.com/webhook",
            auto_register=True
        )
    """
    if endpoint_url:
        app.webhook_endpoint_url = endpoint_url
    
    webhook_manager = WebhookManager(app, auto_register=auto_register)
    return webhook_manager


def bind_service_handlers(service_instance):
    """
    Bind service instance handlers to webhook registry.
    
    Args:
        service_instance: Service class instance with webhook handlers
    
    Example:
        from uap_backend.webhooks import bind_service_handlers
        
        class PurchaseService:
            @webhook_handler("purchased_item.create")
            async def handle_purchase(self, payload):
                pass
        
        # Bind handlers
        purchase_service = PurchaseService()
        bind_service_handlers(purchase_service)
    """
    WebhookRegistry.bind_handlers(service_instance)