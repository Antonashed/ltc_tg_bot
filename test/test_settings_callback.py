import unittest
import asyncio
import os
import base64
import secrets
import sys
from pathlib import Path
import types

# Ensure project root is in import path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Provide dummy aiogram package with basic behavior
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

class DummyInlineKeyboardButton:
    def __init__(self, text=None, callback_data=None, url=None):
        self.text = text
        self.callback_data = callback_data
        self.url = url

class DummyInlineKeyboardMarkup:
    def __init__(self, inline_keyboard=None):
        self.inline_keyboard = inline_keyboard or []

    def add(self, *buttons):
        self.inline_keyboard.append(list(buttons))

    def row(self, *buttons):
        self.inline_keyboard.append(list(buttons))

aiogram.Bot = _Dummy
aiogram.Dispatcher = _Dummy
aiogram.contrib = types.ModuleType("contrib")
aiogram.contrib.fsm_storage = types.ModuleType("fsm_storage")
aiogram.contrib.fsm_storage.memory = types.SimpleNamespace(MemoryStorage=object)
aiogram.types = types.SimpleNamespace(
    Message=_Dummy,
    CallbackQuery=_Dummy,
    InlineKeyboardMarkup=DummyInlineKeyboardMarkup,
    InlineKeyboardButton=DummyInlineKeyboardButton,
    ReplyKeyboardMarkup=_Dummy,
    KeyboardButton=_Dummy,
    ChatType=_Dummy,
)

sys.modules["aiogram"] = aiogram
sys.modules["aiogram.utils"] = aiogram.utils
sys.modules["aiogram.utils.executor"] = aiogram.utils.executor
sys.modules["aiogram.utils.exceptions"] = aiogram.utils.exceptions
sys.modules["aiogram.utils.markdown"] = aiogram.utils.markdown
sys.modules["aiogram.contrib"] = aiogram.contrib
sys.modules["aiogram.contrib.fsm_storage"] = aiogram.contrib.fsm_storage
sys.modules["aiogram.contrib.fsm_storage.memory"] = aiogram.contrib.fsm_storage.memory
sys.modules["aiogram.types"] = aiogram.types

# Ensure encryption key is set
key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
os.environ.setdefault("ENCRYPTION_KEY", key)

import bot.keyboards.inline as inline_kb
from bot.handlers.user.main import settings_callback_handler

class DummyCall:
    def __init__(self):
        self.message = types.SimpleNamespace(chat=types.SimpleNamespace(id=1), message_id=1)
        self.from_user = types.SimpleNamespace(id=42)

class DummyBot:
    def __init__(self):
        self.edited = False
    async def edit_message_text(self, *args, **kwargs):
        self.edited = True

class TestSettingsButton(unittest.TestCase):
    def test_main_menu_contains_settings_button(self):
        inline_kb.InlineKeyboardMarkup = DummyInlineKeyboardMarkup
        inline_kb.InlineKeyboardButton = DummyInlineKeyboardButton
        markup = inline_kb.main_menu(role=1)
        buttons = [btn for row in markup.inline_keyboard for btn in row]
        self.assertTrue(any(b.callback_data == 'settings' for b in buttons))

    def test_settings_callback_handler(self):
        bot = DummyBot()
        call = DummyCall()
        from bot.handlers.user import main as user_main

        async def dummy_get_bot_user_ids(_call):
            return bot, 42

        with unittest.mock.patch.object(user_main, 'get_bot_user_ids', dummy_get_bot_user_ids):
            asyncio.run(settings_callback_handler(call))
        self.assertTrue(bot.edited)

if __name__ == '__main__':
    unittest.main()
