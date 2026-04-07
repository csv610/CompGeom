import argparse
import math
import sys
from typing import List

from compgeom.kernel import Point2D
from compgeom.polygon import is_point_in_polygon

EPSILON = 1e-9


def _cross(a: Point2D, b: Point2D) -> float:
    return a.x * b.y - a.y * b.x


def _dot(a: Point2D, b: Point2D) -> float:
    return a.x * b.x + a.y * b.y


def _length(vector: Point2D) -> float:
    return math.hypot(vector.x, vector.y)


def _normalize(vector: Point2D) -> Point2D:
    magnitude = _length(vector)
    if magnitude < EPSILON:
        raise ValueError("Ray direction must be non-zero.")
    return Point2D(vector.x / magnitude, vector.y / magnitude)


def _ray_segment_intersection(
    origin: Point2D,
    direction: Point2D,
    start: Point2D,
    end: Point2D,
) -> tuple[float, float] | None:
    edge = Point2D(end.x - start.x, end.y - start.y)
    delta = Point2D(start.x - origin.x, start.y - origin.y)
    denominator = _cross(direction, edge)
    if abs(denominator) < EPSILON:
        return None

    distance = _cross(delta, edge) / denominator
    edge_factor = _cross(delta, direction) / denominator
    if distance <= EPSILON:
        return None
    if edge_factor < -EPSILON or edge_factor > 1 + EPSILON:
        return None
    return distance, min(max(edge_factor, 0.0), 1.0)


def simulate_reflections(
    origin: Point2D, direction: Point2D, polygon: list[Point2D], steps: int = 10
) -> list[Point2D]:
    path = [origin]
    current_point = origin
    current_direction = _normalize(direction)

    for _ in range(steps):
        best_hit = None
        min_dist = float("inf")
        hit_edge = None

        for i in range(len(polygon)):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % len(polygon)]

            res = _ray_segment_intersection(current_point, current_direction, p1, p2)
            if res:
                dist, _ = res
                if dist < min_dist:
                    min_dist = dist
                    best_hit = Point2D(
                        current_point.x + current_direction.x * dist,
                        current_point.y + current_direction.y * dist,
                    )
                    hit_edge = (p1, p2)

        if not best_hit:
            break

        path.append(best_hit)
        current_point = best_hit

        edge_vec = Point2D(hit_edge[1].x - hit_edge[0].x, hit_edge[1].y - hit_edge[0].y)
        edge_len = _length(edge_vec)
        normal = Point2D(-edge_vec.y / edge_len, edge_vec.x / edge_len)

        dot_val = _dot(current_direction, normal)
        current_direction = Point2D(
            current_direction.x - 2 * dot_val * normal.x,
            current_direction.y - 2 * dot_val * normal.y,
        )
        current_direction = _normalize(current_direction)

    return path


def _parse_point(line: str, name: str) -> Point2D:
    parts = line.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Invalid {name} format")
    return Point2D(float(parts[0]), float(parts[1]))


def parse_points(lines: list[str]) -> list[Point2D]:
    points = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        points.append(_parse_point(line, f"polygon point {i}"))
    return points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Simulate ray reflections in a polygon."
    )
    parser.add_argument("--steps", type=int, default=10, help="Number of reflections")
    args = parser.parse_args(argv)

    lines = []
    if not sys.stdin.isatty():
        try:
            lines = sys.stdin.readlines()
        except Exception:
            pass

    if not lines:
        lines = ["1 1", "1 0", "0 0", "4 0", "4 2", "0 2"]

    if len(lines) < 3:
        print("Error: Need at least 3 lines: origin, direction, polygon")
        return 1

    origin = _parse_point(lines[0], "origin")
    direction = _parse_point(lines[1], "direction")
    polygon = parse_points(lines[2:])

    if not is_point_in_polygon(origin, polygon):
        print("Error: Origin must be inside or on the boundary of the polygon")
        return 1

    path = simulate_reflections(origin, direction, polygon, args.steps)
    for p in path:
        print(f"{p.x} {p.y}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
