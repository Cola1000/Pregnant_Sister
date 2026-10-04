import base64

from src.keygen import validate_key, generate_nonce, derive_round_keys
from src.padding import pad
from src.modes import encrypt_blocks

def convert_bytes(data) -> bytes:
    if not isinstance(data, (bytes, bytearray)):
        if isinstance(data, str):
            return data.encode("utf-8")
        else:
            return bytes(data)
    return data


def encrypt(data, key, mode="CBC", nonce_size=32) -> bytes:
    try: 
        validate_key(key)
    except:
        print("Error: invalid key") # TODO: error msg

    data = convert_bytes(data)
    data = pad(data)

    nonce = generate_nonce()
    round_keys = derive_round_keys(key, nonce)

    ct = encrypt_blocks(data, round_keys, mode, nonce)
    ct = nonce + ct

    return base64.b64encode(ct)

    