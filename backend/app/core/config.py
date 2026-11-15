from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "development"
    secret_key: str = "development-only-change-me-32bytes-minimum"
    database_url: str = "sqlite:///./agrispace.db"
    cors_origins: str = "http://localhost:5173"
    demo_mode: bool = True
    nasa_power_enabled: bool = False
    nasa_power_base_url: str = "https://power.larc.nasa.gov/api/temporal/daily/point"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 14
    secure_cookies: bool = False
    cookie_domain: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
