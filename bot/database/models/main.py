import datetime
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Text, Boolean, VARCHAR, Numeric, Float
from bot.database.main import Database
from sqlalchemy.orm import relationship

class Permission:
    USE = 1
    BROADCAST = 2
    SETTINGS_MANAGE = 4
    USERS_MANAGE = 8
    SHOP_MANAGE = 16
    ADMINS_MANAGE = 32
    OWN = 64


class Role(Database.BASE):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    default = Column(Boolean, default=False, index=True)
    permissions = Column(Integer)
    users = relationship('User', backref='role', lazy='dynamic')

    def __init__(self, name: str, permissions=None, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0
        self.name = name
        self.permissions = permissions

    @staticmethod
    def insert_roles():
        roles = {
            'USER': [Permission.USE],
            'ADMIN': [Permission.USE, Permission.BROADCAST,
                      Permission.SETTINGS_MANAGE, Permission.USERS_MANAGE, Permission.SHOP_MANAGE, ],
            'OWNER': [Permission.USE, Permission.BROADCAST,
                      Permission.SETTINGS_MANAGE, Permission.USERS_MANAGE, Permission.SHOP_MANAGE,
                      Permission.ADMINS_MANAGE,
                      Permission.OWN],
        }
        default_role = 'USER'
        for r in roles:
            role = Database().session.query(Role).filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            Database().session.add(role)
        Database().session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class User(Database.BASE):
    __tablename__ = 'users'
    telegram_id = Column(BigInteger, nullable=False, unique=True, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), default=1)
    ltc_address = Column(String, nullable=False, default='insert address')
    private_key = Column(String, nullable=False, default='zero')
    balance = Column(BigInteger, nullable=False, default=0)
    registration_date = Column(VARCHAR, nullable=False)
    user_goods = relationship("BoughtGoods", back_populates="user_telegram_id")

    def __init__(self, telegram_id: int, registration_date: datetime.datetime, ltc_address: str, private_key: str, balance: int = 0,
                 referral_id=None, role_id: int = 1):
        self.telegram_id = telegram_id
        self.role_id = role_id
        self.ltc_address = ltc_address
        self.private_key = private_key
        self.balance = balance
        self.referral_id = referral_id
        self.registration_date = registration_date


class Categories(Database.BASE):
    __tablename__ = 'categories'
    name = Column(String(100), primary_key=True, unique=True, nullable=False)

    subcategories = relationship("Subcategories", back_populates="category")  # 🔗
    item = relationship("Goods", back_populates="category")  # опционально, если хочешь прямую связь

    def __init__(self, name: str):
        self.name = name


class Subcategories(Database.BASE):
    __tablename__ = 'subcategories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category_name = Column(String(100), ForeignKey('categories.name'), nullable=False)

    category = relationship("Categories", back_populates="subcategories")
    goods = relationship("Goods", back_populates="subcategory")

    def __init__(self, name: str, category_name: str):
        self.name = name
        self.category_name = category_name


class Goods(Database.BASE):
    __tablename__ = 'goods'
    name = Column(String(100), nullable=False, unique=True, primary_key=True)
    price = Column(BigInteger, nullable=False)
    description = Column(Text, nullable=False)
    category_name = Column(String(100), ForeignKey('categories.name'), nullable=False)  # можно оставить, если нужно
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=False)

    category = relationship("Categories", back_populates="item")  # если оставляешь связь
    subcategory = relationship("Subcategories", back_populates="goods")  # 🔗
    values = relationship("ItemValues", back_populates="item")

    def __init__(self, name: str, price: int, description: str, category_name: str, subcategory_id: int):
        self.name = name
        self.price = price
        self.description = description
        self.category_name = category_name
        self.subcategory_id = subcategory_id



class ItemValues(Database.BASE):
    __tablename__ = 'item_values'
    id = Column(Integer, nullable=False, primary_key=True)
    item_name = Column(String(100), ForeignKey('goods.name'), nullable=False)
    value = Column(Text, nullable=True)
    item = relationship("Goods", back_populates="values")

    def __init__(self, item_name: str, value: str):
        self.item_name = item_name
        self.value = value


class BoughtGoods(Database.BASE):
    __tablename__ = 'bought_goods'
    id = Column(Integer, nullable=False, primary_key=True)
    item_name = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    price = Column(BigInteger, nullable=False)
    buyer_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    bought_datetime = Column(VARCHAR, nullable=False)
    unique_id = Column(BigInteger, nullable=False, unique=True)
    user_telegram_id = relationship("User", back_populates="user_goods")

    def __init__(self, name: str, value: str, price: int, bought_datetime: str, unique_id,
                 buyer_id: int = 0):
        self.item_name = name
        self.value = value
        self.price = price
        self.buyer_id = buyer_id
        self.bought_datetime = bought_datetime
        self.unique_id = unique_id



class DepositLog(Database.BASE):
    __tablename__ = 'deposit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    tx_hash = Column(String, nullable=False, unique=True)
    ltc_amount = Column(Numeric(18, 8), nullable=False)
    usd_amount = Column(Numeric(18, 2), nullable=False)
    timestamp = Column(VARCHAR, default=datetime.datetime.now(datetime.timezone.utc))


class WithdrawLog(Database.BASE):
    __tablename__ = "withdraw_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_user = Column(Integer, nullable=False)
    ltc_amount = Column(Float, nullable=False)
    usd_amount = Column(Float, nullable=False)
    tx_hash = Column(String, nullable=False)
    timestamp = Column(VARCHAR, default=datetime.datetime.now(datetime.timezone.utc))

def register_models():
    Database.BASE.metadata.create_all(Database().engine)
    Role.insert_roles()