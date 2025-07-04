from aiogram import types, Dispatcher
from aiogram.types import CallbackQuery

from bot.keyboards import console
from bot.database.methods import check_role
from bot.misc import TgConfig
from bot.logger_mesh import logger

from bot.handlers.admin.broadcast import register_mailing
from bot.handlers.admin.shop_management_states import register_shop_management
from bot.handlers.admin.user_management_states import register_user_management
from bot.handlers.other import get_bot_user_ids
#from bot.utils.withdraw import withdraw_all_users_to_admin
from aiogram.utils.markdown import text, bold, code
from bot.misc.env import EnvKeys


ADMIN_CHAT_ID = EnvKeys.OWNER_ID

async def console_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role > 1:
        await bot.edit_message_text('⛩️ Меню администратора',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=console())


#async def withdraw_command_handler(message: types.Message):
  #  """Обработчик команды вывода средств"""
 #   logger.info(f"Запрос на вывод от пользователя {message.from_user.id}")

    # Проверка прав (заглушка - реализуйте свою логику)
#    if not await is_admin(message.from_user.id):
#        await message.reply("❌ Доступ запрещен")
#        return

 #   await message.reply("🔄 Начинаю вывод средств...")

 #   try:
#        results = await withdraw_all_users()
#        success_txs = results["success"]
#
  #      if not success_txs:
 #           await message.answer("ℹ️ Нет средств для вывода")
#            return

        # Формируем отчет
#        report = ["✅ Успешные транзакции:"]
#        for tx in success_txs:
#            report.append(
#                f"• Адрес: {tx['address']}\n"
#                f"  Сумма: {tx['amount']} LTC\n"
#                f"  TX: https://blockchair.com/litecoin/transaction/{tx['tx_hash']}"
#            )
#
#        total = sum(tx["amount"] for tx in success_txs)
 #       report.append(f"💵 Итого: {total} LTC")
#
#        await message.answer("\n\n".join(report), disable_web_page_preview=True)
#
##    except Exception as e:
 #       logger.error(f"Ошибка обработчика: {str(e)}")
 #       await message.answer("⚠️ Произошла ошибка при выводе средств")


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(console_callback_handler,
                                       lambda c: c.data == 'console')
#    dp.register_message_handler(withdraw_command_handler, commands=['withdraw'])

    register_mailing(dp)
    register_shop_management(dp)
    register_user_management(dp)
