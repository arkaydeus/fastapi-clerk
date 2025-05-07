from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Note that as we're using Pydantic BaseSettings we don't have to read the .env file
# and we can just use the environment variables directly.
# This is because we're using the SettingsConfigDict to read the environment variables
# from the .env file.

# e.g. database_url will read environment variable DATABASE_URL from the .env file.


class Settings(BaseSettings):
    """Application settings class using Pydantic BaseSettings."""

    # Database settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/fastapi_clerk"

    # Clerk settings
    clerk_secret_key: str = ""  # Clerk secret key from dashboard
    clerk_issuer: str = ""  # The issuer URL from your Clerk JWT, e.g., https://example.clerk.accounts.dev

    # API settings
    api_env: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings to avoid reading .env file on each request."""
    return Settings()
