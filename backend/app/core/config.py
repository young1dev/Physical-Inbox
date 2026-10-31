from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    REFRESH_TOKEN_EXPIRE_DAYS: int = 20
    # JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 20
    # DATABASE_URL: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()