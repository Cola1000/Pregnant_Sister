from utils import xor_bytes, bytes_to_matrix, matrix_to_bytes

# ref: https://github.com/grwna/cryptosystem-complexity-analysis/blob/main/src/aes_rounds.py 

# lookup tables for galois_mult
MUL2 = [0] * 0x100
MUL3 = [0] * 0x100

for i in range(256):
    m2 = (i << 1) ^ 0x1B if (i & 0x80) else (i << 1)
    MUL2[i] = m2 & 0xFF
    MUL3[i] = MUL2[i] ^ i

def sbox(x):
    # affine sbox
    return ((167*x) + 91) % 256


def sub_bytes(state) -> list[list]:
    for i in range(len(state)):
        for j in range(len(state[i])):
            state[i][j] = sbox(state[i][j])
    return state


def shift_rows(state) -> list[list]:
    for i in range(1, len(state)):
        state[i] = state[i][i:] + state[i][:i] 
    return state


def mix_columns(state) -> list[list]:
    n = len(state) # matrix dim
    for c in range(n):
        col = [state[r][c] for r in range(4)]
        new = [
            MUL2[col[0]] ^ MUL3[col[1]] ^ col[2] ^ col[3],
            col[0] ^ MUL2[col[1]] ^ MUL3[col[2]] ^ col[3],
            col[0] ^ col[1] ^ MUL2[col[2]] ^ MUL3[col[3]],
            MUL3[col[0]] ^ col[1] ^ col[2] ^ MUL2[col[3]],
        ]
        for r in range(n):
            state[r][c] = new[r]
    return state


def mod_add(state, round_key) -> bytes:
    return bytes((a + b) % 256 for a, b in zip(state, round_key))


def rotate(state, amount=0) -> bytes:
    # works like rc6 rotation, rotation amount depends on data
    val = int.from_bytes(bytes(state), byteorder='big')
    
    # 7 bits needed (2^7 = 128)
    amount = ((state[0] * 5 + state[-1]) ^ state[8]) % 128
    
    rot = ((val << amount) | (val >> (128 - amount))) & ((1 << 128) - 1)
    return rot.to_bytes(16, byteorder='big')


def f_spn(half, round_key):
    s = xor_bytes(half, round_key)

    m_s = bytes_to_matrix(s)
    m_s = sub_bytes(m_s)
    m_s = shift_rows(m_s)
    m_s = mix_columns(m_s)

    s = matrix_to_bytes(m_s)
    s = mod_add(s, round_key)
    s = rotate(s)

    return s
    