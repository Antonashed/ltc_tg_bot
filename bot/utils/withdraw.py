import asyncio
import aiohttp
import traceback
from bit import Key
from bot.database.models import User, Database
from bot.utils.cryptography import decrypt_wif
from bot.logger_mesh import logger

# Конфигурация сети
ADMIN_LTC_ADDRESS = "LcThcvWgdRU8d2B64DMTw9mKxZXmvhhAyt"
MIN_BALANCE = 0.001  # Минимальный баланс для вывода
FEE_LTC = 0.0001  # Фиксированная комиссия
API_TIMEOUT = 15  # Таймаут API-запросов в секундах


async def get_utxo_sum(address: str) -> float:
    """Получение подтвержденного баланса LTC"""
    url = f"https://api.blockcypher.com/v1/ltc/main/addrs/{address}?unspentOnly=true"
    logger.debug(f"Запрос баланса для {address}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=API_TIMEOUT) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"API error {resp.status}: {error_text}")
                    return 0.0

                data = await resp.json()
                if 'error' in data:
                    logger.error(f"Blockcypher error: {data['error']}")
                    return 0.0

                # Используем только подтвержденные UTXO
                confirmed_utxos = [
                    utxo for utxo in data.get("txrefs", [])
                    if utxo.get("confirmed")
                ]

                total_satoshi = sum(utxo["value"] for utxo in confirmed_utxos)
                return total_satoshi / 1e8  # Конвертация в LTC

    except (asyncio.TimeoutError, aiohttp.ClientError) as e:
        logger.warning(f"Сетевой сбой для {address}: {str(e)}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка для {address}: {str(e)}")

    return 0.0


async def send_transaction(tx_hex: str) -> dict:
    """Отправка транзакции в сеть Litecoin"""
    url = "https://api.blockcypher.com/v1/ltc/main/txs/push"
    logger.debug(f"Отправка транзакции: {tx_hex[:64]}...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url,
                    json={"tx": tx_hex},
                    timeout=API_TIMEOUT
            ) as resp:
                if resp.status != 201:
                    error_text = await resp.text()
                    logger.error(f"Ошибка отправки TX: {resp.status} - {error_text}")
                    return {"error": f"HTTP {resp.status}"}

                return await resp.json()

    except (asyncio.TimeoutError, aiohttp.ClientError) as e:
        logger.error(f"Сетевой сбой при отправке TX: {str(e)}")
        return {"error": "network_error"}
    except Exception as e:
        logger.error(f"Неизвестная ошибка при отправке TX: {str(e)}")
        return {"error": "unknown_error"}


async def process_user_withdrawal(user: User) -> dict:
    """Обработка вывода средств для одного пользователя"""
    logger.info(f"Обработка пользователя {user.telegram_id}")

    # Проверка необходимых данных
    if not user.private_key:
        logger.warning("Пропуск: отсутствует приватный ключ")
        return {"status": "skipped", "reason": "no_private_key"}

    if not user.ltc_address:
        logger.warning("Пропуск: отсутствует LTC-адрес")
        return {"status": "skipped", "reason": "no_address"}

    try:
        # Получаем баланс
        balance = await get_utxo_sum(user.ltc_address)
        logger.info(f"Баланс: {balance} LTC")

        # Проверяем минимальный баланс
        if balance < MIN_BALANCE:
            logger.info("Пропуск: баланс ниже минимума")
            return {"status": "skipped", "reason": "low_balance"}

        # Рассчитываем сумму для отправки
        amount_to_send = round(balance - FEE_LTC, 8)
        if amount_to_send <= 0:
            logger.info("Пропуск: недостаточно средств после комиссии")
            return {"status": "skipped", "reason": "insufficient_funds"}

        # Дешифруем ключ
        wif = decrypt_wif(user.private_key)
        if wif == user.private_key:
            logger.error("Ошибка дешифрования ключа")
            return {"status": "error", "reason": "decryption_failed"}

        # Создаем транзакцию
        key = Key(wif)
        tx_hex = key.create_transaction(
            outputs=[(ADMIN_LTC_ADDRESS, amount_to_send)],
            fee=int(FEE_LTC * 1e8),
            absolute_fee=True
        )

        # Отправляем транзакцию
        result = await send_transaction(tx_hex)
        if "error" in result:
            logger.error(f"Ошибка отправки: {result['error']}")
            return {"status": "error", "reason": "tx_send_failed"}

        # Успешная транзакция
        tx_hash = result['tx']['hash']
        logger.success(f"Успешно! TX: {tx_hash}, Сумма: {amount_to_send} LTC")
        return {
            "status": "success",
            "tx_hash": tx_hash,
            "amount": amount_to_send,
            "address": user.ltc_address
        }

    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}\n{traceback.format_exc()}")
        return {"status": "error", "reason": "unhandled_exception"}


async def withdraw_all_users():
    """Основная функция для вывода средств всех пользователей"""
    logger.info("==== ЗАПУСК ВЫВОДА СРЕДСТВ ====")

    results = {
        "success": [],
        "skipped": [],
        "error": []
    }

    try:
        session = Database().session
        users = session.query(User).all()
        logger.info(f"Найдено пользователей: {len(users)}")

        for user in users:
            result = await process_user_withdrawal(user)
            results[result["status"]].append(result)
            await asyncio.sleep(1)  # Пауза между запросами

    except Exception as e:
        logger.critical(f"ФАТАЛЬНАЯ ОШИБКА: {str(e)}\n{traceback.format_exc()}")
        results["error"].append({
            "status": "fatal_error",
            "error": str(e)
        })

    # Формируем отчет
    success_count = len(results["success"])
    skipped_count = len(results["skipped"])
    error_count = len(results["error"])

    logger.info(
        f"==== ЗАВЕРШЕНО: успешно {success_count}, "
        f"пропущено {skipped_count}, "
        f"ошибок {error_count} ===="
    )

    return results