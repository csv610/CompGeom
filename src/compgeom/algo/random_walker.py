"""Grid walks and space-filling curve helpers."""

from __future__ import annotations

import math
import random
from typing import Dict, List, Optional, Set, Tuple

from compgeom.algo.space_filling_curves import SpaceFillingCurves


class RandomWalker:
    """Class for simulating random walks on discrete grids."""

    @staticmethod
    def simulate_2d(
        width: int, height: int, start_x: int, start_y: int, max_steps: Optional[int] = None
    ) -> Dict:
        """Simulate a random walk on a 2D grid."""
        cx, cy = start_x, start_y
        visit_frequency = {(cx, cy): 1}
        total_steps = 0
        while max_steps is None or total_steps < max_steps:
            moves = []
            if cy + 1 < height:
                moves.append((0, 1))
            if cy - 1 >= 0:
                moves.append((0, -1))
            if cx - 1 >= 0:
                moves.append((-1, 0))
            if cx + 1 < width:
                moves.append((1, 0))
            if not moves:
                break
            dx, dy = random.choice(moves)
            cx += dx
            cy += dy
            total_steps += 1
            visit_frequency[(cx, cy)] = visit_frequency.get((cx, cy), 0) + 1
        return {
            "steps": total_steps,
            "unique_cells": len(visit_frequency),
            "frequencies": visit_frequency,
            "final_pos": (cx, cy),
            "displacement": math.sqrt((cx - start_x) ** 2 + (cy - start_y) ** 2),
        }

    @staticmethod
    def simulate_3d(
        width: int,
        height: int,
        depth: int,
        start_x: int,
        start_y: int,
        start_z: int,
        max_steps: Optional[int] = None,
    ) -> Dict:
        """Simulate a random walk on a 3D grid."""
        cx, cy, cz = start_x, start_y, start_z
        visit_frequency = {(cx, cy, cz): 1}
        total_steps = 0
        while max_steps is None or total_steps < max_steps:
            moves = [
                (dx, dy, dz)
                for dx, dy, dz in [
                    (1, 0, 0),
                    (-1, 0, 0),
                    (0, 1, 0),
                    (0, -1, 0),
                    (0, 0, 1),
                    (0, 0, -1),
                ]
                if 0 <= cx + dx < width and 0 <= cy + dy < height and 0 <= cz + dz < depth
            ]
            if not moves:
                break
            dx, dy, dz = random.choice(moves)
            cx += dx
            cy += dy
            cz += dz
            total_steps += 1
            visit_frequency[(cx, cy, cz)] = visit_frequency.get((cx, cy, cz), 0) + 1
        return {
            "steps": total_steps,
            "unique_cells": len(visit_frequency),
            "frequencies": visit_frequency,
            "final_pos": (cx, cy, cz),
            "displacement": math.sqrt(
                (cx - start_x) ** 2 + (cy - start_y) ** 2 + (cz - start_z) ** 2
            ),
        }

    @staticmethod
    def simulate_saw_2d(width: int, height: int, start_x: int, start_y: int) -> Dict:
        """Simulate a self-avoiding walk (SAW) on a 2D grid."""
        cx, cy = start_x, start_y
        visited = {(cx, cy)}
        path = [(cx, cy)]

        while len(visited) < width * height:
            moves = [
                (dx, dy)
                for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]
                if 0 <= cx + dx < width
                and 0 <= cy + dy < height
                and (cx + dx, cy + dy) not in visited
            ]
            if not moves:
                return {
                    "steps": len(path) - 1,
                    "unique_cells": len(visited),
                    "path": path,
                    "final_pos": (cx, cy),
                    "displacement": math.sqrt((cx - start_x) ** 2 + (cy - start_y) ** 2),
                    "reason": "Trapped",
                }

            dx, dy = random.choice(moves)
            cx += dx
            cy += dy
            visited.add((cx, cy))
            path.append((cx, cy))

        return {
            "steps": len(path) - 1,
            "unique_cells": len(visited),
            "path": path,
            "final_pos": (cx, cy),
            "displacement": math.sqrt((cx - start_x) ** 2 + (cy - start_y) ** 2),
            "reason": "Success",
        }


def simulate_random_walk_2d(n, m, start_x, start_y, max_steps=None):
    return RandomWalker.simulate_2d(n, m, start_x, start_y, max_steps)


def simulate_random_walk_3d(n, m, l, start_x, start_y, start_z, max_steps=None):
    return RandomWalker.simulate_3d(n, m, l, start_x, start_y, start_z, max_steps)


def simulate_saw_2d(n, m, start_x, start_y):
    return RandomWalker.simulate_saw_2d(n, m, start_x, start_y)


def generate_zigzag_path(width, height):
    """Generate a zigzag (boustrophedon-like diagonal) path as (x,y) coordinates."""
    indices = SpaceFillingCurves.zigzag(width, height)
    return [(idx % width, idx // width) for idx in indices]


def generate_spiral_path(
    width: int, height: int, start_x: int | None = None, start_y: int | None = None
) -> List[Tuple[int, int]]:
    """Generate a 2D spiral path starting from a given point, visiting all cells."""
    if start_x is None:
        start_x = width // 2
    if start_y is None:
        start_y = height // 2

    path = [(start_x, start_y)]
    visited = {(start_x, start_y)}
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]
    step_size = 1
    direction_index = 0
    cx, cy = start_x, start_y

    while len(visited) < width * height:
        for _ in range(2):
            for _ in range(step_size):
                cx += dx[direction_index]
                cy += dy[direction_index]
                if 0 <= cx < width and 0 <= cy < height:
                    if (cx, cy) not in visited:
                        path.append((cx, cy))
                        visited.add((cx, cy))
            direction_index = (direction_index + 1) % 4
            if len(visited) >= width * height:
                break
        step_size += 1
        if step_size > max(width, height) * 2:
            break
            
    # If not all cells visited (e.g. start point was at edge), 
    # we might need to fill remaining. But spiral out usually works.
    return path


def generate_spiral_path_3d(
    width: int,
    height: int,
    depth: int,
    start_x: int | None = None,
    start_y: int | None = None,
    start_z: int | None = 0,
) -> List[Tuple[int, int, int]]:
    """Generate a 3D spiral path by stacking 2D spirals."""
    if start_x is None:
        start_x = width // 2
    if start_y is None:
        start_y = height // 2
    if start_z is None:
        start_z = 0

    full_path = []
    
    # We traverse Z layers. To keep the path continuous, 
    # we alternate between spiraling out and spiraling in.
    for z in range(depth):
        layer_path = generate_spiral_path(width, height, start_x, start_y)
        if z % 2 == 1:
            layer_path.reverse()
        
        for x, y in layer_path:
            full_path.append((x, y, z))
            
    return full_path


__all__ = [
    "RandomWalker",
    "generate_spiral_path",
    "generate_spiral_path_3d",
    "generate_zigzag_path",
    "simulate_random_walk_2d",
    "simulate_random_walk_3d",
    "simulate_saw_2d",
]
