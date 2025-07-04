import logging


def setup_logger():
    """Настройка основного логгера приложения"""
    logger = logging.getLogger("bot.logger_mesh")
    logger.setLevel(logging.INFO)

    # Очищаем предыдущие обработчики
    if logger.hasHandlers():
        logger.handlers.clear()

    # Настройка файлового обработчика
    file_handler = logging.FileHandler("bot.log", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Дополнительно: консольный вывод
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Инициализация глобального логгера
logger = setup_logger()