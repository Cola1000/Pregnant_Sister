import math
import operator

def xor_bytes(a, b) -> bytes:
    length = min(len(a), len(b))
    if length == 0:
        return b""
    return bytes(map(operator.xor, a[:length], b[:length]))

def split_blocks(data, block_size=32) -> list[bytes]:
    return [data[i:i + block_size] for i in range(0, len(data), block_size)]

def bytes_to_matrix(data, size=16) -> list[list]:
    n = math.isqrt(size)
    return [list(data[i:i+n]) for i in range(0, size, n)]

def matrix_to_bytes(m) -> bytes:
    return bytes(b for row in m for b in row) # sum concatenates matrix elements to the empty list