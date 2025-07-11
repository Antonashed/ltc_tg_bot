import asyncio

from bot.database import Database
from bot.database.models import User
from bot.payment.incomechecker import check_ltc_transactions
from bot.utils.usdltc import get_ltc_usd_price
from bot.utils.LTClogger import is_transaction_logged
from bot.database.methods import update_balance
from bot.payment.txlogger import log_transaction
from bot.utils.admin_notify import notify_admin
from bot.logger_mesh import logger


async def _process_user_deposit(bot, user):
    """Check deposits for a single user and update their balance."""
    ltc_address = user.ltc_address
    transactions = await check_ltc_transactions(ltc_address)

    for tx in transactions:
        tx_hash = tx["tx_hash"]
        confirmations = tx.get("confirmations", 0)
        value_satoshi = tx.get("value", 0)

        if confirmations >= 6 and not is_transaction_logged(tx_hash):
            ltc_amount = value_satoshi / 1e8
            usd_rate = await get_ltc_usd_price()
            usd_amount = round(ltc_amount * usd_rate, 2)

            # Обновить баланс
            update_balance(user.telegram_id, usd_amount)

            # Сохранить лог
            log_transaction(user.telegram_id, tx_hash, ltc_amount, usd_amount)

            # Отправить уведомление
            await bot.send_message(
                user.telegram_id,
                f"✅ Пополнение {ltc_amount:.4f} LTC (~${usd_amount})\n"
                f"Транзакция: https://live.blockcypher.com/ltc/tx/{tx_hash}"
            )

            await notify_admin(
                bot,
                f"Пополнение баланса: {user.telegram_id} +{usd_amount}$"
            )


# Проверяет пополнения всех пользователей
async def monitor_ltc_deposits(bot, sleep_interval: int = 60):
    """Monitor LTC deposits and update user balances."""
    while True:
        try:
            session = Database().session
            users = session.query(User).all()

            tasks = [asyncio.create_task(_process_user_deposit(bot, user)) for user in users]
            if tasks:
                await asyncio.gather(*tasks)
        except Exception as e:  # noqa: BLE001
            logger.exception(f"Error while monitoring deposits: {e}")
        await asyncio.sleep(sleep_interval)  # Проверка раз в минуту
