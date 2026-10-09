from dataclasses import dataclass


@dataclass
class Grid:
    rows: list[int]
    num_rows: int
    num_cols: int
