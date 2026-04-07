from __future__ import annotations

import math
from typing import List

from compgeom.kernel import Point2D, signed_area_twice

__all__ = ["minkowski_sum"]


def minkowski_sum(poly1: List[Point2D], poly2: List[Point2D]) -> List[Point2D]:
    if not poly1 or not poly2:
        return []

    def prepare_polygon(polygon: List[Point2D]) -> List[Point2D]:
        area_twice = signed_area_twice(polygon)
        ordered = polygon if area_twice >= 0 else list(reversed(polygon))
        start_index = min(
            range(len(ordered)), key=lambda index: (ordered[index].y, ordered[index].x)
        )
        return ordered[start_index:] + ordered[:start_index]

    p1 = prepare_polygon(poly1)
    p2 = prepare_polygon(poly2)
    p1.append(p1[0])
    p2.append(p2[0])

    result: List[Point2D] = []
    i = j = 0
    n = len(p1) - 1
    m = len(p2) - 1
    while i < n or j < m:
        result.append(Point2D(p1[i % n].x + p2[j % m].x, p1[i % n].y + p2[j % m].y))
        if i < n and j < m:
            angle1 = math.atan2(p1[i + 1].y - p1[i].y, p1[i + 1].x - p1[i].x) % (
                2 * math.pi
            )
            angle2 = math.atan2(p2[j + 1].y - p2[j].y, p2[j + 1].x - p2[j].x) % (
                2 * math.pi
            )
            if angle1 < angle2:
                i += 1
            elif angle1 > angle2:
                j += 1
            else:
                i += 1
                j += 1
        elif i < n:
            i += 1
        else:
            j += 1
    return result
