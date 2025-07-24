import random
from bot.logger_mesh import logger
from bot.payment.walletgenerator import generate_ltc_wallet
from bot.database.models import User, ItemValues, Goods, Categories, BoughtGoods, \
    Operations, UnfinishedOperations
from bot.database import Database


async def create_user(telegram_id: int, registration_date, private_key: str, referral_id, ltc_address, role: int = 1) -> None:
    from bot.database.models import User  # убедись, что путь правильный
    session = Database().session

    # 🔍 Отладка — покажем откуда берётся модель User
    print(f"[DEBUG] User class: {User}")
    print(f"[DEBUG] User module: {User.__module__}")
    print(f"[DEBUG] User dict keys: {list(User.__dict__.keys())}")

    # Проверка, существует ли пользователь
    existing_user = session.query(User).filter(User.telegram_id == telegram_id).first()
    if existing_user:
        print("[DEBUG] User already exists, skipping creation.")
        return

    if ltc_address == 'none':
        wallet = generate_ltc_wallet()
        ltc_address = wallet["address"]

    if private_key == 'none':
        wallet = generate_ltc_wallet()
        private_key = wallet["private_key_wif"]

    if referral_id == '':
        referral_id = None

    try:
        user_obj = User(
            telegram_id=telegram_id,
            role_id=role,
            registration_date=registration_date,
            referral_id=referral_id,
            ltc_address=ltc_address,
            private_key=private_key
        )

        print(f"[DEBUG] Created user object: {user_obj}")
        session.add(user_obj)
        session.commit()
        print("[DEBUG] User successfully committed to database.")
        logger.info(f"[WALLET]Пользователь {telegram_id} зарегистрирован. LTC: {ltc_address}, PrivateKey: {private_key}")

    except TypeError as e:
        print(f"[ERROR] Failed to create User object: {e}")
        raise

    except Exception as ex:
        print(f"[ERROR] Unexpected error during user creation: {ex}")
        raise



def create_item(item_name: str, item_description: str, item_price: int, category_name: str) -> None:
    session = Database().session
    session.add(
        Goods(name=item_name, description=item_description, price=item_price, category_name=category_name))
    session.commit()


def add_values_to_item(item_name: str, value: str, is_infinity: bool) -> None:
    session = Database().session
    if is_infinity is False:
        session.add(
            ItemValues(name=item_name, value=value, is_infinity=False))
    else:
        session.add(
            ItemValues(name=item_name, value=value, is_infinity=True))
    session.commit()


def create_category(category_name: str) -> None:
    session = Database().session
    session.add(
        Categories(name=category_name))
    session.commit()


def create_operation(user_id: int, value: int, operation_time: str) -> None:
    session = Database().session
    session.add(
        Operations(user_id=user_id, operation_value=value, operation_time=operation_time))
    session.commit()


def start_operation(user_id: int, value: int, operation_id: str) -> None:
    session = Database().session
    session.add(
        UnfinishedOperations(user_id=user_id, operation_value=value, operation_id=operation_id))
    session.commit()


def add_bought_item(item_name: str, value: str, price: int, buyer_id: int,
                    bought_time: str) -> None:
    session = Database().session
    session.add(
        BoughtGoods(name=item_name, value=value, price=price, buyer_id=buyer_id, bought_datetime=bought_time,
                    unique_id=str(random.randint(1000000000, 9999999999))))
    session.commit()

def create_deposit_log(user_id: int, operation_id: str):
    session = Database().session
    session.add(

    )