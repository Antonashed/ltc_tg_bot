from bot.database.models import Database, DepositLog


def log_transaction(user_id: int, tx_hash: str, ltc_amount: float, usd_amount: float) -> None:
    """Save information about a deposit transaction."""
    session = Database().session
    session.add(
        DepositLog(
            user_id=user_id,
            tx_hash=tx_hash,
            ltc_amount=ltc_amount,
            usd_amount=usd_amount,
        )
    )
    session.commit()
