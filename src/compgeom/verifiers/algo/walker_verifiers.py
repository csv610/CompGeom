from __future__ import annotations

from typing import List, Tuple, Set


def verify_spiral_walker(path: List[Tuple], *args) -> bool:
    """Unified verifier for spiral walker paths."""
    if not path:
        return True
    
    dim = len(path[0])
    if dim == 2:
        return verify_spiral_walker_2d(path, *args)
    elif dim == 3:
        return verify_spiral_walker_3d(path, *args)
    else:
        raise ValueError(f"Unsupported path dimension: {dim}")


def verify_spiral_walker_2d(
    path: List[Tuple[int, int]], width: int, height: int
) -> bool:
    """
    Verifies a 2D spiral walker path.
    1. Every cell in the grid must be visited exactly once.
    2. Every step must be to an adjacent cell (distance 1).
    3. Path length must be width * height.
    """
    n = width * height
    if len(path) != n:
        raise ValueError(f"Path length {len(path)} != expected {n}")

    visited: Set[Tuple[int, int]] = set()
    for i in range(len(path)):
        curr = path[i]
        
        # 1. Bounds check
        if not (0 <= curr[0] < width and 0 <= curr[1] < height):
            raise ValueError(f"Point {curr} at index {i} is out of bounds")
            
        # 2. Uniqueness check
        if curr in visited:
            raise ValueError(f"Point {curr} at index {i} was already visited")
        visited.add(curr)
        
        # 3. Adjacency check
        if i > 0:
            prev = path[i-1]
            dist = abs(curr[0] - prev[0]) + abs(curr[1] - prev[1])
            if dist != 1:
                raise ValueError(f"Step from {prev} to {curr} (index {i}) is not adjacent (dist={dist})")
                
    return True


def verify_spiral_walker_3d(
    path: List[Tuple[int, int, int]], width: int, height: int, depth: int
) -> bool:
    """
    Verifies a 3D spiral walker path.
    1. Every cell in the grid must be visited exactly once.
    2. Every step must be to an adjacent cell (distance 1).
    3. Path length must be width * height * depth.
    """
    n = width * height * depth
    if len(path) != n:
        raise ValueError(f"Path length {len(path)} != expected {n}")

    visited: Set[Tuple[int, int, int]] = set()
    for i in range(len(path)):
        curr = path[i]
        
        # 1. Bounds check
        if not (0 <= curr[0] < width and 0 <= curr[1] < height and 0 <= curr[2] < depth):
            raise ValueError(f"Point {curr} at index {i} is out of bounds")
            
        # 2. Uniqueness check
        if curr in visited:
            raise ValueError(f"Point {curr} at index {i} was already visited")
        visited.add(curr)
        
        # 3. Adjacency check
        if i > 0:
            prev = path[i-1]
            dist = abs(curr[0] - prev[0]) + abs(curr[1] - prev[1]) + abs(curr[2] - prev[2])
            if dist != 1:
                raise ValueError(f"Step from {prev} to {curr} (index {i}) is not adjacent (dist={dist})")
                
    return True
