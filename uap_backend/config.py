from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    API_BASE_URL: str = "https://api.uaproject.xyz"
    API_FULL_URL: str = f"https://api.uaproject.xyz{API_PREFIX}"
    DEBUG: bool = False

    # Authentication
    BACKEND_API_KEY: str
    CALLBACK_SECRET: str

    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra="allow"


settings = Settings()
