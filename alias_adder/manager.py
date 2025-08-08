from concurrent.futures import ThreadPoolExecutor
import threading

from core.config import settings
from core.logging_config import log

from .alias_pool import AliasPool
from .worker import process_account


class FreenetAliasManager:
    def __init__(self):
        self.pool = AliasPool()
        self.output_lock = threading.Lock()

    def run(self):
        if not self.pool.load_files():
            log.error("Could not load initial data. Shutting down.")
            return

        if not self.pool.accounts:
            log.error("No accounts found. Nothing to do.")
            return

        initial_alias_count = self.pool.available_aliases.qsize()
        log.info(
            f"Loaded {len(self.pool.accounts)} accounts"
            f" and {initial_alias_count} aliases."
        )
        log.info(
            f"Starting processing with {settings.MAX_WORKERS} concurrent worker(s)."
        )

        with ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
            for account in self.pool.accounts:
                executor.submit(
                    process_account,
                    account,
                    self.pool.available_aliases,
                    self.pool.proxy_config,
                    self.output_lock,
                )

        log.success("Processing complete for all accounts.")
        self._write_remaining_aliases()

    def _write_remaining_aliases(self):
        log.info("Writing unused aliases to the remaining aliases file...")
        count = 0
        with settings.REMAINING_ALIASES_FILE.open("w", encoding="utf-8") as f:
            while not self.pool.available_aliases.empty():
                try:
                    alias = self.pool.available_aliases.get_nowait()
                    f.write(alias + "\n")
                    count += 1
                except self.pool.available_aliases.empty():
                    break
        log.success(
            f"Successfully wrote {count} remaining aliases"
            f" to {settings.REMAINING_ALIASES_FILE}"
        )
