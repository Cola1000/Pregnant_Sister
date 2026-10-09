from src.types import Grid


# Toroidal Shifting for Horizontal
def rotl(row: int, n: int) -> int:
    mask = (1 << n) - 1
    # wrapping to pos 0 after overflow
    msb = (row >> (n - 1)) & 1
    return ((row << 1) & mask) | msb

def rotr(row: int, n: int) -> int:
    mask = (1 << n) - 1
    # wrapping to pos col - 1 after overflow
    lsb = row & 1
    return ((row >> 1) & mask) | (lsb << (n - 1))

# Adders
def half_adder(a: int, b: int) -> tuple[int, int]:
    s = a ^ b
    c = a & b
    return s, c

def full_adder(a: int, b:int, c: int) -> tuple[int, int]:
    s = a ^ b ^ c
    carry = (a & b) | (c & (a ^ b))
    return s, carry

# Wallace Tree
def count_neighbors(n1, n2, n3, n4, n5, n6, n7, n8) -> tuple[int, int, int]:
    s1, c1 = full_adder(n1, n2, n3)
    s2, c2 = full_adder(n4, n5, n6)
    s3, c3 = half_adder(n7, n8)

    c0, c_extra = full_adder(s1, s2, s3)
    s_c, c_c = full_adder(c1, c2, c3)

    c1, c_high = half_adder(s_c, c_extra)

    c2_or_more = c_c | c_high

    return c0, c1, c2_or_more

# GoL B3/S23 Rule
def next_state(current: int, c0: int, c1: int, c2_or_more: int) -> int:
    # Rules
    # Cell only lives if total neighbor count is 2 or 3 (less than 2 under population, more than 3 overpopulation)
    # 2 in binary is 010 (c1=1, c0=0, c2=0)
    # 3 in binary is 011 (c1=1, c0=1, c2=0)

    count_2_or_3 = c1 & (~c2_or_more)
    count_3 = count_2_or_3 & c0

    # New cell if count is 3 or survival if alive and count is 2 or 3
    return count_3 | (current & count_2_or_3)

def step(grid: Grid) -> Grid:
    m = grid.num_rows
    new_rows = []
    for r in range(m):
        top = grid.rows[(r - 1) % m]
        mid = grid.rows[r]
        bot = grid.rows[(r + 1) % m]

        n_nw = rotl(top, grid.num_cols); n_n = top; n_ne = rotr(top, grid.num_cols)
        n_w  = rotl(mid, grid.num_cols);            n_e  = rotr(mid, grid.num_cols)
        n_sw = rotl(bot, grid.num_cols); n_s = bot; n_se = rotr(bot, grid.num_cols)

        c0, c1, c2_or_more = count_neighbors(
            n_nw, n_n, n_ne,
            n_w,       n_e,
            n_sw, n_s, n_se
        )
        new_rows.append(next_state(mid, c0, c1, c2_or_more))

    return Grid(new_rows, grid.num_rows, grid.num_cols)

def evolve(grid: Grid, generations: int) -> Grid:
    current_grid = grid
    for _ in range(generations):
        current_grid = step(current_grid)
    return current_grid

def bytes_to_grid(data: bytes, rows, cols: int) -> Grid:
    total_bits = int.from_bytes(data, byteorder="big")

    grid_rows = []
    for r in range(rows):
        shift = (rows - 1 - r) * cols
        row_val = (total_bits >> shift) & ((1 << cols) -1)
        grid_rows.append(row_val)

    return Grid(grid_rows, rows, cols)

def grid_to_bytes(grid: Grid) -> bytes:
    total_bits = 0
    for r in grid.rows:
        total_bits = (total_bits << grid.num_cols) | r

    total_bytes = (len(grid.rows) * grid.num_cols + 7) // 8
    return total_bits.to_bytes(total_bytes, byteorder="big")
