import random
import argparse

from compgeom import Point2D
from compgeom import welzl
from compgeom.cli._shared import demo_points


def _parse_points(lines: list[str]) -> list[Point2D]:
    points: list[Point2D] = []
    for line_number, line in enumerate(lines, start=1):
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"Line {line_number}: expected 2 numbers, got {len(parts)}.")
        try:
            points.append(Point2D(float(parts[0]), float(parts[1])))
        except ValueError as exc:
            raise ValueError(f"Line {line_number}: invalid numeric input.") from exc
    return points


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute the smallest enclosing circle for generated 2D points."
    )
    parser.add_argument("--demo", action="store_true", help="Use the built-in demo points.")
    args = parser.parse_args()
    points = [Point2D(point.x, point.y) for point in demo_points()]
    random.shuffle(points)
    center, radius = welzl(list(points), [])
    print(f"Smallest Enclosing Circle:\n  Center: ({center.x:.6f}, {center.y:.6f})\n  Radius: {radius:.6f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
