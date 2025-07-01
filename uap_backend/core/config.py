from typing import Literal, Optional

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class UAProjectAPISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        env_prefix="UAPROJECT_BACKEND_",
    )

    # Core API Settings
    API_VERSION: str = "v3"
    API_BASE_URL: str = "https://api.uaproject.xyz"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    DEBUG: bool = False

    # Authentication
    BACKEND_API_KEY: str
    CALLBACK_SECRET: str

    # HTTP Client Configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    RETRY_BACKOFF_FACTOR: float = 2.0
    MAX_RETRY_DELAY: float = 60.0
    REQUEST_TIMEOUT: float = 30.0
    MAX_CONNECTIONS: int = 100
    KEEPALIVE_TIMEOUT: int = 30

    # Library Constants
    USER_AGENT: str = "UAProject-PyLibrary/1.0"
    BEARER_TOKEN_PREFIX: str = "Bearer"
    API_KEY_HEADER: str = "Authorization"

    # Webhook Headers
    WEBHOOK_SIGNATURE_HEADER: str = "X-Webhook-Signature"
    WEBHOOK_EVENT_HEADER: str = "X-Webhook-Event"
    WEBHOOK_TIMESTAMP_HEADER: str = "X-Webhook-Timestamp"

    # Webhook Auto-Registration
    WEBHOOK_AUTO_REGISTER: bool = True
    WEBHOOK_ENDPOINT_URL: Optional[str] = None
    WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_VERIFY_SIGNATURE: bool = False

    # Webhook Retry Configuration
    WEBHOOK_MAX_RETRIES: int = 3
    WEBHOOK_RETRY_DELAY: int = 60
    WEBHOOK_TIMEOUT: int = 30

    # Computed Properties
    @computed_field
    @property
    def API_PREFIX(self) -> str:
        return f"/{self.API_VERSION}"

    @computed_field
    @property
    def FULL_API_URL(self) -> str:
        return f"{self.API_BASE_URL.rstrip('/')}{self.API_PREFIX}"

    @computed_field
    @property
    def RETRYABLE_STATUS_CODES(self) -> set[int]:
        """HTTP status codes that should trigger retries"""
        return {429, 500, 502, 503, 504}


settings = UAProjectAPISettings()
