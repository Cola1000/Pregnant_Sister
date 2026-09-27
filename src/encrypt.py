import base64

from src.keygen import validate_key, generate_nonce, derive_round_keys
from src.padding import pad
from src.modes import encrypt_blocks


def encrypt(data, key, mode="CBC"):
    pass
