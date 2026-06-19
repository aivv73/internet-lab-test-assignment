import logging
from logging.handlers import RotatingFileHandler

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure file logging for the application."""
    settings.log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    if any(isinstance(handler, RotatingFileHandler) for handler in logger.handlers):
        return

    handler = RotatingFileHandler(
        settings.log_file,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )
    logger.addHandler(handler)
