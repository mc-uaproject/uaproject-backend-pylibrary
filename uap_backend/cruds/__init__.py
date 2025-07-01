"""CRUD Services for UAProject Backend Library"""

from .applications import ApplicationCRUDService
from .balances import BalanceCRUDService
from .base import BaseCRUD
from .files import FileCRUDService
from .punishments import PunishmentsCRUDService
from .purchases import PurchasesCRUDService
from .roles import RoleCRUDService
from .services import ServicesCRUDService
from .transactions import TransactionCRUDService
from .users import UserCRUDService
from .webhooks import WebhookCRUDService

__all__ = [
    # Base CRUD
    "BaseCRUD",
    # Main CRUD Services
    "ApplicationCRUDService",
    "PunishmentsCRUDService",
    "UserCRUDService",
    "WebhookCRUDService",
    "FileCRUDService",
    "RoleCRUDService",
    # Payment CRUD Services
    "BalanceCRUDService",
    "PurchasesCRUDService",
    "ServicesCRUDService",
    "TransactionCRUDService",
]
