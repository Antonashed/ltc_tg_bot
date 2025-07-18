from bot.database.models import Database, Goods, ItemValues, Categories


def delete_item(item_name: str) -> None:
    Database().session.query(Goods).filter(Goods.name == item_name).delete()
    Database().session.query(ItemValues).filter(ItemValues.item_name == item_name).delete()
    Database().session.commit()


def delete_only_items(item_name: str) -> None:
    Database().session.query(ItemValues).filter(ItemValues.item_name == item_name).delete()
    Database().session.commit()


def delete_category(category_name: str) -> None:
    goods = Database().session.query(Goods.name).filter(Goods.category_name == category_name).all()
    for item in goods:
        Database().session.query(ItemValues).filter(ItemValues.item_name == item.name).delete()
    Database().session.query(Goods).filter(Goods.category_name == category_name).delete()
    Database().session.query(Categories).filter(Categories.name == category_name).delete()
    Database().session.commit()


def buy_item(item_id: str, infinity: bool = False) -> None:
    if infinity is False:
        Database().session.query(ItemValues).filter(ItemValues.id == item_id).delete()
        Database().session.commit()
    else:
        pass
