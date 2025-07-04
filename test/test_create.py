import unittest
import asyncio
import os
from unittest.mock import patch, MagicMock
import base64
import secrets
import sys
from pathlib import Path
import types

# Ensure project root is in import path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Provide dummy aiogram package to satisfy imports
aiogram = types.ModuleType("aiogram")
aiogram.utils = types.ModuleType("utils")
aiogram.utils.executor = types.SimpleNamespace(start_polling=lambda *a, **k: None)
aiogram.utils.exceptions = types.SimpleNamespace(
    BotBlocked=type("BotBlocked", (), {}),
    ChatNotFound=type("ChatNotFound", (), {}),
)
aiogram.utils.markdown = types.SimpleNamespace(
    text=lambda *a, **k: "",
    bold=lambda *a, **k: "",
    code=lambda *a, **k: "",
)
class _Dummy:
    def __init__(self, *args, **kwargs):
        pass

aiogram.Bot = _Dummy
aiogram.Dispatcher = _Dummy
aiogram.contrib = types.ModuleType("contrib")
aiogram.contrib.fsm_storage = types.ModuleType("fsm_storage")
aiogram.contrib.fsm_storage.memory = types.SimpleNamespace(MemoryStorage=object)
aiogram.types = types.SimpleNamespace(
    Message=_Dummy,
    CallbackQuery=_Dummy,
    InlineKeyboardMarkup=_Dummy,
    InlineKeyboardButton=_Dummy,
    ReplyKeyboardMarkup=_Dummy,
    KeyboardButton=_Dummy,
    ChatType=_Dummy,
)
sys.modules.setdefault("aiogram", aiogram)
sys.modules.setdefault("aiogram.utils", aiogram.utils)
sys.modules.setdefault("aiogram.utils.executor", aiogram.utils.executor)
sys.modules.setdefault("aiogram.utils.exceptions", aiogram.utils.exceptions)
sys.modules.setdefault("aiogram.utils.markdown", aiogram.utils.markdown)
sys.modules.setdefault("aiogram.contrib", aiogram.contrib)
sys.modules.setdefault("aiogram.contrib.fsm_storage", aiogram.contrib.fsm_storage)
sys.modules.setdefault(
    "aiogram.contrib.fsm_storage.memory", aiogram.contrib.fsm_storage.memory
)
sys.modules.setdefault("aiogram.types", aiogram.types)

# Ensure encryption key is available before importing application modules
key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
os.environ.setdefault("ENCRYPTION_KEY", key)

from bot.database.models import User
from bot.database.methods.create import create_user  # правильный импорт


class TestCreateUser(unittest.TestCase):

    @patch('bot.database.methods.create.Database')  # ✅ правильный путь
    @patch('bot.database.methods.create.generate_ltc_wallet')  # ✅ правильный путь
    def test_create_user_new_user(self, mock_generate_ltc_wallet, mock_database):
        mock_session = MagicMock()
        mock_database.return_value.session = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None

        mock_generate_ltc_wallet.return_value.__getitem__.side_effect = lambda key: {
            'private_key_encrypted': 'mock_private_key',
            'address': 'mock_address'
        }[key]

        telegram_id = 123456
        registration_date = "2025-07-04"
        private_key = 'None'
        ltc_address = 'insert address'
        role = 1

        asyncio.run(create_user(telegram_id, registration_date, private_key, ltc_address, role))

        mock_generate_ltc_wallet.assert_called()
        mock_session.add.assert_called_once()
        user_obj = mock_session.add.call_args[0][0]

        self.assertIsInstance(user_obj, User)
        self.assertEqual(user_obj.telegram_id, telegram_id)
        self.assertEqual(user_obj.registration_date, registration_date)
        self.assertEqual(user_obj.private_key, "mock_private_key")
        self.assertEqual(user_obj.ltc_address, "mock_address")
        mock_session.commit.assert_called_once()

    @patch('bot.database.methods.create.Database')  # ✅ исправлено
    def test_create_user_existing_user(self, mock_database):
        mock_session = MagicMock()
        mock_database.return_value.session = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = MagicMock()

        telegram_id = 123456
        registration_date = "2025-07-04"
        private_key = 'None'
        ltc_address = 'insert address'
        role = 1

        asyncio.run(create_user(telegram_id, registration_date, private_key, ltc_address, role))

        mock_session.commit.assert_not_called()
        mock_session.add.assert_not_called()

    @patch('bot.database.methods.create.Database')
    @patch('bot.database.methods.create.generate_ltc_wallet')
    def test_create_user_no_wallet_needed(self, mock_generate_ltc_wallet, mock_database):
        mock_session = MagicMock()
        mock_database.return_value.session = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None

        telegram_id = 123456
        registration_date = "2025-07-04"
        private_key = 'actual_key'  # ✅ не 'None'
        ltc_address = 'custom_address'  # ✅ не 'insert address'
        role = 1

        asyncio.run(create_user(telegram_id, registration_date, private_key, ltc_address, role))

        mock_generate_ltc_wallet.assert_not_called()
        mock_session.add.assert_called_once()
        user_obj = mock_session.add.call_args[0][0]

        self.assertEqual(user_obj.private_key, 'actual_key')
        self.assertEqual(user_obj.ltc_address, 'custom_address')

if __name__ == '__main__':
    unittest.main()
