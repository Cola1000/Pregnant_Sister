import base64

from src.keygen import validate_key, derive_round_keys
from src.padding import unpad
from src.modes import decrypt_blocks
from src.encrypt import convert_bytes


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