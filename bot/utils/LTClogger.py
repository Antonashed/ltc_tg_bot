from bot.database.models import Database, DepositLog


def is_transaction_logged(tx_hash: str) -> bool:
    session = Database().session
    return session.query(DepositLog).filter(DepositLog.tx_hash == tx_hash).first() is not None
