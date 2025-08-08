from loguru import logger

from .config import settings


# This ensures that all loggers used in the application have a consistent name
log = logger.patch(lambda record: record.update(name="AliasWorker"))
log.add(
    settings.LOG_FILE, rotation="500 KB", backtrace=True, diagnose=True, level="DEBUG"
)
