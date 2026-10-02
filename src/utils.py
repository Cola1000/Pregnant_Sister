
def xor_bytes(a, b) -> bytes:
    length = min(len(a), len(b))

    if length == 0:
        return b""

    num_a = int.from_bytes(a[:length], "big")
    num_b = int.from_bytes(b[:length], "big")
    return (num_a ^ num_b).to_bytes(length, "big")

def split_blocks(data, block_size=32) -> list[bytes]:
    return [data[i:i + block_size] for i in range(0, len(data), block_size)]

