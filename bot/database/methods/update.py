from __future__ import annotations
from bot.database.models import User, ItemValues, Goods, Categories
from bot.database import Database


def set_role(telegram_id: str, role: int) -> None:
    Database().session.query(User).filter(User.telegram_id == telegram_id).update(
        values={User.role_id: role})
    Database().session.commit()


def update_balance(telegram_id: int | str, summ: float) -> None:
    session = Database().session
    session.query(User).filter(User.telegram_id == telegram_id).update(
        values={User.balance: User.balance + summ}
    )
    session.commit()


def buy_item_for_balance(telegram_id: str, summ: int) -> int:
    old_balance = User.balance
    new_balance = old_balance - summ
    Database().session.query(User).filter(User.telegram_id == telegram_id).update(
        values={User.balance: new_balance})
    Database().session.commit()
    return Database().session.query(User.balance).filter(User.telegram_id == telegram_id).one()[0]


def update_item(item_name: str, new_name: str, new_description: str, new_price: int, new_category_name: str) -> None:
    Database().session.query(ItemValues).filter(ItemValues.item_name == item_name).update(
        values={ItemValues.item_name: new_name}
    )
    Database().session.query(Goods).filter(Goods.name == item_name).update(
        values={Goods.name: new_name,
                Goods.description: new_description,
                Goods.price: new_price,
                Goods.category_name: new_category_name}
    )
    Database().session.commit()


def update_category(category_name: str, new_name: str) -> None:
    Database().session.query(Goods).filter(Goods.category_name == category_name).update(
        values={Goods.category_name: new_name})
    Database().session.query(Categories).filter(Categories.name == category_name).update(
        values={Categories.name: new_name})
    Database().session.commit()
