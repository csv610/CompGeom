from __future__ import annotations

from compgeom import Point, dist_point_to_segment, is_point_in_polygon
from compgeom.cli._shared import demo_polygon


def _polygon_distance(polygon_a: list[Point], polygon_b: list[Point]) -> float:
    if any(is_point_in_polygon(point, polygon_b) for point in polygon_a):
        return 0.0
    if any(is_point_in_polygon(point, polygon_a) for point in polygon_b):
        return 0.0

    best = float("inf")
    for point in polygon_a:
        for index, start in enumerate(polygon_b):
            end = polygon_b[(index + 1) % len(polygon_b)]
            best = min(best, dist_point_to_segment(point, start, end))

    for point in polygon_b:
        for index, start in enumerate(polygon_a):
            end = polygon_a[(index + 1) % len(polygon_a)]
            best = min(best, dist_point_to_segment(point, start, end))
    return best


def main() -> int:
    polygon_a = demo_polygon()[:4]
    polygon_b = [point.__class__(point.x + 8.0, point.y + 1.5) for point in demo_polygon()[:4]]
    distance = _polygon_distance(polygon_a, polygon_b)
    print(f"Minimum distance between polygons: {distance:.6f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
