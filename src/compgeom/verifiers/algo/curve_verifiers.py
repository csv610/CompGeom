from __future__ import annotations

from typing import List, Tuple
from compgeom.kernel import EPSILON


def _morton_decode(index: int) -> Tuple[int, int]:
    """Decodes a Morton index into (x, y) coordinates."""
    x = y = 0
    for bit in range(32):
        x |= (index & (1 << (2 * bit))) >> bit
        y |= (index & (1 << (2 * bit + 1))) >> (bit + 1)
    return x, y


def _peano_decode(index: int, level: int) -> Tuple[int, int]:
    """Decodes a Peano index into (x, y) coordinates."""
    x = y = px = py = 0
    for power in range(level - 1, -1, -1):
        power_of_three = 3**power
        digit = (index // (9**power)) % 9
        row = digit // 3
        col = digit % 3 if row % 2 == 0 else 2 - (digit % 3)
        if py % 2 == 1:
            col = 2 - col
        if px % 2 == 1:
            row = 2 - row
        x += col * power_of_three
        y += row * power_of_three
        if col == 1:
            px += 1
        if row == 1:
            py += 1
    return x, y


def verify_peano_curve(path: List[int], level: int) -> bool:
    """
    Verifies if a given path is a valid Peano curve of a specific level.
    1. Path length must be 9^level.
    2. Every index in the path must be unique and in range [0, 9^level - 1].
    3. The sequence of indices must match the Peano traversal.
    """
    expected_length = 9**level
    if len(path) != expected_length:
        raise ValueError(f"Peano curve path length {len(path)} does not match expected {expected_length}")

    width = 3**level
    seen_indices = set()

    for i, cell_index in enumerate(path):
        if cell_index < 0 or cell_index >= expected_length:
             raise ValueError(f"Path index {cell_index} is out of bounds [0, {expected_length-1}]")

        if cell_index in seen_indices:
            raise ValueError(f"Duplicate index {cell_index} found in path")
        seen_indices.add(cell_index)

        # Peano specific check:
        x, y = _peano_decode(i, level)
        expected_cell_index = y * width + x
        if cell_index != expected_cell_index:
            raise ValueError(
                f"Path mismatch at index {i}: expected cell {expected_cell_index} (coords {x},{y}), "
                f"got {cell_index}"
            )

    return True


def verify_morton_curve(path: List[int], level: int) -> bool:
    """
    Verifies if a given path is a valid Morton curve of a specific level.
    1. Path length must be 4^level.
    2. Every index in the path must be unique and in range [0, 4^level - 1].
    3. The sequence of indices must match the Z-order traversal.
    """
    expected_length = 4**level
    if len(path) != expected_length:
        raise ValueError(f"Morton curve path length {len(path)} does not match expected {expected_length}")

    width = 2**level
    seen_indices = set()
    
    for i, cell_index in enumerate(path):
        if cell_index < 0 or cell_index >= expected_length:
             raise ValueError(f"Path index {cell_index} is out of bounds [0, {expected_length-1}]")
        
        if cell_index in seen_indices:
            raise ValueError(f"Duplicate index {cell_index} found in path")
        seen_indices.add(cell_index)

        # Morton (Z-order) specific check:
        # The i-th point in the path should correspond to the Morton decoding of i.
        x, y = _morton_decode(i)
        expected_cell_index = y * width + x
        if cell_index != expected_cell_index:
            raise ValueError(
                f"Path mismatch at index {i}: expected cell {expected_cell_index} (coords {x},{y}), "
                f"got {cell_index}"
            )

    return True


def _hilbert_decode(index: int, order: int) -> Tuple[int, int]:
    """Decodes a Hilbert index into (x, y) coordinates."""
    x = y = 0
    t = index
    for scale in range(order):
        rx = 1 & (t // 2)
        ry = 1 & (t ^ rx)
        if ry == 0:
            if rx == 1:
                x, y = (2**scale - 1 - x), (2**scale - 1 - y)
            x, y = y, x
        x += rx * (2**scale)
        y += ry * (2**scale)
        t //= 4
    return x, y


def verify_hilbert_curve(path: List[int], order: int) -> bool:
    """
    Verifies if a given path is a valid Hilbert curve of a specific order.
    1. Path length must be 4^order.
    2. Every index in the path must be unique and in range [0, 4^order - 1].
    3. The sequence of indices must match the Hilbert traversal.
    """
    expected_length = 4**order
    if len(path) != expected_length:
        raise ValueError(f"Hilbert curve path length {len(path)} does not match expected {expected_length}")

    width = 2**order
    seen_indices = set()

    for i, cell_index in enumerate(path):
        if cell_index < 0 or cell_index >= expected_length:
             raise ValueError(f"Path index {cell_index} is out of bounds [0, {expected_length-1}]")

        if cell_index in seen_indices:
            raise ValueError(f"Duplicate index {cell_index} found in path")
        seen_indices.add(cell_index)

        # Hilbert specific check:
        x, y = _hilbert_decode(i, order)
        expected_cell_index = y * width + x
        if cell_index != expected_cell_index:
            raise ValueError(
                f"Path mismatch at index {i}: expected cell {expected_cell_index} (coords {x},{y}), "
                f"got {cell_index}"
            )

    return True
