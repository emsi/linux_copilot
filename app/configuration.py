"""Configuration module for the backend."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "LinuxCopilot"
    VERSION: str = "0.1.0"

    class Config:
        """Read configuration from .env file."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()
