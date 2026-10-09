import secrets

from src.automaton import evolve, grid_to_bytes
from src.types import Grid


def validate_key(key: str | bytes | bytearray, min_length: int = 32) -> bytes:
    if isinstance(key, str):
        key = key.encode("utf-8")
    elif not isinstance(key, (bytes, bytearray)):
        raise TypeError(f"Key must be str or bytes, got {type(key).__name__}")

    if len(key) < min_length:
        raise ValueError(f"Key must be at least {min_length} bytes, got {len(key)}")

    return bytes(key)


def generate_nonce(size: int = 32) -> bytes:
    return secrets.token_bytes(size)


def shift_nonce(nonce: bytes, amount: int) -> bytes:
    if not nonce:
        return b""
    shift = amount % len(nonce)
    return nonce[shift:] + nonce[:shift]


def rotate_byte(b: int, rot: int) -> int:
    rot = rot % 8
    return ((b << rot) & 0xFF) | (b >> (8 - rot))


def mix_key(key: str | bytes | bytearray, nonce: bytes) -> bytes:
    key_bytes = validate_key(key)

    # fold key into 32 bytes if longer than 32
    key_material = bytearray(key_bytes[:32])
    for i in range(32, len(key_bytes)):
        key_material[i % 32] ^= key_bytes[i]

    # mix with nonce bytes via rotation and xor
    mixed = bytearray(32)
    nonce_len = len(nonce) if len(nonce) > 0 else 1
    for i in range(32):
        s = nonce[i % nonce_len]
        mixed[i] = rotate_byte(key_material[i], s % 8) ^ s

    return bytes(mixed)


def fill_grid(material: bytes, rows: int = 16, cols: int = 16) -> list[list[int]]:
    grid = [[0] * cols for _ in range(rows)]
    mat_len = len(material)
    if mat_len == 0:
        return grid

    top, bottom = 0, rows - 1
    left, right = 0, cols - 1
    idx = 0
    lap = 0

    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            grid[top][c] = (material[idx % mat_len] + lap) % 256
            idx += 1
        top += 1

        for r in range(top, bottom + 1):
            grid[r][right] = (material[idx % mat_len] + lap) % 256
            idx += 1
        right -= 1

        if top <= bottom:
            for c in range(right, left - 1, -1):
                grid[bottom][c] = (material[idx % mat_len] + lap) % 256
                idx += 1
            bottom -= 1

        if left <= right:
            for r in range(bottom, top - 1, -1):
                grid[r][left] = (material[idx % mat_len] + lap) % 256
                idx += 1
            left += 1

        lap += 1

    return grid


def parity_grid(grid: list[list[int]]) -> list[list[int]]:
    return [[val % 2 for val in row] for row in grid]


def key_pattern(key: str | bytes | bytearray, nonce: bytes) -> list[list[int]]:
    material = mix_key(key, nonce)
    grid = fill_grid(material, rows=16, cols=16)
    return parity_grid(grid)


def matrix_to_grid(matrix: list[list[int]]) -> Grid:
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0
    grid_rows = []
    for row in matrix:
        val = 0
        for bit in row:
            val = (val << 1) | (bit & 1)
        grid_rows.append(val)
    return Grid(grid_rows, rows, cols)


def grid_to_matrix(grid: Grid) -> list[list[int]]:
    return [
        [(r >> c) & 1 for c in range(grid.num_cols - 1, -1, -1)]
        for r in grid.rows
    ]


def xor_grids(a: Grid | list[list[int]], b: Grid | list[list[int]]) -> Grid | list[list[int]]:
    if isinstance(a, Grid) and isinstance(b, Grid):
        return Grid(
            rows=[r1 ^ r2 for r1, r2 in zip(a.rows, b.rows)],
            num_rows=a.num_rows,
            num_cols=a.num_cols,
        )
    if isinstance(a, Grid):
        a = grid_to_matrix(a)
    if isinstance(b, Grid):
        b = grid_to_matrix(b)
    return [
        [c1 ^ c2 for c1, c2 in zip(r1, r2)]
        for r1, r2 in zip(a, b)
    ]


def fold_bytes(data: bytes) -> bytes:
    half = len(data) // 2
    return bytes(a ^ b for a, b in zip(data[:half], data[half:half * 2]))


def derive_round_keys(
    key: str | bytes | bytearray,
    nonce: bytes,
    rounds: int = 18,
    generations_per_round: int = 4,
) -> list[bytes]:
    key_bytes = validate_key(key)
    initial_pattern = key_pattern(key_bytes, nonce)
    grid = matrix_to_grid(initial_pattern)

    round_keys = []
    for r in range(rounds):
        if r > 0:
            # shifted nonce reinjection with round perturbation
            shifted_nonce = shift_nonce(nonce, r)
            reinj_nonce = bytes((b ^ ((r * 17) & 0xFF)) for b in shifted_nonce)
            reinj_material = mix_key(key_bytes, reinj_nonce)
            reinj_grid = matrix_to_grid(parity_grid(fill_grid(reinj_material, rows=16, cols=16)))
            grid = xor_grids(grid, reinj_grid)

        # Conway's GoL evolution on toroidal grid
        grid = evolve(grid, generations_per_round)

        # 32 bytes (256-bit grid) folded to 16 bytes (128-bit round key)
        evolved_bytes = grid_to_bytes(grid)
        round_keys.append(fold_bytes(evolved_bytes))

    return round_keys
