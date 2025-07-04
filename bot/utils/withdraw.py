import requests
from bitcoinlib.keys import Key
from bitcoinlib.transactions import Transaction

wif_key = "L4HHiUHKWnWbZAq11uSbMCGQNxZdFFLEsnM7TQ9gddzokNxA6DD1d"
key = Key(wif_key, network='litecoin')

from_address = key.address()
to_address = "LcThcvWgdRU8d2B64DMTw9mKxZXmvhhAyt"

def get_utxos(address):
    url = f"https://api.blockcypher.com/v1/ltc/main/addrs/{address}?unspentOnly=true"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data.get('txrefs', [])

utxos = get_utxos(from_address)

if not utxos:
    raise Exception("UTXO не найдены")

fee = int(0.001 * 1e8)  # комиссия в сатошах
total_input = sum(utxo['value'] for utxo in utxos)  # сумма входов в сатошах
send_amount = total_input - fee

if send_amount <= 0:
    raise Exception("Недостаточно средств после вычета комиссии")

print(f"Отправляем {send_amount / 1e8} LTC с адреса {from_address} на {to_address} с комиссией {fee / 1e8} LTC")

# Создаем пустую транзакцию
tx = Transaction(network='litecoin')

# Добавляем входы (UTXO)
for utxo in utxos:
    tx.add_input(prev_txid=utxo['tx_hash'], output_n=utxo['tx_output_n'], value=utxo['value'], address=from_address)

# Добавляем выход (куда отправляем средства)
tx.add_output(send_amount, to_address)

# Подписываем транзакцию
tx.sign([key])

# Получаем HEX транзакции
raw_tx = tx.raw_hex()
print("Подписанная транзакция:")
print(raw_tx)

# Отправляем транзакцию через BlockCypher API
push_url = "https://api.blockcypher.com/v1/ltc/main/txs/push"
resp = requests.post(push_url, json={"tx": raw_tx})
resp.raise_for_status()
print("Транзакция отправлена! Ответ:")
print(resp.json())
