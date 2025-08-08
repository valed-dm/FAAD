import queue

from core.config import settings
from core.logging_config import log


class AliasPool:
    def __init__(self):
        self.available_aliases = queue.Queue()
        self.accounts = []
        self.proxy_config = {}

    def load_files(self) -> bool:
        """Loads configuration from data files. Returns True on success."""
        try:
            log.info(f"Loading accounts from {settings.INPUT_FILE}...")
            with settings.INPUT_FILE.open("r", encoding="utf-8") as f:
                self.accounts = [
                    line.strip().split(":", 1) for line in f if ":" in line
                ]

            log.info(f"Loading aliases from {settings.ALIASES_FILE}...")
            with settings.ALIASES_FILE.open("r", encoding="utf-8") as f:
                for alias in f:
                    self.available_aliases.put(alias.strip())

            with settings.PROXY_FILE.open("r", encoding="utf-8") as f:
                line = f.readline().strip()
                if not line:
                    self.proxy_config = {}
                else:
                    parts = line.split(":")
                    self.proxy_config = {
                        "http": f"socks5h://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}",
                        "https": f"socks5h://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}",
                    }
            return True
        except FileNotFoundError as e:
            log.error(f"File not found: {e}. Please ensure data files exist.")
            return False
        except Exception as e:
            log.critical(f"An unexpected error occurred during file loading: {e}")
            return False
