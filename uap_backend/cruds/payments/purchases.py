from uaproject_backend_schemas.payments.purchases import (
    PurchasedItemCreate,
    PurchasedItemFilterParams,
    PurchasedItemResponse,
    PurchasedItemUpdate,
)

from uap_backend.cruds.base import BaseCRUD


class PurchasesCRUDService(
    BaseCRUD[
        PurchasedItemResponse, PurchasedItemCreate, PurchasedItemUpdate, PurchasedItemFilterParams
    ]
):
    response_model = PurchasedItemResponse

    def __init__(self, cache_duration=300):
        super().__init__(cache_duration, "/payments/purchases")
