# Author: Gordon Ng
# This file is LLM generated

DIRS = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

def walls_for(x: int, y: int, rows: int, cols: int, *, diagonals: bool = True) -> tuple[int]:
    """
    Returns tuple of open directions (1=open, 0=closed).
    Only directions leading to in-bounds coordinates are open.
    If diagonals=False, diagonal directions are closed.
    """
    flags: list[int] = []
    for idx, (dx, dy) in enumerate(DIRS):
        if not diagonals and idx % 2 == 1:      # diagonals are odd
            flags.append(-1)
            continue
        nx, ny = x + dx, y + dy
        flags.append(0 if 0 <= nx < rows and 0 <= ny < cols else -1)
    return tuple(flags)


def build_grid(rows: int, cols: int, *, alt: list[list[int]] | None = None, diagonals: bool = True):
    """
    Creates grid for pathfinding tests.
    Parameters:
        alt: 2D list of altitudes (defaults to all zeros)
        diagonals: If False, diagonal movements are blocked
    """
    if alt is None:
        alt = [[0] * cols for _ in range(rows)]
    grid = []
    for x in range(rows):
        row = []
        for y in range(cols):
            walls = walls_for(x, y, rows, cols, diagonals=diagonals)
            row.append([(x, y), (y, y), alt[x][y], walls])
        grid.append(row)
    return grid