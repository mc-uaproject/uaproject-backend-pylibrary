"""File CRUD Service based on OpenAPI analysis"""

from typing import TYPE_CHECKING, List

from uaproject_backend_schemas.models.file import File

from uap_backend.cruds.base import BaseCRUD

if TYPE_CHECKING:
    from uaproject_backend_schemas.models.file import (
        FileFilter,
        FileSchemaCreate,
        FileSchemaResponse,
        FileSchemaUpdate,
    )
else:
    FileSchemaCreate = File.schemas.create
    FileSchemaResponse = File.schemas.response
    FileSchemaUpdate = File.schemas.update
    FileFilter = File.filter


class FileCRUDService(BaseCRUD[FileSchemaResponse, FileSchemaCreate, FileSchemaUpdate, FileFilter]):
    """CRUD service for file management"""

    def __init__(self):
        super().__init__("/files", "file")

    async def request_upload(
        self, upload_request: FileSchemaCreate, **kwargs
    ) -> FileSchemaResponse:
        """Request file upload URL - creates file record and gets presigned upload URL"""
        return await self._request("POST", "/upload", data=upload_request, **kwargs)

    async def get_by_user(self, user_id: int, **kwargs) -> List[FileSchemaResponse]:
        """Get files by user ID"""
        return await self._request("GET", f"/user/{user_id}", **kwargs)

    async def get_by_model(
        self, model_name: str, model_id: int, **kwargs
    ) -> List[FileSchemaResponse]:
        """Get files associated with a model"""
        return await self._request("GET", f"/model/{model_name}/{model_id}", **kwargs)

    async def download(self, file_id: int, **kwargs) -> FileSchemaResponse:
        """Get download URL for file"""
        return await self._request("GET", f"/{file_id}/download", **kwargs)

    async def confirm_upload(self, file_id: int, **kwargs) -> FileSchemaResponse:
        """Confirm file upload completion"""
        return await self._request("POST", f"/{file_id}/confirm", **kwargs)
