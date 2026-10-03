from src.feistel import process_block
from src.utils import split_blocks, xor_bytes



# each mode functions returns bytes
# ref: 
# - https://www.geeksforgeeks.org/ethical-hacking/block-cipher-modes-of-operation/
# - https://informatika.stei.itb.ac.id/~rinaldi.munir/Kriptografi/2026-2027/08-Block-Cipher-Bagian1-(2026).pdf
def ecb_encrypt(blocks, round_keys, is_decrypt=False):
    outs = []
    for pt in blocks:
        outs.append(process_block(pt, round_keys, is_decrypt))
    return b"".join(outs)


def ecb_decrypt(blocks, round_keys):
    return ecb_encrypt(blocks, round_keys, is_decrypt=True)


def cbc_encrypt(blocks, round_keys, iv):
    outs = []
    fb = iv # feedback value
    for pt in blocks:
        xored = xor_bytes(fb, pt)
        fb = process_block(xored, round_keys)
        outs.append(fb)

    return b"".join(outs)
    


def cbc_decrypt(blocks, round_keys, iv):
    outs = []
    fb = iv
    for ct in blocks:
        decrypted = process_block(ct, round_keys, is_decrypt=True)
        outs.append(xor_bytes(fb, decrypted))
        fb = ct
    return b"".join(outs)


# full block cfb
def cfb_encrypt(blocks, round_keys, iv):
    outs = []
    fb = iv
    for pt in blocks:
        enc = process_block(fb, round_keys)
        fb = xor_bytes(pt, enc)
        outs.append(fb)
    return b"".join(outs)


def cfb_decrypt(blocks, round_keys, iv):
    outs = []
    fb = iv
    for ct in blocks:
        enc = process_block(fb, round_keys)
        outs.append(xor_bytes(ct, enc))
        fb = ct
    return b"".join(outs)



def ofb_encrypt(blocks, round_keys, iv):
    outs = []
    fb = iv
    for pt in blocks:
        fb = process_block(fb, round_keys)
        outs.append(xor_bytes(fb, pt))
    return b"".join(outs)


def ofb_decrypt(blocks, round_keys, iv):
    return ofb_encrypt(blocks, round_keys, iv)


def ctr_encrypt(blocks, round_keys, nonce):
    outs = []
    ctr = int.from_bytes(nonce, byteorder="big")
    for pt in blocks:
        ctr_bytes = ctr.to_bytes(32, byteorder="big")
        enc = process_block(ctr_bytes, round_keys)
        outs.append(xor_bytes(pt, enc))
        ctr += 1
    return b"".join(outs)


def ctr_decrypt(blocks, round_keys, nonce):
    return ctr_encrypt(blocks, round_keys, nonce)


# split full data into 32-byte chunks (blocks)
# process each blocks according to the mode
def encrypt_blocks(data, round_keys, mode, nonce):
    blocks = split_blocks(data)

    match mode.upper():
        case "ECB":
            return ecb_encrypt(blocks, round_keys)
        case "CBC":
            return cbc_encrypt(blocks, round_keys, nonce)
        case "CFB":
            return cfb_encrypt(blocks, round_keys, nonce)
        case "OFB":
            return ofb_encrypt(blocks, round_keys, nonce)
        case "CTR":
            return ctr_encrypt(blocks, round_keys, nonce)


def decrypt_blocks(data, round_keys, mode, nonce):
    blocks = split_blocks(data)

    match mode.upper():
        case "ECB":
            return ecb_decrypt(blocks, round_keys)
        case "CBC":
            return cbc_decrypt(blocks, round_keys, nonce)
        case "CFB":
            return cfb_decrypt(blocks, round_keys, nonce)
        case "OFB":
            return ofb_decrypt(blocks, round_keys, nonce)
        case "CTR":
            return ctr_decrypt(blocks, round_keys, nonce)
