import unittest
from src.keygen import (
    validate_key,
    generate_nonce,
    shift_nonce,
    rotate_byte,
    mix_key,
    fill_grid,
    parity_grid,
    key_pattern,
    xor_grids,
    fold_bytes,
    derive_round_keys,
    matrix_to_grid,
    grid_to_matrix,
)
from src.types import Grid

class TestKeyGen(unittest.TestCase):
    def setUp(self):
        self.key_str = "0123456789abcdef0123456789abcdef"  # 32 chars
        self.key_bytes = b"0123456789abcdef0123456789abcdef"
        self.long_key = b"LG 24U411A-B FHD IPS Monitor 120Hz, 1ms, with 4 Side Borderless - LG 24U411B-B 144hz"
        self.nonce = b"\x01" * 32

    def test_validate_key_success(self):
        self.assertEqual(validate_key(self.key_str), self.key_bytes)
        self.assertEqual(validate_key(self.key_bytes), self.key_bytes)
        self.assertEqual(validate_key(self.long_key), self.long_key)

    def test_validate_key_too_short(self):
        with self.assertRaises(ValueError):
            validate_key("short_key")
        with self.assertRaises(ValueError):
            validate_key(b"short_key")

    def test_validate_key_invalid_type(self):
        with self.assertRaises(TypeError):
            validate_key(123456)

    def test_generate_nonce(self):
        nonce1 = generate_nonce(32)
        nonce2 = generate_nonce(32)
        self.assertEqual(len(nonce1), 32)
        self.assertEqual(len(nonce2), 32)
        self.assertNotEqual(nonce1, nonce2)

    def test_shift_nonce(self):
        nonce = b"abcdef"
        self.assertEqual(shift_nonce(nonce, 0), b"abcdef")
        self.assertEqual(shift_nonce(nonce, 1), b"bcdefa")
        self.assertEqual(shift_nonce(nonce, 6), b"abcdef")
        self.assertEqual(shift_nonce(nonce, 7), b"bcdefa")

    def test_rotate_byte(self):
        # 0b10000001 = 129
        # rot 1 -> 0b00000011 = 3
        self.assertEqual(rotate_byte(0x81, 0), 0x81)
        self.assertEqual(rotate_byte(0x81, 1), 0x03)
        self.assertEqual(rotate_byte(0x81, 8), 0x81)
        self.assertEqual(rotate_byte(0x01, 7), 0x80)

    def test_mix_key(self):
        m1 = mix_key(self.key_bytes, self.nonce)
        self.assertEqual(len(m1), 32)
        # Deterministic
        m2 = mix_key(self.key_bytes, self.nonce)
        self.assertEqual(m1, m2)
        # Different nonce produces different mix
        m3 = mix_key(self.key_bytes, b"\x02" * 32)
        self.assertNotEqual(m1, m3)

    def test_fill_grid_dimensions_and_spiral(self):
        material = bytes(range(32))
        grid = fill_grid(material, rows=16, cols=16)
        self.assertEqual(len(grid), 16)
        for row in grid:
            self.assertEqual(len(row), 16)
        # Top-left is first element
        self.assertEqual(grid[0][0], material[0])
        # Top-right is 16th element (idx 15)
        self.assertEqual(grid[0][15], material[15])

    def test_parity_grid(self):
        grid = [
            [0, 1, 2, 3],
            [4, 5, 6, 7]
        ]
        expected = [
            [0, 1, 0, 1],
            [0, 1, 0, 1]
        ]
        self.assertEqual(parity_grid(grid), expected)

    def test_key_pattern(self):
        pattern = key_pattern(self.key_bytes, self.nonce)
        self.assertEqual(len(pattern), 16)
        for row in pattern:
            self.assertEqual(len(row), 16)
            for cell in row:
                self.assertIn(cell, (0, 1))

    def test_xor_grids(self):
        g1 = [[0, 1], [1, 0]]
        g2 = [[1, 1], [0, 0]]
        expected = [[1, 0], [1, 0]]
        self.assertEqual(xor_grids(g1, g2), expected)

        grid1 = Grid([0b01, 0b10], 2, 2)
        grid2 = Grid([0b11, 0b00], 2, 2)
        res_grid = xor_grids(grid1, grid2)
        self.assertIsInstance(res_grid, Grid)
        self.assertEqual(res_grid.rows, [0b10, 0b10])

    def test_matrix_grid_conversions(self):
        matrix = [
            [1, 0, 1, 0],
            [0, 1, 0, 1],
        ]
        grid = matrix_to_grid(matrix)
        self.assertEqual(grid.num_rows, 2)
        self.assertEqual(grid.num_cols, 4)
        self.assertEqual(grid.rows, [0b1010, 0b0101])

        reconstructed = grid_to_matrix(grid)
        self.assertEqual(reconstructed, matrix)

    def test_fold_bytes(self):
        data = b"0123456789abcdef" + b"0123456789abcdef"
        folded = fold_bytes(data)
        self.assertEqual(len(folded), 16)
        self.assertEqual(folded, bytes([0] * 16))

        d2 = b"\x00" * 16 + b"\xFF" * 16
        self.assertEqual(fold_bytes(d2), b"\xFF" * 16)

    def test_derive_round_keys_shape_and_determinism(self):
        rks1 = derive_round_keys(self.key_bytes, self.nonce, rounds=18)
        self.assertEqual(len(rks1), 18)
        for rk in rks1:
            self.assertEqual(len(rk), 16)

        # Deterministic with same key and nonce
        rks2 = derive_round_keys(self.key_bytes, self.nonce, rounds=18)
        self.assertEqual(rks1, rks2)

        # Different round keys across rounds (not all identical)
        self.assertNotEqual(rks1[0], rks1[1])

        # Different nonce produces completely different round keys
        rks3 = derive_round_keys(self.key_bytes, b"\x02" * 32, rounds=18)
        self.assertNotEqual(rks1[0], rks3[0])

if __name__ == "__main__":
    unittest.main()
