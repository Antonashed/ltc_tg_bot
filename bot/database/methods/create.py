import random

from bot.logger_mesh import logger
from bot.payment.walletgenerator import generate_ltc_wallet
from bot.database.models import ItemValues, Goods, Categories, BoughtGoods, Subcategories
from bot.database import Database


async def create_user(telegram_id: int, registration_date, private_key: str, ltc_address, role: int = 1) -> None:
    from bot.database.models import User
    session = Database().session

    # Проверка, существует ли пользователь
    existing_user = session.query(User).filter(User.telegram_id == telegram_id).first()
    if existing_user:
        return

    if ltc_address == 'insert address':
        wallet = generate_ltc_wallet()
        ltc_address = wallet["address"]

    if private_key == 'None':
        wallet = generate_ltc_wallet()
        private_key = wallet["private_key_encrypted"]

    try:
        user_obj = User(
            telegram_id=telegram_id,
            role_id=role,
            registration_date=registration_date,
            ltc_address=ltc_address,
            private_key=private_key
        )

        session.add(user_obj)
        session.commit()
        logger.info(f"[WALLET]Пользователь {telegram_id} зарегистрирован. LTC: {ltc_address}, PrivateKey: {private_key}")

    except TypeError as e:
        print(f"[ERROR] Failed to create User object: {e}")
        raise

    except Exception as ex:
        print(f"[ERROR] Unexpected error during user creation: {ex}")
        raise



def create_item(item_name: str, item_description: str, item_price: int, category_name: str, subcategory_id: int) -> None:
    session = Database().session
    session.add(
        Goods(name=item_name, description=item_description, price=item_price, category_name=category_name, subcategory_id=subcategory_id))
    session.commit()


def add_values_to_item(item_name: str, value: str) -> None:
    session = Database().session
    session.add(
        ItemValues(item_name=item_name, value=value))
    session.commit()


def create_category(category_name: str) -> None:
    session = Database().session
    session.add(
        Categories(name=category_name))
    session.commit()


def create_subcategory(subcategory_name: str, category_name: str):
    session = Database().session
    session.add(
        Subcategories(name=subcategory_name, category_name=category_name)
    )
    session.commit()


def add_bought_item(item_name: str, value: str, price: int, buyer_id: int,
                    bought_time: str) -> None:
    session = Database().session
    session.add(
        BoughtGoods(name=item_name, value=value, price=price, buyer_id=buyer_id, bought_datetime=bought_time,
                    unique_id=str(random.randint(1000000000, 9999999999))))
    session.commit()
