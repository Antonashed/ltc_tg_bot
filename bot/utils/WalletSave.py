import os

def save_wallet_to_file(user_id: int, address: str, private_key: str):
    folder = "wallets"
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"wallet_{user_id}.txt")
    with open(file_path, "w") as f:
        f.write(f"LTC Address: {address}\n")
        f.write(f"Private Key (WIF): {private_key}\n")

    print(f"[INFO] Данные кошелька пользователя {user_id} сохранены в {file_path}")
