"""Grid walks and space-filling curve helpers."""

from __future__ import annotations

import math
import random


def simulate_random_walk_2d(n, m, start_x, start_y, max_steps=None):
    cx, cy = start_x, start_y
    visit_frequency = {(cx, cy): 1}
    total_steps = 0
    while max_steps is None or total_steps < max_steps:
        moves = []
        if cy + 1 < m:
            moves.append((0, 1))
        if cy - 1 >= 0:
            moves.append((0, -1))
        if cx - 1 >= 0:
            moves.append((-1, 0))
        if cx + 1 < n:
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


def simulate_random_walk_3d(n, m, l, start_x, start_y, start_z, max_steps=None):
    cx, cy, cz = start_x, start_y, start_z
    visit_frequency = {(cx, cy, cz): 1}
    total_steps = 0
    while max_steps is None or total_steps < max_steps:
        moves = [
            (dx, dy, dz)
            for dx, dy, dz in [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
            if 0 <= cx + dx < n and 0 <= cy + dy < m and 0 <= cz + dz < l
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
        "displacement": math.sqrt((cx - start_x) ** 2 + (cy - start_y) ** 2 + (cz - start_z) ** 2),
    }


def simulate_saw_2d(n, m, start_x, start_y):
    cx, cy = start_x, start_y
    visited = {(cx, cy)}
    path = [(cx, cy)]

    while len(visited) < n * m:
        moves = [
            (dx, dy)
            for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]
            if 0 <= cx + dx < n and 0 <= cy + dy < m and (cx + dx, cy + dy) not in visited
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


def peano_index_to_coords(index, level):
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


def morton_index_to_coords(index):
    x = y = 0
    for bit in range(32):
        x |= (index & (1 << (2 * bit))) >> bit
        y |= (index & (1 << (2 * bit + 1))) >> (bit + 1)
    return x, y


def hilbert_index_to_coords(index, order):
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


def generate_zigzag_path(width, height):
    path = []
    for diagonal in range(width + height - 1):
        if diagonal % 2 == 0:
            y = min(diagonal, height - 1)
            x = diagonal - y
            while y >= 0 and x < width:
                path.append((x, y))
                y -= 1
                x += 1
        else:
            x = min(diagonal, width - 1)
            y = diagonal - x
            while x >= 0 and y < height:
                path.append((x, y))
                x -= 1
                y += 1
    return path


def generate_spiral_path(width, height, start_x=None, start_y=None):
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
                if 0 <= cx < width and 0 <= cy < height and (cx, cy) not in visited:
                    path.append((cx, cy))
                    visited.add((cx, cy))
                if abs(cx - start_x) > width and abs(cy - start_y) > height:
                    break
            direction_index = (direction_index + 1) % 4
            if len(visited) >= width * height:
                break
        step_size += 1
        if abs(cx - start_x) > width and abs(cy - start_y) > height:
            break
    return path


__all__ = [
    "generate_spiral_path",
    "generate_zigzag_path",
    "hilbert_index_to_coords",
    "morton_index_to_coords",
    "peano_index_to_coords",
    "simulate_random_walk_2d",
    "simulate_random_walk_3d",
    "simulate_saw_2d",
]
