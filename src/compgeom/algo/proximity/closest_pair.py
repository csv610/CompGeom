from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from compgeom.kernel import Point2D, distance

__all__ = [
    "closest_pair_divide_and_conquer",
    "closest_pair_grid_based",
    "closest_pair",
]


def closest_pair_divide_and_conquer(
    points: List[Point2D],
) -> Tuple[float, Tuple[Optional[Point2D], Optional[Point2D]]]:
    """Traditional O(N log N) divide and conquer algorithm."""
    if not points:
        return float("inf"), (None, None)

    points_x = sorted(points, key=lambda p: p.x)
    points_y = sorted(points, key=lambda p: p.y)

    return _closest_pair_divide_and_conquer_recursive(points_x, points_y)


def _closest_pair_divide_and_conquer_recursive(
    points_x: List[Point2D], points_y: List[Point2D]
) -> Tuple[float, Tuple[Optional[Point2D], Optional[Point2D]]]:
    n = len(points_x)
    if n <= 3:
        min_dist = float("inf")
        pair = (None, None)
        for i in range(n):
            for j in range(i + 1, n):
                d = distance(points_x[i], points_x[j])
                if d < min_dist:
                    min_dist = d
                    pair = (points_x[i], points_x[j])
        return min_dist, pair

    mid = n // 2
    mid_point = points_x[mid]

    # Better way to split points_y in O(n):
    left_set = set(points_x[:mid])
    points_y_left = [p for p in points_y if p in left_set]
    points_y_right = [p for p in points_y if p not in left_set]

    d1, pair1 = _closest_pair_divide_and_conquer_recursive(points_x[:mid], points_y_left)
    d2, pair2 = _closest_pair_divide_and_conquer_recursive(
        points_x[mid:], points_y_right
    )

    if d1 < d2:
        best_d, best_pair = d1, pair1
    else:
        best_d, best_pair = d2, pair2

    strip = [p for p in points_y if abs(p.x - mid_point.x) < best_d]

    for i in range(len(strip)):
        for j in range(i + 1, len(strip)):
            if strip[j].y - strip[i].y >= best_d:
                break
            d = distance(strip[i], strip[j])
            if d < best_d:
                best_d = d
                best_pair = (strip[i], strip[j])

    return best_d, best_pair


def closest_pair_grid_based(
    points_iterator: Iterable[Point2D], sample_size: int = 1000
) -> Tuple[float, Tuple[Point2D, Point2D]]:
    """
    O(N) randomized grid-based algorithm for massive datasets.
    Suitable for billions of points as it can process them in a stream.
    """
    points_list = []
    try:
        for _ in range(sample_size):
            p = next(points_iterator)
            points_list.append(p)
    except StopIteration:
        pass

    if len(points_list) < 2:
        raise ValueError("Need at least 2 points.")

    best_d, best_pair = closest_pair_divide_and_conquer(points_list)

    grid: Dict[Tuple[int, int], Point2D] = {}

    def add_to_grid(p: Point2D, d: float):
        gx, gy = int(p.x / d), int(p.y / d)
        local_best_d = d
        local_pair = None

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                key = (gx + dx, gy + dy)
                if key in grid:
                    other = grid[key]
                    dist = distance(p, other)
                    if dist < local_best_d:
                        local_best_d = dist
                        local_pair = (p, other)

        if local_pair:
            return local_best_d, local_pair

        grid[(gx, gy)] = p
        return d, None

    for p in points_list:
        gx, gy = int(p.x / best_d), int(p.y / best_d)
        grid[(gx, gy)] = p

    for p in points_iterator:
        new_d, new_pair = add_to_grid(p, best_d)
        if new_pair:
            best_d = new_d
            best_pair = new_pair

    return best_d, best_pair


def closest_pair(points: List[Point2D]):
    """Wrapper for closest_pair_divide_and_conquer."""
    return closest_pair_divide_and_conquer(points)
