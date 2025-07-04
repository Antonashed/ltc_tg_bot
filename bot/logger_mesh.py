import logging

from bot.utils.admin_notify import TelegramLogHandler


def setup_logger() -> logging.Logger:
    """Configure application logger."""

    logger = logging.getLogger("bot.logger_mesh")
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler("bot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    telegram_handler = TelegramLogHandler()
    telegram_handler.setFormatter(formatter)
    logger.addHandler(telegram_handler)

    return logger


logger = setup_logger()

