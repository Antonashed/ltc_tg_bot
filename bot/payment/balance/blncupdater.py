from bot.database.models import Database, User

#Обновление баланса
def update_user_balance(telegram_id: int, usd_amount: float) -> None:
    session = Database().session
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.balance += int(usd_amount)  # если храним в центах
        session.commit()
