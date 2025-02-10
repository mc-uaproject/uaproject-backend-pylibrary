from typing import Any, Dict


class ServiceError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        return {"error": self.message, "status_code": self.status_code}


class APIError(Exception):
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)
