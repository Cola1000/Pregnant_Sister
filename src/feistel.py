from automaton import evolve, bytes_to_grid, grid_to_bytes
from spn import f_spn  # f_spn(half, round_key):
from utils import xor_bytes


def f_gol(half, round_key, generations=4) -> bytes:
    rxor = xor_bytes(half, round_key)
    
    grid = bytes_to_grid(rxor, rows=8, cols=16)
    evolved = evolve(grid, generations)
    flattened = grid_to_bytes(evolved)
    
    # additional xor to mitigate GoL collisions
    out = xor_bytes(flattened, half)

    return out


def round_function(half, round_key, round_index, total_rounds=18) -> bytes:
    # TODO: pastiin indexing 0 based or 1
    if round_index == 1 or round_index == total_rounds:
        return f_gol(half, round_key)
    else:
        return f_spn(half, round_key)



# feistel for encrypt and decrypt
# ref: https://www.youtube.com/live/8l9xAvuGJFo
def process_block(block, round_keys, is_decrypt = False) -> bytes:
    rounds = list(range(1,19)) # list of indices
    if is_decrypt:
        rounds = rounds[::-1]


    # bytes
    l = block[:16]
    r = block[16:]

    for i in rounds:
        store_r = r
        r = xor_bytes(l, round_function(r, round_keys[i-1], i))
        l = store_r

    return r + l