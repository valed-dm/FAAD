from functools import cached_property
from pathlib import Path
from typing import List
from typing import Optional

from pydantic import computed_field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    # Load secrets from the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Credentials from .env ---
    CLIENT_ID: str
    CLIENT_SECRET: str

    # NEW: An optional field to catch the user's input path from an environment variable
    # We will set this variable from main.py before loading the settings
    DATA_DIR_INPUT: Optional[str] = None

    # --- Base Directories (Output and Logs remain relative to the script) ---
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    OUTPUT_DIR: Path = BASE_DIR / "output"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # --- DYNAMIC DATA DIRECTORY ---
    # This field is computed. It checks if the user provided a path.
    # If so, it uses it. If not, it falls back to the default `data` folder.
    @computed_field
    @cached_property
    def DATA_DIR(self) -> Path:
        if self.DATA_DIR_INPUT:
            # Create a Path object from the user's input string.
            # pathlib handles Windows/Linux slashes automatically.
            return Path(self.DATA_DIR_INPUT)
        # Fallback to the default location if no input was given
        return self.BASE_DIR / "data"

    # --- File Paths (now depend on the computed DATA_DIR) ---
    @computed_field
    @cached_property
    def INPUT_FILE(self) -> Path:
        return self.DATA_DIR / "input.txt"

    @computed_field
    @cached_property
    def ALIASES_FILE(self) -> Path:
        return self.DATA_DIR / "aliases.txt"

    @computed_field
    @cached_property
    def REMAINING_ALIASES_FILE(self) -> Path:
        return self.DATA_DIR / "remaining_aliases.txt"

    @computed_field
    @cached_property
    def PROXY_FILE(self) -> Path:
        return self.DATA_DIR / "proxy.txt"

    # --- Other file paths remain the same ---
    LOG_FILE: Path = LOGS_DIR / "alias_adder.log"
    CRITICAL_ERRORS_FILE: Path = OUTPUT_DIR / "critical_errors.txt"
    OUTPUT_FILE: Path = OUTPUT_DIR / "output.txt"

    # --- Freenet URLs ---
    LOGIN_PAGE_URL: str = "https://power.freenet.de/"
    OAUTH_HANDSHAKE_URL: str = "https://oauth.freenet.de/"
    LOGIN_URL: str = "https://oauth.freenet.de/oauth/token"
    MAIL_ACCOUNTS_URL: str = "https://api.mail.freenet.de/v2.0/mail/accounts"
    SETTINGS_URL: str = "https://api.mail.freenet.de/v2.0/customer/settings"

    # --- App Configuration ---
    MAX_ALIASES_PER_ACCOUNT: int = 10
    MAX_WORKERS: int = 5
    BROWSER_PROFILES: List[str] = ["chrome110", "chrome107", "chrome104", "chrome99"]


settings = Settings()
