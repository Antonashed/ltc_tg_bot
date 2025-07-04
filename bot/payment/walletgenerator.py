from bit import Key
from bit.format import bytes_to_wif
import hashlib
import base58
from bot.utils.crypters import encrypt_wif

def public_key_to_ltc_address(public_key_hex: str) -> str:
    """
    Преобразует публичный ключ в адрес Litecoin (P2PKH, mainnet).
    """
    pubkey_bytes = bytes.fromhex(public_key_hex)
    sha = hashlib.sha256(pubkey_bytes).digest()
    ripemd = hashlib.new('ripemd160', sha).digest()

    versioned_payload = b'\x30' + ripemd  # Litecoin mainnet prefix for P2PKH
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
    full_payload = versioned_payload + checksum
    return base58.b58encode(full_payload).decode()

def generate_ltc_wallet():
    """
    Генерирует связанный приватный WIF-ключ и Litecoin-адрес.
    """
    key = Key()
    raw_private_key = key.to_bytes()

    # Приватный ключ в WIF с Litecoin-префиксом
    wif_key = bytes_to_wif(raw_private_key, compressed=True, version=b'\xb0')
    encrypted_wif = encrypt_wif(wif_key)

    # Публичный ключ и LTC-адрес
    public_key = key.public_key.hex()
    ltc_address = public_key_to_ltc_address(public_key)

    return {
        "private_key_encrypted": encrypted_wif,
        "public_key": public_key,
        "address": ltc_address
    }