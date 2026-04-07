from __future__ import annotations

from typing import List, Tuple
from compgeom.algo.rectangle_packing import PackedRect
from compgeom.kernel import EPSILON


def verify_rectangle_packing(original_dimensions: List[Tuple[float, float]], 
                            total_width: float, 
                            total_height: float, 
                            placements: List[PackedRect]) -> bool:
    """
    Rigorously verifies rectangle packing results.
    1. Every original rectangle must appear exactly once in the placements.
    2. Placements must have correct original dimensions.
    3. No two rectangles should overlap.
    4. All rectangles must be within the [total_width, total_height] container.
    """
    n = len(original_dimensions)
    if len(placements) != n:
        raise ValueError(f"Placement count {len(placements)} != original count {n}")

    # 1 & 2. Correct dimensions and uniqueness
    placed_ids = set()
    for p in placements:
        if p.id < 0 or p.id >= n:
            raise ValueError(f"Invalid rectangle id {p.id}")
        if p.id in placed_ids:
            raise ValueError(f"Duplicate rectangle id {p.id} in placements")
        placed_ids.add(p.id)
        
        orig_w, orig_h = original_dimensions[p.id]
        if abs(p.width - orig_w) > EPSILON or abs(p.height - orig_h) > EPSILON:
            # Check if rotated (if rotations were allowed, but here they aren't explicitly)
            if not (abs(p.width - orig_h) < EPSILON and abs(p.height - orig_w) < EPSILON):
                raise ValueError(f"Rectangle {p.id} dimensions {p.width}x{p.height} != original {orig_w}x{orig_h}")

    # 3. No overlaps: O(N^2)
    for i in range(len(placements)):
        for j in range(i + 1, len(placements)):
            r1 = placements[i]
            r2 = placements[j]
            
            # Standard rectangle intersection check
            if (r1.x < r2.x + r2.width - EPSILON and 
                r1.x + r1.width > r2.x + EPSILON and 
                r1.y < r2.y + r2.height - EPSILON and 
                r1.y + r1.height > r2.y + EPSILON):
                raise ValueError(f"Overlap detected between rectangle {r1.id} and {r2.id}")

    # 4. Container check
    for p in placements:
        if p.x < -EPSILON or p.y < -EPSILON:
             raise ValueError(f"Rectangle {p.id} has negative coordinates: ({p.x}, {p.y})")
        if p.x + p.width > total_width + EPSILON:
             raise ValueError(f"Rectangle {p.id} exceeds container width: {p.x + p.width} > {total_width}")
        if p.y + p.height > total_height + EPSILON:
             raise ValueError(f"Rectangle {p.id} exceeds container height: {p.y + p.height} > {total_height}")

    return True
