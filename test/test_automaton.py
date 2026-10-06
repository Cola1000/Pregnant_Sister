import os

from src.automaton import bytes_to_grid, evolve, grid_to_bytes, step
from src.feistel import f_gol
from src.types import Grid


def test_rt():
    for _ in range(100):
        original = os.urandom(16)
        grid = bytes_to_grid(original, 8, 16)
        reconstructed = grid_to_bytes(grid)
        assert original == reconstructed, f"[FAIL] Byte round-trip: Mismatch! {original} != {reconstructed}"
    print("[PASS] Byte round-trip")

def test_still_life():
    rows = [3, 3, 0, 0]
    grid = Grid(rows, 4, 4)

    evolved = evolve(grid, 5)
    assert evolved.rows == [3, 3, 0, 0], f"[FAIL] Still life (2x2 block): Mismatch! {rows} != {evolved.rows}"
    print("[PASS] Still life (2x2 block)")

def test_blinker():
    init = [0, 14, 0, 0, 0]
    grid = Grid(init, 5, 5)
    gen1 = step(grid)

    assert gen1.rows == [4, 4, 4, 0, 0]

    gen2 = step(gen1)

    assert gen2.rows == init
    print("[PASS] Blinker oscillator")

def test_toroidal_wrap():
    init = [0, 0, 19, 0, 0]
    grid = Grid(init, 5, 5)
    gen1 = step(grid)
    assert gen1.rows == [0, 1, 1, 1, 0]
    gen2 = step(gen1)
    assert gen2.rows == init
    print("[PASS] Toroidal boundary swap")

def test_feistel_round():
    half = b"\x01" * 16
    round_key = b"\x02" * 16
    out = f_gol(half, round_key, 4)
    assert len(out) == 16
    assert out != half
    print("[PASS] Feistel f_gol round test")

test_rt()
test_still_life()
test_blinker()
test_toroidal_wrap()
test_feistel_round()
