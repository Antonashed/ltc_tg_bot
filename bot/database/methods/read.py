from __future__ import annotations
from typing import Optional

import datetime

from sqlalchemy import exc, func
from sqlalchemy.exc import SQLAlchemyError

from bot.database.models import Database, User, ItemValues, Goods, Categories, Role, BoughtGoods


def check_user(telegram_id: int) -> Optional[User]:
    try:
        return Database().session.query(User).filter(User.telegram_id == telegram_id).one()
    except exc.NoResultFound:
        return None


def check_role(telegram_id: int) -> Optional[int]:
    try:
        role_id = Database().session.query(User.role_id).filter(User.telegram_id == telegram_id).one()[0]
        return Database().session.query(Role.permissions).filter(Role.id == role_id).one()[0]
    except exc.NoResultFound:
        return None


def check_role_name_by_id(role_id: int) -> Optional[str]:
    try:
        return Database().session.query(Role.name).filter(Role.id == role_id).one()[0]
    except exc.NoResultFound:
        return None


def select_max_role_id() -> int:
    return Database().session.query(func.max(Role.id)).scalar()


def select_today_users(date: str) -> Optional[int]:
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        start_of_day = datetime.datetime.combine(date_obj, datetime.time.min)
        end_of_day = datetime.datetime.combine(date_obj, datetime.time.max)

        return Database().session.query(User).filter(
            User.registration_date >= str(start_of_day),
            User.registration_date <= str(end_of_day)
        ).count()
    except (ValueError, SQLAlchemyError):
        return None


def get_user_count() -> int:
    return Database().session.query(User).count()


def select_admins() -> Optional[int]:
    try:
        return Database().session.query(func.count()).filter(User.role_id > 1).scalar()
    except SQLAlchemyError:
        return None


def get_all_users() -> list[tuple[int]]:
    return Database().session.query(User.telegram_id).all()


def get_all_categories() -> list[str]:
    return [category[0] for category in Database().session.query(Categories.name).all()]


def get_all_items(category_name: str) -> list[str]:
    return [item[0] for item in
            Database().session.query(Goods.name).filter(Goods.category_name == category_name).all()]


def get_bought_item_info(item_id: str) -> Optional[dict]:
    result = Database().session.query(BoughtGoods).filter(BoughtGoods.id == item_id).first()
    return result.__dict__ if result else None


def get_item_info(item_name: str) -> Optional[dict]:
    result = Database().session.query(Goods).filter(Goods.name == item_name).first()
    return result.__dict__ if result else None


def get_user_balance(telegram_id: int) -> Optional[float]:
    result = Database().session.query(User.balance).filter(User.telegram_id == telegram_id).first()
    return result[0] if result else None


def get_all_admins() -> list[int]:
    return [admin[0] for admin in Database().session.query(User.telegram_id).filter(User.role_id == 'ADMIN').all()]


def check_item(item_name: str) -> Optional[dict]:
    result = Database().session.query(Goods).filter(Goods.name == item_name).first()
    return result.__dict__ if result else None


def check_category(category_name: str) -> Optional[dict]:
    result = Database().session.query(Categories).filter(Categories.name == category_name).first()
    return result.__dict__ if result else None


def get_item_value(item_name: str) -> Optional[dict]:
    result = Database().session.query(ItemValues).filter(ItemValues.item_name == item_name).first()
    return result.__dict__ if result else None


def select_item_values_amount(item_name: str) -> int:
    return Database().session.query(func.count()).filter(ItemValues.item_name == item_name).scalar()


def check_value(item_name: str) -> Optional[bool]:
    try:
        result = False
        values = select_item_values_amount(item_name)
        for i in range(values):
            is_inf = Database().session.query(ItemValues).filter(ItemValues.item_name == item_name).first()
            if is_inf and getattr(is_inf, "is_infinity", False):
                result = True
        return result
    except exc.NoResultFound:
        return False


def select_user_items(buyer_id: int) -> int:
    return Database().session.query(func.count()).filter(BoughtGoods.buyer_id == buyer_id).scalar()


def select_bought_items(buyer_id: int) -> list[Goods]:
    return Database().session.query(BoughtGoods).filter(BoughtGoods.buyer_id == buyer_id).all()


def select_bought_item(unique_id: int) -> Optional[dict]:
    result = Database().session.query(BoughtGoods).filter(BoughtGoods.unique_id == unique_id).first()
    return result.__dict__ if result else None


def bought_items_list(buyer_id: int) -> list[str]:
    return [
        item[0] for item in
        Database().session.query(BoughtGoods.item_name).filter(BoughtGoods.buyer_id == buyer_id).all()]


def select_all_users() -> int:
    return Database().session.query(func.count(User.telegram_id)).scalar()


def select_count_items() -> int:
    return Database().session.query(ItemValues).count()


def select_count_goods() -> int:
    return Database().session.query(Goods).count()


def select_count_categories() -> int:
    return Database().session.query(Categories).count()


def select_count_bought_items() -> int:
    return Database().session.query(BoughtGoods).count()


def select_today_orders(date: str) -> Optional[int]:
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        start_of_day = datetime.datetime.combine(date_obj, datetime.time.min)
        end_of_day = datetime.datetime.combine(date_obj, datetime.time.max)

        return (
            Database().session.query(func.sum(BoughtGoods.price))
            .filter(
                func.date(BoughtGoods.bought_datetime) >= start_of_day.date(),
                func.date(BoughtGoods.bought_datetime) <= end_of_day.date()
            )
            .scalar() or 0
        )
    except (ValueError, SQLAlchemyError):
        return None


def select_all_orders() -> float:
    return Database().session.query(func.sum(BoughtGoods.price)).scalar() or 0


def select_users_balance() -> float:
    return Database().session.query(func.sum(User.balance)).scalar()


def check_user_referrals(user_id: int) -> int:
    return Database().session.query(User).filter(User.referral_id == user_id).count()


def get_user_referral(user_id: int) -> Optional[int]:
    result = Database().session.query(User.referral_id).filter(User.telegram_id == user_id).first()
    return result[0] if result else None


def get_ltc_address(user_id: int) -> Optional[str]:
    result = Database().session.query(User.ltc_address).filter(User.telegram_id == user_id).first()
    return result[0] if result else None
