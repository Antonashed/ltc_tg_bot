import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from aiogram.types import Message
from bot.handlers.user.main import start, TgConfig, EnvKeys  # импорт напрямую


class TestStartWalletCreation(unittest.IsolatedAsyncioTestCase):

    @patch("bot.handlers.main.save_wallet_to_file")
    @patch("bot.handlers.main.create_user", new_callable=AsyncMock)
    @patch("bot.handlers.main.generate_ltc_wallet")
    @patch("bot.handlers.main.check_user")
    @patch("bot.handlers.main.select_max_role_id")
    @patch("bot.handlers.main.check_role")
    @patch("bot.handlers.main.get_bot_user_ids")
    @patch("bot.handlers.main.main_menu")
    async def test_wallet_created_and_saved(
        self,
        mock_main_menu,
        mock_get_bot_user_ids,
        mock_check_role,
        mock_select_max_role,
        mock_check_user,
        mock_generate_wallet,
        mock_create_user,
        mock_save_wallet
    ):
        # ===== УСТАНОВКА конфигов ВРУЧНУЮ (вариант 1) =====
        TgConfig.STATE = {}
        TgConfig.CHANNEL_URL = "https://t.me/mychannel"
        TgConfig.HELPER_URL = "@helper"
        EnvKeys.OWNER_ID = "123"

        user_id = 123
        mock_bot = AsyncMock()
        mock_get_bot_user_ids.return_value = (mock_bot, user_id)

        mock_check_user.return_value = None
        mock_select_max_role.return_value = 5
        mock_check_role.return_value = 1

        wallet = {
            "address": "ltc123",
            "private_key_encrypted": "enc_key",
            "private_key_wif": "raw_wif"
        }
        mock_generate_wallet.return_value = wallet
        mock_main_menu.return_value = MagicMock()

        mock_message = MagicMock(spec=Message)
        mock_message.chat.type = "private"
        mock_message.text = "/start"
        mock_message.chat.id = 1000
        mock_message.message_id = 42
        mock_message.from_user.id = user_id

        mock_bot.get_chat_member.return_value.status = "member"

        # ===== Вызов =====
        await start(mock_message)

        # ===== Проверки =====
        mock_generate_wallet.assert_called_once()
        mock_create_user.assert_awaited_once()

        mock_save_wallet.assert_called_once_with(user_id, "ltc123", "raw_wif")
        mock_bot.send_message.assert_awaited_once()
        mock_bot.delete_message.assert_awaited_once()
