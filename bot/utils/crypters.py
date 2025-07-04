from cryptography.fernet import Fernet
import os
import logging

logger = logging.getLogger("bot.logger_mesh")

# Инициализация системы шифрования
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if ENCRYPTION_KEY is None:
    raise RuntimeError(
        "ENCRYPTION_KEY environment variable is required for encryption"
    )

try:
    cipher = Fernet(ENCRYPTION_KEY.encode())
except Exception as e:
    logger.critical(f"Ошибка инициализации шифрования: {str(e)}")
    cipher = None


def encrypt_wif(wif: str) -> str:
    """Шифрование WIF-ключа"""
    if not cipher:
        logger.error("Попытка шифрования без инициализированного шифратора")
        return wif

    try:
        return cipher.encrypt(wif.encode()).decode()
    except Exception as e:
        logger.error(f"Ошибка шифрования: {str(e)}")
        return wif


def decrypt_wif(encrypted_wif: str) -> str:
    """Дешифрование WIF-ключа"""
    if not cipher:
        logger.error("Попытка дешифрования без инициализированного шифратора")
        return encrypted_wif

    try:
        return cipher.decrypt(encrypted_wif.encode()).decode()
    except Exception as e:
        logger.error(f"Ошибка дешифрования: {str(e)}")
        return encrypted_wif


