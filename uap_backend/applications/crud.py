from typing import List, Optional
from .schemas import Application, ApplicationCreate, ApplicationUpdate
from ..base.crud import BaseCRUD
from ..config import settings


class ApplicationCRUD(BaseCRUD[Application, ApplicationCreate, ApplicationUpdate]):
    def __init__(self):
        super().__init__(Application)
        self.base_url = f"{settings.SERVICE_HOST}:{settings.SERVICE_PORT}/applications"

    async def create(self, data: ApplicationCreate) -> Application:
        result = await self._request("POST", self.base_url, json=data.model_dump())
        return Application.model_validate(result)

    async def get(self, application_id: int) -> Optional[Application]:
        result = await self._request("GET", f"{self.base_url}/{application_id}")
        return Application.model_validate(result) if result else None

    async def update(self, application_id: int, data: ApplicationUpdate) -> Application:
        result = await self._request(
            "PATCH",
            f"{self.base_url}/{application_id}",
            json=data.model_dump(exclude_unset=True),
        )
        return Application.model_validate(result)

    async def delete(self, application_id: int) -> None:
        await self._request("DELETE", f"{self.base_url}/{application_id}")

    async def list(
        self, skip: int = 0, limit: int = 100, status: Optional[str] = None
    ) -> List[Application]:
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        result = await self._request("GET", self.base_url, params=params)
        return [Application.model_validate(item) for item in result]
