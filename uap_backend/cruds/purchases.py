from typing import TYPE_CHECKING

from uaproject_backend_schemas.models.purchased_item import PurchasedItem

from uap_backend.cruds.base import BaseCRUD

if TYPE_CHECKING:
    from uaproject_backend_schemas.models.purchased_item import (
        PurchasedItemFilter,
        PurchasedItemSchemaCreate,
        PurchasedItemSchemaResponse,
        PurchasedItemSchemaUpdate,
    )
else:
    PurchasedItemSchemaCreate = PurchasedItem.schemas.create
    PurchasedItemSchemaResponse = PurchasedItem.schemas.response
    PurchasedItemSchemaUpdate = PurchasedItem.schemas.update
    PurchasedItemFilter = PurchasedItem.filter


class PurchasesCRUDService(
    BaseCRUD[
        PurchasedItemSchemaResponse,
        PurchasedItemSchemaCreate,
        PurchasedItemSchemaUpdate,
        PurchasedItemFilter,
    ]
):
    def __init__(self):
        super().__init__("/purchases", "purchase")
