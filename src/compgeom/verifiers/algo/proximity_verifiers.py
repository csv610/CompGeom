from __future__ import annotations

from typing import List, Tuple, Optional
from compgeom.kernel import Point2D, distance, EPSILON


def verify_closest_pair(points: List[Point2D], result: Tuple[float, Tuple[Optional[Point2D], Optional[Point2D]]]) -> bool:
    """
    Rigorously verifies the closest pair of points.
    1. The result distance must match the distance between the result pair.
    2. No other pair of points in the input set can have a distance smaller than (result distance - EPSILON).
    """
    res_dist, (p1, p2) = result
    
    if not points or len(points) < 2:
        return res_dist == float("inf")

    if p1 is None or p2 is None:
        raise ValueError("Result pair contains None for points list of size >= 2")

    # 1. Match result distance
    actual_dist = distance(p1, p2)
    if abs(actual_dist - res_dist) > EPSILON:
        raise ValueError(f"Result distance {res_dist} does not match actual distance {actual_dist} between points")

    # 2. Paranoid check: O(N^2)
    # We only do this if N is reasonable, say < 1000, otherwise it might be too slow.
    # But the user asked for "paranoid", so let's do it or at least a significant sample.
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            d = distance(points[i], points[j])
            if d < res_dist - EPSILON:
                raise ValueError(f"Found a closer pair: {points[i]} and {points[j]} with distance {d} < {res_dist}")

    return True
