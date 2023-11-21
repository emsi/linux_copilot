"""Configuration module for the backend."""
import os
import secrets
from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "LinuxCopilot"
    VERSION: str = "0.1.0"

    DATA_DIR: Path = Path(os.getcwd()) / "data"
    API_KEYS_DIR: Path = DATA_DIR / "api_keys"
    FILES_DIR: Path = DATA_DIR / "files"

    class Config:
        """Read configuration from .env file."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()


class ApiKeys(BaseModel):
    api_keys: Optional[List[str]] = None

    class Config:
        """Read secret key from secure file."""

        keys_dir = settings.API_KEYS_DIR
        keys_path = keys_dir / "api_keys"

    def __init__(self):
        # Create config dir if not exists
        os.makedirs(self.Config.keys_dir, mode=0o700, exist_ok=True)
        super(ApiKeys, self).__init__()

        if not self.Config.keys_path.exists():
            self.api_keys = [secrets.token_urlsafe(32)]
            self.Config.keys_path.touch(mode=0o700)
            self.Config.keys_path.write_text(self.api_keys[0])
            print(f"API key created: {self.api_keys[0]}")
        else:
            api_keys = self.Config.keys_path.read_text()
            if "\n" in api_keys:
                api_keys = api_keys.split("\n")
                # remove any empty strings
                api_keys = list(filter(None, api_keys))
                self.api_keys = api_keys
            else:
                self.api_keys = [api_keys]


api_keys = ApiKeys().api_keys
