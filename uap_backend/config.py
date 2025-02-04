from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Settings
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    DEBUG: bool = False

    # Service URLs
    SERVICE_HOST: str = "http://localhost"
    SERVICE_PORT: int = 8000

    # Authentication
    AUTH_SECRET_KEY: str
    CALLBACK_SECRET: str
    
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
