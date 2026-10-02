import base64

from src.keygen import validate_key, generate_nonce, derive_round_keys
from src.padding import pad, unpad
from src.modes import encrypt_blocks, decrypt_blocks

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
    ct += nonce

    return base64.b64encode(ct)

def decrypt(data, key, mode="CBC", nonce_size=32) -> bytes:
    try: 
        validate_key(key)
    except:
        print("Error: invalid key") # TODO: error msg

    data = convert_bytes(data)

    decoded = base64.b64decode(data) # ct
    nonce = decoded[-nonce_size:]
    round_keys = derive_round_keys(key, nonce)
    pt = decrypt_blocks(data, round_keys, mode, nonce)
    return unpad(pt)
    