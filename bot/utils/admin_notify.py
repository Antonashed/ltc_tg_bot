import asyncio
import logging

from bot.misc.env import EnvKeys


ADMIN_CHAT_ID = EnvKeys.OWNER_ID
telegram_bot = None


def set_telegram_bot(bot) -> None:
    """Store bot instance for future notifications."""
    global telegram_bot
    telegram_bot = bot


async def notify_admin(bot, text: str) -> None:
    """Send a message to the admin chat."""
    admin_id = ADMIN_CHAT_ID
    if not admin_id:
        return
    try:
        await bot.send_message(chat_id=int(admin_id), text=text)
    except Exception as exc:
        logging.getLogger(__name__).error("Failed to notify admin: %s", exc)


class TelegramLogHandler(logging.Handler):
    """Logging handler that sends ERROR logs to Telegram."""

    def emit(self, record: logging.LogRecord) -> None:
        if telegram_bot and ADMIN_CHAT_ID and record.levelno >= logging.ERROR:
            message = self.format(record)
            asyncio.create_task(
                telegram_bot.send_message(int(ADMIN_CHAT_ID), f"⚠️ {message}")
            )


