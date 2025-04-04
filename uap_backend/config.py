from pydantic_settings import BaseSettings


class UAProjectAPISettings(BaseSettings):
    # API Settings
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    API_BASE_URL: str = "https://api.uaproject.xyz"
    DEBUG: bool = False

    # Authentication
    BACKEND_API_KEY: str
    CALLBACK_SECRET: str

    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5
    CACHE_DURATION: float = 300

    class Config:
        env_file = ".env"
        env_prefix = "UAPROJECT_BACKEND_"


settings = UAProjectAPISettings()
