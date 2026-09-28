import base64

from src.keygen import validate_key, derive_round_keys
from src.padding import unpad
from src.modes import decrypt_blocks


def decrypt(ciphertext, key, mode="CBC", nonce_size=32) -> bytes:
    pass
