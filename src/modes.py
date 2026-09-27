from src.feistel import encrypt_block, decrypt_block, xor_bytes


def split_blocks(data, block_size=32):
    pass


def ecb_encrypt(data, round_keys):
    pass


def ecb_decrypt(data, round_keys):
    pass


def cbc_encrypt(data, round_keys, iv):
    pass


def cbc_decrypt(data, round_keys, iv):
    pass


def cfb_encrypt(data, round_keys, iv):
    pass


def cfb_decrypt(data, round_keys, iv):
    pass


def ofb_encrypt(data, round_keys, iv):
    pass


def ofb_decrypt(data, round_keys, iv):
    pass


def ctr_encrypt(data, round_keys, nonce):
    pass


def ctr_decrypt(data, round_keys, nonce):
    pass


def encrypt_blocks(data, round_keys, mode, nonce):
    pass


def decrypt_blocks(data, round_keys, mode, nonce):
    pass
