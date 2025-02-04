from datetime import datetime
from pydantic import BaseModel


class BaseBackendModel(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

class BaseUserBackendModel(BaseBackendModel):
    user_id: int