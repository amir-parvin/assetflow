from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AssetFlow"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/assetflow"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/assetflow"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me-in-production-use-a-real-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://assetflow.alamin.rocks"]

    class Config:
        env_file = ".env"


settings = Settings()
