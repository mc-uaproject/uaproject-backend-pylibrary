"""
Enhanced Python client library for interacting with the UAProject API Backend.

Provides convenient access to all API resources through CRUD services with
improved architecture following backend patterns.
"""

from .core import HTTPClient, settings
from .core.errors import *
from .cruds import *
from .logger import get_logger
from .webhooks import (
    WebhookManager,
    WebhookRegistry,
    bind_service_handlers,
    on_create,
    on_delete,
    on_update,
    setup_webhooks,
    webhook_handler,
)

__version__ = "2.0.0"

__all__ = [
    # Core
    "HTTPClient",
    "settings", 
    "get_logger",
    
    # Errors
    "CRUDNotFoundError",
    "CRUDValidationError", 
    "APIConnectionError",
    "APIAuthenticationError",
    "APIPermissionError",
    "APIRateLimitError",
    "APIServerError",
    "SerializationError",
    "ConfigurationError",
    "WebhookValidationError",
    
    # CRUD Services
    "BaseCRUD",
    "ApplicationCRUDService",
    "PunishmentsCRUDService", 
    "UserCRUDService",
    "WebhookCRUDService",
    "FileCRUDService",
    "RoleCRUDService",
    "BalanceCRUDService",
    "PurchasesCRUDService",
    "ServicesCRUDService",
    "TransactionCRUDService",
    
    # Webhooks
    "WebhookRegistry",
    "WebhookManager",
    "setup_webhooks",
    "bind_service_handlers",
    "webhook_handler",
    "on_create",
    "on_update",
    "on_delete",
]