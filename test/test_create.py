import unittest
import asyncio
from unittest.mock import patch, MagicMock
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
