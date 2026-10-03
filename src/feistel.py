from src.automaton import evolve, bytes_to_grid, grid_to_bytes
from src.spn import f_spn  # f_spn(half, round_key):


def f_gol(half, round_key, generations=4) -> bytes:
    pass


def round_function(half, round_key, round_index, total_rounds=18) -> bytes:
    # TODO: pastiin indexing 0 based or 1
    if round_index == 1 or round_index == total_rounds:
        return f_gol(half, round_key)
    else:
        return f_spn(half, round_key)



# feistel for encrypt and decrypt
# ref: https://www.youtube.com/live/8l9xAvuGJFo
def process_block(block, round_keys, is_decrypt = False):
    l = block[:16]
    r = block[16:]

    pass
